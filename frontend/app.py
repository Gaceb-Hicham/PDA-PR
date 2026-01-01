"""
Application Streamlit - Plateforme EDT Examens
Version avec saisie manuelle, export Excel et caching
"""
import streamlit as st
import pandas as pd
from io import BytesIO
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configuration
st.set_page_config(
    page_title="Plateforme EDT Examens",
    page_icon="🎓",
    layout="wide"
)

# Sidebar Navigation
st.sidebar.title("🎓 EDT Examens")
st.sidebar.markdown("Université M'Hamed Bougara")
st.sidebar.markdown("---")

pages = [
    "🏠 Accueil",
    "➕ Saisie des données",
    "📊 Afficher les données",
    "📅 Génération EDT",
    "📥 Export Excel/CSV",
    "📄 Export PDF",
    "📋 Planning par groupe"
]

selection = st.sidebar.radio("Navigation", pages, label_visibility="collapsed")


def get_db():
    """Connexion à la base de données"""
    try:
        from database import execute_query, get_cursor
        return execute_query, get_cursor
    except Exception as e:
        return None, None


# Fonctions de requête avec cache pour améliorer les performances
@st.cache_data(ttl=300)
def get_cached_departments():
    """Récupère les départements (cache 5 min)"""
    query, _ = get_db()
    if query:
        return query("SELECT id, nom, code FROM departements ORDER BY nom")
    return []


@st.cache_data(ttl=300)
def get_cached_formations():
    """Récupère les formations (cache 5 min)"""
    query, _ = get_db()
    if query:
        return query("""
            SELECT f.id, f.nom, f.code, f.niveau, d.nom as dept, d.id as dept_id
            FROM formations f
            JOIN departements d ON f.dept_id = d.id
            ORDER BY d.nom, f.niveau, f.nom
        """)
    return []


@st.cache_data(ttl=300)
def get_cached_professors():
    """Récupère les professeurs (cache 5 min)"""
    query, _ = get_db()
    if query:
        return query("""
            SELECT p.id, p.nom, p.prenom, d.nom as dept, d.id as dept_id
            FROM professeurs p
            JOIN departements d ON p.dept_id = d.id
            ORDER BY d.nom, p.nom
        """)
    return []


@st.cache_data(ttl=300)
def get_cached_rooms():
    """Récupère les salles (cache 5 min)"""
    query, _ = get_db()
    if query:
        return query("SELECT id, nom, code, type, capacite, batiment FROM lieu_examen ORDER BY type, code")
    return []


def export_to_excel(dataframe, filename):
    """Exporte un DataFrame en Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    return output


# ============================================================================
# PAGE: ACCUEIL
# ============================================================================
if "Accueil" in selection:
    st.title("🎓 Plateforme EDT Examens")
    
    st.markdown("""
    ## Bienvenue!
    
    ### 📋 Fonctionnalités
    
    | Page | Description |
    |------|-------------|
    | **Saisie des données** | Ajouter manuellement: départements, formations, groupes, profs, salles |
    | **Afficher les données** | Voir toutes les données saisies |
    | **Génération EDT** | Générer automatiquement le planning d'examens |
    | **Export Excel** | Télécharger les données en format Excel |
    | **Planning par groupe** | Voir le planning comme dans votre capture d'écran |
    
    ### 🔄 Workflow
    
    1. **Saisir les données** → Ajouter départements, formations, groupes, salles, modules
    2. **Générer le planning** → L'algorithme crée automatiquement l'EDT
    3. **Exporter** → Télécharger en Excel pour impression
    """)
    
    # Test connexion
    query, cursor = get_db()
    if query:
        try:
            r = query("SELECT COUNT(*) as c FROM departements", fetch='one')
            if r and r['c'] > 0:
                st.success(f"✅ Connecté - {r['c']} départements trouvés")
            else:
                st.warning("⚠️ Base vide - Utilisez 'Saisie des données' pour commencer")
        except:
            st.error("❌ Tables non créées - Exécutez database/schema.sql")
    else:
        st.error("❌ Erreur de connexion MySQL")


# ============================================================================
# PAGE: SAISIE DES DONNÉES
# ============================================================================
elif "Saisie des données" in selection:
    st.title("➕ Saisie Manuelle des Données")
    
    query, get_cursor_func = get_db()
    if not query:
        st.error("Erreur de connexion")
        st.stop()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏛️ Départements", 
        "📚 Formations/Groupes",
        "👨‍🏫 Professeurs", 
        "🏢 Salles",
        "📖 Modules"
    ])
    
    # --- Départements ---
    with tab1:
        st.subheader("Ajouter un Département")
        
        with st.form("add_dept"):
            col1, col2 = st.columns(2)
            dept_nom = col1.text_input("Nom du département", placeholder="Informatique")
            dept_code = col2.text_input("Code", placeholder="INFO")
            
            if st.form_submit_button("➕ Ajouter", type="primary"):
                if dept_nom and dept_code:
                    try:
                        query(
                            "INSERT INTO departements (nom, code) VALUES (%s, %s)",
                            (dept_nom, dept_code), fetch='none'
                        )
                        st.success(f"✅ Département '{dept_nom}' ajouté!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Remplissez tous les champs")
        
        # Afficher existants
        st.markdown("---")
        st.subheader("Départements existants")
        depts = query("SELECT id, nom, code FROM departements ORDER BY nom")
        if depts:
            st.dataframe(pd.DataFrame(depts), use_container_width=True, hide_index=True)
    
    # --- Formations et Groupes ---
    with tab2:
        st.subheader("Ajouter une Formation avec Groupes")
        
        depts = query("SELECT id, nom FROM departements ORDER BY nom")
        if not depts:
            st.warning("Ajoutez d'abord un département")
        else:
            with st.form("add_formation"):
                col1, col2 = st.columns(2)
                
                dept_options = {d['nom']: d['id'] for d in depts}
                selected_dept = col1.selectbox("Département", list(dept_options.keys()))
                
                formation_nom = col2.text_input("Nom", placeholder="Génie Logiciel")
                
                col3, col4, col5 = st.columns(3)
                formation_code = col3.text_input("Code", placeholder="GL")
                niveau = col4.selectbox("Niveau", ["L1", "L2", "L3", "M1", "M2"])
                nb_groupes = col5.number_input("Nombre de groupes", min_value=1, max_value=10, value=3)
                
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if formation_nom and formation_code:
                        try:
                            # Ajouter la formation
                            code_full = f"{niveau}_{formation_code}"
                            query(
                                """INSERT INTO formations (nom, code, dept_id, niveau, nb_modules) 
                                   VALUES (%s, %s, %s, %s, 6)""",
                                (f"{niveau} - {formation_nom}", code_full, dept_options[selected_dept], niveau),
                                fetch='none'
                            )
                            st.success(f"✅ Formation '{formation_nom}' ajoutée avec {nb_groupes} groupes!")
                            st.info(f"Groupes créés: {formation_code}01 à {formation_code}{nb_groupes:02d}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur: {e}")
        
        # Afficher formations
        st.markdown("---")
        st.subheader("Formations existantes")
        formations = query("""
            SELECT f.code, f.nom, f.niveau, d.nom as departement
            FROM formations f
            JOIN departements d ON f.dept_id = d.id
            ORDER BY d.nom, f.niveau
            LIMIT 30
        """)
        if formations:
            st.dataframe(pd.DataFrame(formations), use_container_width=True, hide_index=True)
    
    # --- Professeurs ---
    with tab3:
        st.subheader("Ajouter un Professeur")
        
        depts = query("SELECT id, nom FROM departements ORDER BY nom")
        if not depts:
            st.warning("Ajoutez d'abord un département")
        else:
            with st.form("add_prof"):
                col1, col2, col3 = st.columns(3)
                
                prof_nom = col1.text_input("Nom", placeholder="BENALI")
                prof_prenom = col2.text_input("Prénom", placeholder="Ahmed")
                
                dept_options = {d['nom']: d['id'] for d in depts}
                selected_dept = col3.selectbox("Département", list(dept_options.keys()))
                
                col4, col5 = st.columns(2)
                grade = col4.selectbox("Grade", ["MAA", "MAB", "MCA", "MCB", "PR"])
                specialite = col5.text_input("Spécialité", placeholder="Intelligence Artificielle")
                
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if prof_nom and prof_prenom:
                        try:
                            matricule = f"P{dept_options[selected_dept]}{prof_nom[:3].upper()}"
                            query(
                                """INSERT INTO professeurs (matricule, nom, prenom, dept_id, grade, specialite)
                                   VALUES (%s, %s, %s, %s, %s, %s)""",
                                (matricule, prof_nom, prof_prenom, dept_options[selected_dept], grade, specialite),
                                fetch='none'
                            )
                            st.success(f"✅ Professeur {prof_prenom} {prof_nom} ajouté!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur: {e}")
        
        st.markdown("---")
        profs = query("SELECT nom, prenom, grade, specialite FROM professeurs ORDER BY nom LIMIT 20")
        if profs:
            st.dataframe(pd.DataFrame(profs), use_container_width=True, hide_index=True)
    
    # --- Salles ---
    with tab4:
        st.subheader("Ajouter une Salle / Amphithéâtre")
        
        with st.form("add_salle"):
            col1, col2, col3 = st.columns(3)
            
            salle_nom = col1.text_input("Nom", placeholder="Amphithéâtre 10")
            salle_code = col2.text_input("Code", placeholder="AMP10")
            salle_type = col3.selectbox("Type", ["AMPHI", "SALLE", "LABO"])
            
            col4, col5 = st.columns(2)
            capacite = col4.number_input("Capacité", min_value=10, max_value=500, value=100)
            batiment = col5.text_input("Bâtiment", placeholder="Bloc A")
            
            if st.form_submit_button("➕ Ajouter", type="primary"):
                if salle_nom and salle_code:
                    try:
                        query(
                            """INSERT INTO lieu_examen (nom, code, capacite, type, batiment)
                               VALUES (%s, %s, %s, %s, %s)""",
                            (salle_nom, salle_code, capacite, salle_type, batiment),
                            fetch='none'
                        )
                        st.success(f"✅ {salle_type} '{salle_nom}' ajouté!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
        
        st.markdown("---")
        salles = query("SELECT nom, code, type, capacite, batiment FROM lieu_examen ORDER BY type, code LIMIT 20")
        if salles:
            st.dataframe(pd.DataFrame(salles), use_container_width=True, hide_index=True)
    
    # --- Modules ---
    with tab5:
        st.subheader("Ajouter un Module")
        
        formations = query("SELECT id, nom, code FROM formations ORDER BY nom")
        if not formations:
            st.warning("Ajoutez d'abord une formation")
        else:
            with st.form("add_module"):
                col1, col2 = st.columns(2)
                
                form_options = {f['nom']: f['id'] for f in formations}
                selected_form = col1.selectbox("Formation", list(form_options.keys()))
                
                module_nom = col2.text_input("Nom du module", placeholder="Algorithmique Avancée")
                
                col3, col4, col5 = st.columns(3)
                module_code = col3.text_input("Code", placeholder="AAC")
                semestre = col4.selectbox("Semestre", ["S1", "S2"])
                credits = col5.number_input("Crédits", min_value=1, max_value=10, value=4)
                
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if module_nom and module_code:
                        try:
                            query(
                                """INSERT INTO modules (code, nom, credits, formation_id, semestre)
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (module_code, module_nom, credits, form_options[selected_form], semestre),
                                fetch='none'
                            )
                            st.success(f"✅ Module '{module_nom}' ajouté!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur: {e}")
        
        st.markdown("---")
        modules = query("""
            SELECT m.code, m.nom, m.credits, m.semestre, f.nom as formation
            FROM modules m
            JOIN formations f ON m.formation_id = f.id
            ORDER BY f.nom, m.semestre
            LIMIT 30
        """)
        if modules:
            st.dataframe(pd.DataFrame(modules), use_container_width=True, hide_index=True)


# ============================================================================
# PAGE: AFFICHER LES DONNÉES
# ============================================================================
elif "Afficher les données" in selection:
    st.title("📊 Données Existantes")
    
    query, _ = get_db()
    if not query:
        st.error("Erreur de connexion")
        st.stop()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Départements", "Formations", "Professeurs", "Salles"])
    
    with tab1:
        data = query("SELECT nom as Département, code as Code FROM departements ORDER BY nom")
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.info("Aucun département")
    
    with tab2:
        data = query("""
            SELECT f.code as Code, f.nom as Formation, f.niveau as Niveau, 
                   d.nom as Département
            FROM formations f
            JOIN departements d ON f.dept_id = d.id
            ORDER BY d.nom, f.niveau
        """)
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    
    with tab3:
        data = query("""
            SELECT p.nom as Nom, p.prenom as Prénom, p.grade as Grade,
                   p.specialite as Spécialité, d.nom as Département
            FROM professeurs p
            JOIN departements d ON p.dept_id = d.id
            ORDER BY p.nom
        """)
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    
    with tab4:
        data = query("""
            SELECT nom as Nom, code as Code, type as Type, 
                   capacite as Capacité, batiment as Bâtiment
            FROM lieu_examen
            ORDER BY type, code
        """)
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)


# ============================================================================
# PAGE: GÉNÉRATION EDT
# ============================================================================
elif "Génération EDT" in selection:
    st.title("📅 Génération de l'EDT")
    
    query, _ = get_db()
    if not query:
        st.error("Erreur de connexion")
        st.stop()
    
    st.markdown("""
    ### Comment ça fonctionne?
    
    L'algorithme va:
    1. Prendre tous les modules du semestre S1
    2. Pour chaque groupe de chaque formation
    3. Attribuer une date, un créneau et une salle
    4. En respectant: max 1 exam/jour/étudiant, capacité des salles, etc.
    """)
    
    if st.button("🚀 Générer le Planning", type="primary", use_container_width=True):
        with st.spinner("Génération en cours..."):
            try:
                from services.optimization import run_optimization
                report = run_optimization(1)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("✅ Examens planifiés", report.get('scheduled', 0))
                col2.metric("⚠️ Conflits", report.get('conflicts', 0))
                col3.metric("⏱️ Temps", f"{report.get('execution_time', 0):.1f}s")
                
                st.success("Génération terminée! Allez dans 'Planning par groupe' pour voir le résultat.")
            except Exception as e:
                st.error(f"Erreur: {e}")


# ============================================================================
# PAGE: EXPORT EXCEL
# ============================================================================
elif "Export Excel" in selection:
    st.title("📥 Export Excel / CSV")
    
    query, _ = get_db()
    if not query:
        st.error("Erreur de connexion")
        st.stop()
    
    st.markdown("### Télécharger les données en format Excel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Données de base")
        
        # Départements
        if st.button("📥 Départements", use_container_width=True):
            data = query("SELECT nom, code FROM departements ORDER BY nom")
            if data:
                df = pd.DataFrame(data)
                excel = export_to_excel(df, "departements.xlsx")
                st.download_button("⬇️ Télécharger", excel, "departements.xlsx", 
                                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Professeurs
        if st.button("📥 Professeurs", use_container_width=True):
            data = query("""
                SELECT p.nom, p.prenom, p.grade, p.specialite, d.nom as departement
                FROM professeurs p
                JOIN departements d ON p.dept_id = d.id
            """)
            if data:
                df = pd.DataFrame(data)
                excel = export_to_excel(df, "professeurs.xlsx")
                st.download_button("⬇️ Télécharger", excel, "professeurs.xlsx",
                                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Salles
        if st.button("📥 Salles", use_container_width=True):
            data = query("SELECT nom, code, type, capacite, batiment FROM lieu_examen")
            if data:
                df = pd.DataFrame(data)
                excel = export_to_excel(df, "salles.xlsx")
                st.download_button("⬇️ Télécharger", excel, "salles.xlsx",
                                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    with col2:
        st.subheader("📅 Planning des examens")
        
        if st.button("📥 Planning Complet", use_container_width=True, type="primary"):
            data = query("""
                SELECT e.date_examen as Date, ch.libelle as Créneau,
                       m.code as Module, m.nom as 'Nom Module',
                       f.nom as Formation, l.nom as Salle
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN formations f ON m.formation_id = f.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                ORDER BY e.date_examen, ch.ordre
            """)
            if data:
                df = pd.DataFrame(data)
                excel = export_to_excel(df, "planning_examens.xlsx")
                st.download_button("⬇️ Télécharger", excel, "planning_examens.xlsx",
                                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.warning("Aucun examen planifié. Générez d'abord le planning.")


# ============================================================================
# PAGE: EXPORT PDF
# ============================================================================
elif "Export PDF" in selection:
    st.title("📄 Export PDF - Plannings")
    
    query, _ = get_db()
    if not query:
        st.error("Erreur de connexion")
        st.stop()
    
    st.markdown("""
    ### Générer des PDF pour:
    - **Planning étudiant** - Par formation/groupe
    - **Planning professeur** - Surveillances assignées
    - **Planning salle** - Occupation des amphithéâtres
    """)
    
    tab1, tab2, tab3 = st.tabs(["👨‍🎓 Étudiants", "👨‍🏫 Professeurs", "🏢 Salles"])
    
    # --- PDF Étudiant ---
    with tab1:
        st.subheader("📄 Planning Étudiant / Formation")
        
        # Filtres
        col1, col2 = st.columns(2)
        
        # Filtre département
        depts = query("SELECT id, nom FROM departements ORDER BY nom")
        with col1:
            if depts:
                dept_opts = {"Tous les départements": None}
                dept_opts.update({d['nom']: d['id'] for d in depts})
                filter_dept = st.selectbox("Département:", list(dept_opts.keys()), key="pdf_dept")
                dept_id = dept_opts[filter_dept]
            else:
                dept_id = None
        
        # Filtre niveau
        with col2:
            niveaux = ["Tous", "L1", "L2", "L3", "M1", "M2"]
            filter_niveau = st.selectbox("Niveau:", niveaux, key="pdf_niveau")
        
        # Formations filtrées
        formations_query = """
            SELECT f.id, f.nom, f.code, f.niveau, d.nom as dept
            FROM formations f
            JOIN departements d ON f.dept_id = d.id
            WHERE 1=1
        """
        params = []
        if dept_id:
            formations_query += " AND f.dept_id = %s"
            params.append(dept_id)
        if filter_niveau != "Tous":
            formations_query += " AND f.niveau = %s"
            params.append(filter_niveau)
        formations_query += " ORDER BY d.nom, f.niveau, f.nom"
        
        formations = query(formations_query, tuple(params) if params else None)
        
        if formations:
            form_options = {f"{f['dept']} - {f['nom']}": (f['id'], f['code'], f['niveau']) for f in formations}
            selected = st.selectbox("Formation:", list(form_options.keys()), key="pdf_form")
            formation_id, formation_code, niveau = form_options[selected]
            
            groupe = st.text_input("Groupe (ex: GL01-GL02):", value=f"{formation_code}01-02")
            
            if st.button("📄 Générer PDF Étudiant", type="primary"):
                examens = query("""
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
                """, (formation_id,))
                
                if examens:
                    try:
                        from services.pdf_generator import generate_student_schedule_pdf
                        pdf = generate_student_schedule_pdf(
                            selected.split(" - ")[-1], groupe, niveau, examens
                        )
                        st.download_button(
                            "⬇️ Télécharger PDF", pdf, 
                            f"planning_{formation_code}_{groupe}.pdf",
                            "application/pdf"
                        )
                        st.success("✅ PDF généré!")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucun examen planifié pour cette formation")
        else:
            st.warning("Aucune formation trouvée avec ces filtres")
    
    # --- PDF Professeur ---
    with tab2:
        st.subheader("📄 Planning Professeur (Surveillances)")
        
        # Filtre département
        depts = query("SELECT id, nom FROM departements ORDER BY nom")
        if depts:
            dept_opts = {"Tous les départements": None}
            dept_opts.update({d['nom']: d['id'] for d in depts})
            filter_dept_prof = st.selectbox("Filtrer par département:", list(dept_opts.keys()), key="pdf_dept_prof")
            prof_dept_id = dept_opts[filter_dept_prof]
        else:
            prof_dept_id = None
        
        prof_query = """
            SELECT p.id, p.nom, p.prenom, d.nom as dept
            FROM professeurs p
            JOIN departements d ON p.dept_id = d.id
        """
        if prof_dept_id:
            prof_query += " WHERE p.dept_id = %s"
            profs = query(prof_query + " ORDER BY p.nom, p.prenom", (prof_dept_id,))
        else:
            profs = query(prof_query + " ORDER BY d.nom, p.nom, p.prenom")
        
        if profs:
            prof_options = {f"{p['prenom']} {p['nom']} ({p['dept']})": (p['id'], p['nom'], p['prenom'], p['dept']) 
                          for p in profs}
            selected = st.selectbox("Professeur:", list(prof_options.keys()), key="pdf_prof")
            prof_id, nom, prenom, dept = prof_options[selected]
            
            if st.button("📄 Générer PDF Professeur", type="primary"):
                surveillances = query("""
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
                """, (prof_id,))
                
                if surveillances:
                    try:
                        from services.pdf_generator import generate_professor_schedule_pdf
                        pdf = generate_professor_schedule_pdf(nom, prenom, dept, surveillances)
                        st.download_button(
                            "⬇️ Télécharger PDF", pdf,
                            f"surveillances_{nom}_{prenom}.pdf",
                            "application/pdf"
                        )
                        st.success("✅ PDF généré!")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucune surveillance assignée à ce professeur")
        else:
            st.warning("Aucun professeur trouvé")
    
    # --- PDF Salle ---
    with tab3:
        st.subheader("📄 Planning Salle / Amphithéâtre")
        
        salles = query("SELECT id, nom, code, capacite FROM lieu_examen ORDER BY code")
        
        if salles:
            salle_options = {f"{s['code']} - {s['nom']} ({s['capacite']} places)": 
                           (s['id'], s['nom'], s['code'], s['capacite']) for s in salles}
            selected = st.selectbox("Choisir la salle:", list(salle_options.keys()), key="pdf_salle")
            salle_id, salle_nom, salle_code, capacite = salle_options[selected]
            
            if st.button("📄 Générer PDF Salle", type="primary"):
                examens = query("""
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
                """, (salle_id,))
                
                if examens:
                    try:
                        from services.pdf_generator import generate_room_schedule_pdf
                        pdf = generate_room_schedule_pdf(salle_nom, salle_code, capacite, examens)
                        st.download_button(
                            "⬇️ Télécharger PDF", pdf,
                            f"occupation_{salle_code}.pdf",
                            "application/pdf"
                        )
                        st.success("✅ PDF généré!")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucun examen planifié dans cette salle")
        else:
            st.warning("Aucune salle trouvée")


# ============================================================================
# PAGE: PLANNING PAR GROUPE
# ============================================================================
elif "Planning par groupe" in selection:
    st.title("📋 Planning par Groupe")
    
    query, _ = get_db()
    if not query:
        st.error("Erreur de connexion")
        st.stop()
    
    st.markdown("""
    ### Format similaire à votre planning réel
    
    Chaque formation a plusieurs groupes, et chaque groupe a sa salle assignée.
    """)
    
    # Sélection de la formation
    formations = query("""
        SELECT f.id, f.nom, f.code
        FROM formations f
        ORDER BY f.nom
    """)
    
    if formations:
        form_options = {f['nom']: f['id'] for f in formations}
        selected_form = st.selectbox("Choisir une formation:", list(form_options.keys()))
        formation_id = form_options[selected_form]
        
        # Récupérer le planning
        planning = query("""
            SELECT e.date_examen, ch.heure_debut, ch.libelle,
                   m.code as module, l.code as salle
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN lieu_examen l ON e.salle_id = l.id
            JOIN creneaux_horaires ch ON e.creneau_id = ch.id
            WHERE m.formation_id = %s
            ORDER BY e.date_examen, ch.ordre
        """, (formation_id,))
        
        if planning:
            # Créer un tableau style planning
            df = pd.DataFrame(planning)
            
            st.subheader(f"Planning: {selected_form}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export
            excel = export_to_excel(df, "planning.xlsx")
            st.download_button("📥 Exporter en Excel", excel, f"planning_{selected_form}.xlsx",
                              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Aucun examen planifié pour cette formation. Générez d'abord le planning.")
    else:
        st.warning("Aucune formation trouvée. Ajoutez des formations dans 'Saisie des données'.")
