"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ExamPro - Consultation des Plannings                                        ║
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
from design import inject_premium_css, page_header

inject_premium_css()


def q(sql, params=None):
    try:
        return execute_query(sql, params) or []
    except:
        return []


@st.cache_data(ttl=300)
def get_forms():
    return q("""SELECT f.id, f.nom, f.niveau, d.nom as dept FROM formations f 
                JOIN departements d ON f.dept_id = d.id ORDER BY d.nom, f.niveau, f.nom LIMIT 150""")


@st.cache_data(ttl=300)
def get_profs():
    return q("""SELECT p.id, p.nom, p.prenom, p.grade, d.nom as dept FROM professeurs p 
                JOIN departements d ON p.dept_id = d.id ORDER BY d.nom, p.nom LIMIT 200""")


def render_consultation():
    page_header("📋", "Consultation des Plannings", "Recherchez les emplois du temps par formation ou professeur")
    
    # Selection type
    st.markdown("""
    <style>
        .type-selector {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .type-btn {
            flex: 1;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .type-btn:hover, .type-btn.active {
            background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(236,72,153,0.1) 100%);
            border-color: rgba(99,102,241,0.4);
        }
        .type-btn .icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .type-btn .label { color: #F8FAFC; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)
    
    typ = st.radio("Type de consultation", ["👨‍🎓 Par Formation", "👨‍🏫 Par Professeur"], horizontal=True, label_visibility="collapsed")
    
    st.divider()
    
    if "Formation" in typ:
        st.markdown("### 📚 Planning par Formation")
        
        formations = get_forms()
        if not formations:
            st.warning("Aucune formation trouvée")
            return
        
        # Filtres
        depts = list(set(f['dept'] for f in formations))
        c1, c2 = st.columns(2)
        sel_dept = c1.selectbox("🏛️ Département", ["Tous"] + sorted(depts))
        
        if sel_dept != "Tous":
            formations = [f for f in formations if f['dept'] == sel_dept]
        
        sel_form = c2.selectbox("📚 Formation", [f['nom'] for f in formations])
        fid = next(f['id'] for f in formations if f['nom'] == sel_form)
        
        exams = q("""
            SELECT e.date_examen as Date,
                   CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),' - ',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                   m.code as Code, m.nom as Module, COALESCE(e.groupe, 'G01') as Groupe, l.nom as Salle
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN lieu_examen l ON e.salle_id = l.id
            JOIN creneaux_horaires ch ON e.creneau_id = ch.id
            WHERE m.formation_id = %s ORDER BY e.date_examen, ch.ordre LIMIT 80
        """, (fid,))
        
        if exams:
            st.success(f"📅 {len(exams)} examens trouvés")
            st.dataframe(pd.DataFrame(exams), hide_index=True, use_container_width=True)
        else:
            st.info("📋 Aucun examen planifié pour cette formation")
    
    else:
        st.markdown("### 👨‍🏫 Planning Professeur")
        
        profs = get_profs()
        if not profs:
            st.warning("Aucun professeur trouvé")
            return
        
        # Filtres
        depts = list(set(p['dept'] for p in profs))
        c1, c2 = st.columns(2)
        sel_dept = c1.selectbox("🏛️ Département", ["Tous"] + sorted(depts), key="prof_dept")
        
        if sel_dept != "Tous":
            profs = [p for p in profs if p['dept'] == sel_dept]
        
        sel_prof = c2.selectbox("👨‍🏫 Professeur", [f"{p['prenom']} {p['nom']} - {p['grade']}" for p in profs])
        pid = next(p['id'] for p in profs if f"{p['prenom']} {p['nom']} - {p['grade']}" == sel_prof)
        
        survs = q("""
            SELECT e.date_examen as Date,
                   CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),' - ',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                   m.code as Code, m.nom as Module, l.nom as Salle, s.role as Rôle
            FROM surveillances s
            JOIN examens e ON s.examen_id = e.id
            JOIN modules m ON e.module_id = m.id
            JOIN lieu_examen l ON e.salle_id = l.id
            JOIN creneaux_horaires ch ON e.creneau_id = ch.id
            WHERE s.professeur_id = %s ORDER BY e.date_examen LIMIT 80
        """, (pid,))
        
        if survs:
            st.success(f"📅 {len(survs)} surveillances")
            st.dataframe(pd.DataFrame(survs), hide_index=True, use_container_width=True)
        else:
            st.info("📋 Aucune surveillance assignée")


if __name__ == "__main__":
    render_consultation()
