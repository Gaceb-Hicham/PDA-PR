"""
Page Statistiques - Rapports et analyses
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.statistics import (
    get_department_stats, get_room_utilization, 
    get_professor_workload, get_formation_exam_progress
)
from database import execute_query


def render_stats():
    """Affiche la page de statistiques"""
    st.header("📊 Statistiques et Rapports")
    
    session_id = 1
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏛️ Départements",
        "🏢 Salles",
        "👨‍🏫 Professeurs",
        "📚 Formations"
    ])
    
    with tab1:
        render_department_stats()
    
    with tab2:
        render_room_stats(session_id)
    
    with tab3:
        render_professor_stats(session_id)
    
    with tab4:
        render_formation_stats(session_id)


def render_department_stats():
    """Statistiques par département"""
    st.subheader("🏛️ Statistiques par Département")
    
    stats = get_department_stats()
    
    if stats:
        df = pd.DataFrame(stats)
        
        # Graphique comparatif
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Étudiants', x=df['departement'], 
                            y=df['nb_etudiants'], marker_color='#FF6B35'))
        fig.add_trace(go.Bar(name='Professeurs', x=df['departement'], 
                            y=df['nb_professeurs'], marker_color='#004E89'))
        fig.add_trace(go.Bar(name='Modules', x=df['departement'], 
                            y=df['nb_modules'], marker_color='#2ECC71'))
        
        fig.update_layout(
            barmode='group',
            title="Comparaison par Département",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau détaillé
        df_display = df[['departement', 'nb_formations', 'nb_etudiants', 
                        'nb_professeurs', 'nb_modules']]
        df_display.columns = ['Département', 'Formations', 'Étudiants', 
                             'Professeurs', 'Modules']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée disponible")


def render_room_stats(session_id):
    """Statistiques des salles"""
    st.subheader("🏢 Utilisation des Salles")
    
    rooms = get_room_utilization(session_id)
    
    if rooms:
        df = pd.DataFrame(rooms)
        
        # Graphique d'utilisation
        fig = px.bar(
            df.head(20),
            x='nom',
            y='taux_utilisation',
            color='type',
            title="Taux d'Utilisation des Salles (Top 20)",
            color_discrete_map={'AMPHI': '#FF6B35', 'SALLE': '#004E89', 'LABO': '#2ECC71'}
        )
        fig.update_layout(
            xaxis_title="Salle",
            yaxis_title="Taux d'utilisation (%)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Résumé par type
        col1, col2, col3 = st.columns(3)
        
        amphis = df[df['type'] == 'AMPHI']
        salles = df[df['type'] == 'SALLE']
        labos = df[df['type'] == 'LABO']
        
        with col1:
            st.metric("🏛️ Amphithéâtres", len(amphis), 
                     f"Moy: {amphis['taux_utilisation'].mean():.1f}%" if len(amphis) > 0 else "0%")
        with col2:
            st.metric("🚪 Salles", len(salles),
                     f"Moy: {salles['taux_utilisation'].mean():.1f}%" if len(salles) > 0 else "0%")
        with col3:
            st.metric("🔬 Laboratoires", len(labos),
                     f"Moy: {labos['taux_utilisation'].mean():.1f}%" if len(labos) > 0 else "0%")
    else:
        st.info("Aucune donnée d'utilisation disponible")


def render_professor_stats(session_id):
    """Statistiques des professeurs"""
    st.subheader("👨‍🏫 Charge des Professeurs")
    
    workload = get_professor_workload(session_id)
    
    if workload:
        df = pd.DataFrame(workload)
        
        # Distribution des surveillances
        fig = px.histogram(
            df,
            x='nb_surveillances',
            color='departement',
            title="Distribution des Surveillances par Professeur",
            nbins=10
        )
        fig.update_layout(
            xaxis_title="Nombre de surveillances",
            yaxis_title="Nombre de professeurs",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top professeurs
        st.subheader("Top 10 - Plus de surveillances")
        df_top = df.nlargest(10, 'nb_surveillances')[
            ['nom', 'prenom', 'departement', 'grade', 'nb_surveillances']
        ]
        df_top.columns = ['Nom', 'Prénom', 'Département', 'Grade', 'Surveillances']
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée de charge disponible")


def render_formation_stats(session_id):
    """Statistiques par formation"""
    st.subheader("📚 Progression par Formation")
    
    # Filtre département
    depts = execute_query("SELECT id, nom FROM departements ORDER BY nom")
    dept_options = {"Tous les départements": None}
    dept_options.update({d['nom']: d['id'] for d in depts})
    selected_dept = st.selectbox("Filtrer par département", options=list(dept_options.keys()))
    
    progress = get_formation_exam_progress(session_id, dept_options[selected_dept])
    
    if progress:
        df = pd.DataFrame(progress)
        
        # Graphique de progression
        fig = px.bar(
            df,
            x='formation',
            y='taux_planification',
            color='niveau',
            title="Taux de Planification par Formation",
            hover_data=['total_modules', 'modules_planifies']
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Taux de planification (%)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau
        df_display = df[['formation', 'niveau', 'departement', 'total_modules', 
                        'modules_planifies', 'taux_planification']]
        df_display.columns = ['Formation', 'Niveau', 'Département', 'Total Modules',
                            'Modules Planifiés', 'Taux (%)']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée de progression disponible")


if __name__ == "__main__":
    render_stats()
