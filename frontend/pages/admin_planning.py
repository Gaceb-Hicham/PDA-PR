"""
Page Administration - Planification EDT
"""
import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.optimization import run_optimization, ExamScheduler
from database import execute_query, get_cursor


def render_planning():
    """Affiche la page de planification EDT"""
    st.header("📅 Planification des Emplois du Temps")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🚀 Génération", "📋 Planning Actuel", "🏛️ Salles"])
    
    with tab1:
        render_generation_tab()
    
    with tab2:
        render_current_planning()
    
    with tab3:
        render_rooms_management()


def render_generation_tab():
    """Onglet de génération EDT"""
    st.subheader("🚀 Génération Automatique de l'EDT")
    
    # Sélection de la session
    sessions = execute_query("SELECT * FROM sessions_examen ORDER BY date_debut DESC")
    
    if not sessions:
        st.warning("Aucune session d'examen trouvée. Créez d'abord une session.")
        return
    
    session_options = {f"{s['nom']} ({s['date_debut']} - {s['date_fin']})": s['id'] for s in sessions}
    selected_session = st.selectbox("Session d'examen", options=list(session_options.keys()))
    session_id = session_options[selected_session]
    
    # Informations session
    session = next(s for s in sessions if s['id'] == session_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📅 Début: {session['date_debut']}")
    with col2:
        st.info(f"📅 Fin: {session['date_fin']}")
    with col3:
        st.info(f"📊 Statut: {session['statut']}")
    
    st.markdown("---")
    
    # Options d'optimisation
    st.subheader("⚙️ Paramètres d'Optimisation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_exam_student = st.number_input(
            "Max examens/jour/étudiant",
            min_value=1, max_value=3, value=1
        )
        prioritize_dept = st.checkbox("Priorité surveillants du département", value=True)
    
    with col2:
        max_exam_prof = st.number_input(
            "Max surveillances/jour/prof",
            min_value=1, max_value=5, value=3
        )
        balance_workload = st.checkbox("Équilibrer les charges", value=True)
    
    st.markdown("---")
    
    # Bouton de génération
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Lancer la Génération", use_container_width=True, type="primary"):
            with st.spinner("⏳ Génération en cours... (objectif: < 45 secondes)"):
                try:
                    # Supprimer les anciens examens
                    with get_cursor() as cursor:
                        cursor.execute("DELETE FROM examens WHERE session_id = %s", (session_id,))
                    
                    # Lancer l'optimisation
                    start_time = datetime.now()
                    report = run_optimization(session_id)
                    end_time = datetime.now()
                    
                    exec_time = (end_time - start_time).total_seconds()
                    
                    # Afficher les résultats
                    st.success(f"✅ Génération terminée en {exec_time:.2f} secondes!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Examens Planifiés", report.get('scheduled', 0))
                    with col2:
                        st.metric("Conflits", report.get('conflicts', 0))
                    with col3:
                        success_rate = report.get('success_rate', 0)
                        st.metric("Taux de Réussite", f"{success_rate:.1f}%")
                    
                    # Vérifier la contrainte de temps
                    if exec_time <= 45:
                        st.success("⏱️ Objectif de performance atteint (< 45s)")
                    else:
                        st.warning(f"⏱️ Temps d'exécution supérieur à l'objectif (45s)")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération: {e}")


def render_current_planning():
    """Affiche le planning actuel"""
    st.subheader("📋 Planning des Examens")
    
    session_id = 1
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        depts = execute_query("SELECT id, nom FROM departements ORDER BY nom")
        dept_options = {"Tous": None}
        dept_options.update({d['nom']: d['id'] for d in depts})
        selected_dept = st.selectbox("Département", options=list(dept_options.keys()))
    
    with col2:
        dates = execute_query(
            "SELECT DISTINCT date_examen FROM examens WHERE session_id = %s ORDER BY date_examen",
            (session_id,)
        )
        date_options = ["Toutes"] + [str(d['date_examen']) for d in dates]
        selected_date = st.selectbox("Date", options=date_options)
    
    with col3:
        salles = execute_query("SELECT id, nom FROM lieu_examen ORDER BY nom")
        salle_options = {"Toutes": None}
        salle_options.update({s['nom']: s['id'] for s in salles})
        selected_salle = st.selectbox("Salle", options=list(salle_options.keys()))
    
    # Construire la requête
    query = """
        SELECT 
            e.date_examen AS Date,
            ch.libelle AS Créneau,
            m.code AS 'Code Module',
            m.nom AS Module,
            f.nom AS Formation,
            d.nom AS Département,
            l.nom AS Salle,
            e.nb_etudiants_prevus AS Étudiants,
            e.statut AS Statut
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        JOIN lieu_examen l ON e.salle_id = l.id
        JOIN creneaux_horaires ch ON e.creneau_id = ch.id
        WHERE e.session_id = %s
    """
    params = [session_id]
    
    if dept_options[selected_dept]:
        query += " AND d.id = %s"
        params.append(dept_options[selected_dept])
    
    if selected_date != "Toutes":
        query += " AND e.date_examen = %s"
        params.append(selected_date)
    
    if salle_options[selected_salle]:
        query += " AND l.id = %s"
        params.append(salle_options[selected_salle])
    
    query += " ORDER BY e.date_examen, ch.ordre"
    
    # Exécuter et afficher
    examens = execute_query(query, tuple(params))
    
    if examens:
        df = pd.DataFrame(examens)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Exporter CSV",
            csv,
            "planning_examens.csv",
            "text/csv",
            use_container_width=True
        )
    else:
        st.info("Aucun examen ne correspond aux critères sélectionnés.")


def render_rooms_management():
    """Gestion des salles"""
    st.subheader("🏛️ Gestion des Salles")
    
    salles = execute_query("""
        SELECT l.*, 
               COUNT(e.id) as nb_examens
        FROM lieu_examen l
        LEFT JOIN examens e ON e.salle_id = l.id
        GROUP BY l.id
        ORDER BY l.type, l.capacite DESC
    """)
    
    if salles:
        df = pd.DataFrame(salles)
        df = df[['nom', 'code', 'type', 'capacite', 'batiment', 'disponible', 'nb_examens']]
        df.columns = ['Nom', 'Code', 'Type', 'Capacité', 'Bâtiment', 'Disponible', 'Examens']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune salle trouvée.")


if __name__ == "__main__":
    render_planning()
