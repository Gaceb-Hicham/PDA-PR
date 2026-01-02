"""
Application Streamlit - EDT Examens
VERSION COMPLÈTE avec TOUS les formulaires de saisie manuelle
Optimisé pour 130,000+ inscriptions
"""
import streamlit as st
import pandas as pd
from datetime import date, time, datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

st.set_page_config(page_title="EDT Examens", page_icon="🎓", layout="wide")

# ============================================================================
# BASE DE DONNÉES
# ============================================================================

@st.cache_resource
def get_db():
    try:
        from database import execute_query, get_cursor
        return execute_query, get_cursor
    except Exception as e:
        st.error(f"Erreur connexion: {e}")
        return None, None

db, cursor_fn = get_db()

def q(sql, params=None, fetch='all'):
    """Query avec gestion d'erreur"""
    if not db:
        return [] if fetch == 'all' else None
    try:
        r = db(sql, params, fetch=fetch)
        return r if r else ([] if fetch == 'all' else None)
    except Exception as e:
        st.error(f"Erreur SQL: {e}")
        return [] if fetch == 'all' else None

def insert(sql, params):
    """Insert et retourne le lastrowid"""
    if not db:
        return None
    try:
        return db(sql, params, fetch='none')
    except Exception as e:
        st.error(f"Erreur INSERT: {e}")
        return None


# ============================================================================
# DONNÉES CACHÉES
# ============================================================================

@st.cache_data(ttl=120)
def get_depts():
    return q("SELECT id, nom, code FROM departements ORDER BY nom LIMIT 50")

@st.cache_data(ttl=120)
def get_formations():
    return q("""SELECT f.id, f.nom, f.code, f.niveau, d.nom as dept, d.id as dept_id
                FROM formations f JOIN departements d ON f.dept_id = d.id 
                ORDER BY d.nom, f.niveau, f.nom LIMIT 250""")

@st.cache_data(ttl=120)
def get_profs():
    return q("""SELECT p.id, p.nom, p.prenom, p.grade, d.nom as dept, d.id as dept_id
                FROM professeurs p JOIN departements d ON p.dept_id = d.id 
                ORDER BY d.nom, p.nom LIMIT 250""")

@st.cache_data(ttl=120)
def get_salles():
    return q("SELECT id, nom, code, type, capacite, batiment FROM lieu_examen ORDER BY type, code LIMIT 100")

@st.cache_data(ttl=120)
def get_sessions():
    return q("SELECT id, nom, type_session, date_debut, date_fin, annee_universitaire FROM sessions_examen ORDER BY date_debut DESC LIMIT 20")

@st.cache_data(ttl=120)
def get_creneaux():
    return q("SELECT id, libelle, heure_debut, heure_fin, ordre FROM creneaux_horaires ORDER BY ordre")

@st.cache_data(ttl=120)
def get_modules(formation_id=None):
    if formation_id:
        return q("SELECT id, code, nom, credits, semestre FROM modules WHERE formation_id = %s ORDER BY semestre, nom LIMIT 50", (formation_id,))
    return q("SELECT m.id, m.code, m.nom, m.credits, m.semestre, f.nom as formation FROM modules m JOIN formations f ON m.formation_id = f.id ORDER BY f.nom, m.semestre LIMIT 100")

def fmt_time(t):
    if not t:
        return ""
    if hasattr(t, 'strftime'):
        return t.strftime('%H:%M')
    s = str(t)
    if 'day' in s:
        parts = s.split(' ')
        s = parts[-1] if len(parts) >= 2 else s
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
# PAGE: ACCUEIL
# ============================================================================

if "Accueil" in page:
    st.title("🎓 Plateforme EDT Examens")
    st.info("**Bienvenue!** Utilisez le menu à gauche pour naviguer.")
    
    # Stats rapides
    stats = q("""SELECT 
        (SELECT COUNT(*) FROM departements) as depts,
        (SELECT COUNT(*) FROM formations) as forms,
        (SELECT COUNT(*) FROM professeurs) as profs,
        (SELECT COUNT(*) FROM etudiants) as etuds,
        (SELECT COUNT(*) FROM modules) as mods,
        (SELECT COUNT(*) FROM inscriptions) as inscrip,
        (SELECT COUNT(*) FROM lieu_examen) as salles,
        (SELECT COUNT(*) FROM examens) as exams
    """, fetch='one')
    
    if stats:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏛️ Départements", stats['depts'])
        c2.metric("📚 Formations", stats['forms'])
        c3.metric("👨‍🏫 Professeurs", stats['profs'])
        c4.metric("🏢 Salles", stats['salles'])
        
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("👨‍🎓 Étudiants", f"{stats['etuds']:,}")
        c6.metric("📖 Modules", stats['mods'])
        c7.metric("📝 Inscriptions", f"{stats['inscrip']:,}")
        c8.metric("📅 Examens", stats['exams'])


# ============================================================================
# PAGE: CONFIGURATION (Sessions + Créneaux)
# ============================================================================

elif "Configuration" in page:
    st.title("⚙️ Configuration")
    
    tab1, tab2 = st.tabs(["📅 Sessions d'Examen", "🕐 Créneaux Horaires"])
    
    # --- Sessions ---
    with tab1:
        st.subheader("📅 Sessions d'Examen")
        
        sessions = get_sessions()
        if sessions:
            df = pd.DataFrame([{
                'Nom': s['nom'],
                'Type': s['type_session'],
                'Début': s['date_debut'],
                'Fin': s['date_fin'],
                'Année': s['annee_universitaire']
            } for s in sessions])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.subheader("➕ Créer une Session")
        with st.form("session_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom de la session", "Session Normale S1 2025-2026")
            type_sess = c2.selectbox("Type", ["NORMALE", "RATTRAPAGE"])
            
            c3, c4 = st.columns(2)
            date_debut = c3.date_input("Date de début", date(2026, 1, 6))
            date_fin = c4.date_input("Date de fin", date(2026, 1, 24))
            
            annee = st.text_input("Année universitaire", "2025-2026")
            
            if st.form_submit_button("✅ Créer la Session", type="primary"):
                if nom and date_debut and date_fin:
                    insert("""INSERT INTO sessions_examen 
                              (nom, type_session, date_debut, date_fin, annee_universitaire, statut) 
                              VALUES (%s, %s, %s, %s, %s, 'PLANIFICATION')""",
                           (nom, type_sess, date_debut, date_fin, annee))
                    st.success("✅ Session créée!")
                    st.cache_data.clear()
                    st.rerun()
    
    # --- Créneaux ---
    with tab2:
        st.subheader("🕐 Créneaux Horaires")
        
        creneaux = get_creneaux()
        if creneaux:
            df = pd.DataFrame([{
                'Ordre': c['ordre'],
                'Libellé': c['libelle'] or '',
                'Début': fmt_time(c['heure_debut']),
                'Fin': fmt_time(c['heure_fin'])
            } for c in creneaux])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Aucun créneau. Ajoutez-en pour générer les plannings!")
        
        st.subheader("➕ Ajouter un Créneau")
        with st.form("creneau_form"):
            c1, c2, c3 = st.columns(3)
            ordre = c1.number_input("Ordre", min_value=1, max_value=10, value=len(creneaux)+1 if creneaux else 1)
            heure_debut = c2.time_input("Heure de début", time(8, 0))
            heure_fin = c3.time_input("Heure de fin", time(9, 30))
            
            if st.form_submit_button("✅ Ajouter le Créneau", type="primary"):
                libelle = f"{heure_debut.strftime('%H:%M')} - {heure_fin.strftime('%H:%M')}"
                insert("""INSERT INTO creneaux_horaires (libelle, heure_debut, heure_fin, ordre)
                          VALUES (%s, %s, %s, %s)""",
                       (libelle, heure_debut, heure_fin, ordre))
                st.success("✅ Créneau ajouté!")
                st.cache_data.clear()
                st.rerun()


# ============================================================================
# PAGE: SAISIE DONNÉES
# ============================================================================

elif "Saisie" in page:
    st.title("📝 Saisie des Données")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏛️ Départements", "📚 Formations", "👨‍🏫 Professeurs", 
        "🏢 Salles", "📖 Modules", "👨‍🎓 Étudiants", "📝 Inscriptions"
    ])
    
    # --- DÉPARTEMENTS ---
    with tab1:
        st.subheader("🏛️ Départements")
        
        depts = get_depts()
        if depts:
            st.dataframe(pd.DataFrame(depts), use_container_width=True, hide_index=True)
        
        st.subheader("➕ Ajouter un Département")
        with st.form("dept_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom du département", placeholder="Informatique")
            code = c2.text_input("Code", placeholder="INFO")
            
            if st.form_submit_button("✅ Ajouter", type="primary"):
                if nom and code:
                    insert("INSERT INTO departements (nom, code) VALUES (%s, %s)", (nom, code))
                    st.success(f"✅ Département '{nom}' créé!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("Remplissez tous les champs")
    
    # --- FORMATIONS ---
    with tab2:
        st.subheader("📚 Formations")
        
        formations = get_formations()
        if formations:
            df = pd.DataFrame([{
                'Formation': f['nom'],
                'Code': f['code'],
                'Niveau': f['niveau'],
                'Département': f['dept']
            } for f in formations[:50]])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.subheader("➕ Ajouter une Formation")
        depts = get_depts()
        if depts:
            with st.form("formation_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom de la formation", placeholder="Génie Logiciel")
                code = c2.text_input("Code", placeholder="GL")
                
                c3, c4 = st.columns(2)
                dept_sel = c3.selectbox("Département", [d['nom'] for d in depts])
                niveau = c4.selectbox("Niveau", ["L1", "L2", "L3", "M1", "M2"])
                
                if st.form_submit_button("✅ Ajouter", type="primary"):
                    if nom and code:
                        dept_id = next(d['id'] for d in depts if d['nom'] == dept_sel)
                        full_name = f"{niveau} - {nom}"
                        insert("""INSERT INTO formations (nom, code, dept_id, niveau, nb_modules)
                                  VALUES (%s, %s, %s, %s, 6)""",
                               (full_name, code, dept_id, niveau))
                        st.success(f"✅ Formation '{full_name}' créée!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.warning("Créez d'abord un département")
    
    # --- PROFESSEURS ---
    with tab3:
        st.subheader("👨‍🏫 Professeurs")
        
        profs = get_profs()
        if profs:
            df = pd.DataFrame([{
                'Nom': p['nom'],
                'Prénom': p['prenom'],
                'Grade': p['grade'],
                'Département': p['dept']
            } for p in profs[:50]])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.subheader("➕ Ajouter un Professeur")
        depts = get_depts()
        if depts:
            with st.form("prof_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom", placeholder="BENALI")
                prenom = c2.text_input("Prénom", placeholder="Ahmed")
                
                c3, c4 = st.columns(2)
                dept_sel = c3.selectbox("Département", [d['nom'] for d in depts], key="prof_dept")
                grade = c4.selectbox("Grade", ["MAA", "MAB", "MCA", "MCB", "PR"])
                
                email = st.text_input("Email (optionnel)", placeholder="ahmed.benali@univ.dz")
                specialite = st.text_input("Spécialité (optionnel)", placeholder="Intelligence Artificielle")
                
                if st.form_submit_button("✅ Ajouter", type="primary"):
                    if nom and prenom:
                        dept_id = next(d['id'] for d in depts if d['nom'] == dept_sel)
                        matricule = f"P{dept_id}{nom[:3].upper()}{len(profs) if profs else 0}"
                        insert("""INSERT INTO professeurs (matricule, nom, prenom, email, dept_id, grade, specialite)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                               (matricule, nom, prenom, email or None, dept_id, grade, specialite or None))
                        st.success(f"✅ Professeur '{prenom} {nom}' créé!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.warning("Créez d'abord un département")
    
    # --- SALLES ---
    with tab4:
        st.subheader("🏢 Salles d'Examen")
        
        salles = get_salles()
        if salles:
            df = pd.DataFrame([{
                'Nom': s['nom'],
                'Code': s['code'],
                'Type': s['type'],
                'Capacité': s['capacite'],
                'Bâtiment': s['batiment'] or ''
            } for s in salles])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.subheader("➕ Ajouter une Salle")
        with st.form("salle_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom de la salle", placeholder="Amphithéâtre 1")
            code = c2.text_input("Code", placeholder="AMP01")
            
            c3, c4, c5 = st.columns(3)
            type_salle = c3.selectbox("Type", ["AMPHI", "SALLE", "LABO"])
            capacite = c4.number_input("Capacité", min_value=10, max_value=500, value=100)
            batiment = c5.text_input("Bâtiment", placeholder="Bloc A")
            
            if st.form_submit_button("✅ Ajouter", type="primary"):
                if nom and code:
                    insert("""INSERT INTO lieu_examen (nom, code, capacite, type, batiment, disponible)
                              VALUES (%s, %s, %s, %s, %s, TRUE)""",
                           (nom, code, capacite, type_salle, batiment or None))
                    st.success(f"✅ Salle '{nom}' créée!")
                    st.cache_data.clear()
                    st.rerun()
    
    # --- MODULES ---
    with tab5:
        st.subheader("📖 Modules")
        
        formations = get_formations()
        if formations:
            sel_form = st.selectbox("Sélectionner une formation", [f['nom'] for f in formations])
            form_id = next(f['id'] for f in formations if f['nom'] == sel_form)
            
            modules = get_modules(form_id)
            if modules:
                df = pd.DataFrame([{
                    'Code': m['code'],
                    'Nom': m['nom'],
                    'Crédits': m['credits'],
                    'Semestre': m['semestre']
                } for m in modules])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun module pour cette formation")
            
            st.subheader("➕ Ajouter un Module")
            with st.form("module_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom du module", placeholder="Programmation Avancée")
                code = c2.text_input("Code", placeholder="PROG01")
                
                c3, c4 = st.columns(2)
                semestre = c3.selectbox("Semestre", ["S1", "S2"])
                credits = c4.number_input("Crédits", min_value=1, max_value=10, value=4)
                
                if st.form_submit_button("✅ Ajouter", type="primary"):
                    if nom and code:
                        insert("""INSERT INTO modules (code, nom, credits, formation_id, semestre, coefficient)
                                  VALUES (%s, %s, %s, %s, %s, %s)""",
                               (code, nom, credits, form_id, semestre, credits/2))
                        st.success(f"✅ Module '{nom}' créé!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.warning("Créez d'abord une formation")
    
    # --- ÉTUDIANTS ---
    with tab6:
        st.subheader("👨‍🎓 Étudiants")
        
        # Afficher les étudiants par formation
        formations = get_formations()
        if formations:
            sel_form = st.selectbox("Filtrer par formation", ["Toutes"] + [f['nom'] for f in formations], key="etud_filter")
            
            if sel_form == "Toutes":
                etudiants = q("""
                    SELECT e.matricule, e.nom, e.prenom, e.groupe, f.nom as formation
                    FROM etudiants e
                    JOIN formations f ON e.formation_id = f.id
                    ORDER BY f.nom, e.groupe, e.nom
                    LIMIT 100
                """)
            else:
                form_id = next(f['id'] for f in formations if f['nom'] == sel_form)
                etudiants = q("""
                    SELECT e.matricule, e.nom, e.prenom, e.groupe, f.nom as formation
                    FROM etudiants e
                    JOIN formations f ON e.formation_id = f.id
                    WHERE e.formation_id = %s
                    ORDER BY e.groupe, e.nom
                    LIMIT 100
                """, (form_id,))
            
            if etudiants:
                df = pd.DataFrame([{
                    'Matricule': e['matricule'],
                    'Nom': e['nom'],
                    'Prénom': e['prenom'],
                    'Groupe': e['groupe'] or 'G01',
                    'Formation': e['formation']
                } for e in etudiants])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.caption(f"Affichage limité à 100 étudiants")
            else:
                st.info("Aucun étudiant trouvé")
        
        st.subheader("➕ Ajouter un Étudiant")
        if formations:
            with st.form("etudiant_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom", placeholder="AMRANI")
                prenom = c2.text_input("Prénom", placeholder="Mohamed")
                
                c3, c4 = st.columns(2)
                form_sel = c3.selectbox("Formation", [f['nom'] for f in formations], key="etud_form")
                groupe = c4.text_input("Groupe", "G01", help="Ex: G01, G02, G03...")
                
                promo = st.number_input("Année de promotion", min_value=2020, max_value=2030, value=2025)
                
                if st.form_submit_button("✅ Ajouter", type="primary"):
                    if nom and prenom:
                        form_id = next(f['id'] for f in formations if f['nom'] == form_sel)
                        matricule = f"E{form_id:04d}{len(etudiants) if etudiants else 0:04d}"
                        insert("""INSERT INTO etudiants (matricule, nom, prenom, formation_id, groupe, promo)
                                  VALUES (%s, %s, %s, %s, %s, %s)""",
                               (matricule, nom, prenom, form_id, groupe, promo))
                        st.success(f"✅ Étudiant '{prenom} {nom}' créé avec matricule {matricule}!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.warning("Créez d'abord une formation")
    
    # --- INSCRIPTIONS ---
    with tab7:
        st.subheader("📝 Inscriptions aux Modules")
        
        st.info("""
        **Comment fonctionnent les examens?**
        1. Chaque module inscrit génère un examen lors de la génération de l'EDT
        2. Les étudiants sont automatiquement inscrits à tous les modules de leur formation
        3. Lors de la génération, les groupes d'une même formation passent le même examen, mais dans des salles différentes
        """)
        
        formations = get_formations()
        if formations:
            sel_form = st.selectbox("Formation", [f['nom'] for f in formations], key="inscr_form")
            form_id = next(f['id'] for f in formations if f['nom'] == sel_form)
            
            # Stats inscriptions
            stats = q("""
                SELECT 
                    (SELECT COUNT(*) FROM etudiants WHERE formation_id = %s) as nb_etudiants,
                    (SELECT COUNT(*) FROM modules WHERE formation_id = %s) as nb_modules,
                    (SELECT COUNT(*) FROM inscriptions i 
                     JOIN modules m ON i.module_id = m.id 
                     WHERE m.formation_id = %s) as nb_inscriptions
            """, (form_id, form_id, form_id), fetch='one')
            
            if stats:
                c1, c2, c3 = st.columns(3)
                c1.metric("Étudiants", stats['nb_etudiants'])
                c2.metric("Modules", stats['nb_modules'])
                c3.metric("Inscriptions", stats['nb_inscriptions'])
            
            st.divider()
            
            # Bouton pour inscrire tous les étudiants à tous les modules
            st.subheader("⚡ Inscription Automatique")
            st.warning("Cette action inscrit TOUS les étudiants de cette formation à TOUS ses modules S1")
            
            if st.button("📝 Inscrire tous les étudiants aux modules S1", type="primary"):
                with st.spinner("Inscription en cours..."):
                    # Récupérer les étudiants et modules
                    etudiants = q("SELECT id FROM etudiants WHERE formation_id = %s", (form_id,))
                    modules = q("SELECT id FROM modules WHERE formation_id = %s AND semestre = 'S1'", (form_id,))
                    
                    if not etudiants:
                        st.error("Aucun étudiant dans cette formation")
                    elif not modules:
                        st.error("Aucun module S1 dans cette formation")
                    else:
                        count = 0
                        for etud in etudiants:
                            for mod in modules:
                                try:
                                    insert("""INSERT IGNORE INTO inscriptions 
                                              (etudiant_id, module_id, annee_universitaire, statut)
                                              VALUES (%s, %s, '2025/2026', 'INSCRIT')""",
                                           (etud['id'], mod['id']))
                                    count += 1
                                except:
                                    pass
                        
                        st.success(f"✅ {count} inscriptions créées!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.warning("Créez d'abord une formation")


# ============================================================================
# PAGE: GÉNÉRATION EDT
# ============================================================================

elif "Génération" in page:
    st.title("📅 Génération de l'Emploi du Temps")
    
    sessions = get_sessions()
    creneaux = get_creneaux()
    
    if not sessions:
        st.error("⚠️ Aucune session d'examen. Allez dans **Configuration** pour en créer une.")
    elif not creneaux:
        st.error("⚠️ Aucun créneau horaire. Allez dans **Configuration** pour en ajouter.")
    else:
        st.subheader("Sélectionner la session")
        sel_session = st.selectbox("Session d'examen", [s['nom'] for s in sessions])
        session_id = next(s['id'] for s in sessions if s['nom'] == sel_session)
        
        session = next(s for s in sessions if s['id'] == session_id)
        
        c1, c2, c3 = st.columns(3)
        c1.info(f"📅 Début: {session['date_debut']}")
        c2.info(f"📅 Fin: {session['date_fin']}")
        c3.info(f"🕐 Créneaux: {len(creneaux)}")
        
        # Stats
        stats = q("""SELECT 
            (SELECT COUNT(*) FROM modules WHERE semestre = 'S1') as modules_s1,
            (SELECT COUNT(*) FROM lieu_examen WHERE disponible = TRUE) as salles,
            (SELECT COUNT(*) FROM professeurs) as profs,
            (SELECT COUNT(*) FROM examens WHERE session_id = %s) as examens_existants
        """, (session_id,), fetch='one')
        
        if stats:
            st.divider()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📖 Modules S1", stats['modules_s1'])
            c2.metric("🏢 Salles disponibles", stats['salles'])
            c3.metric("👨‍🏫 Professeurs", stats['profs'])
            c4.metric("📅 Examens existants", stats['examens_existants'])
            
            if stats['modules_s1'] == 0:
                st.warning("⚠️ Aucun module au semestre S1. Ajoutez des modules dans **Saisie Données**.")
            
            if stats['salles'] == 0:
                st.warning("⚠️ Aucune salle disponible. Ajoutez des salles dans **Saisie Données**.")
        
        st.divider()
        
        if st.button("🚀 Générer l'Emploi du Temps", type="primary", use_container_width=True):
            with st.spinner("⏳ Génération en cours... (peut prendre jusqu'à 45 secondes)"):
                try:
                    # Supprimer les anciens examens
                    q("DELETE FROM surveillances WHERE examen_id IN (SELECT id FROM examens WHERE session_id = %s)", (session_id,))
                    q("DELETE FROM conflits WHERE examen1_id IN (SELECT id FROM examens WHERE session_id = %s)", (session_id,))
                    q("DELETE FROM examens WHERE session_id = %s", (session_id,))
                    
                    start = datetime.now()
                    
                    from services.optimization import run_optimization
                    report = run_optimization(session_id)
                    
                    elapsed = (datetime.now() - start).total_seconds()
                    
                    st.success(f"✅ Génération terminée en {elapsed:.2f} secondes!")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("📅 Examens planifiés", report.get('scheduled', 0))
                    c2.metric("⚠️ Conflits", report.get('conflicts', 0))
                    c3.metric("📊 Taux de réussite", f"{report.get('success_rate', 0):.1f}%")
                    
                    if report.get('scheduled', 0) > 0:
                        st.balloons()
                    
                    st.cache_data.clear()
                    
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
                    import traceback
                    st.code(traceback.format_exc())


# ============================================================================
# PAGE: PLANNINGS
# ============================================================================

elif "Plannings" in page:
    st.title("📊 Consultation des Plannings")
    
    tab1, tab2, tab3 = st.tabs(["📚 Par Formation", "👨‍🏫 Par Professeur", "🏢 Par Salle"])
    
    with tab1:
        formations = get_formations()
        if formations:
            sel = st.selectbox("Formation", [f['nom'] for f in formations], key="plan_form")
            form_id = next(f['id'] for f in formations if f['nom'] == sel)
            
            exams = q("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),' - ',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                       CONCAT(m.nom, ' (', m.code, ')') as Module,
                       l.nom as Salle, e.nb_etudiants_prevus as Étudiants
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE m.formation_id = %s
                ORDER BY e.date_examen, ch.ordre LIMIT 100
            """, (form_id,))
            
            if exams:
                st.success(f"📅 {len(exams)} examens planifiés")
                st.dataframe(pd.DataFrame(exams), use_container_width=True, hide_index=True)
            else:
                st.info("Aucun examen planifié pour cette formation. Générez l'EDT d'abord.")
    
    with tab2:
        profs = get_profs()
        if profs:
            sel = st.selectbox("Professeur", [f"{p['prenom']} {p['nom']} ({p['dept']})" for p in profs], key="plan_prof")
            prof_id = next(p['id'] for p in profs if f"{p['prenom']} {p['nom']} ({p['dept']})" == sel)
            
            survs = q("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),' - ',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                       m.nom as Module, l.nom as Salle, s.role as Rôle
                FROM surveillances s
                JOIN examens e ON s.examen_id = e.id
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE s.professeur_id = %s
                ORDER BY e.date_examen, ch.ordre LIMIT 100
            """, (prof_id,))
            
            if survs:
                st.success(f"📅 {len(survs)} surveillances assignées")
                st.dataframe(pd.DataFrame(survs), use_container_width=True, hide_index=True)
            else:
                st.info("Aucune surveillance assignée")
    
    with tab3:
        salles = get_salles()
        if salles:
            sel = st.selectbox("Salle", [f"{s['code']} - {s['nom']} ({s['capacite']} places)" for s in salles], key="plan_salle")
            salle_id = next(s['id'] for s in salles if f"{s['code']} - {s['nom']} ({s['capacite']} places)" == sel)
            
            exams = q("""
                SELECT e.date_examen as Date,
                       CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),' - ',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                       m.nom as Module, f.nom as Formation
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN formations f ON m.formation_id = f.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE e.salle_id = %s
                ORDER BY e.date_examen, ch.ordre LIMIT 100
            """, (salle_id,))
            
            if exams:
                st.success(f"📅 {len(exams)} examens dans cette salle")
                st.dataframe(pd.DataFrame(exams), use_container_width=True, hide_index=True)
            else:
                st.info("Aucun examen dans cette salle")


# ============================================================================
# PAGE: EXPORT PDF
# ============================================================================

elif "PDF" in page:
    st.title("📄 Export PDF des Plannings")
    
    tab1, tab2, tab3 = st.tabs(["📚 Étudiants", "👨‍🏫 Professeurs", "🏢 Salles"])
    
    with tab1:
        st.subheader("📚 Planning Étudiant")
        formations = get_formations()
        if formations:
            sel = st.selectbox("Formation", [f['nom'] for f in formations], key="pdf_form")
            form_data = next(f for f in formations if f['nom'] == sel)
            groupe = st.text_input("Groupe (optionnel)", "G01")
            
            if st.button("📄 Générer PDF Étudiant", type="primary"):
                exams = q("""
                    SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin,
                           m.code as module_code, m.nom as module_nom, l.code as salle
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN lieu_examen l ON e.salle_id = l.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    WHERE m.formation_id = %s
                    ORDER BY e.date_examen, ch.ordre
                """, (form_data['id'],))
                
                if exams:
                    try:
                        from services.pdf_generator import generate_student_schedule_pdf
                        pdf = generate_student_schedule_pdf(sel, groupe, form_data['niveau'], exams)
                        st.download_button("⬇️ Télécharger le PDF", pdf, f"planning_{groupe}.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucun examen planifié")
    
    with tab2:
        st.subheader("👨‍🏫 Planning Professeur")
        profs = get_profs()
        if profs:
            sel = st.selectbox("Professeur", [f"{p['prenom']} {p['nom']}" for p in profs], key="pdf_prof")
            prof_data = next(p for p in profs if f"{p['prenom']} {p['nom']}" == sel)
            
            if st.button("📄 Générer PDF Professeur", type="primary"):
                survs = q("""
                    SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin,
                           m.code as module_code, m.nom as module_nom, l.code as salle, s.role
                    FROM surveillances s
                    JOIN examens e ON s.examen_id = e.id
                    JOIN modules m ON e.module_id = m.id
                    JOIN lieu_examen l ON e.salle_id = l.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    WHERE s.professeur_id = %s
                    ORDER BY e.date_examen
                """, (prof_data['id'],))
                
                if survs:
                    try:
                        from services.pdf_generator import generate_professor_schedule_pdf
                        pdf = generate_professor_schedule_pdf(prof_data['nom'], prof_data['prenom'], prof_data['dept'], survs)
                        st.download_button("⬇️ Télécharger le PDF", pdf, f"surveillances_{prof_data['nom']}.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucune surveillance assignée")
    
    with tab3:
        st.subheader("🏢 Planning Salle")
        salles = get_salles()
        if salles:
            sel = st.selectbox("Salle", [f"{s['code']} - {s['nom']}" for s in salles], key="pdf_salle")
            salle_data = next(s for s in salles if f"{s['code']} - {s['nom']}" == sel)
            
            if st.button("📄 Générer PDF Salle", type="primary"):
                exams = q("""
                    SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin,
                           m.code as module_code, m.nom as module_nom, f.nom as formation
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN formations f ON m.formation_id = f.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    WHERE e.salle_id = %s
                    ORDER BY e.date_examen
                """, (salle_data['id'],))
                
                if exams:
                    try:
                        from services.pdf_generator import generate_room_schedule_pdf
                        pdf = generate_room_schedule_pdf(salle_data['nom'], salle_data['code'], salle_data['capacite'], exams)
                        st.download_button("⬇️ Télécharger le PDF", pdf, f"salle_{salle_data['code']}.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucun examen dans cette salle")
