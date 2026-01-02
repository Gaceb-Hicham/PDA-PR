"""
Page Dashboard Doyen - VERSION OPTIMISÉE
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.statistics import get_global_stats, get_department_stats, get_daily_exam_distribution
from database import execute_query


def q(sql, params=None, fetch='all'):
    try:
        return execute_query(sql, params, fetch=fetch)
    except:
        return [] if fetch == 'all' else None


def render_dashboard():
    st.header("🏠 Tableau de Bord Global")
    
    try:
        # Stats globales - une seule requête optimisée
        stats = get_global_stats()
        
        # Métriques principales
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("👨‍🎓 Étudiants", f"{stats.get('total_etudiants', 0):,}", "Actifs")
        c2.metric("👨‍🏫 Professeurs", f"{stats.get('total_professeurs', 0):,}", "Corps enseignant")
        c3.metric("📚 Formations", f"{stats.get('total_formations', 0):,}", "L1 à M2")
        c4.metric("📖 Modules", f"{stats.get('total_modules', 0):,}", "S1 & S2")
        c5.metric("📝 Inscriptions", f"{stats.get('total_inscriptions', 0):,}", "Total")
        
        st.divider()
        
        # Graphiques par département
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📊 Répartition par Département")
            dept_stats = get_department_stats()
            
            if dept_stats:
                df = pd.DataFrame(dept_stats)
                fig = px.bar(df, x='departement', y=['nb_etudiants', 'nb_professeurs'],
                           barmode='group', color_discrete_sequence=['#FF6B35', '#004E89'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white', xaxis_title="", yaxis_title="Nombre")
                st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("🏛️ Modules par Département")
            if dept_stats:
                df = pd.DataFrame(dept_stats)
                fig = px.pie(df, values='nb_modules', names='departement',
                           color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white')
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Examens planifiés
        st.subheader("📅 Planning des Examens")
        
        exam_count = q("SELECT COUNT(*) as total FROM examens WHERE session_id = 1", fetch='one')
        
        if exam_count and exam_count['total'] > 0:
            c1, c2 = st.columns([2, 1])
            
            with c1:
                daily = get_daily_exam_distribution(1)
                if daily:
                    df = pd.DataFrame(daily)
                    fig = px.line(df, x='date_examen', y='nb_examens', markers=True)
                    fig.update_traces(line_color='#FF6B35')
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                    font_color='white')
                    st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.metric("📝 Examens Planifiés", exam_count['total'])
                conflicts = q("SELECT COUNT(*) as c FROM conflits WHERE resolu = FALSE", fetch='one')
                if conflicts and conflicts['c'] > 0:
                    st.error(f"⚠️ {conflicts['c']} conflits")
                else:
                    st.success("✅ Aucun conflit")
        else:
            st.warning("⚠️ Aucun examen planifié")
        
        # Récapitulatif
        st.divider()
        st.subheader("📋 Récapitulatif")
        if dept_stats:
            df = pd.DataFrame(dept_stats)
            df = df[['departement', 'code', 'nb_formations', 'nb_etudiants', 'nb_professeurs', 'nb_modules']]
            df.columns = ['Département', 'Code', 'Formations', 'Étudiants', 'Professeurs', 'Modules']
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error(f"❌ Erreur: {e}")


if __name__ == "__main__":
    render_dashboard()
