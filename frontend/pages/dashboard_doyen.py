"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ExamPro - Tableau de Bord Doyen                                             ║
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

from services.statistics import get_global_stats, get_department_stats, get_daily_exam_distribution
from database import execute_query
from design import inject_premium_css, page_header, stats_row

inject_premium_css()


def q(sql, params=None, fetch='all'):
    try:
        return execute_query(sql, params, fetch=fetch)
    except:
        return [] if fetch == 'all' else None


def render_dashboard():
    page_header("🎓", "Tableau de Bord Doyen", "Vue d'ensemble de la faculté et du planning des examens")
    
    try:
        stats = get_global_stats()
        
        # Stats premium
        stats_row([
            {"icon": "👨‍🎓", "value": f"{stats.get('total_etudiants', 0):,}", "label": "Étudiants"},
            {"icon": "👨‍🏫", "value": stats.get('total_professeurs', 0), "label": "Professeurs"},
            {"icon": "📚", "value": stats.get('total_formations', 0), "label": "Formations"},
            {"icon": "📖", "value": stats.get('total_modules', 0), "label": "Modules"},
            {"icon": "📝", "value": f"{stats.get('total_inscriptions', 0):,}", "label": "Inscriptions"}
        ])
        
        st.divider()
        
        # Charts
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### 📊 Répartition par Département")
            dept_stats = get_department_stats()
            
            if dept_stats:
                df = pd.DataFrame(dept_stats)
                fig = px.bar(df, x='departement', y=['nb_etudiants', 'nb_professeurs'],
                           barmode='group', 
                           color_discrete_sequence=['#6366F1', '#EC4899'],
                           labels={'value': 'Nombre', 'variable': 'Type'})
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#94A3B8', 
                    xaxis_title="", 
                    yaxis_title="",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.markdown("### 🎓 Modules par Département")
            if dept_stats:
                df = pd.DataFrame(dept_stats)
                fig = px.pie(df, values='nb_modules', names='departement',
                           color_discrete_sequence=['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#06B6D4'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#94A3B8'
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Examens
        st.markdown("### 📅 Planning des Examens")
        
        exam_count = q("SELECT COUNT(*) as total FROM examens WHERE session_id = 1", fetch='one')
        
        if exam_count and exam_count['total'] > 0:
            c1, c2 = st.columns([3, 1])
            
            with c1:
                daily = get_daily_exam_distribution(1)
                if daily:
                    df = pd.DataFrame(daily)
                    fig = px.area(df, x='date_examen', y='nb_examens')
                    fig.update_traces(fill='tozeroy', line_color='#6366F1', fillcolor='rgba(99,102,241,0.3)')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#94A3B8',
                        xaxis_title="Date",
                        yaxis_title="Nombre d'examens"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.1) 100%); 
                            border: 1px solid rgba(99,102,241,0.3); border-radius: 16px; padding: 1.5rem; text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 800; color: #F8FAFC;">{exam_count['total']}</div>
                    <div style="color: #94A3B8; font-size: 0.85rem;">Examens Planifiés</div>
                </div>
                """, unsafe_allow_html=True)
                
                conflicts = q("SELECT COUNT(*) as c FROM conflits WHERE resolu = FALSE", fetch='one')
                if conflicts and conflicts['c'] > 0:
                    st.markdown(f"""
                    <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); 
                                border-radius: 12px; padding: 1rem; text-align: center; margin-top: 1rem;">
                        <span style="color: #FCA5A5; font-weight: 600;">⚠️ {conflicts['c']} conflits</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); 
                                border-radius: 12px; padding: 1rem; text-align: center; margin-top: 1rem;">
                        <span style="color: #6EE7B7; font-weight: 600;">✅ Aucun conflit</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📋 Aucun examen planifié. Lancez la génération de l'emploi du temps.")
        
        # Table récap
        st.divider()
        st.markdown("### 📋 Récapitulatif par Département")
        if dept_stats:
            df = pd.DataFrame(dept_stats)
            df = df[['departement', 'code', 'nb_formations', 'nb_etudiants', 'nb_professeurs', 'nb_modules']]
            df.columns = ['Département', 'Code', 'Formations', 'Étudiants', 'Professeurs', 'Modules']
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error(f"❌ Erreur: {e}")


if __name__ == "__main__":
    render_dashboard()
