"""
Page Consultation - Optimisée pour 130k+ inscriptions
"""
import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
from database import execute_query

def q(sql, params=None):
    try:
        return execute_query(sql, params) or []
    except:
        return []

@st.cache_data(ttl=300)
def get_forms():
    return q("""SELECT f.id, f.nom, d.nom as dept FROM formations f 
                JOIN departements d ON f.dept_id = d.id ORDER BY f.nom LIMIT 100""")

@st.cache_data(ttl=300)
def get_profs():
    return q("""SELECT p.id, p.nom, p.prenom, d.nom as dept FROM professeurs p 
                JOIN departements d ON p.dept_id = d.id ORDER BY p.nom LIMIT 200""")

def render_consultation():
    st.header("📋 Consultation")
    
    typ = st.radio("", ["👨‍🎓 Étudiant", "👨‍🏫 Professeur"], horizontal=True)
    st.divider()
    
    if "Étudiant" in typ:
        f = get_forms()
        if not f: st.warning("Aucune formation"); return
        
        sel = st.selectbox("Formation", [x['nom'] for x in f])
        fid = next(x['id'] for x in f if x['nom'] == sel)
        
        exams = q("""
            SELECT e.date_examen as Date,
                   CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),' - ',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                   m.code as Code, m.nom as Module, l.nom as Salle
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN lieu_examen l ON e.salle_id = l.id
            JOIN creneaux_horaires ch ON e.creneau_id = ch.id
            WHERE m.formation_id = %s ORDER BY e.date_examen, ch.ordre LIMIT 50
        """, (fid,))
        
        if exams:
            st.success(f"📅 {len(exams)} examens")
            st.dataframe(pd.DataFrame(exams), hide_index=True, use_container_width=True)
        else:
            st.info("Aucun examen planifié")
    
    else:
        p = get_profs()
        if not p: st.warning("Aucun professeur"); return
        
        sel = st.selectbox("Professeur", [f"{x['prenom']} {x['nom']} ({x['dept']})" for x in p])
        pid = next(x['id'] for x in p if f"{x['prenom']} {x['nom']} ({x['dept']})" == sel)
        
        survs = q("""
            SELECT e.date_examen as Date,
                   CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),' - ',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                   m.code as Code, m.nom as Module, l.nom as Salle, s.role as Rôle
            FROM surveillances s
            JOIN examens e ON s.examen_id = e.id
            JOIN modules m ON e.module_id = m.id
            JOIN lieu_examen l ON e.salle_id = l.id
            JOIN creneaux_horaires ch ON e.creneau_id = ch.id
            WHERE s.professeur_id = %s ORDER BY e.date_examen LIMIT 50
        """, (pid,))
        
        if survs:
            st.success(f"📅 {len(survs)} surveillances")
            st.dataframe(pd.DataFrame(survs), hide_index=True, use_container_width=True)
        else:
            st.info("Aucune surveillance")

if __name__ == "__main__":
    render_consultation()
