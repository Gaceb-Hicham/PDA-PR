"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ExamPro - Planification EDT                                                 ║
║  Design Premium                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database import execute_query, get_cursor
from design import inject_premium_css, page_header, stats_row

# Inject CSS
inject_premium_css()

def q(sql, params=None, fetch='all'):
    try:
        return execute_query(sql, params, fetch=fetch)
    except:
        return [] if fetch == 'all' else None


def render_planning():
    page_header("📅", "Planification EDT", "Génération et gestion des emplois du temps d'examens")
    
    tab1, tab2, tab3 = st.tabs(["🚀 Génération", "📋 Planning", "🏛️ Salles"])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1: Génération
    # ═══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🚀 Génération Automatique")
        
        sessions = q("SELECT * FROM sessions_examen ORDER BY date_debut DESC LIMIT 10")
        
        if not sessions:
            st.warning("⚠️ Aucune session trouvée. Créez-en une dans la Configuration.")
            return
        
        opts = {f"{s['nom']} ({s['date_debut']} - {s['date_fin']})": s['id'] for s in sessions}
        sel = st.selectbox("📅 Session d'examen", list(opts.keys()))
        sid = opts[sel]
        
        session = next(s for s in sessions if s['id'] == sid)
        
        # Stats de la session
        stats_row([
            {"icon": "📅", "value": str(session['date_debut']), "label": "Début"},
            {"icon": "📅", "value": str(session['date_fin']), "label": "Fin"},
            {"icon": "📊", "value": session['statut'], "label": "Statut"}
        ])
        
        # Stats actuelles
        current_stats = q("""SELECT 
            (SELECT COUNT(*) FROM modules WHERE semestre='S1') as mods,
            (SELECT COUNT(*) FROM lieu_examen WHERE disponible=TRUE) as salles,
            (SELECT COUNT(*) FROM examens WHERE session_id=%s) as existing
        """, (sid,), fetch='one')
        
        if current_stats:
            stats_row([
                {"icon": "📖", "value": current_stats['mods'] or 0, "label": "Modules S1"},
                {"icon": "🏢", "value": current_stats['salles'] or 0, "label": "Salles"},
                {"icon": "📅", "value": current_stats['existing'] or 0, "label": "Examens Existants"}
            ])
        
        st.divider()
        
        if st.button("🚀 LANCER LA GÉNÉRATION", type="primary", use_container_width=True):
            with st.spinner("⏳ Génération en cours... (peut prendre jusqu'à 60 secondes)"):
                try:
                    with get_cursor() as cursor:
                        cursor.execute("DELETE FROM surveillances WHERE examen_id IN (SELECT id FROM examens WHERE session_id = %s)", (sid,))
                        cursor.execute("DELETE FROM conflits WHERE examen1_id IN (SELECT id FROM examens WHERE session_id = %s)", (sid,))
                        cursor.execute("DELETE FROM examens WHERE session_id = %s", (sid,))
                    
                    from services.optimization import run_optimization
                    start = datetime.now()
                    report = run_optimization(sid)
                    time_taken = (datetime.now() - start).total_seconds()
                    
                    st.balloons()
                    st.success(f"✅ Génération terminée en {time_taken:.2f} secondes!")
                    
                    stats_row([
                        {"icon": "📅", "value": report.get('scheduled', 0), "label": "Examens Planifiés"},
                        {"icon": "⚠️", "value": report.get('conflicts', 0), "label": "Conflits"},
                        {"icon": "📊", "value": f"{report.get('success_rate', 0):.1f}%", "label": "Taux de Réussite"}
                    ])
                    
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2: Planning
    # ═══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📋 Planning Actuel")
        
        c1, c2 = st.columns(2)
        
        depts = q("SELECT id, nom FROM departements ORDER BY nom LIMIT 20")
        dept_opts = {"Tous les départements": None}
        dept_opts.update({d['nom']: d['id'] for d in depts} if depts else {})
        sel_dept = c1.selectbox("🏛️ Département", list(dept_opts.keys()))
        
        dates = q("SELECT DISTINCT date_examen FROM examens WHERE session_id = 1 ORDER BY date_examen LIMIT 30")
        date_opts = ["Toutes les dates"] + [str(d['date_examen']) for d in dates] if dates else ["Toutes les dates"]
        sel_date = c2.selectbox("📅 Date", date_opts)
        
        sql = """
            SELECT 
                e.date_examen AS Date,
                CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) AS Horaire,
                m.code AS Code, m.nom AS Module, f.nom AS Formation,
                COALESCE(e.groupe, 'G01') AS Groupe,
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
        
        if sel_date != "Toutes les dates":
            sql += " AND e.date_examen = %s"
            params.append(sel_date)
        
        sql += " ORDER BY e.date_examen, ch.ordre LIMIT 150"
        
        exams = q(sql, tuple(params) if params else None)
        
        if exams:
            st.success(f"📅 {len(exams)} examens trouvés")
            st.dataframe(pd.DataFrame(exams), use_container_width=True, hide_index=True)
        else:
            st.info("📋 Aucun examen trouvé. Lancez la génération !")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3: Salles
    # ═══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 🏛️ Gestion des Salles")
        
        # Filtres par type
        types = q("SELECT DISTINCT type FROM lieu_examen WHERE type IS NOT NULL")
        type_list = ["Tous"] + [t['type'] for t in types] if types else ["Tous"]
        sel_type = st.selectbox("🏢 Type de salle", type_list)
        
        sql = """
            SELECT l.nom, l.code, l.type, l.capacite, COALESCE(l.batiment, '-') as batiment,
                   COUNT(e.id) as examens
            FROM lieu_examen l
            LEFT JOIN examens e ON e.salle_id = l.id
        """
        
        if sel_type != "Tous":
            sql += f" WHERE l.type = '{sel_type}'"
        
        sql += " GROUP BY l.id ORDER BY l.type, l.capacite DESC LIMIT 80"
        
        salles = q(sql)
        
        if salles:
            # Stats des salles
            total_cap = sum(s['capacite'] for s in salles)
            total_exams = sum(s['examens'] for s in salles)
            
            stats_row([
                {"icon": "🏢", "value": len(salles), "label": "Salles"},
                {"icon": "👥", "value": f"{total_cap:,}", "label": "Capacité Totale"},
                {"icon": "📅", "value": total_exams, "label": "Examens Assignés"}
            ])
            
            df = pd.DataFrame(salles)
            df.columns = ['Nom', 'Code', 'Type', 'Capacité', 'Bâtiment', 'Examens']
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("🏢 Aucune salle trouvée")


if __name__ == "__main__":
    render_planning()
