"""
Application Streamlit - Plateforme EDT Examens
Version optimisée avec cache et saisie manuelle complète
"""
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date, time, datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configuration
st.set_page_config(
    page_title="Plateforme EDT Examens",
    page_icon="🎓",
    layout="wide"
)

# ============================================================================
# CONNEXION BASE DE DONNÉES
# ============================================================================

@st.cache_resource
def get_db_connection():
    """Initialise la connexion une seule fois"""
    try:
        from database import execute_query, get_cursor
        return execute_query, get_cursor
    except Exception as e:
        return None, None

query_fn, cursor_fn = get_db_connection()


def safe_query(sql, params=None, fetch='all'):
    """Exécute une requête de manière sécurisée"""
    if not query_fn:
        return [] if fetch == 'all' else None
    try:
        return query_fn(sql, params, fetch=fetch)
    except Exception as e:
        st.error(f"Erreur DB: {e}")
        return [] if fetch == 'all' else None


# ============================================================================
# DONNÉES CACHÉES (pour performance)
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def load_departments():
    return safe_query("SELECT id, nom, code FROM departements ORDER BY nom") or []

@st.cache_data(ttl=300, show_spinner=False)
def load_formations():
    return safe_query("""
        SELECT f.id, f.nom, f.code, f.niveau, d.nom as dept, d.id as dept_id
        FROM formations f JOIN departements d ON f.dept_id = d.id
        ORDER BY d.nom, f.niveau, f.nom
    """) or []

@st.cache_data(ttl=300, show_spinner=False)
def load_professors():
    return safe_query("""
        SELECT p.id, p.nom, p.prenom, p.grade, d.nom as dept, d.id as dept_id
        FROM professeurs p JOIN departements d ON p.dept_id = d.id
        ORDER BY d.nom, p.nom
    """) or []

@st.cache_data(ttl=300, show_spinner=False)
def load_rooms():
    return safe_query("SELECT id, nom, code, type, capacite FROM lieu_examen ORDER BY type, code") or []

@st.cache_data(ttl=300, show_spinner=False)
def load_sessions():
    return safe_query("SELECT id, nom, semestre, date_debut, date_fin FROM sessions_examen ORDER BY date_debut DESC") or []

@st.cache_data(ttl=300, show_spinner=False)
def load_time_slots():
    return safe_query("""
        SELECT id, heure_debut, heure_fin, ordre 
        FROM creneaux_horaires ORDER BY ordre
    """) or []


def format_time(t):
    """Formate un temps en HH:MM"""
    if t is None:
        return ""
    if hasattr(t, 'strftime'):
        return t.strftime('%H:%M')
    return str(t)[:5]


def export_excel(df, name):
    """Export DataFrame en Excel"""
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf


# ============================================================================
# NAVIGATION
# ============================================================================

st.sidebar.title("🎓 EDT Examens")
st.sidebar.caption("Université M'Hamed Bougara")
st.sidebar.divider()

pages = [
    "🏠 Accueil",
    "⚙️ Configuration",
    "📝 Saisie Données",
    "📅 Génération EDT",
    "📊 Plannings",
    "📄 Export PDF"
]

page = st.sidebar.radio("Navigation", pages, label_visibility="collapsed")


# ============================================================================
# PAGE: ACCUEIL
# ============================================================================

if "Accueil" in page:
    st.title("🎓 Plateforme EDT Examens")
    
    st.info("""
    **Cette plateforme permet de:**
    - Saisir manuellement toutes les données (départements, formations, professeurs, salles, créneaux)
    - Générer automatiquement les emplois du temps d'examens
    - Exporter les plannings en PDF/Excel
    """)
    
    # Stats rapides
    depts = load_departments()
    forms = load_formations()
    profs = load_professors()
    rooms = load_rooms()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏛️ Départements", len(depts))
    col2.metric("📚 Formations", len(forms))
    col3.metric("👨‍🏫 Professeurs", len(profs))
    col4.metric("🏢 Salles", len(rooms))
    
    st.divider()
    st.subheader("📋 Workflow")
    st.markdown("""
    1. **Configuration** → Définir les dates de session et créneaux horaires
    2. **Saisie Données** → Ajouter départements, formations, profs, salles, modules
    3. **Génération EDT** → L'algorithme crée automatiquement le planning
    4. **Plannings** → Consulter et exporter les résultats
    """)


# ============================================================================
# PAGE: CONFIGURATION (Session et Créneaux)
# ============================================================================

elif "Configuration" in page:
    st.title("⚙️ Configuration")
    
    tab1, tab2 = st.tabs(["📅 Session d'Examens", "🕐 Créneaux Horaires"])
    
    with tab1:
        st.subheader("Définir la session d'examens")
        
        sessions = load_sessions()
        if sessions:
            st.dataframe(pd.DataFrame([{
                'Nom': s['nom'],
                'Semestre': s['semestre'],
                'Début': s['date_debut'],
                'Fin': s['date_fin']
            } for s in sessions]), use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("**Ajouter une nouvelle session:**")
        
        with st.form("session_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom", value="Session S1 2025-2026")
            semestre = c2.selectbox("Semestre", ["S1", "S2"])
            
            c3, c4 = st.columns(2)
            debut = c3.date_input("Date début", value=date(2026, 1, 6))
            fin = c4.date_input("Date fin", value=date(2026, 1, 24))
            
            annee = st.text_input("Année universitaire", value="2025-2026")
            
            if st.form_submit_button("➕ Créer Session", type="primary"):
                try:
                    safe_query("""
                        INSERT INTO sessions_examen (nom, semestre, annee_universitaire, date_debut, date_fin, active)
                        VALUES (%s, %s, %s, %s, %s, TRUE)
                    """, (nom, semestre, annee, debut, fin), fetch='none')
                    st.success("✅ Session créée!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
    
    with tab2:
        st.subheader("Créneaux horaires")
        st.caption("Les heures exactes pour les examens")
        
        slots = load_time_slots()
        if slots:
            st.dataframe(pd.DataFrame([{
                'Ordre': s['ordre'],
                'Début': format_time(s['heure_debut']),
                'Fin': format_time(s['heure_fin'])
            } for s in slots]), use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("**Ajouter un créneau:**")
        
        with st.form("slot_form"):
            c1, c2, c3 = st.columns(3)
            ordre = c1.number_input("Ordre", min_value=1, max_value=10, value=len(slots)+1 if slots else 1)
            h_debut = c2.time_input("Heure début", value=time(8, 0))
            h_fin = c3.time_input("Heure fin", value=time(9, 30))
            
            if st.form_submit_button("➕ Ajouter", type="primary"):
                try:
                    libelle = f"{h_debut.strftime('%H:%M')} - {h_fin.strftime('%H:%M')}"
                    safe_query("""
                        INSERT INTO creneaux_horaires (libelle, heure_debut, heure_fin, ordre)
                        VALUES (%s, %s, %s, %s)
                    """, (libelle, h_debut, h_fin, ordre), fetch='none')
                    st.success("✅ Créneau ajouté!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")


# ============================================================================
# PAGE: SAISIE DONNÉES
# ============================================================================

elif "Saisie" in page:
    st.title("📝 Saisie des Données")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏛️ Départements", "📚 Formations", "👨‍🏫 Professeurs", "🏢 Salles", "📖 Modules"
    ])
    
    # --- DÉPARTEMENTS ---
    with tab1:
        depts = load_departments()
        if depts:
            st.dataframe(pd.DataFrame(depts)[['nom', 'code']], use_container_width=True, hide_index=True)
        
        with st.form("dept_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom du département")
            code = c2.text_input("Code (ex: INFO)")
            
            if st.form_submit_button("➕ Ajouter", type="primary"):
                if nom and code:
                    safe_query("INSERT INTO departements (nom, code) VALUES (%s, %s)", (nom, code), fetch='none')
                    st.success("✅ Département ajouté!")
                    st.cache_data.clear()
                    st.rerun()
    
    # --- FORMATIONS ---
    with tab2:
        forms = load_formations()
        if forms:
            st.dataframe(pd.DataFrame([{
                'Formation': f['nom'], 'Code': f['code'], 'Niveau': f['niveau'], 'Département': f['dept']
            } for f in forms]), use_container_width=True, hide_index=True)
        
        depts = load_departments()
        if depts:
            with st.form("form_form"):
                c1, c2, c3 = st.columns(3)
                dept = c1.selectbox("Département", [d['nom'] for d in depts])
                nom = c2.text_input("Nom (ex: Génie Logiciel)")
                code = c3.text_input("Code (ex: GL)")
                niveau = st.selectbox("Niveau", ["L1", "L2", "L3", "M1", "M2"])
                
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if nom and code:
                        dept_id = next(d['id'] for d in depts if d['nom'] == dept)
                        safe_query("""
                            INSERT INTO formations (nom, code, dept_id, niveau, nb_modules)
                            VALUES (%s, %s, %s, %s, 6)
                        """, (f"{niveau} - {nom}", code, dept_id, niveau), fetch='none')
                        st.success("✅ Formation ajoutée!")
                        st.cache_data.clear()
                        st.rerun()
    
    # --- PROFESSEURS ---
    with tab3:
        profs = load_professors()
        if profs:
            st.dataframe(pd.DataFrame([{
                'Nom': p['nom'], 'Prénom': p['prenom'], 'Grade': p['grade'], 'Département': p['dept']
            } for p in profs[:50]]), use_container_width=True, hide_index=True)
        
        depts = load_departments()
        if depts:
            with st.form("prof_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom")
                prenom = c2.text_input("Prénom")
                c3, c4 = st.columns(2)
                dept = c3.selectbox("Département", [d['nom'] for d in depts])
                grade = c4.selectbox("Grade", ["MAA", "MAB", "MCA", "MCB", "PR"])
                
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if nom and prenom:
                        dept_id = next(d['id'] for d in depts if d['nom'] == dept)
                        matricule = f"P{dept_id}{nom[:3].upper()}{len(profs)}"
                        safe_query("""
                            INSERT INTO professeurs (matricule, nom, prenom, dept_id, grade)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (matricule, nom, prenom, dept_id, grade), fetch='none')
                        st.success("✅ Professeur ajouté!")
                        st.cache_data.clear()
                        st.rerun()
    
    # --- SALLES ---
    with tab4:
        rooms = load_rooms()
        if rooms:
            st.dataframe(pd.DataFrame([{
                'Nom': r['nom'], 'Code': r['code'], 'Type': r['type'], 'Capacité': r['capacite']
            } for r in rooms]), use_container_width=True, hide_index=True)
        
        with st.form("room_form"):
            c1, c2, c3 = st.columns(3)
            nom = c1.text_input("Nom (ex: Amphithéâtre 10)")
            code = c2.text_input("Code (ex: AMP10)")
            type_s = c3.selectbox("Type", ["AMPHI", "SALLE", "LABO"])
            capacite = st.number_input("Capacité", min_value=10, max_value=500, value=100)
            
            if st.form_submit_button("➕ Ajouter", type="primary"):
                if nom and code:
                    safe_query("""
                        INSERT INTO lieu_examen (nom, code, capacite, type, disponible)
                        VALUES (%s, %s, %s, %s, TRUE)
                    """, (nom, code, capacite, type_s), fetch='none')
                    st.success("✅ Salle ajoutée!")
                    st.cache_data.clear()
                    st.rerun()
    
    # --- MODULES ---
    with tab5:
        forms = load_formations()
        if forms:
            form_sel = st.selectbox("Formation:", [f['nom'] for f in forms])
            form_id = next(f['id'] for f in forms if f['nom'] == form_sel)
            
            modules = safe_query("""
                SELECT m.code, m.nom, m.credits, m.semestre
                FROM modules m WHERE m.formation_id = %s
                ORDER BY m.semestre, m.nom
            """, (form_id,))
            
            if modules:
                st.dataframe(pd.DataFrame(modules), use_container_width=True, hide_index=True)
            
            with st.form("module_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom du module")
                code = c2.text_input("Code (ex: AAC)")
                c3, c4 = st.columns(2)
                semestre = c3.selectbox("Semestre", ["S1", "S2"])
                credits = c4.number_input("Crédits", min_value=1, max_value=10, value=4)
                
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if nom and code:
                        safe_query("""
                            INSERT INTO modules (code, nom, credits, formation_id, semestre)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (code, nom, credits, form_id, semestre), fetch='none')
                        st.success("✅ Module ajouté!")
                        st.rerun()


# ============================================================================
# PAGE: GÉNÉRATION EDT
# ============================================================================

elif "Génération" in page:
    st.title("📅 Génération de l'EDT")
    
    sessions = load_sessions()
    if not sessions:
        st.warning("⚠️ Créez d'abord une session dans Configuration")
    else:
        session = st.selectbox("Session:", [s['nom'] for s in sessions])
        session_id = next(s['id'] for s in sessions if s['nom'] == session)
        
        st.info(f"Session: {session}")
        
        if st.button("🚀 Générer le Planning", type="primary", use_container_width=True):
            with st.spinner("Génération en cours..."):
                try:
                    # Supprimer anciens résultats
                    safe_query("DELETE FROM surveillances WHERE examen_id IN (SELECT id FROM examens WHERE session_id = %s)", (session_id,), fetch='none')
                    safe_query("DELETE FROM examens WHERE session_id = %s", (session_id,), fetch='none')
                    
                    from services.optimization import run_optimization
                    report = run_optimization(session_id)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("✅ Examens", report.get('scheduled', 0))
                    c2.metric("⚠️ Conflits", report.get('conflicts', 0))
                    c3.metric("⏱️ Temps", f"{report.get('execution_time', 0):.1f}s")
                    
                    st.success("Génération terminée!")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Erreur: {e}")


# ============================================================================
# PAGE: PLANNINGS
# ============================================================================

elif "Plannings" in page:
    st.title("📊 Plannings")
    
    tab1, tab2, tab3 = st.tabs(["👨‍🎓 Par Formation", "👨‍🏫 Par Professeur", "🏢 Par Salle"])
    
    with tab1:
        forms = load_formations()
        if forms:
            form = st.selectbox("Formation:", [f['nom'] for f in forms], key="pf")
            form_id = next(f['id'] for f in forms if f['nom'] == form)
            
            exams = safe_query("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut, '%H:%i'), ' - ', TIME_FORMAT(ch.heure_fin, '%H:%i')) as Horaire,
                       CONCAT(m.nom, ' (', m.code, ')') as Module,
                       l.code as Salle
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE m.formation_id = %s
                ORDER BY e.date_examen, ch.ordre
            """, (form_id,))
            
            if exams:
                df = pd.DataFrame(exams)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("📥 Excel", export_excel(df, "planning"), "planning.xlsx")
            else:
                st.info("Aucun examen planifié")
    
    with tab2:
        profs = load_professors()
        if profs:
            prof = st.selectbox("Professeur:", [f"{p['prenom']} {p['nom']}" for p in profs], key="pp")
            prof_id = next(p['id'] for p in profs if f"{p['prenom']} {p['nom']}" == prof)
            
            survs = safe_query("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut, '%H:%i'), ' - ', TIME_FORMAT(ch.heure_fin, '%H:%i')) as Horaire,
                       CONCAT(m.nom, ' (', m.code, ')') as Module,
                       l.code as Salle,
                       s.role as Rôle
                FROM surveillances s
                JOIN examens e ON s.examen_id = e.id
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE s.professeur_id = %s
                ORDER BY e.date_examen, ch.ordre
            """, (prof_id,))
            
            if survs:
                df = pd.DataFrame(survs)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("📥 Excel", export_excel(df, "surveillances"), "surveillances.xlsx")
            else:
                st.info("Aucune surveillance assignée")
    
    with tab3:
        rooms = load_rooms()
        if rooms:
            room = st.selectbox("Salle:", [f"{r['code']} - {r['nom']}" for r in rooms], key="pr")
            room_id = next(r['id'] for r in rooms if f"{r['code']} - {r['nom']}" == room)
            
            exams = safe_query("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut, '%H:%i'), ' - ', TIME_FORMAT(ch.heure_fin, '%H:%i')) as Horaire,
                       CONCAT(m.nom, ' (', m.code, ')') as Module,
                       f.nom as Formation
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN formations f ON m.formation_id = f.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE e.salle_id = %s
                ORDER BY e.date_examen, ch.ordre
            """, (room_id,))
            
            if exams:
                df = pd.DataFrame(exams)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun examen dans cette salle")


# ============================================================================
# PAGE: EXPORT PDF
# ============================================================================

elif "PDF" in page:
    st.title("📄 Export PDF")
    
    tab1, tab2, tab3 = st.tabs(["👨‍🎓 Étudiants", "👨‍🏫 Professeurs", "🏢 Salles"])
    
    with tab1:
        forms = load_formations()
        if forms:
            form = st.selectbox("Formation:", [f['nom'] for f in forms], key="pdf_f")
            form_id = next(f['id'] for f in forms if f['nom'] == form)
            groupe = st.text_input("Groupe:", value="G01")
            
            if st.button("📄 Générer PDF", type="primary", key="pdf_b1"):
                exams = safe_query("""
                    SELECT e.date_examen as date,
                           ch.heure_debut, ch.heure_fin,
                           m.code as module_code, m.nom as module_nom,
                           l.code as salle
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN lieu_examen l ON e.salle_id = l.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    WHERE m.formation_id = %s
                    ORDER BY e.date_examen, ch.ordre
                """, (form_id,))
                
                if exams:
                    from services.pdf_generator import generate_student_schedule_pdf
                    niveau = next(f['niveau'] for f in forms if f['id'] == form_id)
                    pdf = generate_student_schedule_pdf(form.split(" - ")[-1], groupe, niveau, exams)
                    st.download_button("⬇️ Télécharger", pdf, f"planning_{groupe}.pdf", "application/pdf")
                else:
                    st.warning("Aucun examen")
    
    with tab2:
        profs = load_professors()
        if profs:
            prof = st.selectbox("Professeur:", [f"{p['prenom']} {p['nom']} ({p['dept']})" for p in profs], key="pdf_p")
            prof_data = next(p for p in profs if f"{p['prenom']} {p['nom']} ({p['dept']})" == prof)
            
            if st.button("📄 Générer PDF", type="primary", key="pdf_b2"):
                survs = safe_query("""
                    SELECT e.date_examen as date,
                           ch.heure_debut, ch.heure_fin,
                           m.code as module_code, m.nom as module_nom,
                           l.code as salle, s.role
                    FROM surveillances s
                    JOIN examens e ON s.examen_id = e.id
                    JOIN modules m ON e.module_id = m.id
                    JOIN lieu_examen l ON e.salle_id = l.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    WHERE s.professeur_id = %s
                    ORDER BY e.date_examen, ch.ordre
                """, (prof_data['id'],))
                
                if survs:
                    from services.pdf_generator import generate_professor_schedule_pdf
                    pdf = generate_professor_schedule_pdf(prof_data['nom'], prof_data['prenom'], prof_data['dept'], survs)
                    st.download_button("⬇️ Télécharger", pdf, f"surveillances_{prof_data['nom']}.pdf", "application/pdf")
                else:
                    st.warning("Aucune surveillance")
    
    with tab3:
        rooms = load_rooms()
        if rooms:
            room = st.selectbox("Salle:", [f"{r['code']} - {r['nom']} ({r['capacite']} places)" for r in rooms], key="pdf_r")
            room_data = next(r for r in rooms if f"{r['code']} - {r['nom']} ({r['capacite']} places)" == room)
            
            if st.button("📄 Générer PDF", type="primary", key="pdf_b3"):
                exams = safe_query("""
                    SELECT e.date_examen as date,
                           ch.heure_debut, ch.heure_fin,
                           m.code as module_code, m.nom as module_nom,
                           f.nom as formation
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN formations f ON m.formation_id = f.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    WHERE e.salle_id = %s
                    ORDER BY e.date_examen, ch.ordre
                """, (room_data['id'],))
                
                if exams:
                    from services.pdf_generator import generate_room_schedule_pdf
                    pdf = generate_room_schedule_pdf(room_data['nom'], room_data['code'], room_data['capacite'], exams)
                    st.download_button("⬇️ Télécharger", pdf, f"salle_{room_data['code']}.pdf", "application/pdf")
                else:
                    st.warning("Aucun examen")
