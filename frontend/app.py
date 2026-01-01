"""
Application Streamlit - Plateforme EDT Examens
Version stable et simplifiée
"""
import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configuration
st.set_page_config(
    page_title="Plateforme EDT Examens",
    page_icon="🎓",
    layout="wide"
)

# État de la page
if 'page' not in st.session_state:
    st.session_state.page = "Accueil"

# Sidebar Navigation
st.sidebar.title("🎓 EDT Examens")
st.sidebar.markdown("---")

pages = [
    "🏠 Accueil",
    "📊 Tableau de bord",
    "➕ Gestion des données",
    "📅 Génération EDT",
    "⚠️ Conflits",
    "📋 Consultation"
]

selection = st.sidebar.radio("Navigation", pages, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.info("Université M'Hamed Bougara\nFaculté des Sciences\nSession S1 2025/2026")


# ============================================================================
# FONCTIONS DE CONNEXION
# ============================================================================

def get_db_connection():
    """Connexion simple à la base de données"""
    try:
        from database import execute_query
        return True, execute_query
    except Exception as e:
        return False, str(e)


# ============================================================================
# PAGES
# ============================================================================

if "Accueil" in selection:
    st.title("🎓 Plateforme d'Optimisation des EDT d'Examens")
    
    st.markdown("""
    ## Bienvenue!
    
    Cette plateforme permet de **planifier automatiquement les emplois du temps d'examens** 
    en respectant toutes les contraintes académiques.
    
    ### 📋 Comment ça marche?
    
    1. **Les données sont pré-chargées** (professeurs, salles, formations, modules)
       - Via le script `seed_data.py` pour les données de démonstration
       - Ou via l'interface "Gestion des données" pour ajouter manuellement
    
    2. **L'algorithme génère automatiquement le planning**
       - Respecte: max 1 examen/jour par étudiant
       - Respecte: max 3 surveillances/jour par prof
       - Respecte: capacité des salles
       - Optimise: répartition équitable des surveillances
    
    3. **Vous pouvez consulter le résultat**
       - Voir les conflits détectés
       - Exporter les plannings
    
    ### 🚀 Pour commencer
    
    1. Allez dans **"Gestion des données"** pour voir/ajouter les données
    2. Allez dans **"Génération EDT"** pour créer le planning
    3. Consultez les résultats dans **"Tableau de bord"**
    """)
    
    # Test de connexion
    st.markdown("---")
    st.subheader("🔌 État de la connexion")
    
    connected, result = get_db_connection()
    if connected:
        try:
            count = result("SELECT COUNT(*) as c FROM etudiants", fetch='one')
            if count and count['c'] > 0:
                st.success(f"✅ Base de données connectée - {count['c']:,} étudiants trouvés")
            else:
                st.warning("⚠️ Connecté mais aucune donnée. Exécutez `python seed_data.py`")
        except:
            st.warning("⚠️ Connecté mais tables non créées. Exécutez le script SQL.")
    else:
        st.error(f"❌ Erreur de connexion: {result}")


elif "Tableau de bord" in selection:
    st.title("📊 Tableau de Bord")
    
    connected, query = get_db_connection()
    if not connected:
        st.error("Erreur de connexion à la base de données")
    else:
        try:
            # Métriques
            col1, col2, col3, col4 = st.columns(4)
            
            r = query("SELECT COUNT(*) as c FROM etudiants", fetch='one')
            col1.metric("👨‍🎓 Étudiants", f"{r['c']:,}" if r else 0)
            
            r = query("SELECT COUNT(*) as c FROM professeurs", fetch='one')
            col2.metric("👨‍🏫 Professeurs", f"{r['c']:,}" if r else 0)
            
            r = query("SELECT COUNT(*) as c FROM formations", fetch='one')
            col3.metric("📚 Formations", f"{r['c']:,}" if r else 0)
            
            r = query("SELECT COUNT(*) as c FROM examens", fetch='one')
            col4.metric("📝 Examens planifiés", f"{r['c']:,}" if r else 0)
            
            st.markdown("---")
            
            # Départements
            st.subheader("🏛️ Départements")
            depts = query("""
                SELECT d.nom as Département, d.code as Code,
                       COUNT(DISTINCT p.id) as Professeurs,
                       COUNT(DISTINCT f.id) as Formations
                FROM departements d
                LEFT JOIN professeurs p ON p.dept_id = d.id
                LEFT JOIN formations f ON f.dept_id = d.id
                GROUP BY d.id, d.nom, d.code
                ORDER BY d.nom
            """)
            if depts:
                st.dataframe(pd.DataFrame(depts), use_container_width=True, hide_index=True)
                
        except Exception as e:
            st.error(f"Erreur: {e}")


elif "Gestion des données" in selection:
    st.title("➕ Gestion des Données")
    
    st.markdown("""
    ### Comment les données sont-elles ajoutées?
    
    **Option 1: Données de démonstration (recommandé pour tester)**
    
    Exécutez dans le terminal:
    ```
    cd backend
    python seed_data.py
    ```
    Cela crée automatiquement ~13,000 étudiants, 175 professeurs, etc.
    
    ---
    
    **Option 2: Entrée manuelle (pour production)**
    
    Dans un système réel, vous auriez des formulaires pour ajouter:
    - Départements
    - Formations
    - Professeurs
    - Salles d'examen
    - Etc.
    """)
    
    connected, query = get_db_connection()
    if connected:
        st.markdown("---")
        st.subheader("📊 Données actuelles dans la base")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Départements", "Professeurs", "Salles", "Formations"])
        
        with tab1:
            try:
                data = query("SELECT nom, code FROM departements ORDER BY nom LIMIT 20")
                if data:
                    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                else:
                    st.info("Aucun département. Exécutez seed_data.py")
            except Exception as e:
                st.error(str(e))
        
        with tab2:
            try:
                data = query("""
                    SELECT p.nom, p.prenom, p.grade, d.nom as departement
                    FROM professeurs p
                    JOIN departements d ON p.dept_id = d.id
                    ORDER BY p.nom LIMIT 20
                """)
                if data:
                    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                else:
                    st.info("Aucun professeur")
            except Exception as e:
                st.error(str(e))
        
        with tab3:
            try:
                data = query("""
                    SELECT nom, code, type, capacite, batiment
                    FROM lieu_examen
                    ORDER BY type, capacite DESC LIMIT 20
                """)
                if data:
                    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                else:
                    st.info("Aucune salle")
            except Exception as e:
                st.error(str(e))
        
        with tab4:
            try:
                data = query("""
                    SELECT f.nom, f.niveau, d.nom as departement
                    FROM formations f
                    JOIN departements d ON f.dept_id = d.id
                    ORDER BY d.nom, f.niveau LIMIT 20
                """)
                if data:
                    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                else:
                    st.info("Aucune formation")
            except Exception as e:
                st.error(str(e))


elif "Génération EDT" in selection:
    st.title("📅 Génération de l'Emploi du Temps")
    
    st.markdown("""
    ### Comment fonctionne la génération automatique?
    
    L'algorithme:
    1. Récupère tous les modules à planifier (semestre S1)
    2. Pour chaque module, cherche un créneau valide:
       - Vérifie qu'aucun étudiant inscrit n'a déjà un examen ce jour
       - Vérifie qu'un professeur est disponible (max 3 surveillances/jour)
       - Vérifie qu'une salle de capacité suffisante est libre
    3. Affecte le meilleur créneau trouvé
    4. Détecte et signale les conflits impossibles à résoudre
    
    **Objectif**: Générer le planning en moins de 45 secondes
    """)
    
    st.markdown("---")
    
    connected, query = get_db_connection()
    if not connected:
        st.error("Erreur de connexion")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 Lancer la génération")
            
            if st.button("Générer le planning", type="primary", use_container_width=True):
                with st.spinner("Génération en cours..."):
                    try:
                        from services.optimization import run_optimization
                        report = run_optimization(1)
                        
                        st.success("✅ Génération terminée!")
                        st.metric("Examens planifiés", report.get('scheduled', 0))
                        st.metric("Conflits", report.get('conflicts', 0))
                        st.metric("Temps", f"{report.get('execution_time', 0):.2f}s")
                        
                    except Exception as e:
                        st.error(f"Erreur: {e}")
        
        with col2:
            st.subheader("📋 Planning actuel")
            
            try:
                examens = query("""
                    SELECT e.date_examen, ch.libelle as creneau, 
                           m.code, l.nom as salle
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN lieu_examen l ON e.salle_id = l.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    ORDER BY e.date_examen, ch.ordre
                    LIMIT 50
                """)
                if examens:
                    st.dataframe(pd.DataFrame(examens), use_container_width=True, hide_index=True)
                else:
                    st.info("Aucun examen planifié. Cliquez sur 'Générer'.")
            except Exception as e:
                st.error(str(e))


elif "Conflits" in selection:
    st.title("⚠️ Conflits Détectés")
    
    connected, query = get_db_connection()
    if connected:
        try:
            count = query("SELECT COUNT(*) as c FROM conflits WHERE resolu = FALSE", fetch='one')
            total = count['c'] if count else 0
            
            if total > 0:
                st.error(f"⚠️ {total} conflits non résolus")
                
                conflicts = query("""
                    SELECT type_conflit, severite, description, created_at
                    FROM conflits
                    WHERE resolu = FALSE
                    ORDER BY severite, created_at DESC
                    LIMIT 20
                """)
                if conflicts:
                    st.dataframe(pd.DataFrame(conflicts), use_container_width=True, hide_index=True)
            else:
                st.success("✅ Aucun conflit détecté!")
                
        except Exception as e:
            st.info("Aucun conflit ou table non créée")


elif "Consultation" in selection:
    st.title("📋 Consultation des Plannings")
    
    st.info("Cette page permet aux étudiants et professeurs de consulter leur planning personnel.")
    
    connected, query = get_db_connection()
    if connected:
        user_type = st.radio("Je suis:", ["Étudiant", "Professeur"], horizontal=True)
        
        if user_type == "Étudiant":
            st.subheader("🎓 Mon planning d'examens")
            
            try:
                formations = query("""
                    SELECT f.id, CONCAT(f.niveau, ' - ', f.nom) as label
                    FROM formations f
                    ORDER BY f.niveau, f.nom
                    LIMIT 30
                """)
                if formations:
                    options = {f['label']: f['id'] for f in formations}
                    selected = st.selectbox("Ma formation:", list(options.keys()))
                    formation_id = options[selected]
                    
                    examens = query("""
                        SELECT e.date_examen, ch.libelle, m.nom as module, l.nom as salle
                        FROM examens e
                        JOIN modules m ON e.module_id = m.id
                        JOIN lieu_examen l ON e.salle_id = l.id
                        JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                        WHERE m.formation_id = %s
                        ORDER BY e.date_examen, ch.ordre
                    """, (formation_id,))
                    
                    if examens:
                        st.dataframe(pd.DataFrame(examens), use_container_width=True, hide_index=True)
                    else:
                        st.info("Aucun examen planifié pour cette formation")
            except Exception as e:
                st.error(str(e))
        else:
            st.subheader("👨‍🏫 Mes surveillances")
            st.info("Sélectionnez votre nom pour voir vos surveillances assignées.")
