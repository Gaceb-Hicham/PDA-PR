"""
Page Conflits - Détection et gestion des conflits
"""
import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.conflicts import (
    detect_student_conflicts, detect_room_conflicts,
    detect_professor_overload, detect_capacity_overflow, get_conflict_stats
)
from database import execute_query


def render_conflicts():
    """Affiche la page de gestion des conflits"""
    st.header("⚠️ Détection et Gestion des Conflits")
    
    session_id = 1
    
    # Résumé des conflits
    st.subheader("📊 Résumé")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        student_conflicts = detect_student_conflicts(session_id)
        st.metric(
            "👨‍🎓 Conflits Étudiants",
            len(student_conflicts),
            delta="2+ examens/jour" if student_conflicts else None,
            delta_color="inverse"
        )
    
    with col2:
        room_conflicts = detect_room_conflicts(session_id)
        st.metric(
            "🏛️ Conflits Salles",
            len(room_conflicts),
            delta="Double réservation" if room_conflicts else None,
            delta_color="inverse"
        )
    
    with col3:
        prof_overload = detect_professor_overload(session_id)
        st.metric(
            "👨‍🏫 Surcharge Profs",
            len(prof_overload),
            delta=">3 surv/jour" if prof_overload else None,
            delta_color="inverse"
        )
    
    with col4:
        capacity_issues = detect_capacity_overflow(session_id)
        st.metric(
            "📊 Dépassement Capacité",
            len(capacity_issues),
            delta="Salle insuffisante" if capacity_issues else None,
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Tabs pour les différents types de conflits
    tab1, tab2, tab3, tab4 = st.tabs([
        "👨‍🎓 Étudiants", 
        "🏛️ Salles", 
        "👨‍🏫 Professeurs",
        "📊 Capacité"
    ])
    
    with tab1:
        render_student_conflicts(student_conflicts)
    
    with tab2:
        render_room_conflicts(room_conflicts)
    
    with tab3:
        render_prof_conflicts(prof_overload)
    
    with tab4:
        render_capacity_conflicts(capacity_issues)


def render_student_conflicts(conflicts):
    """Affiche les conflits étudiants"""
    st.subheader("👨‍🎓 Étudiants avec plusieurs examens le même jour")
    
    if conflicts:
        df = pd.DataFrame(conflicts)
        df.columns = ['ID', 'Nom', 'Prénom', 'Date', 'Module 1', 'Module 2']
        df = df.drop('ID', axis=1)
        
        st.error(f"⚠️ {len(conflicts)} conflits détectés!")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **Actions recommandées:**
        - Replanifier un des deux examens à une autre date
        - Vérifier les inscriptions de l'étudiant
        """)
    else:
        st.success("✅ Aucun conflit étudiant détecté")


def render_room_conflicts(conflicts):
    """Affiche les conflits de salles"""
    st.subheader("🏛️ Doubles réservations de salles")
    
    if conflicts:
        df = pd.DataFrame(conflicts)
        st.error(f"⚠️ {len(conflicts)} conflits détectés!")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **Actions recommandées:**
        - Changer la salle d'un des examens
        - Modifier l'horaire d'un examen
        """)
    else:
        st.success("✅ Aucun conflit de salle détecté")


def render_prof_conflicts(conflicts):
    """Affiche les surcharges professeurs"""
    st.subheader("👨‍🏫 Professeurs surchargés (>3 surveillances/jour)")
    
    if conflicts:
        df = pd.DataFrame(conflicts)
        st.warning(f"⚠️ {len(conflicts)} surcharges détectées!")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **Actions recommandées:**
        - Réassigner certaines surveillances
        - Équilibrer la charge entre professeurs
        """)
    else:
        st.success("✅ Aucune surcharge professeur détectée")


def render_capacity_conflicts(conflicts):
    """Affiche les dépassements de capacité"""
    st.subheader("📊 Salles sous-dimensionnées")
    
    if conflicts:
        df = pd.DataFrame(conflicts)
        st.warning(f"⚠️ {len(conflicts)} dépassements détectés!")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **Actions recommandées:**
        - Affecter une salle plus grande
        - Diviser l'examen en plusieurs salles
        """)
    else:
        st.success("✅ Aucun dépassement de capacité détecté")


if __name__ == "__main__":
    render_conflicts()
