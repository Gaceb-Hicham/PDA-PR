"""
Application Streamlit - Plateforme EDT Examens
Version ULTRA-OPTIMISÉE pour performance maximale
"""
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date, time, datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configuration - Important: désactiver les avertissements
st.set_page_config(
    page_title="EDT Examens",
    page_icon="🎓",
    layout="wide"
)

# ============================================================================
# CONNEXION DB - CACHE PERSISTANT
# ============================================================================

@st.cache_resource
def init_database():
    """Initialise la connexion une seule fois au démarrage"""
    try:
        from database import execute_query, get_cursor
        return execute_query, get_cursor
    except Exception as e:
        st.error(f"Erreur connexion: {e}")
        return None, None

query_fn, cursor_fn = init_database()

def q(sql, params=None):
    """Requête rapide avec gestion d'erreur"""
    if not query_fn:
        return []
    try:
        result = query_fn(sql, params)
        return result if result else []
    except Exception as e:
        return []


# ============================================================================
# CACHE DES DONNÉES - TTL 5 MINUTES
# ============================================================================

@st.cache_data(ttl=300)
def get_departments():
    return q("SELECT id, nom, code FROM departements ORDER BY nom LIMIT 50")

@st.cache_data(ttl=300)
def get_formations():
    return q("""
        SELECT f.id, f.nom, f.code, f.niveau, d.nom as dept, d.id as dept_id
        FROM formations f 
        JOIN departements d ON f.dept_id = d.id
        ORDER BY d.nom, f.niveau, f.nom LIMIT 200
    """)

@st.cache_data(ttl=300)
def get_professors():
    return q("""
        SELECT p.id, p.nom, p.prenom, p.grade, d.nom as dept
        FROM professeurs p 
        JOIN departements d ON p.dept_id = d.id
        ORDER BY d.nom, p.nom LIMIT 500
    """)

@st.cache_data(ttl=300)  
def get_rooms():
    return q("SELECT id, nom, code, type, capacite FROM lieu_examen ORDER BY type, code LIMIT 100")

@st.cache_data(ttl=300)
def get_sessions():
    return q("SELECT id, nom, type_session, date_debut, date_fin, annee_universitaire FROM sessions_examen ORDER BY date_debut DESC LIMIT 10")

@st.cache_data(ttl=300)
def get_time_slots():
    return q("SELECT id, heure_debut, heure_fin, ordre FROM creneaux_horaires ORDER BY ordre")


def fmt_time(t):
    """Formater heure en HH:MM"""
    if t is None:
        return ""
    if hasattr(t, 'strftime'):
        return t.strftime('%H:%M')
    s = str(t)
    return s[:5] if len(s) >= 5 else s


# ============================================================================
# NAVIGATION
# ============================================================================

st.sidebar.title("🎓 EDT Examens")
st.sidebar.caption("Université M'Hamed Bougara")
st.sidebar.divider()

page = st.sidebar.radio("Navigation", [
    "🏠 Accueil",
    "⚙️ Configuration", 
    "📝 Saisie Données",
    "📅 Génération EDT",
    "📊 Plannings",
    "📄 Export PDF"
], label_visibility="collapsed")


# ============================================================================
# ACCUEIL
# ============================================================================

if "Accueil" in page:
    st.title("🎓 Plateforme EDT Examens")
    
    st.info("""
    **Fonctionnalités:**
    - Saisie manuelle des données (départements, formations, professeurs, salles)
    - Génération automatique des emplois du temps
    - Export PDF/Excel des plannings
    """)
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Départements", len(get_departments()))
    col2.metric("Formations", len(get_formations()))
    col3.metric("Professeurs", len(get_professors()))
    col4.metric("Salles", len(get_rooms()))


# ============================================================================
# CONFIGURATION
# ============================================================================

elif "Configuration" in page:
    st.title("⚙️ Configuration")
    
    tab1, tab2 = st.tabs(["📅 Session", "🕐 Créneaux"])
    
    with tab1:
        sessions = get_sessions()
        if sessions:
            st.dataframe(pd.DataFrame([{
                'Nom': s['nom'], 
                'Type': s['type_session'],
                'Début': s['date_debut'], 
                'Fin': s['date_fin']
            } for s in sessions]), hide_index=True)
        
        with st.form("session"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom", "Session S1 2025-2026")
            typ = c2.selectbox("Type", ["NORMALE", "RATTRAPAGE"])
            c3, c4 = st.columns(2)
            d1 = c3.date_input("Début", date(2026, 1, 6))
            d2 = c4.date_input("Fin", date(2026, 1, 24))
            annee = st.text_input("Année", "2025-2026")
            
            if st.form_submit_button("➕ Créer", type="primary"):
                q("""INSERT INTO sessions_examen (nom, type_session, annee_universitaire, date_debut, date_fin)
                     VALUES (%s, %s, %s, %s, %s)""", (nom, typ, annee, d1, d2))
                st.cache_data.clear()
                st.rerun()
    
    with tab2:
        slots = get_time_slots()
        if slots:
            st.dataframe(pd.DataFrame([{
                'Ordre': s['ordre'],
                'Début': fmt_time(s['heure_debut']),
                'Fin': fmt_time(s['heure_fin'])
            } for s in slots]), hide_index=True)
        
        with st.form("slot"):
            c1, c2, c3 = st.columns(3)
            ordre = c1.number_input("Ordre", 1, 10, len(slots)+1 if slots else 1)
            h1 = c2.time_input("Début", time(8, 0))
            h2 = c3.time_input("Fin", time(9, 30))
            
            if st.form_submit_button("➕ Ajouter", type="primary"):
                lib = f"{h1.strftime('%H:%M')} - {h2.strftime('%H:%M')}"
                q("""INSERT INTO creneaux_horaires (libelle, heure_debut, heure_fin, ordre)
                     VALUES (%s, %s, %s, %s)""", (lib, h1, h2, ordre))
                st.cache_data.clear()
                st.rerun()


# ============================================================================
# SAISIE DONNÉES
# ============================================================================

elif "Saisie" in page:
    st.title("📝 Saisie des Données")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏛️ Depts", "📚 Formations", "👨‍🏫 Profs", "🏢 Salles", "📖 Modules"])
    
    with tab1:
        depts = get_departments()
        if depts:
            st.dataframe(pd.DataFrame(depts)[['nom', 'code']], hide_index=True)
        
        with st.form("dept"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom")
            code = c2.text_input("Code")
            if st.form_submit_button("➕", type="primary") and nom:
                q("INSERT INTO departements (nom, code) VALUES (%s, %s)", (nom, code))
                st.cache_data.clear()
                st.rerun()
    
    with tab2:
        forms = get_formations()
        if forms:
            st.dataframe(pd.DataFrame([{
                'Formation': f['nom'], 'Code': f['code'], 'Niveau': f['niveau'], 'Dept': f['dept']
            } for f in forms[:50]]), hide_index=True)
        
        depts = get_departments()
        if depts:
            with st.form("form"):
                c1, c2, c3 = st.columns(3)
                dept = c1.selectbox("Dept", [d['nom'] for d in depts])
                nom = c2.text_input("Nom")
                code = c3.text_input("Code")
                niveau = st.selectbox("Niveau", ["L1", "L2", "L3", "M1", "M2"])
                
                if st.form_submit_button("➕", type="primary") and nom:
                    did = next(d['id'] for d in depts if d['nom'] == dept)
                    q("""INSERT INTO formations (nom, code, dept_id, niveau, nb_modules)
                         VALUES (%s, %s, %s, %s, 6)""", (f"{niveau} - {nom}", code, did, niveau))
                    st.cache_data.clear()
                    st.rerun()
    
    with tab3:
        profs = get_professors()
        if profs:
            st.dataframe(pd.DataFrame([{
                'Nom': p['nom'], 'Prénom': p['prenom'], 'Grade': p['grade'], 'Dept': p['dept']
            } for p in profs[:50]]), hide_index=True)
        
        depts = get_departments()
        if depts:
            with st.form("prof"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom")
                prenom = c2.text_input("Prénom")
                c3, c4 = st.columns(2)
                dept = c3.selectbox("Dept", [d['nom'] for d in depts])
                grade = c4.selectbox("Grade", ["MAA", "MAB", "MCA", "MCB", "PR"])
                
                if st.form_submit_button("➕", type="primary") and nom:
                    did = next(d['id'] for d in depts if d['nom'] == dept)
                    mat = f"P{did}{nom[:3].upper()}{len(profs)}"
                    q("""INSERT INTO professeurs (matricule, nom, prenom, dept_id, grade)
                         VALUES (%s, %s, %s, %s, %s)""", (mat, nom, prenom, did, grade))
                    st.cache_data.clear()
                    st.rerun()
    
    with tab4:
        rooms = get_rooms()
        if rooms:
            st.dataframe(pd.DataFrame([{
                'Nom': r['nom'], 'Code': r['code'], 'Type': r['type'], 'Capacité': r['capacite']
            } for r in rooms]), hide_index=True)
        
        with st.form("room"):
            c1, c2, c3 = st.columns(3)
            nom = c1.text_input("Nom")
            code = c2.text_input("Code")
            typ = c3.selectbox("Type", ["AMPHI", "SALLE", "LABO"])
            cap = st.number_input("Capacité", 10, 500, 100)
            
            if st.form_submit_button("➕", type="primary") and nom:
                q("""INSERT INTO lieu_examen (nom, code, capacite, type, disponible)
                     VALUES (%s, %s, %s, %s, TRUE)""", (nom, code, cap, typ))
                st.cache_data.clear()
                st.rerun()
    
    with tab5:
        forms = get_formations()
        if forms:
            sel = st.selectbox("Formation", [f['nom'] for f in forms])
            fid = next(f['id'] for f in forms if f['nom'] == sel)
            
            mods = q("SELECT code, nom, credits, semestre FROM modules WHERE formation_id = %s LIMIT 50", (fid,))
            if mods:
                st.dataframe(pd.DataFrame(mods), hide_index=True)
            
            with st.form("mod"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom")
                code = c2.text_input("Code")
                c3, c4 = st.columns(2)
                sem = c3.selectbox("Semestre", ["S1", "S2"])
                cred = c4.number_input("Crédits", 1, 10, 4)
                
                if st.form_submit_button("➕", type="primary") and nom:
                    q("""INSERT INTO modules (code, nom, credits, formation_id, semestre)
                         VALUES (%s, %s, %s, %s, %s)""", (code, nom, cred, fid, sem))
                    st.rerun()


# ============================================================================
# GÉNÉRATION EDT
# ============================================================================

elif "Génération" in page:
    st.title("📅 Génération EDT")
    
    sessions = get_sessions()
    if not sessions:
        st.warning("⚠️ Créez d'abord une session dans Configuration")
    else:
        sel = st.selectbox("Session", [s['nom'] for s in sessions])
        sid = next(s['id'] for s in sessions if s['nom'] == sel)
        
        if st.button("🚀 Générer le Planning", type="primary", use_container_width=True):
            with st.spinner("Génération..."):
                try:
                    q("DELETE FROM surveillances WHERE examen_id IN (SELECT id FROM examens WHERE session_id = %s)", (sid,))
                    q("DELETE FROM examens WHERE session_id = %s", (sid,))
                    
                    from services.optimization import run_optimization
                    report = run_optimization(sid)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("✅ Examens", report.get('scheduled', 0))
                    c2.metric("⚠️ Conflits", report.get('conflicts', 0))
                    c3.metric("⏱️ Temps", f"{report.get('execution_time', 0):.1f}s")
                    
                    st.success("Terminé!")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Erreur: {e}")


# ============================================================================
# PLANNINGS
# ============================================================================

elif "Plannings" in page:
    st.title("📊 Plannings")
    
    tab1, tab2, tab3 = st.tabs(["Par Formation", "Par Professeur", "Par Salle"])
    
    with tab1:
        forms = get_formations()
        if forms:
            sel = st.selectbox("Formation", [f['nom'] for f in forms], key="pf")
            fid = next(f['id'] for f in forms if f['nom'] == sel)
            
            exams = q("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut, '%H:%i'), ' - ', TIME_FORMAT(ch.heure_fin, '%H:%i')) as Horaire,
                       CONCAT(m.nom, ' (', m.code, ')') as Module,
                       l.code as Salle
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE m.formation_id = %s
                ORDER BY e.date_examen, ch.ordre LIMIT 100
            """, (fid,))
            
            if exams:
                st.dataframe(pd.DataFrame(exams), hide_index=True, use_container_width=True)
            else:
                st.info("Aucun examen planifié")
    
    with tab2:
        profs = get_professors()
        if profs:
            sel = st.selectbox("Professeur", [f"{p['prenom']} {p['nom']}" for p in profs], key="pp")
            pid = next(p['id'] for p in profs if f"{p['prenom']} {p['nom']}" == sel)
            
            survs = q("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut, '%H:%i'), ' - ', TIME_FORMAT(ch.heure_fin, '%H:%i')) as Horaire,
                       m.nom as Module, l.code as Salle, s.role as Rôle
                FROM surveillances s
                JOIN examens e ON s.examen_id = e.id
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE s.professeur_id = %s
                ORDER BY e.date_examen, ch.ordre LIMIT 100
            """, (pid,))
            
            if survs:
                st.dataframe(pd.DataFrame(survs), hide_index=True, use_container_width=True)
            else:
                st.info("Aucune surveillance")
    
    with tab3:
        rooms = get_rooms()
        if rooms:
            sel = st.selectbox("Salle", [f"{r['code']} - {r['nom']}" for r in rooms], key="pr")
            rid = next(r['id'] for r in rooms if f"{r['code']} - {r['nom']}" == sel)
            
            exams = q("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut, '%H:%i'), ' - ', TIME_FORMAT(ch.heure_fin, '%H:%i')) as Horaire,
                       m.nom as Module, f.nom as Formation
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN formations f ON m.formation_id = f.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE e.salle_id = %s
                ORDER BY e.date_examen, ch.ordre LIMIT 100
            """, (rid,))
            
            if exams:
                st.dataframe(pd.DataFrame(exams), hide_index=True, use_container_width=True)
            else:
                st.info("Aucun examen")


# ============================================================================
# EXPORT PDF
# ============================================================================

elif "PDF" in page:
    st.title("📄 Export PDF")
    
    tab1, tab2, tab3 = st.tabs(["Étudiants", "Professeurs", "Salles"])
    
    with tab1:
        forms = get_formations()
        if forms:
            sel = st.selectbox("Formation", [f['nom'] for f in forms], key="pdf1")
            fid = next(f['id'] for f in forms if f['nom'] == sel)
            groupe = st.text_input("Groupe", "G01")
            
            if st.button("📄 Générer PDF", key="b1", type="primary"):
                exams = q("""
                    SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin,
                           m.code as module_code, m.nom as module_nom, l.code as salle
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN lieu_examen l ON e.salle_id = l.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    WHERE m.formation_id = %s
                    ORDER BY e.date_examen, ch.ordre
                """, (fid,))
                
                if exams:
                    try:
                        from services.pdf_generator import generate_student_schedule_pdf
                        f_data = next(f for f in forms if f['id'] == fid)
                        pdf = generate_student_schedule_pdf(sel.split(" - ")[-1], groupe, f_data['niveau'], exams)
                        st.download_button("⬇️ Télécharger", pdf, f"planning_{groupe}.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucun examen")
    
    with tab2:
        profs = get_professors()
        if profs:
            sel = st.selectbox("Professeur", [f"{p['prenom']} {p['nom']} ({p['dept']})" for p in profs], key="pdf2")
            pdata = next(p for p in profs if f"{p['prenom']} {p['nom']} ({p['dept']})" == sel)
            
            if st.button("📄 Générer PDF", key="b2", type="primary"):
                survs = q("""
                    SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin,
                           m.code as module_code, m.nom as module_nom, l.code as salle, s.role
                    FROM surveillances s
                    JOIN examens e ON s.examen_id = e.id
                    JOIN modules m ON e.module_id = m.id
                    JOIN lieu_examen l ON e.salle_id = l.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    WHERE s.professeur_id = %s ORDER BY e.date_examen
                """, (pdata['id'],))
                
                if survs:
                    try:
                        from services.pdf_generator import generate_professor_schedule_pdf
                        pdf = generate_professor_schedule_pdf(pdata['nom'], pdata['prenom'], pdata['dept'], survs)
                        st.download_button("⬇️ Télécharger", pdf, f"surv_{pdata['nom']}.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucune surveillance")
    
    with tab3:
        rooms = get_rooms()
        if rooms:
            sel = st.selectbox("Salle", [f"{r['code']} - {r['nom']} ({r['capacite']} places)" for r in rooms], key="pdf3")
            rdata = next(r for r in rooms if f"{r['code']} - {r['nom']} ({r['capacite']} places)" == sel)
            
            if st.button("📄 Générer PDF", key="b3", type="primary"):
                exams = q("""
                    SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin,
                           m.code as module_code, m.nom as module_nom, f.nom as formation
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN formations f ON m.formation_id = f.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    WHERE e.salle_id = %s ORDER BY e.date_examen
                """, (rdata['id'],))
                
                if exams:
                    try:
                        from services.pdf_generator import generate_room_schedule_pdf
                        pdf = generate_room_schedule_pdf(rdata['nom'], rdata['code'], rdata['capacite'], exams)
                        st.download_button("⬇️ Télécharger", pdf, f"salle_{rdata['code']}.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucun examen")
