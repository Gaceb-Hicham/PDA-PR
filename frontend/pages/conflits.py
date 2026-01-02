"""
Page Conflits - VERSION OPTIMISÉE
Utilise des requêtes COUNT() rapides et du cache
"""
import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from database import execute_query


def q(sql, params=None):
    try:
        return execute_query(sql, params) or []
    except:
        return []


@st.cache_data(ttl=120)
def get_conflict_counts(session_id):
    """Compte les conflits rapidement avec COUNT()"""
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
    """Examens avec dépassement de capacité"""
    return q("""
        SELECT m.code, m.nom as module, l.nom as salle, l.capacite, e.nb_etudiants_prevus as etudiants
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN lieu_examen l ON e.salle_id = l.id
        WHERE e.session_id = %s AND e.nb_etudiants_prevus > l.capacite
        LIMIT 50
    """, (session_id,))


def render_conflicts():
    st.header("⚠️ Détection et Gestion des Conflits")
    
    session_id = 1
    
    # Résumé avec COUNT() rapide
    st.subheader("📊 Résumé")
    
    counts = get_conflict_counts(session_id)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👨‍🎓 Étudiants", counts['student_conflicts'], 
              delta="2+ examens/jour" if counts['student_conflicts'] else None, delta_color="inverse")
    c2.metric("🏛️ Salles", counts['room_conflicts'],
              delta="Double réservation" if counts['room_conflicts'] else None, delta_color="inverse")
    c3.metric("👨‍🏫 Professeurs", counts['prof_conflicts'],
              delta=">3 surv/jour" if counts['prof_conflicts'] else None, delta_color="inverse")
    c4.metric("📊 Capacité", counts['capacity_issues'],
              delta="Salle insuffisante" if counts['capacity_issues'] else None, delta_color="inverse")
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👨‍🎓 Étudiants", "🏛️ Salles", "👨‍🏫 Professeurs", "📊 Capacité"])
    
    with tab1:
        st.subheader("👨‍🎓 Conflits Étudiants")
        if counts['student_conflicts'] > 0:
            conflicts = q("""
                SELECT c.description, c.severite
                FROM conflits c
                JOIN examens e ON c.examen1_id = e.id
                WHERE e.session_id = %s AND c.resolu = FALSE AND c.type_conflit = 'ETUDIANT'
                LIMIT 20
            """, (session_id,))
            if conflicts:
                st.error(f"⚠️ {len(conflicts)} conflits")
                st.dataframe(pd.DataFrame(conflicts), hide_index=True)
            else:
                st.success("✅ Aucun conflit")
        else:
            st.success("✅ Aucun conflit étudiant")
    
    with tab2:
        st.subheader("🏛️ Conflits Salles")
        if counts['room_conflicts'] > 0:
            conflicts = q("""
                SELECT c.description, c.severite
                FROM conflits c
                JOIN examens e ON c.examen1_id = e.id
                WHERE e.session_id = %s AND c.resolu = FALSE AND c.type_conflit = 'SALLE'
                LIMIT 20
            """, (session_id,))
            if conflicts:
                st.error(f"⚠️ {len(conflicts)} conflits")
                st.dataframe(pd.DataFrame(conflicts), hide_index=True)
            else:
                st.success("✅ Aucun conflit")
        else:
            st.success("✅ Aucun conflit de salle")
    
    with tab3:
        st.subheader("👨‍🏫 Surcharge Professeurs")
        if counts['prof_conflicts'] > 0:
            conflicts = q("""
                SELECT c.description, c.severite
                FROM conflits c
                JOIN examens e ON c.examen1_id = e.id
                WHERE e.session_id = %s AND c.resolu = FALSE AND c.type_conflit = 'PROFESSEUR'
                LIMIT 20
            """, (session_id,))
            if conflicts:
                st.warning(f"⚠️ {len(conflicts)} surcharges")
                st.dataframe(pd.DataFrame(conflicts), hide_index=True)
            else:
                st.success("✅ Aucune surcharge")
        else:
            st.success("✅ Aucune surcharge professeur")
    
    with tab4:
        st.subheader("📊 Dépassement Capacité")
        capacity_issues = get_capacity_issues(session_id)
        if capacity_issues:
            st.warning(f"⚠️ {len(capacity_issues)} dépassements")
            df = pd.DataFrame(capacity_issues)
            df.columns = ['Code', 'Module', 'Salle', 'Capacité', 'Étudiants']
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.success("✅ Aucun dépassement de capacité")


if __name__ == "__main__":
    render_conflicts()
