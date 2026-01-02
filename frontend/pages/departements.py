"""
Page Départements - VERSION OPTIMISÉE
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from database import execute_query


def q(sql, params=None, fetch='all'):
    try:
        return execute_query(sql, params, fetch=fetch)
    except:
        return [] if fetch == 'all' else None


def render_departments():
    st.header("🏛️ Gestion des Départements")
    
    depts = q("SELECT * FROM departements ORDER BY nom")
    
    if not depts:
        st.warning("Aucun département trouvé")
        return
    
    dept_opts = {d['nom']: d['id'] for d in depts}
    sel = st.selectbox("Département", list(dept_opts.keys()))
    did = dept_opts[sel]
    
    st.divider()
    
    dept = next(d for d in depts if d['id'] == did)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(f"📊 {dept['nom']}")
        st.caption(f"Code: {dept['code']}")
    
    # Stats rapides
    stats = q("""
        SELECT 
            (SELECT COUNT(*) FROM formations f WHERE f.dept_id = %s) as forms,
            (SELECT COUNT(*) FROM professeurs p WHERE p.dept_id = %s) as profs,
            (SELECT COUNT(*) FROM etudiants e 
             JOIN formations f ON e.formation_id = f.id WHERE f.dept_id = %s) as etuds,
            (SELECT COUNT(*) FROM modules m 
             JOIN formations f ON m.formation_id = f.id WHERE f.dept_id = %s) as mods
    """, (did, did, did, did))
    
    if stats:
        s = stats[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📚 Formations", s['forms'])
        c2.metric("👨‍🎓 Étudiants", s['etuds'])
        c3.metric("👨‍🏫 Professeurs", s['profs'])
        c4.metric("📖 Modules", s['mods'])
    
    st.divider()
    
    # Tabs avec Étudiants et Salles
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Formations", "👨‍🏫 Professeurs", "👨‍🎓 Étudiants", "🏢 Salles", "📅 Examens"])
    
    with tab1:
        forms = q("""
            SELECT f.nom, f.code, f.niveau,
                   (SELECT COUNT(*) FROM etudiants e WHERE e.formation_id = f.id) as etudiants,
                   (SELECT COUNT(*) FROM modules m WHERE m.formation_id = f.id) as modules
            FROM formations f
            WHERE f.dept_id = %s
            ORDER BY f.niveau, f.nom
            LIMIT 50
        """, (did,))
        
        if forms:
            df = pd.DataFrame(forms)
            df.columns = ['Formation', 'Code', 'Niveau', 'Étudiants', 'Modules']
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune formation")
    
    with tab2:
        profs = q("""
            SELECT p.nom, p.prenom, p.grade, p.specialite,
                   (SELECT COUNT(*) FROM surveillances s WHERE s.professeur_id = p.id) as survs
            FROM professeurs p
            WHERE p.dept_id = %s
            ORDER BY p.grade DESC, p.nom
            LIMIT 50
        """, (did,))
        
        if profs:
            df = pd.DataFrame(profs)
            df.columns = ['Nom', 'Prénom', 'Grade', 'Spécialité', 'Surveillances']
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun professeur")
    
    with tab3:
        # Étudiants du département
        etudiants = q("""
            SELECT e.matricule, e.nom, e.prenom, COALESCE(e.groupe, 'G01') as groupe,
                   f.nom as formation, f.niveau
            FROM etudiants e
            JOIN formations f ON e.formation_id = f.id
            WHERE f.dept_id = %s
            ORDER BY f.nom, e.groupe, e.nom
            LIMIT 100
        """, (did,))
        
        if etudiants:
            df = pd.DataFrame(etudiants)
            df.columns = ['Matricule', 'Nom', 'Prénom', 'Groupe', 'Formation', 'Niveau']
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"{len(etudiants)} étudiants affichés (max 100)")
        else:
            st.info("Aucun étudiant")
    
    with tab4:
        # Salles utilisées par ce département
        salles = q("""
            SELECT DISTINCT l.nom, l.code, l.type, l.capacite,
                   (SELECT COUNT(*) FROM examens e2 
                    JOIN modules m2 ON e2.module_id = m2.id 
                    JOIN formations f2 ON m2.formation_id = f2.id 
                    WHERE e2.salle_id = l.id AND f2.dept_id = %s) as examens
            FROM lieu_examen l
            JOIN examens e ON e.salle_id = l.id
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE f.dept_id = %s
            ORDER BY l.type, l.capacite DESC
            LIMIT 50
        """, (did, did))
        
        if salles:
            df = pd.DataFrame(salles)
            df.columns = ['Salle', 'Code', 'Type', 'Capacité', 'Examens']
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune salle utilisée par ce département")
    
    with tab5:
        exams = q("""
            SELECT e.date_examen as Date,
                   CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),' - ',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                   m.code as Code, m.nom as Module, COALESCE(e.groupe, 'G01') as Groupe, l.nom as Salle
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN lieu_examen l ON e.salle_id = l.id
            JOIN creneaux_horaires ch ON e.creneau_id = ch.id
            WHERE f.dept_id = %s
            ORDER BY e.date_examen, ch.ordre
            LIMIT 50
        """, (did,))
        
        if exams:
            df = pd.DataFrame(exams)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun examen planifié")


if __name__ == "__main__":
    render_departments()
