"""
Page Statistiques - VERSION OPTIMISÉE
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from database import execute_query


def q(sql, params=None):
    try:
        return execute_query(sql, params) or []
    except:
        return []


def render_stats():
    st.header("📊 Statistiques")
    
    tab1, tab2, tab3 = st.tabs(["Générales", "Par Département", "Examens"])
    
    with tab1:
        st.subheader("📈 Statistiques Globales")
        
        stats = q("""
            SELECT 
                (SELECT COUNT(*) FROM departements) as depts,
                (SELECT COUNT(*) FROM formations) as forms,
                (SELECT COUNT(*) FROM modules) as mods,
                (SELECT COUNT(*) FROM professeurs) as profs,
                (SELECT COUNT(*) FROM etudiants) as etuds,
                (SELECT COUNT(*) FROM inscriptions) as inscrip,
                (SELECT COUNT(*) FROM examens) as exams,
                (SELECT COUNT(*) FROM surveillances) as survs
        """)
        
        if stats:
            s = stats[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Départements", s['depts'])
            c2.metric("Formations", s['forms'])
            c3.metric("Modules", s['mods'])
            c4.metric("Professeurs", s['profs'])
            
            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Étudiants", f"{s['etuds']:,}")
            c6.metric("Inscriptions", f"{s['inscrip']:,}")
            c7.metric("Examens", s['exams'])
            c8.metric("Surveillances", s['survs'])
    
    with tab2:
        st.subheader("🏛️ Par Département")
        
        dept_stats = q("""
            SELECT 
                d.nom as Département,
                d.code as Code,
                (SELECT COUNT(*) FROM formations f WHERE f.dept_id = d.id) as Formations,
                (SELECT COUNT(*) FROM professeurs p WHERE p.dept_id = d.id) as Professeurs,
                (SELECT COUNT(*) FROM etudiants e 
                 JOIN formations f ON e.formation_id = f.id WHERE f.dept_id = d.id) as Étudiants
            FROM departements d
            ORDER BY d.nom
        """)
        
        if dept_stats:
            df = pd.DataFrame(dept_stats)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            fig = px.bar(df, x='Département', y='Étudiants', color='Département')
            fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', 
                            paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📅 Statistiques Examens")
        
        exam_stats = q("""
            SELECT 
                e.date_examen as Date,
                COUNT(*) as Examens,
                SUM(e.nb_etudiants_prevus) as Étudiants,
                COUNT(DISTINCT e.salle_id) as Salles
            FROM examens e
            WHERE e.session_id = 1
            GROUP BY e.date_examen
            ORDER BY e.date_examen
            LIMIT 30
        """)
        
        if exam_stats:
            df = pd.DataFrame(exam_stats)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            fig = px.line(df, x='Date', y='Examens', markers=True)
            fig.update_traces(line_color='#FF6B35')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun examen planifié")


if __name__ == "__main__":
    render_stats()
