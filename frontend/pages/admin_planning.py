"""
Page Admin Planning - VERSION OPTIMISÉE
"""
import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from database import execute_query, get_cursor


def q(sql, params=None, fetch='all'):
    try:
        return execute_query(sql, params, fetch=fetch)
    except:
        return [] if fetch == 'all' else None


def render_planning():
    st.header("📅 Planification EDT")
    
    tab1, tab2, tab3 = st.tabs(["🚀 Génération", "📋 Planning", "🏛️ Salles"])
    
    with tab1:
        st.subheader("🚀 Génération Automatique")
        
        sessions = q("SELECT * FROM sessions_examen ORDER BY date_debut DESC LIMIT 10")
        
        if not sessions:
            st.warning("Aucune session trouvée")
            return
        
        opts = {f"{s['nom']} ({s['date_debut']} - {s['date_fin']})": s['id'] for s in sessions}
        sel = st.selectbox("Session", list(opts.keys()))
        sid = opts[sel]
        
        session = next(s for s in sessions if s['id'] == sid)
        
        c1, c2, c3 = st.columns(3)
        c1.info(f"📅 Début: {session['date_debut']}")
        c2.info(f"📅 Fin: {session['date_fin']}")
        c3.info(f"📊 Statut: {session['statut']}")
        
        st.divider()
        
        if st.button("🚀 Lancer la Génération", type="primary", use_container_width=True):
            with st.spinner("Génération en cours..."):
                try:
                    with get_cursor() as cursor:
                        cursor.execute("DELETE FROM surveillances WHERE examen_id IN (SELECT id FROM examens WHERE session_id = %s)", (sid,))
                        cursor.execute("DELETE FROM examens WHERE session_id = %s", (sid,))
                    
                    from services.optimization import run_optimization
                    start = datetime.now()
                    report = run_optimization(sid)
                    time_taken = (datetime.now() - start).total_seconds()
                    
                    st.success(f"✅ Terminé en {time_taken:.2f}s!")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Examens", report.get('scheduled', 0))
                    c2.metric("Conflits", report.get('conflicts', 0))
                    c3.metric("Taux", f"{report.get('success_rate', 0):.1f}%")
                    
                except Exception as e:
                    st.error(f"Erreur: {e}")
    
    with tab2:
        st.subheader("📋 Planning Actuel")
        
        # Filtres simples
        c1, c2 = st.columns(2)
        depts = q("SELECT id, nom FROM departements ORDER BY nom LIMIT 20")
        dept_opts = {"Tous": None}
        dept_opts.update({d['nom']: d['id'] for d in depts} if depts else {})
        sel_dept = c1.selectbox("Département", list(dept_opts.keys()))
        
        dates = q("SELECT DISTINCT date_examen FROM examens WHERE session_id = 1 ORDER BY date_examen LIMIT 30")
        date_opts = ["Toutes"] + [str(d['date_examen']) for d in dates] if dates else ["Toutes"]
        sel_date = c2.selectbox("Date", date_opts)
        
        # Requête avec filtres
        sql = """
            SELECT 
                e.date_examen AS Date,
                CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) AS Horaire,
                m.code AS Code, m.nom AS Module, f.nom AS Formation,
                l.nom AS Salle, e.nb_etudiants_prevus AS Étudiants
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN departements d ON f.dept_id = d.id
            JOIN lieu_examen l ON e.salle_id = l.id
            JOIN creneaux_horaires ch ON e.creneau_id = ch.id
            WHERE e.session_id = 1
        """
        params = []
        
        if dept_opts[sel_dept]:
            sql += " AND d.id = %s"
            params.append(dept_opts[sel_dept])
        
        if sel_date != "Toutes":
            sql += " AND e.date_examen = %s"
            params.append(sel_date)
        
        sql += " ORDER BY e.date_examen, ch.ordre LIMIT 100"
        
        exams = q(sql, tuple(params) if params else None)
        
        if exams:
            st.dataframe(pd.DataFrame(exams), use_container_width=True, hide_index=True)
        else:
            st.info("Aucun examen")
    
    with tab3:
        st.subheader("🏛️ Gestion des Salles")
        
        salles = q("""
            SELECT l.nom, l.code, l.type, l.capacite, l.batiment,
                   COUNT(e.id) as examens
            FROM lieu_examen l
            LEFT JOIN examens e ON e.salle_id = l.id
            GROUP BY l.id
            ORDER BY l.type, l.capacite DESC
            LIMIT 60
        """)
        
        if salles:
            df = pd.DataFrame(salles)
            df.columns = ['Nom', 'Code', 'Type', 'Capacité', 'Bâtiment', 'Examens']
            st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    render_planning()
