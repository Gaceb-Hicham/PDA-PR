"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ExamPro - Gestion des Conflits                                              ║
║  Design Premium                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import streamlit as st
import pandas as pd
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


@st.cache_data(ttl=120)
def get_conflict_counts(session_id):
    result = q("""
        SELECT 
            (SELECT COUNT(*) FROM conflits c 
             JOIN examens e ON c.examen1_id = e.id 
             WHERE e.session_id = %s AND c.resolu = FALSE 
             AND c.type_conflit = 'ETUDIANT') as student_conflicts,
            (SELECT COUNT(*) FROM conflits c 
             JOIN examens e ON c.examen1_id = e.id 
             WHERE e.session_id = %s AND c.resolu = FALSE 
             AND c.type_conflit = 'SALLE') as room_conflicts,
            (SELECT COUNT(*) FROM conflits c 
             JOIN examens e ON c.examen1_id = e.id 
             WHERE e.session_id = %s AND c.resolu = FALSE 
             AND c.type_conflit = 'PROFESSEUR') as prof_conflicts,
            (SELECT COUNT(*) FROM examens e 
             JOIN lieu_examen l ON e.salle_id = l.id 
             WHERE e.session_id = %s AND e.nb_etudiants_prevus > l.capacite) as capacity_issues
    """, (session_id, session_id, session_id, session_id))
    return result[0] if result else {'student_conflicts': 0, 'room_conflicts': 0, 'prof_conflicts': 0, 'capacity_issues': 0}


@st.cache_data(ttl=120)
def get_capacity_issues(session_id):
    return q("""
        SELECT m.code, m.nom as module, l.nom as salle, l.capacite, e.nb_etudiants_prevus as etudiants
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN lieu_examen l ON e.salle_id = l.id
        WHERE e.session_id = %s AND e.nb_etudiants_prevus > l.capacite
        LIMIT 50
    """, (session_id,))


def render_conflicts():
    page_header("⚠️", "Détection des Conflits", "Surveillance et résolution des problèmes de planification")
    
    session_id = 1
    counts = get_conflict_counts(session_id)
    
    total_conflicts = (counts['student_conflicts'] or 0) + (counts['room_conflicts'] or 0) + (counts['prof_conflicts'] or 0) + (counts['capacity_issues'] or 0)
    
    # Stats premium
    stats_row([
        {"icon": "👨‍🎓", "value": counts['student_conflicts'] or 0, "label": "Conflits Étudiants"},
        {"icon": "🏛️", "value": counts['room_conflicts'] or 0, "label": "Conflits Salles"},
        {"icon": "👨‍🏫", "value": counts['prof_conflicts'] or 0, "label": "Surcharge Profs"},
        {"icon": "📊", "value": counts['capacity_issues'] or 0, "label": "Dépassement Cap."}
    ])
    
    # Status global
    if total_conflicts == 0:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; margin: 1rem 0;">
            <span style="font-size: 2rem;">✅</span>
            <p style="color: #6EE7B7; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0 0 0;">Aucun conflit détecté !</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; margin: 1rem 0;">
            <span style="font-size: 2rem;">⚠️</span>
            <p style="color: #FCA5A5; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0 0 0;">{total_conflicts} problème(s) à résoudre</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    tab1, tab2, tab3, tab4 = st.tabs(["👨‍🎓 Étudiants", "🏛️ Salles", "👨‍🏫 Professeurs", "📊 Capacité"])
    
    with tab1:
        st.markdown("### 👨‍🎓 Conflits Étudiants")
        st.caption("Étudiants ayant 2+ examens le même jour/créneau")
        if counts['student_conflicts'] > 0:
            conflicts = q("""
                SELECT c.description, c.severite
                FROM conflits c
                JOIN examens e ON c.examen1_id = e.id
                WHERE e.session_id = %s AND c.resolu = FALSE AND c.type_conflit = 'ETUDIANT'
                LIMIT 20
            """, (session_id,))
            if conflicts:
                st.dataframe(pd.DataFrame(conflicts), hide_index=True, use_container_width=True)
        else:
            st.success("✅ Aucun conflit étudiant")
    
    with tab2:
        st.markdown("### 🏛️ Conflits Salles")
        st.caption("Double réservation de salles")
        if counts['room_conflicts'] > 0:
            conflicts = q("""
                SELECT c.description, c.severite
                FROM conflits c
                JOIN examens e ON c.examen1_id = e.id
                WHERE e.session_id = %s AND c.resolu = FALSE AND c.type_conflit = 'SALLE'
                LIMIT 20
            """, (session_id,))
            if conflicts:
                st.dataframe(pd.DataFrame(conflicts), hide_index=True, use_container_width=True)
        else:
            st.success("✅ Aucun conflit de salle")
    
    with tab3:
        st.markdown("### 👨‍🏫 Surcharge Professeurs")
        st.caption("Professeurs avec trop de surveillances/jour")
        if counts['prof_conflicts'] > 0:
            conflicts = q("""
                SELECT c.description, c.severite
                FROM conflits c
                JOIN examens e ON c.examen1_id = e.id
                WHERE e.session_id = %s AND c.resolu = FALSE AND c.type_conflit = 'PROFESSEUR'
                LIMIT 20
            """, (session_id,))
            if conflicts:
                st.dataframe(pd.DataFrame(conflicts), hide_index=True, use_container_width=True)
        else:
            st.success("✅ Aucune surcharge")
    
    with tab4:
        st.markdown("### 📊 Dépassement Capacité")
        st.caption("Examens avec plus d'étudiants que la capacité de la salle")
        capacity_issues = get_capacity_issues(session_id)
        if capacity_issues:
            df = pd.DataFrame(capacity_issues)
            df.columns = ['Code', 'Module', 'Salle', 'Capacité', 'Étudiants']
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.success("✅ Aucun dépassement")


if __name__ == "__main__":
    render_conflicts()
