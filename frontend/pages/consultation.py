"""
Page Consultation - Vue Étudiant/Professeur
"""
import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from database import execute_query


def render_consultation():
    """Affiche la page de consultation des plannings"""
    st.header("📋 Consultation du Planning")
    
    # Choix du type d'utilisateur
    user_type = st.radio(
        "Je suis:",
        ["👨‍🎓 Étudiant", "👨‍🏫 Professeur"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if "Étudiant" in user_type:
        render_student_view()
    else:
        render_professor_view()


def render_student_view():
    """Vue étudiant"""
    st.subheader("👨‍🎓 Mon Planning d'Examens")
    
    # Sélection de la formation
    formations = execute_query("""
        SELECT f.id, f.nom, f.niveau, d.nom as dept
        FROM formations f
        JOIN departements d ON f.dept_id = d.id
        ORDER BY d.nom, f.niveau, f.nom
    """)
    
    if not formations:
        st.warning("Aucune formation trouvée")
        return
    
    formation_options = {f"{f['dept']} - {f['nom']}": f['id'] for f in formations}
    selected = st.selectbox("Ma formation", options=list(formation_options.keys()))
    formation_id = formation_options[selected]
    
    session_id = 1
    
    # Récupérer les examens
    examens = execute_query("""
        SELECT 
            e.date_examen as Date,
            ch.libelle as Créneau,
            ch.heure_debut as Début,
            ch.heure_fin as Fin,
            m.code as Code,
            m.nom as Module,
            l.nom as Salle,
            l.batiment as Bâtiment
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN lieu_examen l ON e.salle_id = l.id
        JOIN creneaux_horaires ch ON e.creneau_id = ch.id
        WHERE f.id = %s AND e.session_id = %s AND m.semestre = 'S1'
        ORDER BY e.date_examen, ch.ordre
    """, (formation_id, session_id))
    
    if examens:
        st.success(f"📅 {len(examens)} examens prévus")
        
        df = pd.DataFrame(examens)
        
        # Affichage par date
        for date in df['Date'].unique():
            st.markdown(f"### 📅 {date}")
            day_exams = df[df['Date'] == date]
            
            for _, exam in day_exams.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        **{exam['Code']}** - {exam['Module']}  
                        🕐 {exam['Créneau']} ({exam['Début']} - {exam['Fin']})
                        """)
                    with col2:
                        st.markdown(f"📍 {exam['Salle']}")
                    st.markdown("---")
        
        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger mon planning", csv, "mon_planning.csv", "text/csv")
    else:
        st.info("Aucun examen planifié pour cette formation")


def render_professor_view():
    """Vue professeur"""
    st.subheader("👨‍🏫 Mes Surveillances")
    
    # Sélection du professeur
    profs = execute_query("""
        SELECT p.id, p.nom, p.prenom, d.nom as dept
        FROM professeurs p
        JOIN departements d ON p.dept_id = d.id
        ORDER BY d.nom, p.nom
    """)
    
    if not profs:
        st.warning("Aucun professeur trouvé")
        return
    
    prof_options = {f"{p['prenom']} {p['nom']} ({p['dept']})": p['id'] for p in profs}
    selected = st.selectbox("Mon nom", options=list(prof_options.keys()))
    prof_id = prof_options[selected]
    
    session_id = 1
    
    # Récupérer les surveillances
    surveillances = execute_query("""
        SELECT 
            e.date_examen as Date,
            ch.libelle as Créneau,
            ch.heure_debut as Début,
            ch.heure_fin as Fin,
            m.code as Code,
            m.nom as Module,
            l.nom as Salle,
            s.role as Rôle
        FROM surveillances s
        JOIN examens e ON s.examen_id = e.id
        JOIN modules m ON e.module_id = m.id
        JOIN lieu_examen l ON e.salle_id = l.id
        JOIN creneaux_horaires ch ON e.creneau_id = ch.id
        WHERE s.professeur_id = %s AND e.session_id = %s
        ORDER BY e.date_examen, ch.ordre
    """, (prof_id, session_id))
    
    if surveillances:
        st.success(f"📅 {len(surveillances)} surveillances assignées")
        
        df = pd.DataFrame(surveillances)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Résumé
        col1, col2 = st.columns(2)
        with col1:
            resp = len(df[df['Rôle'] == 'RESPONSABLE'])
            st.metric("🎯 Responsable", resp)
        with col2:
            surv = len(df[df['Rôle'] == 'SURVEILLANT'])
            st.metric("👁️ Surveillant", surv)
        
        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger", csv, "mes_surveillances.csv", "text/csv")
    else:
        st.info("Aucune surveillance assignée")


if __name__ == "__main__":
    render_consultation()
