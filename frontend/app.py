"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  EXAM SCHEDULER PRO - Plateforme de Gestion des Examens                     ║
║  Design Premium avec Glassmorphism & Animations                             ║
║  Université M'Hamed Bougara - Faculté des Sciences                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import streamlit as st
import pandas as pd
from datetime import date, time, datetime
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURATION & DESIGN PREMIUM                                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

st.set_page_config(
    page_title="ExamPro | Gestion des Examens",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Additional inline CSS for components that need Python injection
    st.markdown("""
    <style>
        /* Dynamic header gradient */
        .hero-gradient {
            background: linear-gradient(135deg, 
                rgba(99, 102, 241, 0.15) 0%, 
                rgba(236, 72, 153, 0.1) 50%,
                rgba(16, 185, 129, 0.1) 100%);
            border-radius: 24px;
            padding: 2.5rem;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .hero-gradient::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 50%);
            animation: rotate 20s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.25rem;
            margin: 2rem 0;
        }
        
        .stat-box {
            background: linear-gradient(145deg, rgba(30,30,50,0.9) 0%, rgba(20,20,35,0.95) 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .stat-box:hover {
            transform: translateY(-6px) scale(1.02);
            border-color: rgba(99, 102, 241, 0.5);
            box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
        }
        
        .stat-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            display: block;
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #F8FAFC 0%, #94A3B8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.25rem 0;
        }
        
        .stat-label {
            color: #64748B;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }
        
        /* Action Cards */
        .action-card {
            background: linear-gradient(145deg, rgba(99,102,241,0.1) 0%, rgba(236,72,153,0.05) 100%);
            border: 1px solid rgba(99,102,241,0.2);
            border-radius: 16px;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .action-card:hover {
            background: linear-gradient(145deg, rgba(99,102,241,0.2) 0%, rgba(236,72,153,0.1) 100%);
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(99, 102, 241, 0.15);
        }
        
        /* Section Headers */
        .section-title {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin: 2rem 0 1rem 0;
        }
        
        .section-title h2 {
            color: #F8FAFC;
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0;
        }
        
        .section-title .badge {
            background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        /* Premium Table Styling */
        .premium-table {
            background: rgba(30,30,50,0.6);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        /* Floating Action Button */
        .fab {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
            cursor: pointer;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .fab:hover {
            transform: scale(1.1) rotate(90deg);
            box-shadow: 0 12px 32px rgba(99, 102, 241, 0.5);
        }
        
        /* Welcome Banner */
        .welcome-banner {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%);
            border-radius: 20px;
            padding: 3rem 2rem;
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .welcome-banner::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.5;
        }
        
        .welcome-banner h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0 0 0.5rem 0;
            position: relative;
        }
        
        .welcome-banner p {
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
            margin: 0;
            position: relative;
        }
        
        /* Form Card */
        .form-card {
            background: linear-gradient(145deg, rgba(30,30,50,0.8) 0%, rgba(20,20,35,0.9) 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1.5rem;
            margin-top: 1rem;
        }
        
        /* Status Badge */
        .status-active { color: #10B981; }
        .status-pending { color: #F59E0B; }
        .status-inactive { color: #64748B; }
        
        /* Progress Ring */
        .progress-ring {
            width: 120px;
            height: 120px;
            margin: 0 auto;
        }
        
        /* Quick Access Grid */
        .quick-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .quick-item {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .quick-item:hover {
            background: rgba(99, 102, 241, 0.1);
            border-color: rgba(99, 102, 241, 0.3);
            transform: translateY(-2px);
        }
        
        .quick-item .icon {
            font-size: 1.75rem;
            margin-bottom: 0.5rem;
        }
        
        .quick-item .label {
            color: #94A3B8;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .quick-grid { grid-template-columns: repeat(2, 1fr); }
            .welcome-banner h1 { font-size: 1.75rem; }
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  DATABASE CONNECTION                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@st.cache_resource
def get_db():
    try:
        from database import execute_query
        return execute_query
    except Exception as e:
        return None

db = get_db()

def q(sql, params=None, fetch='all'):
    if not db: return [] if fetch == 'all' else None
    try:
        r = db(sql, params, fetch=fetch)
        return r if r else ([] if fetch == 'all' else None)
    except: return [] if fetch == 'all' else None

def insert(sql, params):
    if not db: return None
    try: return db(sql, params, fetch='none')
    except: return None

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CACHED DATA                                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@st.cache_data(ttl=120)
def get_depts():
    return q("SELECT id, nom, code FROM departements ORDER BY nom LIMIT 50")

@st.cache_data(ttl=120)
def get_formations():
    return q("""SELECT f.id, f.nom, f.code, f.niveau, d.nom as dept, d.id as dept_id
                FROM formations f JOIN departements d ON f.dept_id = d.id 
                ORDER BY d.nom, f.niveau, f.nom LIMIT 250""")

@st.cache_data(ttl=120)
def get_profs():
    return q("""SELECT p.id, p.nom, p.prenom, p.grade, d.nom as dept, d.id as dept_id
                FROM professeurs p JOIN departements d ON p.dept_id = d.id 
                ORDER BY d.nom, p.nom LIMIT 250""")

@st.cache_data(ttl=120)
def get_salles():
    return q("SELECT id, nom, code, type, capacite, batiment FROM lieu_examen ORDER BY type, code LIMIT 100")

@st.cache_data(ttl=120)
def get_sessions():
    return q("SELECT id, nom, type_session, date_debut, date_fin, annee_universitaire FROM sessions_examen ORDER BY date_debut DESC LIMIT 20")

@st.cache_data(ttl=120)
def get_creneaux():
    return q("SELECT id, libelle, heure_debut, heure_fin, ordre FROM creneaux_horaires ORDER BY ordre")

@st.cache_data(ttl=120)
def get_modules(fid=None):
    if fid: return q("SELECT id, code, nom, credits, semestre FROM modules WHERE formation_id = %s ORDER BY semestre, nom LIMIT 50", (fid,))
    return q("SELECT m.id, m.code, m.nom, m.credits, m.semestre, f.nom as formation FROM modules m JOIN formations f ON m.formation_id = f.id ORDER BY f.nom LIMIT 100")

def fmt_time(t):
    if not t: return ""
    if hasattr(t, 'strftime'): return t.strftime('%H:%M')
    s = str(t)
    return s[:5] if len(s) >= 5 else s

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR NAVIGATION                                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h1>⚡ ExamPro</h1>
        <p>Gestion des Examens</p>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio("", [
        "🏠 Dashboard",
        "⚙️ Configuration",
        "📝 Données",
        "🚀 Génération",
        "📊 Plannings",
        "📄 Export"
    ], label_visibility="collapsed")
    
    st.divider()
    
    # Mini stats in sidebar - fixed display
    stats = q("""SELECT 
        (SELECT COUNT(*) FROM examens) as exams,
        (SELECT COUNT(*) FROM professeurs) as profs
    """, fetch='one')
    
    if stats:
        st.markdown(f"""
        <div style="display: flex; gap: 0.5rem; padding: 0 0.5rem;">
            <div style="flex: 1; background: rgba(99,102,241,0.15); border-radius: 12px; padding: 0.75rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #64748B;">📅 Examens</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">{stats['exams'] or 0}</div>
            </div>
            <div style="flex: 1; background: rgba(236,72,153,0.15); border-radius: 12px; padding: 0.75rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #64748B;">👨‍🏫 Profs</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">{stats['profs'] or 0}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="position: absolute; bottom: 1rem; left: 1rem; right: 1rem;">
        <p style="color: #64748B; font-size: 0.7rem; text-align: center;">
            v2.0 • Université Boumerdès
        </p>
    </div>
    """, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: DASHBOARD                                                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

if "Dashboard" in page:
    # Welcome Banner
    st.markdown("""
    <div class="welcome-banner">
        <h1>🎓 Bienvenue sur ExamPro</h1>
        <p>Plateforme Intelligente de Gestion des Emplois du Temps d'Examens</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    stats = q("""SELECT 
        (SELECT COUNT(*) FROM departements) as depts,
        (SELECT COUNT(*) FROM formations) as forms,
        (SELECT COUNT(*) FROM professeurs) as profs,
        (SELECT COUNT(*) FROM etudiants) as etuds,
        (SELECT COUNT(*) FROM modules) as mods,
        (SELECT COUNT(*) FROM inscriptions) as inscrip,
        (SELECT COUNT(*) FROM lieu_examen) as salles,
        (SELECT COUNT(*) FROM examens) as exams
    """, fetch='one')
    
    if stats:
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-box">
                <span class="stat-icon">🏛️</span>
                <div class="stat-value">{stats['depts'] or 0}</div>
                <div class="stat-label">Départements</div>
            </div>
            <div class="stat-box">
                <span class="stat-icon">📚</span>
                <div class="stat-value">{stats['forms'] or 0}</div>
                <div class="stat-label">Formations</div>
            </div>
            <div class="stat-box">
                <span class="stat-icon">👨‍🏫</span>
                <div class="stat-value">{stats['profs'] or 0}</div>
                <div class="stat-label">Professeurs</div>
            </div>
            <div class="stat-box">
                <span class="stat-icon">🏢</span>
                <div class="stat-value">{stats['salles'] or 0}</div>
                <div class="stat-label">Salles</div>
            </div>
            <div class="stat-box">
                <span class="stat-icon">👨‍🎓</span>
                <div class="stat-value">{stats['etuds'] or 0:,}</div>
                <div class="stat-label">Étudiants</div>
            </div>
            <div class="stat-box">
                <span class="stat-icon">📖</span>
                <div class="stat-value">{stats['mods'] or 0}</div>
                <div class="stat-label">Modules</div>
            </div>
            <div class="stat-box">
                <span class="stat-icon">📝</span>
                <div class="stat-value">{stats['inscrip'] or 0:,}</div>
                <div class="stat-label">Inscriptions</div>
            </div>
            <div class="stat-box">
                <span class="stat-icon">📅</span>
                <div class="stat-value">{stats['exams'] or 0}</div>
                <div class="stat-label">Examens</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions & Recent Exams
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="section-title"><h2>⚡ Accès Rapide</h2></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="quick-grid">
            <div class="quick-item"><div class="icon">📅</div><div class="label">Générer EDT</div></div>
            <div class="quick-item"><div class="icon">📊</div><div class="label">Plannings</div></div>
            <div class="quick-item"><div class="icon">📄</div><div class="label">Export PDF</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Session active
        session = q("SELECT nom, date_debut, date_fin FROM sessions_examen ORDER BY date_debut DESC LIMIT 1", fetch='one')
        if session:
            st.markdown(f"""
            <div class="form-card">
                <p style="color: #64748B; font-size: 0.8rem; margin: 0;">SESSION ACTIVE</p>
                <p style="color: #F8FAFC; font-weight: 600; margin: 0.5rem 0;">{session['nom']}</p>
                <p style="color: #10B981; font-size: 0.85rem; margin: 0;">
                    📅 {session['date_debut']} → {session['date_fin']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-title"><h2>📅 Derniers Examens</h2><span class="badge">Récent</span></div>', unsafe_allow_html=True)
        
        recent = q("""
            SELECT e.date_examen as Date,
                   CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                   m.nom as Module, f.nom as Formation, l.nom as Salle
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            JOIN lieu_examen l ON e.salle_id = l.id
            JOIN creneaux_horaires ch ON e.creneau_id = ch.id
            ORDER BY e.date_examen DESC, ch.ordre LIMIT 8
        """)
        
        if recent:
            st.dataframe(pd.DataFrame(recent), use_container_width=True, hide_index=True)
        else:
            st.info("🔔 Aucun examen planifié. Allez dans **Génération** pour créer le planning.")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: CONFIGURATION                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "Configuration" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">⚙️ Configuration</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Gérer les sessions d'examen et les créneaux horaires</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📅 Sessions", "🕐 Créneaux"])
    
    with tab1:
        sessions = get_sessions()
        if sessions:
            df = pd.DataFrame([{'Nom': s['nom'], 'Type': s['type_session'], 'Début': s['date_debut'], 'Fin': s['date_fin']} for s in sessions])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.subheader("➕ Nouvelle Session")
        with st.form("session_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom", "Session S1 2025-2026")
            type_sess = c2.selectbox("Type", ["NORMALE", "RATTRAPAGE"])
            c3, c4 = st.columns(2)
            d1 = c3.date_input("Début", date(2026, 1, 6))
            d2 = c4.date_input("Fin", date(2026, 1, 24))
            if st.form_submit_button("✅ Créer", type="primary", use_container_width=True):
                insert("INSERT INTO sessions_examen (nom, type_session, date_debut, date_fin, annee_universitaire, statut) VALUES (%s,%s,%s,%s,'2025-2026','PLANIFICATION')", (nom, type_sess, d1, d2))
                st.success("✅ Session créée!"); st.cache_data.clear(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        creneaux = get_creneaux()
        if creneaux:
            df = pd.DataFrame([{'Ordre': c['ordre'], 'Horaire': f"{fmt_time(c['heure_debut'])} - {fmt_time(c['heure_fin'])}"} for c in creneaux])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Ajoutez des créneaux pour générer les plannings")
        
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.subheader("➕ Nouveau Créneau")
        with st.form("creneau_form"):
            c1, c2, c3 = st.columns(3)
            ordre = c1.number_input("Ordre", 1, 10, len(creneaux)+1 if creneaux else 1)
            h1 = c2.time_input("Début", time(8,0))
            h2 = c3.time_input("Fin", time(9,30))
            if st.form_submit_button("✅ Ajouter", type="primary", use_container_width=True):
                lib = f"{h1.strftime('%H:%M')} - {h2.strftime('%H:%M')}"
                insert("INSERT INTO creneaux_horaires (libelle, heure_debut, heure_fin, ordre) VALUES (%s,%s,%s,%s)", (lib, h1, h2, ordre))
                st.success("✅ Créneau ajouté!"); st.cache_data.clear(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: DONNÉES                                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "Données" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">📝 Saisie des Données</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Gérer départements, formations, professeurs, salles et modules</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏛️ Depts", "📚 Forms", "👨‍🏫 Profs", "🏢 Salles", "📖 Modules", "👨‍🎓 Étudiants"])
    
    # Départements
    with tab1:
        depts = get_depts()
        if depts: st.dataframe(pd.DataFrame(depts), use_container_width=True, hide_index=True)
        with st.form("dept_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom", placeholder="Informatique")
            code = c2.text_input("Code", placeholder="INFO")
            if st.form_submit_button("➕ Ajouter", type="primary"):
                if nom and code:
                    insert("INSERT INTO departements (nom, code) VALUES (%s,%s)", (nom, code))
                    st.success("✅"); st.cache_data.clear(); st.rerun()
    
    # Formations
    with tab2:
        formations = get_formations()
        if formations:
            df = pd.DataFrame([{'Nom': f['nom'], 'Code': f['code'], 'Niveau': f['niveau'], 'Dept': f['dept']} for f in formations[:30]])
            st.dataframe(df, use_container_width=True, hide_index=True)
        depts = get_depts()
        if depts:
            with st.form("form_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom", placeholder="Génie Logiciel")
                code = c2.text_input("Code", placeholder="GL")
                c3, c4 = st.columns(2)
                dept_sel = c3.selectbox("Département", [d['nom'] for d in depts])
                niveau = c4.selectbox("Niveau", ["L1", "L2", "L3", "M1", "M2"])
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if nom and code:
                        did = next(d['id'] for d in depts if d['nom'] == dept_sel)
                        insert("INSERT INTO formations (nom, code, dept_id, niveau, nb_modules) VALUES (%s,%s,%s,%s,6)", (f"{niveau} - {nom}", code, did, niveau))
                        st.success("✅"); st.cache_data.clear(); st.rerun()
    
    # Professeurs
    with tab3:
        profs = get_profs()
        if profs:
            df = pd.DataFrame([{'Nom': f"{p['prenom']} {p['nom']}", 'Grade': p['grade'], 'Dept': p['dept']} for p in profs[:30]])
            st.dataframe(df, use_container_width=True, hide_index=True)
        depts = get_depts()
        if depts:
            with st.form("prof_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom", placeholder="BENALI")
                prenom = c2.text_input("Prénom", placeholder="Ahmed")
                c3, c4 = st.columns(2)
                dept_sel = c3.selectbox("Département", [d['nom'] for d in depts], key="pd")
                grade = c4.selectbox("Grade", ["MAA", "MAB", "MCA", "MCB", "PR"])
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if nom and prenom:
                        did = next(d['id'] for d in depts if d['nom'] == dept_sel)
                        mat = f"P{did}{nom[:3].upper()}{len(profs) if profs else 0}"
                        insert("INSERT INTO professeurs (matricule, nom, prenom, dept_id, grade) VALUES (%s,%s,%s,%s,%s)", (mat, nom, prenom, did, grade))
                        st.success("✅"); st.cache_data.clear(); st.rerun()
    
    # Salles
    with tab4:
        salles = get_salles()
        if salles:
            df = pd.DataFrame([{'Nom': s['nom'], 'Code': s['code'], 'Type': s['type'], 'Capacité': s['capacite']} for s in salles])
            st.dataframe(df, use_container_width=True, hide_index=True)
        with st.form("salle_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom", placeholder="Amphi 1")
            code = c2.text_input("Code", placeholder="AMP01")
            c3, c4 = st.columns(2)
            typ = c3.selectbox("Type", ["AMPHI", "SALLE", "LABO"])
            cap = c4.number_input("Capacité", 10, 500, 100)
            if st.form_submit_button("➕ Ajouter", type="primary"):
                if nom and code:
                    insert("INSERT INTO lieu_examen (nom, code, type, capacite, disponible) VALUES (%s,%s,%s,%s,TRUE)", (nom, code, typ, cap))
                    st.success("✅"); st.cache_data.clear(); st.rerun()
    
    # Modules
    with tab5:
        formations = get_formations()
        if formations:
            sel_f = st.selectbox("Formation", [f['nom'] for f in formations], key="mf")
            fid = next(f['id'] for f in formations if f['nom'] == sel_f)
            mods = get_modules(fid)
            if mods:
                df = pd.DataFrame([{'Code': m['code'], 'Nom': m['nom'], 'Crédits': m['credits'], 'Sem': m['semestre']} for m in mods])
                st.dataframe(df, use_container_width=True, hide_index=True)
            with st.form("mod_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom du module", placeholder="Programmation")
                code = c2.text_input("Code", placeholder="PROG01")
                c3, c4 = st.columns(2)
                sem = c3.selectbox("Semestre", ["S1", "S2"])
                cred = c4.number_input("Crédits", 1, 10, 4)
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if nom and code:
                        insert("INSERT INTO modules (code, nom, credits, formation_id, semestre, coefficient) VALUES (%s,%s,%s,%s,%s,%s)", (code, nom, cred, fid, sem, cred/2))
                        st.success("✅"); st.cache_data.clear(); st.rerun()
    
    # Étudiants
    with tab6:
        formations = get_formations()
        if formations:
            sel_f = st.selectbox("Formation", [f['nom'] for f in formations], key="ef")
            fid = next(f['id'] for f in formations if f['nom'] == sel_f)
            etuds = q("SELECT matricule, nom, prenom, COALESCE(groupe,'G01') as groupe FROM etudiants WHERE formation_id=%s ORDER BY groupe, nom LIMIT 50", (fid,))
            if etuds:
                st.dataframe(pd.DataFrame(etuds), use_container_width=True, hide_index=True)
            with st.form("etud_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom", placeholder="AMRANI")
                prenom = c2.text_input("Prénom", placeholder="Mohamed")
                groupe = st.text_input("Groupe", "G01")
                if st.form_submit_button("➕ Ajouter", type="primary"):
                    if nom and prenom:
                        mat = f"E{fid:04d}{len(etuds) if etuds else 0:04d}"
                        insert("INSERT INTO etudiants (matricule, nom, prenom, formation_id, groupe, promo) VALUES (%s,%s,%s,%s,%s,2025)", (mat, nom, prenom, fid, groupe))
                        st.success(f"✅ Matricule: {mat}"); st.cache_data.clear(); st.rerun()
            
            st.divider()
            if st.button("⚡ Inscrire tous aux modules S1", type="secondary"):
                es = q("SELECT id FROM etudiants WHERE formation_id=%s", (fid,))
                ms = q("SELECT id FROM modules WHERE formation_id=%s AND semestre='S1'", (fid,))
                if es and ms:
                    cnt = 0
                    for e in es:
                        for m in ms:
                            try: insert("INSERT IGNORE INTO inscriptions (etudiant_id, module_id, annee_universitaire, statut) VALUES (%s,%s,'2025/2026','INSCRIT')", (e['id'], m['id'])); cnt += 1
                            except: pass
                    st.success(f"✅ {cnt} inscriptions!"); st.cache_data.clear()


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: GÉNÉRATION                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "Génération" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">🚀 Génération de l'Emploi du Temps</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Créez automatiquement le planning optimal des examens</p>
    </div>
    """, unsafe_allow_html=True)
    
    sessions = get_sessions()
    creneaux = get_creneaux()
    
    if not sessions:
        st.error("⚠️ Créez une session dans Configuration")
    elif not creneaux:
        st.error("⚠️ Ajoutez des créneaux dans Configuration")
    else:
        sel_s = st.selectbox("📅 Session", [s['nom'] for s in sessions])
        sid = next(s['id'] for s in sessions if s['nom'] == sel_s)
        session = next(s for s in sessions if s['id'] == sid)
        
        c1, c2, c3 = st.columns(3)
        c1.info(f"📅 Début: {session['date_debut']}")
        c2.info(f"📅 Fin: {session['date_fin']}")
        c3.info(f"🕐 {len(creneaux)} créneaux")
        
        stats = q("""SELECT 
            (SELECT COUNT(*) FROM modules WHERE semestre='S1') as mods,
            (SELECT COUNT(*) FROM lieu_examen WHERE disponible=TRUE) as salles,
            (SELECT COUNT(*) FROM examens WHERE session_id=%s) as existing
        """, (sid,), fetch='one')
        
        if stats:
            st.markdown(f"""
            <div class="stats-grid" style="grid-template-columns: repeat(3, 1fr);">
                <div class="stat-box"><span class="stat-icon">📖</span><div class="stat-value">{stats['mods'] or 0}</div><div class="stat-label">Modules S1</div></div>
                <div class="stat-box"><span class="stat-icon">🏢</span><div class="stat-value">{stats['salles'] or 0}</div><div class="stat-label">Salles</div></div>
                <div class="stat-box"><span class="stat-icon">📅</span><div class="stat-value">{stats['existing'] or 0}</div><div class="stat-label">Examens existants</div></div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        if st.button("🚀 GÉNÉRER L'EMPLOI DU TEMPS", type="primary", use_container_width=True):
            with st.spinner("⏳ Génération en cours..."):
                try:
                    q("DELETE FROM surveillances WHERE examen_id IN (SELECT id FROM examens WHERE session_id=%s)", (sid,))
                    q("DELETE FROM conflits WHERE examen1_id IN (SELECT id FROM examens WHERE session_id=%s)", (sid,))
                    q("DELETE FROM examens WHERE session_id=%s", (sid,))
                    
                    from services.optimization import run_optimization
                    start = datetime.now()
                    r = run_optimization(sid)
                    elapsed = (datetime.now() - start).total_seconds()
                    
                    st.balloons()
                    st.success(f"✅ Terminé en {elapsed:.1f}s!")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("📅 Planifiés", r.get('scheduled', 0))
                    c2.metric("⚠️ Conflits", r.get('conflicts', 0))
                    c3.metric("📊 Taux", f"{r.get('success_rate', 0):.1f}%")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"❌ {e}")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: PLANNINGS                                                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "Plannings" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">📊 Consultation des Plannings</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Visualisez les emplois du temps par formation, professeur ou salle</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Formation", "🏛️ Département", "👨‍🏫 Professeur", "🏢 Salle"])
    
    with tab1:
        formations = get_formations()
        if formations:
            c1, c2 = st.columns(2)
            sel_f = c1.selectbox("Formation", [f['nom'] for f in formations], key="pf")
            fid = next(f['id'] for f in formations if f['nom'] == sel_f)
            
            groupes = q("SELECT DISTINCT COALESCE(e.groupe,'G01') as g FROM examens e JOIN modules m ON e.module_id=m.id WHERE m.formation_id=%s ORDER BY g", (fid,))
            glist = ["Tous"] + [g['g'] for g in groupes] if groupes else ["Tous"]
            sel_g = c2.selectbox("Groupe", glist, key="pg")
            
            if sel_g == "Tous":
                exams = q("""SELECT e.date_examen as Date, CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                           m.nom as Module, COALESCE(e.groupe,'G01') as Groupe, l.nom as Salle
                           FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id 
                           JOIN creneaux_horaires ch ON e.creneau_id=ch.id WHERE m.formation_id=%s ORDER BY e.date_examen, ch.ordre LIMIT 100""", (fid,))
            else:
                exams = q("""SELECT e.date_examen as Date, CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                           m.nom as Module, l.nom as Salle
                           FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id 
                           JOIN creneaux_horaires ch ON e.creneau_id=ch.id WHERE m.formation_id=%s AND (e.groupe=%s OR e.groupe IS NULL) ORDER BY e.date_examen LIMIT 100""", (fid, sel_g))
            
            if exams:
                st.success(f"📅 {len(exams)} examens")
                st.dataframe(pd.DataFrame(exams), use_container_width=True, hide_index=True)
            else:
                st.info("Aucun examen")
    
    with tab2:
        depts = get_depts()
        if depts:
            sel_d = st.selectbox("Département", [d['nom'] for d in depts], key="pd2")
            did = next(d['id'] for d in depts if d['nom'] == sel_d)
            
            forms = q("SELECT id, nom FROM formations WHERE dept_id=%s ORDER BY niveau, nom LIMIT 50", (did,))
            if forms:
                st.info(f"📚 {len(forms)} formations")
                for f in forms:
                    with st.expander(f"📗 {f['nom']}", expanded=False):
                        exams = q("""SELECT e.date_examen as Date, CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                                   m.nom as Module, COALESCE(e.groupe,'G01') as Groupe, l.nom as Salle
                                   FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id 
                                   JOIN creneaux_horaires ch ON e.creneau_id=ch.id WHERE m.formation_id=%s ORDER BY e.groupe, e.date_examen LIMIT 50""", (f['id'],))
                        if exams: st.dataframe(pd.DataFrame(exams), hide_index=True, use_container_width=True)
                        else: st.caption("Aucun examen")
    
    with tab3:
        depts = get_depts()
        profs = get_profs()
        c1, c2 = st.columns([1, 2])
        df = c1.selectbox("Département", ["Tous"] + [d['nom'] for d in depts], key="pdf")
        if df != "Tous": profs = [p for p in profs if p['dept'] == df]
        
        if profs:
            sel_p = c2.selectbox("Professeur", [f"{p['prenom']} {p['nom']}" for p in profs], key="pp")
            pid = next(p['id'] for p in profs if f"{p['prenom']} {p['nom']}" == sel_p)
            
            survs = q("""SELECT e.date_examen as Date, CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                       m.nom as Module, l.nom as Salle, s.role as Rôle
                       FROM surveillances s JOIN examens e ON s.examen_id=e.id JOIN modules m ON e.module_id=m.id
                       JOIN lieu_examen l ON e.salle_id=l.id JOIN creneaux_horaires ch ON e.creneau_id=ch.id
                       WHERE s.professeur_id=%s ORDER BY e.date_examen LIMIT 100""", (pid,))
            
            if survs:
                st.success(f"📅 {len(survs)} surveillances")
                st.dataframe(pd.DataFrame(survs), use_container_width=True, hide_index=True)
            else:
                st.info("Aucune surveillance")
    
    with tab4:
        salles = get_salles()
        types = list(set(s['type'] for s in salles if s.get('type')))
        c1, c2 = st.columns([1, 2])
        tf = c1.selectbox("Type", ["Tous"] + types, key="stf")
        if tf != "Tous": salles = [s for s in salles if s.get('type') == tf]
        
        if salles:
            sel_s = c2.selectbox("Salle", [f"{s['nom']} ({s['capacite']})" for s in salles], key="ps")
            sid = next(s['id'] for s in salles if f"{s['nom']} ({s['capacite']})" == sel_s)
            
            exams = q("""SELECT e.date_examen as Date, CONCAT(TIME_FORMAT(ch.heure_debut,'%H:%i'),'-',TIME_FORMAT(ch.heure_fin,'%H:%i')) as Horaire,
                       m.nom as Module, f.nom as Formation
                       FROM examens e JOIN modules m ON e.module_id=m.id JOIN formations f ON m.formation_id=f.id
                       JOIN creneaux_horaires ch ON e.creneau_id=ch.id WHERE e.salle_id=%s ORDER BY e.date_examen LIMIT 100""", (sid,))
            
            if exams:
                st.success(f"📅 {len(exams)} examens")
                st.dataframe(pd.DataFrame(exams), use_container_width=True, hide_index=True)
            else:
                st.info("Aucun examen")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: EXPORT                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "Export" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">📄 Export PDF</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Téléchargez les plannings au format PDF</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Formation", "🏛️ Département", "👨‍🏫 Professeur", "🏢 Salle"])
    
    with tab1:
        formations = get_formations()
        if formations:
            c1, c2 = st.columns(2)
            sel_f = c1.selectbox("Formation", [f['nom'] for f in formations], key="ef1")
            fd = next(f for f in formations if f['nom'] == sel_f)
            
            groupes = q("SELECT DISTINCT COALESCE(e.groupe,'G01') as g FROM examens e JOIN modules m ON e.module_id=m.id WHERE m.formation_id=%s ORDER BY g", (fd['id'],))
            opts = ["Tous (multi-pages)"] + [g['g'] for g in groupes] if groupes else ["G01"]
            sel_g = c2.selectbox("Groupe", opts, key="eg1")
            
            if st.button("📄 Générer PDF", type="primary", key="b1"):
                if sel_g == "Tous (multi-pages)":
                    all_ex = {}
                    for g in groupes:
                        ex = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, m.code as module_code, m.nom as module_nom, l.code as salle
                                FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id
                                JOIN creneaux_horaires ch ON e.creneau_id=ch.id WHERE m.formation_id=%s AND (e.groupe=%s OR e.groupe IS NULL) ORDER BY e.date_examen""", (fd['id'], g['g']))
                        if ex: all_ex[g['g']] = ex
                    if all_ex:
                        try:
                            from services.pdf_generator import generate_multi_group_pdf
                            pdf = generate_multi_group_pdf(sel_f, fd['niveau'], all_ex)
                            st.download_button("⬇️ Télécharger", pdf, f"planning_{sel_f}.pdf", "application/pdf")
                        except Exception as e: st.error(f"Erreur: {e}")
                else:
                    ex = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, m.code as module_code, m.nom as module_nom, l.code as salle
                            FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id
                            JOIN creneaux_horaires ch ON e.creneau_id=ch.id WHERE m.formation_id=%s AND (e.groupe=%s OR e.groupe IS NULL) ORDER BY e.date_examen""", (fd['id'], sel_g))
                    if ex:
                        try:
                            from services.pdf_generator import generate_student_schedule_pdf
                            pdf = generate_student_schedule_pdf(sel_f, sel_g, fd['niveau'], ex)
                            st.download_button("⬇️ Télécharger", pdf, f"planning_{sel_g}.pdf", "application/pdf")
                        except Exception as e: st.error(f"Erreur: {e}")
    
    with tab2:
        depts = get_depts()
        if depts:
            sel_d = st.selectbox("Département", [d['nom'] for d in depts], key="ed2")
            did = next(d['id'] for d in depts if d['nom'] == sel_d)
            
            forms = q("SELECT id, nom, niveau FROM formations WHERE dept_id=%s ORDER BY niveau, nom LIMIT 50", (did,))
            if forms:
                st.success(f"📚 {len(forms)} formations seront incluses")
                if st.button("📄 Générer PDF Département", type="primary", key="b2"):
                    all_data = {}
                    for f in forms:
                        ex = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, m.code as module_code, m.nom as module_nom, 
                                COALESCE(e.groupe,'G01') as groupe, l.code as salle
                                FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id
                                JOIN creneaux_horaires ch ON e.creneau_id=ch.id WHERE m.formation_id=%s ORDER BY e.groupe, e.date_examen""", (f['id'],))
                        if ex: all_data[f['nom']] = {'niveau': f['niveau'], 'exams': ex}
                    if all_data:
                        try:
                            from services.pdf_generator import generate_department_pdf
                            pdf = generate_department_pdf(sel_d, all_data)
                            st.download_button("⬇️ Télécharger", pdf, f"dept_{sel_d}.pdf", "application/pdf")
                        except Exception as e: st.error(f"Erreur: {e}")
    
    with tab3:
        depts = get_depts()
        profs = get_profs()
        c1, c2 = st.columns([1, 2])
        df = c1.selectbox("Département", ["Tous"] + [d['nom'] for d in depts], key="epd")
        if df != "Tous": profs = [p for p in profs if p['dept'] == df]
        
        if profs:
            sel_p = c2.selectbox("Professeur", [f"{p['prenom']} {p['nom']}" for p in profs], key="ep3")
            pd2 = next(p for p in profs if f"{p['prenom']} {p['nom']}" == sel_p)
            
            if st.button("📄 Générer PDF", type="primary", key="b3"):
                survs = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, m.code as module_code, m.nom as module_nom, l.code as salle, s.role
                            FROM surveillances s JOIN examens e ON s.examen_id=e.id JOIN modules m ON e.module_id=m.id
                            JOIN lieu_examen l ON e.salle_id=l.id JOIN creneaux_horaires ch ON e.creneau_id=ch.id WHERE s.professeur_id=%s ORDER BY e.date_examen""", (pd2['id'],))
                if survs:
                    try:
                        from services.pdf_generator import generate_professor_schedule_pdf
                        pdf = generate_professor_schedule_pdf(pd2['nom'], pd2['prenom'], pd2['dept'], survs)
                        st.download_button("⬇️ Télécharger", pdf, f"prof_{pd2['nom']}.pdf", "application/pdf")
                    except Exception as e: st.error(f"Erreur: {e}")
    
    with tab4:
        salles = get_salles()
        types = list(set(s['type'] for s in salles if s.get('type')))
        c1, c2 = st.columns([1, 2])
        tf = c1.selectbox("Type", ["Tous"] + types, key="est")
        if tf != "Tous": salles = [s for s in salles if s.get('type') == tf]
        
        if salles:
            sel_s = c2.selectbox("Salle", [f"{s['nom']} ({s['capacite']})" for s in salles], key="es4")
            sd = next(s for s in salles if f"{s['nom']} ({s['capacite']})" == sel_s)
            
            if st.button("📄 Générer PDF", type="primary", key="b4"):
                ex = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, m.code as module_code, m.nom as module_nom, f.nom as formation
                        FROM examens e JOIN modules m ON e.module_id=m.id JOIN formations f ON m.formation_id=f.id
                        JOIN creneaux_horaires ch ON e.creneau_id=ch.id WHERE e.salle_id=%s ORDER BY e.date_examen""", (sd['id'],))
                if ex:
                    try:
                        from services.pdf_generator import generate_room_schedule_pdf
                        pdf = generate_room_schedule_pdf(sd['nom'], sd['code'], sd['capacite'], ex)
                        st.download_button("⬇️ Télécharger", pdf, f"salle_{sd['code']}.pdf", "application/pdf")
                    except Exception as e: st.error(f"Erreur: {e}")
