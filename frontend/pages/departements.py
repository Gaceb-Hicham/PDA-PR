"""
Page Départements - Vue Chef de Département
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.statistics import get_department_stats, get_formation_exam_progress
from database import execute_query


def render_departments():
    """Affiche la page de gestion des départements"""
    st.header("🏛️ Gestion des Départements")
    
    # Sélection du département
    depts = execute_query("SELECT * FROM departements ORDER BY nom")
    
    if not depts:
        st.warning("Aucun département trouvé. Veuillez d'abord générer les données.")
        return
    
    dept_options = {d['nom']: d['id'] for d in depts}
    selected_dept = st.selectbox("Sélectionner un département", options=list(dept_options.keys()))
    dept_id = dept_options[selected_dept]
    
    st.markdown("---")
    
    # Informations du département
    dept = next(d for d in depts if d['id'] == dept_id)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📊 {dept['nom']}")
        st.caption(f"Code: {dept['code']}")
    
    with col2:
        if dept['chef_dept_id']:
            chef = execute_query(
                "SELECT nom, prenom FROM professeurs WHERE id = %s",
                (dept['chef_dept_id'],), fetch='one'
            )
            if chef:
                st.info(f"👤 Chef: {chef['prenom']} {chef['nom']}")
    
    # Statistiques
    stats = get_department_stats(dept_id)
    
    if stats:
        stat = stats[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Formations", stat.get('nb_formations', 0))
        with col2:
            st.metric("👨‍🎓 Étudiants", stat.get('nb_etudiants', 0))
        with col3:
            st.metric("👨‍🏫 Professeurs", stat.get('nb_professeurs', 0))
        with col4:
            st.metric("📖 Modules", stat.get('nb_modules', 0))
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📚 Formations", "👨‍🏫 Professeurs", "📅 Examens"])
    
    with tab1:
        render_dept_formations(dept_id)
    
    with tab2:
        render_dept_professors(dept_id)
    
    with tab3:
        render_dept_exams(dept_id)


def render_dept_formations(dept_id):
    """Formations du département"""
    st.subheader("📚 Formations")
    
    formations = execute_query("""
        SELECT f.*, COUNT(DISTINCT e.id) as nb_etudiants, COUNT(DISTINCT m.id) as nb_modules
        FROM formations f
        LEFT JOIN etudiants e ON e.formation_id = f.id
        LEFT JOIN modules m ON m.formation_id = f.id
        WHERE f.dept_id = %s
        GROUP BY f.id
        ORDER BY f.niveau, f.nom
    """, (dept_id,))
    
    if formations:
        df = pd.DataFrame(formations)
        df_display = df[['nom', 'code', 'niveau', 'nb_modules', 'nb_etudiants']]
        df_display.columns = ['Formation', 'Code', 'Niveau', 'Modules', 'Étudiants']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Graphique par niveau
        fig = px.pie(df, values='nb_etudiants', names='niveau',
                    title="Répartition des Étudiants par Niveau")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune formation trouvée")


def render_dept_professors(dept_id):
    """Professeurs du département"""
    st.subheader("👨‍🏫 Corps Enseignant")
    
    profs = execute_query("""
        SELECT p.*, COUNT(s.id) as nb_surveillances
        FROM professeurs p
        LEFT JOIN surveillances s ON s.professeur_id = p.id
        WHERE p.dept_id = %s
        GROUP BY p.id
        ORDER BY p.grade DESC, p.nom
    """, (dept_id,))
    
    if profs:
        df = pd.DataFrame(profs)
        df_display = df[['nom', 'prenom', 'grade', 'specialite', 'nb_surveillances']]
        df_display.columns = ['Nom', 'Prénom', 'Grade', 'Spécialité', 'Surveillances']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Répartition par grade
        grade_counts = df['grade'].value_counts()
        fig = px.bar(x=grade_counts.index, y=grade_counts.values,
                    title="Répartition par Grade",
                    labels={'x': 'Grade', 'y': 'Nombre'})
        fig.update_traces(marker_color='#FF6B35')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun professeur trouvé")


def render_dept_exams(dept_id):
    """Examens du département"""
    st.subheader("📅 Examens Planifiés")
    
    session_id = 1
    
    examens = execute_query("""
        SELECT e.date_examen, ch.libelle as creneau, m.code, m.nom as module,
               l.nom as salle, e.nb_etudiants_prevus as etudiants
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN lieu_examen l ON e.salle_id = l.id
        JOIN creneaux_horaires ch ON e.creneau_id = ch.id
        WHERE f.dept_id = %s AND e.session_id = %s
        ORDER BY e.date_examen, ch.ordre
    """, (dept_id, session_id))
    
    if examens:
        df = pd.DataFrame(examens)
        df.columns = ['Date', 'Créneau', 'Code', 'Module', 'Salle', 'Étudiants']
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter", csv, "examens_dept.csv", "text/csv")
    else:
        st.info("Aucun examen planifié pour ce département")


if __name__ == "__main__":
    render_departments()
