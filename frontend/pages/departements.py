"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ExamPro - Gestion des Départements                                         ║
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


def q(sql, params=None, fetch='all'):
    try:
        return execute_query(sql, params, fetch=fetch)
    except:
        return [] if fetch == 'all' else None


def render_departments():
    page_header("🏛️", "Gestion des Départements", "Vue détaillée des départements et de leurs ressources")
    
    depts = q("SELECT * FROM departements ORDER BY nom")
    
    if not depts:
        st.warning("⚠️ Aucun département trouvé")
        return
    
    dept_opts = {d['nom']: d['id'] for d in depts}
    sel = st.selectbox("🏛️ Sélectionner un département", list(dept_opts.keys()))
    did = dept_opts[sel]
    
    dept = next(d for d in depts if d['id'] == did)
    
    # Header département
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.1) 100%);
                border: 1px solid rgba(99,102,241,0.2); border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="color: #F8FAFC; margin: 0; font-size: 1.5rem;">{dept['nom']}</h2>
                <p style="color: #94A3B8; margin: 0.25rem 0 0 0;">Code: <span style="color: #6366F1; font-weight: 600;">{dept['code']}</span></p>
            </div>
            <div style="font-size: 3rem; opacity: 0.5;">🎓</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
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
        stats_row([
            {"icon": "📚", "value": s['forms'], "label": "Formations"},
            {"icon": "👨‍🎓", "value": f"{s['etuds']:,}", "label": "Étudiants"},
            {"icon": "👨‍🏫", "value": s['profs'], "label": "Professeurs"},
            {"icon": "📖", "value": s['mods'], "label": "Modules"}
        ])
    
    st.divider()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Formations", "👨‍🏫 Professeurs", "👨‍🎓 Étudiants", "🏢 Salles", "📅 Examens"])
    
    with tab1:
        st.markdown("### 📚 Formations")
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
            st.info("📚 Aucune formation")
    
    with tab2:
        st.markdown("### 👨‍🏫 Professeurs")
        profs = q("""
            SELECT p.nom, p.prenom, p.grade, COALESCE(p.specialite, '-') as spec,
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
            st.info("👨‍🏫 Aucun professeur")
    
    with tab3:
        st.markdown("### 👨‍🎓 Étudiants")
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
            st.caption(f"📊 {len(etudiants)} étudiants affichés (max 100)")
        else:
            st.info("👨‍🎓 Aucun étudiant")
    
    with tab4:
        st.markdown("### 🏢 Salles Utilisées")
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
            st.info("🏢 Aucune salle utilisée par ce département")
    
    with tab5:
        st.markdown("### 📅 Examens")
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
            LIMIT 80
        """, (did,))
        
        if exams:
            st.success(f"📅 {len(exams)} examens")
            df = pd.DataFrame(exams)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📅 Aucun examen planifié")


if __name__ == "__main__":
    render_departments()
