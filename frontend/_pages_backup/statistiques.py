"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ExamPro - Statistiques                                                      ║
║  Design Premium                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database import execute_query
from design import inject_premium_css, page_header, stats_row

inject_premium_css()


def q(sql, params=None):
    try:
        return execute_query(sql, params) or []
    except:
        return []


def render_stats():
    page_header("📊", "Statistiques", "Analyse détaillée des données de la faculté")
    
    tab1, tab2, tab3 = st.tabs(["📈 Générales", "🏛️ Départements", "📅 Examens"])
    
    with tab1:
        st.markdown("### 📈 Statistiques Globales")
        
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
            stats_row([
                {"icon": "🏛️", "value": s['depts'], "label": "Départements"},
                {"icon": "📚", "value": s['forms'], "label": "Formations"},
                {"icon": "📖", "value": s['mods'], "label": "Modules"},
                {"icon": "👨‍🏫", "value": s['profs'], "label": "Professeurs"}
            ])
            stats_row([
                {"icon": "👨‍🎓", "value": f"{s['etuds']:,}", "label": "Étudiants"},
                {"icon": "📝", "value": f"{s['inscrip']:,}", "label": "Inscriptions"},
                {"icon": "📅", "value": s['exams'], "label": "Examens"},
                {"icon": "👁️", "value": s['survs'], "label": "Surveillances"}
            ])
    
    with tab2:
        st.markdown("### 🏛️ Statistiques par Département")
        
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
            
            st.markdown("#### 📊 Répartition des Étudiants")
            fig = px.bar(df, x='Département', y='Étudiants', 
                        color='Étudiants',
                        color_continuous_scale=['#6366F1', '#EC4899'])
            fig.update_layout(
                showlegend=False, 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                font_color='#94A3B8',
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 🎓 Répartition Professeurs/Formations")
            fig2 = px.scatter(df, x='Professeurs', y='Formations', size='Étudiants',
                            color='Département', size_max=60,
                            color_discrete_sequence=['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981'])
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                font_color='#94A3B8'
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.markdown("### 📅 Statistiques des Examens")
        
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
            # Summary
            total_exams = sum(e['Examens'] for e in exam_stats)
            total_students = sum(e['Étudiants'] or 0 for e in exam_stats)
            
            stats_row([
                {"icon": "📅", "value": len(exam_stats), "label": "Jours d'examens"},
                {"icon": "📝", "value": total_exams, "label": "Total Examens"},
                {"icon": "👨‍🎓", "value": f"{total_students:,}", "label": "Places Étudiants"}
            ])
            
            st.divider()
            
            df = pd.DataFrame(exam_stats)
            
            st.markdown("#### 📊 Distribution Journalière")
            fig = px.area(df, x='Date', y='Examens')
            fig.update_traces(fill='tozeroy', line_color='#6366F1', fillcolor='rgba(99,102,241,0.3)')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#94A3B8'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 📋 Détail par Jour")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📋 Aucun examen planifié")


if __name__ == "__main__":
    render_stats()
