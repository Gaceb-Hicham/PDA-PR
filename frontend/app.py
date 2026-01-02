"""
Application Streamlit - EDT Examens
VERSION HAUTE PERFORMANCE pour 130,000+ inscriptions
Toutes les requêtes sont optimisées avec LIMIT et pagination
"""
import streamlit as st
import pandas as pd
from datetime import date, time
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

st.set_page_config(page_title="EDT Examens", page_icon="🎓", layout="wide")

# ============================================================================
# BASE DE DONNÉES - Cache de ressource pour éviter reconnexions
# ============================================================================

@st.cache_resource
def get_db():
    try:
        from database import execute_query
        return execute_query
    except:
        return None

db = get_db()

def q(sql, params=None):
    """Query avec gestion d'erreur silencieuse"""
    if not db: return []
    try:
        r = db(sql, params)
        return r if r else []
    except Exception as e:
        st.error(f"DB: {e}")
        return []


# ============================================================================
# DONNÉES CACHÉES - Maximum 5 minutes, avec LIMIT strict
# ============================================================================

@st.cache_data(ttl=300)
def depts():
    """7 départements max"""
    return q("SELECT id, nom, code FROM departements ORDER BY nom LIMIT 20")

@st.cache_data(ttl=300)  
def formations():
    """~200 formations - on prend les 100 premières pour le dropdown"""
    return q("""SELECT f.id, f.nom, f.niveau, d.nom as dept 
                FROM formations f JOIN departements d ON f.dept_id = d.id 
                ORDER BY d.nom, f.niveau LIMIT 100""")

@st.cache_data(ttl=300)
def profs():
    """~175 professeurs"""
    return q("""SELECT p.id, p.nom, p.prenom, d.nom as dept 
                FROM professeurs p JOIN departements d ON p.dept_id = d.id 
                ORDER BY p.nom LIMIT 200""")

@st.cache_data(ttl=300)
def salles():
    """~55 salles"""
    return q("SELECT id, nom, code, type, capacite FROM lieu_examen ORDER BY type, code LIMIT 100")

@st.cache_data(ttl=300)
def sessions():
    """Sessions d'examen - max 10"""
    return q("SELECT id, nom, type_session, date_debut, date_fin FROM sessions_examen ORDER BY date_debut DESC LIMIT 10")

@st.cache_data(ttl=300)
def creneaux():
    """5 créneaux horaires"""
    return q("SELECT id, heure_debut, heure_fin, ordre FROM creneaux_horaires ORDER BY ordre")

def fmt(t):
    if not t: return ""
    if hasattr(t, 'strftime'): return t.strftime('%H:%M')
    s = str(t)
    return s[:5] if len(s) >= 5 else s


# ============================================================================
# NAVIGATION
# ============================================================================

st.sidebar.title("🎓 EDT Examens")
st.sidebar.divider()
page = st.sidebar.radio("", ["🏠 Accueil", "⚙️ Config", "📝 Données", "📅 Génération", "📊 Planning", "📄 PDF"], label_visibility="collapsed")


# ============================================================================
# ACCUEIL - Statistiques rapides avec COUNT()
# ============================================================================

if "Accueil" in page:
    st.title("🎓 Plateforme EDT Examens")
    
    # Requêtes COUNT() - très rapides même avec beaucoup de données
    stats = q("""SELECT 
        (SELECT COUNT(*) FROM departements) as depts,
        (SELECT COUNT(*) FROM formations) as forms,
        (SELECT COUNT(*) FROM professeurs) as profs,
        (SELECT COUNT(*) FROM etudiants) as etuds,
        (SELECT COUNT(*) FROM modules) as mods,
        (SELECT COUNT(*) FROM inscriptions) as inscrip,
        (SELECT COUNT(*) FROM lieu_examen) as salles
    """)
    
    if stats:
        s = stats[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Départements", s['depts'])
        c2.metric("Formations", s['forms'])
        c3.metric("Professeurs", s['profs'])
        c4.metric("Salles", s['salles'])
        
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Étudiants", f"{s['etuds']:,}")
        c6.metric("Modules", s['mods'])
        c7.metric("Inscriptions", f"{s['inscrip']:,}")


# ============================================================================
# CONFIGURATION
# ============================================================================

elif "Config" in page:
    st.title("⚙️ Configuration")
    
    tab1, tab2 = st.tabs(["📅 Session", "🕐 Créneaux"])
    
    with tab1:
        sess = sessions()
        if sess:
            st.dataframe(pd.DataFrame(sess), hide_index=True)
        
        with st.form("s"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom", "Session S1 2025-2026")
            typ = c2.selectbox("Type", ["NORMALE", "RATTRAPAGE"])
            c3, c4 = st.columns(2)
            d1, d2 = c3.date_input("Début", date(2026,1,6)), c4.date_input("Fin", date(2026,1,24))
            if st.form_submit_button("➕", type="primary"):
                q("INSERT INTO sessions_examen (nom, type_session, date_debut, date_fin, annee_universitaire) VALUES (%s,%s,%s,%s,'2025-2026')", (nom, typ, d1, d2))
                st.cache_data.clear()
                st.rerun()
    
    with tab2:
        cr = creneaux()
        if cr:
            st.dataframe(pd.DataFrame([{'Ordre': c['ordre'], 'Début': fmt(c['heure_debut']), 'Fin': fmt(c['heure_fin'])} for c in cr]), hide_index=True)


# ============================================================================
# SAISIE DONNÉES
# ============================================================================

elif "Données" in page:
    st.title("📝 Données")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Depts", "Formations", "Profs", "Salles"])
    
    with tab1:
        d = depts()
        if d: st.dataframe(pd.DataFrame(d), hide_index=True)
        with st.form("d"):
            c1, c2 = st.columns(2)
            if st.form_submit_button("➕") and c1.text_input("Nom"):
                pass  # Form handling
    
    with tab2:
        f = formations()
        if f: st.dataframe(pd.DataFrame([{'Formation': x['nom'], 'Niveau': x['niveau'], 'Dept': x['dept']} for x in f[:50]]), hide_index=True)
    
    with tab3:
        p = profs()
        if p: st.dataframe(pd.DataFrame([{'Nom': x['nom'], 'Prénom': x['prenom'], 'Dept': x['dept']} for x in p[:50]]), hide_index=True)
    
    with tab4:
        s = salles()
        if s: st.dataframe(pd.DataFrame(s), hide_index=True)


# ============================================================================
# GÉNÉRATION EDT
# ============================================================================

elif "Génération" in page:
    st.title("📅 Génération EDT")
    
    sess = sessions()
    if not sess:
        st.warning("Créez d'abord une session")
    else:
        sel = st.selectbox("Session", [s['nom'] for s in sess])
        sid = next(s['id'] for s in sess if s['nom'] == sel)
        
        # Stats avant génération
        nb_mods = q("SELECT COUNT(*) as c FROM modules WHERE semestre = 'S1'")
        st.info(f"📚 {nb_mods[0]['c'] if nb_mods else 0} modules à planifier")
        
        if st.button("🚀 Générer", type="primary", use_container_width=True):
            with st.spinner("Génération..."):
                try:
                    # Supprimer anciens
                    q("DELETE FROM surveillances WHERE examen_id IN (SELECT id FROM examens WHERE session_id = %s)", (sid,))
                    q("DELETE FROM examens WHERE session_id = %s", (sid,))
                    
                    from services.optimization import run_optimization
                    r = run_optimization(sid)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Examens", r.get('scheduled', 0))
                    c2.metric("Conflits", r.get('conflicts', 0))
                    c3.metric("Temps", f"{r.get('execution_time', 0):.1f}s")
                    st.success("✅ Terminé!")
                except Exception as e:
                    st.error(str(e))


# ============================================================================
# PLANNING - Avec pagination
# ============================================================================

elif "Planning" in page:
    st.title("📊 Planning")
    
    tab1, tab2, tab3 = st.tabs(["Formation", "Professeur", "Salle"])
    
    with tab1:
        f = formations()
        if f:
            sel = st.selectbox("Formation", [x['nom'] for x in f], key="f1")
            fid = next(x['id'] for x in f if x['nom'] == sel)
            
            # Requête optimisée avec LIMIT
            exams = q("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                       m.nom as Module, l.code as Salle
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE m.formation_id = %s
                ORDER BY e.date_examen, ch.ordre LIMIT 50
            """, (fid,))
            
            if exams:
                st.dataframe(pd.DataFrame(exams), hide_index=True, use_container_width=True)
            else:
                st.info("Aucun examen")
    
    with tab2:
        p = profs()
        if p:
            sel = st.selectbox("Professeur", [f"{x['prenom']} {x['nom']}" for x in p], key="p1")
            pid = next(x['id'] for x in p if f"{x['prenom']} {x['nom']}" == sel)
            
            survs = q("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                       m.nom as Module, l.code as Salle
                FROM surveillances s
                JOIN examens e ON s.examen_id = e.id
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE s.professeur_id = %s LIMIT 50
            """, (pid,))
            
            if survs:
                st.dataframe(pd.DataFrame(survs), hide_index=True, use_container_width=True)
            else:
                st.info("Aucune surveillance")
    
    with tab3:
        s = salles()
        if s:
            sel = st.selectbox("Salle", [f"{x['code']} - {x['nom']}" for x in s], key="s1")
            rid = next(x['id'] for x in s if f"{x['code']} - {x['nom']}" == sel)
            
            exams = q("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                       m.nom as Module
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE e.salle_id = %s LIMIT 50
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
    
    f = formations()
    if f:
        sel = st.selectbox("Formation", [x['nom'] for x in f])
        fid = next(x['id'] for x in f if x['nom'] == sel)
        groupe = st.text_input("Groupe", "G01")
        
        if st.button("📄 Générer PDF", type="primary"):
            exams = q("""
                SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin,
                       m.code as module_code, m.nom as module_nom, l.code as salle
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE m.formation_id = %s ORDER BY e.date_examen LIMIT 100
            """, (fid,))
            
            if exams:
                try:
                    from services.pdf_generator import generate_student_schedule_pdf
                    fdata = next(x for x in f if x['id'] == fid)
                    pdf = generate_student_schedule_pdf(sel, groupe, fdata['niveau'], exams)
                    st.download_button("⬇️ Télécharger", pdf, f"planning_{groupe}.pdf", "application/pdf")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Aucun examen")
