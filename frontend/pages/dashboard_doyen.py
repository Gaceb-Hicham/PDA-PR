"""
Page Tableau de bord - Vue Vice-Doyen/Doyen
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.statistics import (
    get_global_stats, get_department_stats, get_session_stats,
    get_daily_exam_distribution, get_kpis_dashboard
)
from database import execute_query


def render_dashboard():
    """Affiche le tableau de bord principal"""
    st.header("🏠 Tableau de Bord Global")
    
    # Récupérer les KPIs
    try:
        stats = get_global_stats()
        session_id = 1  # Session par défaut
        
        # Ligne de métriques principales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="👨‍🎓 Étudiants",
                value=f"{stats.get('total_etudiants', 0):,}",
                delta="Actifs"
            )
        
        with col2:
            st.metric(
                label="👨‍🏫 Professeurs",
                value=f"{stats.get('total_professeurs', 0):,}",
                delta="Corps enseignant"
            )
        
        with col3:
            st.metric(
                label="📚 Formations",
                value=f"{stats.get('total_formations', 0):,}",
                delta="L1 à M2"
            )
        
        with col4:
            st.metric(
                label="📖 Modules",
                value=f"{stats.get('total_modules', 0):,}",
                delta="S1 & S2"
            )
        
        with col5:
            st.metric(
                label="📝 Inscriptions",
                value=f"{stats.get('total_inscriptions', 0):,}",
                delta="Total"
            )
        
        st.markdown("---")
        
        # Graphiques
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📊 Répartition par Département")
            dept_stats = get_department_stats()
            
            if dept_stats:
                df_dept = pd.DataFrame(dept_stats)
                fig = px.bar(
                    df_dept,
                    x='departement',
                    y=['nb_etudiants', 'nb_professeurs'],
                    title="Étudiants et Professeurs par Département",
                    barmode='group',
                    color_discrete_sequence=['#FF6B35', '#004E89']
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis_title="",
                    yaxis_title="Nombre",
                    legend_title=""
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée de département disponible")
        
        with col_right:
            st.subheader("🏛️ Modules par Département")
            
            if dept_stats:
                df_dept = pd.DataFrame(dept_stats)
                fig = px.pie(
                    df_dept,
                    values='nb_modules',
                    names='departement',
                    title="Distribution des Modules",
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Section examens planifiés
        st.markdown("---")
        st.subheader("📅 Planning des Examens")
        
        # Vérifier si des examens sont planifiés
        examens = execute_query(
            "SELECT COUNT(*) as total FROM examens WHERE session_id = %s",
            (session_id,), fetch='one'
        )
        
        if examens and examens['total'] > 0:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                daily_dist = get_daily_exam_distribution(session_id)
                if daily_dist:
                    df_daily = pd.DataFrame(daily_dist)
                    fig = px.line(
                        df_daily,
                        x='date_examen',
                        y='nb_examens',
                        title="Examens par Jour",
                        markers=True
                    )
                    fig.update_traces(line_color='#FF6B35')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("📝 Examens Planifiés", examens['total'])
                
                # Statut des conflits
                conflits = execute_query(
                    "SELECT COUNT(*) as total FROM conflits WHERE resolu = FALSE",
                    fetch='one'
                )
                if conflits and conflits['total'] > 0:
                    st.error(f"⚠️ {conflits['total']} conflits non résolus")
                else:
                    st.success("✅ Aucun conflit")
        else:
            st.warning("⚠️ Aucun examen planifié. Utilisez la page Planification pour générer l'EDT.")
            
            if st.button("📅 Aller à la Planification"):
                st.session_state['page'] = 'planning'
                st.rerun()
        
        # Tableau récapitulatif des départements
        st.markdown("---")
        st.subheader("📋 Récapitulatif par Département")
        
        if dept_stats:
            df_recap = pd.DataFrame(dept_stats)
            df_recap.columns = ['ID', 'Département', 'Code', 'Formations', 
                               'Étudiants', 'Professeurs', 'Modules', 'Inscriptions']
            df_recap = df_recap.drop('ID', axis=1)
            st.dataframe(df_recap, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error(f"❌ Erreur de connexion à la base de données: {e}")
        st.info("Assurez-vous que MySQL est en cours d'exécution et que les données ont été générées.")


if __name__ == "__main__":
    render_dashboard()
