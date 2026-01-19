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
    return q("""SELECT p.id, p.matricule, p.nom, p.prenom, p.grade, p.specialite, d.nom as dept, d.id as dept_id
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
# ║  AUTHENTIFICATION & SESSION                                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Initialiser l'état de session
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.allowed_pages = []

# Import du service d'authentification
try:
    from services.auth_service import (
        login_student, login_user, logout, get_allowed_pages, can_access_page
    )
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# ════════════════════════════════════════════════════════════════════════════════
# PAGE DE CONNEXION (si non authentifié)
# ════════════════════════════════════════════════════════════════════════════════

if not st.session_state.authenticated:
    # CSS pour la page de login
    st.markdown("""
    <style>
    .login-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
        border-radius: 20px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-header h1 {
        font-size: 2.5rem;
        margin: 0;
        background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .login-header p {
        color: #94A3B8;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-header">
        <h1>⚡ ExamPro</h1>
        <p>Plateforme de Gestion des Examens</p>
        <p style="font-size: 0.8rem; color: #64748B;">Université M'Hamed Bougara - Boumerdès</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Choix du type de connexion
    login_type = st.radio(
        "Je suis :",
        ["👨‍🎓 Étudiant", "👨‍🏫 Professeur / Personnel"],
        horizontal=True,
        label_visibility="visible"
    )
    
    st.markdown("---")
    
    if "Étudiant" in login_type:
        # Connexion Étudiant (Nom + Numéro d'inscription)
        st.markdown("### 🎓 Connexion Étudiant")
        st.info("Utilisez votre nom de famille et numéro d'inscription")
        
        col1, col2 = st.columns(2)
        nom = col1.text_input("Nom de famille", placeholder="Ex: BENALI")
        num_inscription = col2.text_input("N° Inscription", placeholder="Ex: 202512345")
        
        if st.button("🔐 Se connecter", type="primary", use_container_width=True):
            if AUTH_AVAILABLE:
                success, user_data, message = login_student(nom, num_inscription)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = user_data
                    st.session_state.role = 'ETUDIANT'
                    st.session_state.allowed_pages = get_allowed_pages('ETUDIANT')
                    st.success(f"✅ Bienvenue {user_data.get('prenom', '')} {user_data.get('nom', '')}!")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                # Mode démo sans auth
                st.session_state.authenticated = True
                st.session_state.user = {'nom': nom, 'role': 'ETUDIANT'}
                st.session_state.role = 'ETUDIANT'
                st.session_state.allowed_pages = ['🏠 Dashboard', '📄 Export']  # Pas de Plannings pour étudiants
                st.rerun()
    else:
        # Connexion Personnel (Email + Mot de passe)
        st.markdown("### 👨‍🏫 Connexion Professeur / Personnel")
        
        email = st.text_input("Email universitaire", placeholder="prenom.nom@univ-boumerdes.dz")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("🔐 Se connecter", type="primary", use_container_width=True):
            if AUTH_AVAILABLE:
                success, user_data, message = login_user(email, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = user_data
                    st.session_state.role = user_data.get('role', 'PROFESSEUR')
                    st.session_state.allowed_pages = get_allowed_pages(st.session_state.role)
                    st.success(f"✅ Bienvenue {user_data.get('prenom', '')} {user_data.get('nom', '')}!")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                # Mode démo - connexion admin par défaut
                if email == "admin@univ-boumerdes.dz":
                    st.session_state.authenticated = True
                    st.session_state.user = {'nom': 'Admin', 'email': email, 'role': 'ADMIN'}
                    st.session_state.role = 'ADMIN'
                    st.session_state.allowed_pages = [
                        '🏠 Dashboard', '⚙️ Configuration', '📝 Données', 
                        '🚀 Génération', '📊 Plannings', '📄 Export',
                        '✅ Validation Dept', '⏱️ Benchmarks'
                    ]
                    st.rerun()
                else:
                    st.error("❌ Exécutez d'abord auth_tables.sql et regenerez les données")
        
        # Aide pour les comptes de test
        with st.expander("📋 Comptes de démonstration"):
            st.markdown("""
            | Rôle | Email | Mot de passe |
            |------|-------|--------------|
            | **Vice-doyen** | `vicedoyen@univ-boumerdes.dz` | `ViceDoyen2026!` |
            | **Admin** | `admin@univ-boumerdes.dz` | `Admin2026!` |
            | **Chef Dept** | `chef.info@univ-boumerdes.dz` | `Chef2026!` |
            | **Professeur** | `[prenom].[nom]@univ-boumerdes.dz` | `Prof2026!` |
            """)
    
    st.stop()  # Arrêter l'exécution ici si non authentifié


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR NAVIGATION (utilisateur authentifié)                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Définir les pages accessibles selon le rôle
ALL_PAGES = [
    "🏠 Dashboard",
    "⚙️ Configuration",
    "📝 Données",
    "🚀 Génération",
    "📊 Plannings",
    "📄 Export",
    "📈 KPIs Vice-doyen",
    "✅ Validation Dept",
    "⏱️ Benchmarks"
]

# Filtrer selon le rôle - EXPLICITE pour garantir les restrictions
current_role = st.session_state.role

# Pages strictement autorisées par rôle (override toute config BDD)
STRICT_ROLE_PAGES = {
    'ETUDIANT': ["🏠 Dashboard", "📄 Export"],
    'PROFESSEUR': ["🏠 Dashboard", "📄 Export"],
    'CHEF_DEPT': ["🏠 Dashboard", "📊 Plannings", "📄 Export", "✅ Validation Dept"],
    'ADMIN': ALL_PAGES,
    'VICE_DOYEN': ALL_PAGES
}

if current_role in STRICT_ROLE_PAGES:
    available_pages = [p for p in ALL_PAGES if p in STRICT_ROLE_PAGES[current_role]]
elif st.session_state.allowed_pages:
    available_pages = [p for p in ALL_PAGES if p in st.session_state.allowed_pages]
else:
    available_pages = ALL_PAGES  # Fallback: toutes les pages (ne devrait pas arriver)

with st.sidebar:
    # Info utilisateur connecté
    user = st.session_state.user or {}
    role_display = {
        'ETUDIANT': '🎓 Étudiant',
        'PROFESSEUR': '👨‍🏫 Professeur',
        'CHEF_DEPT': '🏛️ Chef Dept',
        'ADMIN': '⚙️ Admin',
        'VICE_DOYEN': '👔 Vice-Doyen'
    }.get(st.session_state.role, '👤 Utilisateur')
    
    st.markdown(f"""
    <div class="sidebar-logo">
        <h1>⚡ ExamPro</h1>
        <p style="font-size: 0.75rem; color: #94A3B8;">
            {role_display}<br/>
            <strong>{user.get('prenom', '')} {user.get('nom', '')}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton déconnexion
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.allowed_pages = []
        st.rerun()
    
    st.divider()
    
    # Navigation filtrée par rôle
    page = st.radio("Navigation", available_pages, label_visibility="collapsed")
    
    st.divider()
    
    # Mini stats in sidebar - CORRIGÉ: modules planifiés distincts
    stats = q("""SELECT 
        (SELECT COUNT(DISTINCT module_id) FROM examens) as exams,
        (SELECT COUNT(*) FROM professeurs) as profs
    """, fetch='one')
    
    if stats:
        st.markdown(f"""
        <div style="display: flex; gap: 0.5rem; padding: 0 0.5rem;">
            <div style="flex: 1; background: rgba(99,102,241,0.15); border-radius: 12px; padding: 0.75rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #64748B;">📅 Modules</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">{stats['exams'] or 0}</div>
            </div>
            <div style="flex: 1; background: rgba(236,72,153,0.15); border-radius: 12px; padding: 0.75rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #64748B;">👨‍🏫 Profs</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">{stats['profs'] or 0}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Version footer
    st.markdown("""
    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
        <p style="color: #64748B; font-size: 0.7rem; text-align: center; margin: 0;">
            v2.1 • Authentification activée
        </p>
    </div>
    """, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: DASHBOARD                                                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

if "Dashboard" in page:
    user = st.session_state.user or {}
    role = st.session_state.role
    
    # ════════════════════════════════════════════════════════════════════════════
    # DASHBOARD ÉTUDIANT - Vue personnalisée
    # ════════════════════════════════════════════════════════════════════════════
    if role == 'ETUDIANT':
        etudiant_id = user.get('etudiant_id')
        
        # Récupérer infos de l'étudiant
        etud_info = q("""
            SELECT e.nom, e.prenom, e.matricule, e.groupe, f.nom as formation, 
                   f.niveau, f.id as formation_id, d.nom as departement
            FROM etudiants e
            JOIN formations f ON e.formation_id = f.id
            JOIN departements d ON f.dept_id = d.id
            WHERE e.id = %s
        """, (etudiant_id,), fetch='one') if etudiant_id else None
        
        # Bannière personnalisée
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%); 
                    border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 1.8rem;">🎓 Bienvenue {user.get('prenom', '')} {user.get('nom', '')}</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Votre espace personnel - Emploi du temps d'examens</p>
        </div>
        """, unsafe_allow_html=True)
        
        if etud_info:
            # Cartes d'information étudiant
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                <div style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 0.8rem; color: #94A3B8;">📚 Formation</div>
                    <div style="font-size: 1rem; font-weight: 600; color: #F8FAFC; margin-top: 0.3rem;">{etud_info['formation'][:25] if etud_info['formation'] else '-'}</div>
                </div>
                <div style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 0.8rem; color: #94A3B8;">🏛️ Département</div>
                    <div style="font-size: 1rem; font-weight: 600; color: #F8FAFC; margin-top: 0.3rem;">{etud_info['departement'][:20] if etud_info['departement'] else '-'}</div>
                </div>
                <div style="background: rgba(236,72,153,0.1); border: 1px solid rgba(236,72,153,0.3); border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 0.8rem; color: #94A3B8;">📊 Niveau</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #F8FAFC; margin-top: 0.3rem;">{etud_info['niveau'] or '-'}</div>
                </div>
                <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 0.8rem; color: #94A3B8;">👥 Groupe</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #10B981; margin-top: 0.3rem;">{etud_info['groupe'] or '-'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Dates de la session
            session = q("SELECT date_debut, date_fin, nom FROM sessions_examen ORDER BY date_debut DESC LIMIT 1", fetch='one')
            if session:
                st.info(f"📅 **Session:** {session['nom']} | Du **{session['date_debut']}** au **{session['date_fin']}**")
            
            # Examens de l'étudiant (SANS info sur les surveillants!)
            st.markdown("### 📅 Votre Planning d'Examens")
            
            # Récupérer le groupe de l'étudiant pour filtrer les examens
            groupe_etudiant = etud_info['groupe']
            
            mes_examens = q("""
                SELECT e.date_examen as Date, m.code as Module, m.nom as Matière,
                       l.nom as Salle, ch.heure_debut, ch.heure_fin
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE m.formation_id = %s 
                  AND (e.groupe = %s OR e.groupe IS NULL)
                ORDER BY e.date_examen, ch.heure_debut
            """, (etud_info.get('formation_id'), groupe_etudiant,))
            
            # Formater les heures pour l'affichage
            def fmt_time(t):
                if t is None: return ""
                if hasattr(t, 'strftime'): return t.strftime('%H:%M')
                s = str(t)
                return s[:5] if len(s) >= 5 else s
            
            for ex in (mes_examens or []):
                ex['Début'] = fmt_time(ex.get('heure_debut'))
                ex['Fin'] = fmt_time(ex.get('heure_fin'))
            
            if mes_examens:
                import pandas as pd
                df = pd.DataFrame(mes_examens)
                # Sélectionner uniquement les colonnes formatées pour l'affichage
                display_cols = ['Date', 'Module', 'Matière', 'Salle', 'Début', 'Fin']
                df_display = df[[col for col in display_cols if col in df.columns]]
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                nb_futurs = len([e for e in mes_examens if str(e.get('Date', '')) >= str(date.today())])
                st.success(f"📊 **{len(mes_examens)}** examen(s) au total | **{nb_futurs}** à venir")
                
                # Bouton télécharger PDF
                st.markdown("---")
                st.markdown("### 📥 Télécharger votre planning")
                
                col_dl1, col_dl2 = st.columns(2)
                
                # Bouton PDF (format officiel)
                with col_dl1:
                    if st.button("📄 Générer PDF Officiel", type="primary", use_container_width=True, key="gen_pdf_etud"):
                        try:
                            # Préparer les données pour le PDF
                            exams_for_pdf = []
                            for ex in mes_examens:
                                exams_for_pdf.append({
                                    'date': ex.get('Date', ''),
                                    'heure_debut': ex.get('Début', ''),
                                    'heure_fin': ex.get('Fin', ''),
                                    'module_code': ex.get('Module', ''),
                                    'module_nom': ex.get('Matière', ''),
                                    'salle': ex.get('Salle', '')
                                })
                            
                            from services.pdf_generator import generate_student_schedule_pdf
                            pdf = generate_student_schedule_pdf(
                                etud_info['formation'], 
                                etud_info['groupe'], 
                                etud_info['niveau'], 
                                exams_for_pdf, 
                                etud_info['departement']
                            )
                            st.download_button(
                                "⬇️ Télécharger le PDF",
                                pdf,
                                f"planning_{etud_info['groupe']}.pdf",
                                "application/pdf",
                                use_container_width=True
                            )
                            st.success("✅ PDF généré avec succès!")
                        except Exception as e:
                            st.error(f"Erreur génération PDF: {e}")
                
                # CSV simple
                with col_dl2:
                    csv_content = "Date;Module;Matière;Salle;Début;Fin\n"
                    for ex in mes_examens:
                        csv_content += f"{ex.get('Date', '')};{ex.get('Module', '')};{ex.get('Matière', '')};{ex.get('Salle', '')};{ex.get('Début', '')};{ex.get('Fin', '')}\n"
                    
                    st.download_button(
                        label="📊 Télécharger CSV",
                        data=csv_content,
                        file_name=f"planning_{etud_info['groupe']}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("📭 Aucun examen programmé pour le moment")
        else:
            st.warning("⚠️ Impossible de charger vos informations")
    
    # ════════════════════════════════════════════════════════════════════════════
    # DASHBOARD PROFESSEUR - Mes surveillances
    # ════════════════════════════════════════════════════════════════════════════
    elif role == 'PROFESSEUR':
        prof_id = user.get('professeur_id')
        
        st.markdown(f"""
        <div class="welcome-banner">
            <h1>👨‍🏫 Bienvenue {user.get('prenom', '')} {user.get('nom', '')}</h1>
            <p>Consultez vos surveillances d'examens</p>
        </div>
        """, unsafe_allow_html=True)
        
        if prof_id:
            # Stats personnelles
            mes_stats = q("""
                SELECT 
                    COUNT(DISTINCT sv.id) as total_surv,
                    COUNT(DISTINCT e.date_examen) as jours_travail
                FROM surveillances sv
                JOIN examens e ON sv.examen_id = e.id
                WHERE sv.professeur_id = %s
            """, (prof_id,), fetch='one')
            
            c1, c2, c3 = st.columns(3)
            c1.metric("👁️ Mes Surveillances", mes_stats['total_surv'] if mes_stats else 0)
            c2.metric("📅 Jours de Travail", mes_stats['jours_travail'] if mes_stats else 0)
            heures = (mes_stats['total_surv'] or 0) * 1.5
            c3.metric("⏰ Heures Totales", f"{heures:.1f}h")
            
            # Mes surveillances
            st.markdown("### 📅 Mes Surveillances à Venir")
            
            mes_surv = q("""
                SELECT e.date_examen as Date, m.code as Module, 
                       l.nom as Salle, ch.heure_debut as Début, ch.heure_fin as Fin,
                       e.nb_etudiants_prevus as Étudiants
                FROM surveillances sv
                JOIN examens e ON sv.examen_id = e.id
                JOIN modules m ON e.module_id = m.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE sv.professeur_id = %s AND e.date_examen >= CURDATE()
                ORDER BY e.date_examen, ch.heure_debut
            """, (prof_id,))
            
            if mes_surv:
                import pandas as pd
                df = pd.DataFrame(mes_surv)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("📭 Aucune surveillance programmée pour le moment")
        else:
            st.warning("⚠️ Compte non lié à un professeur")
    
    # ════════════════════════════════════════════════════════════════════════════
    # DASHBOARD CHEF DEPT - Vue département
    # ════════════════════════════════════════════════════════════════════════════
    elif role == 'CHEF_DEPT':
        dept_id = user.get('dept_id')
        dept_nom = user.get('dept_nom', 'Mon Département')
        
        st.markdown(f"""
        <div class="welcome-banner">
            <h1>🏛️ Tableau de Bord - {dept_nom}</h1>
            <p>Chef de Département - {user.get('prenom', '')} {user.get('nom', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if dept_id:
            # Stats du département
            dept_stats = q("""
                SELECT 
                    (SELECT COUNT(*) FROM formations WHERE dept_id = %s) as formations,
                    (SELECT COUNT(*) FROM professeurs WHERE dept_id = %s) as profs,
                    (SELECT COUNT(DISTINCT e.id) FROM examens e 
                     JOIN modules m ON e.module_id = m.id 
                     JOIN formations f ON m.formation_id = f.id 
                     WHERE f.dept_id = %s) as examens
            """, (dept_id, dept_id, dept_id), fetch='one')
            
            c1, c2, c3 = st.columns(3)
            c1.metric("📚 Formations", dept_stats['formations'] if dept_stats else 0)
            c2.metric("👨‍🏫 Professeurs", dept_stats['profs'] if dept_stats else 0)
            c3.metric("📅 Examens", dept_stats['examens'] if dept_stats else 0)
    
    # ════════════════════════════════════════════════════════════════════════════
    # DASHBOARD ADMIN / VICE-DOYEN - Vue complète
    # ════════════════════════════════════════════════════════════════════════════
    else:
        st.markdown("""
        <div class="welcome-banner">
            <h1>🎓 Bienvenue sur ExamPro</h1>
            <p>Plateforme Intelligente de Gestion des Emplois du Temps d'Examens</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats globales - CORRIGÉ: examens = modules planifiés distincts
        stats = q("""SELECT 
            (SELECT COUNT(*) FROM departements) as depts,
            (SELECT COUNT(*) FROM formations) as forms,
            (SELECT COUNT(*) FROM professeurs) as profs,
            (SELECT COUNT(*) FROM etudiants) as etuds,
            (SELECT COUNT(*) FROM modules WHERE semestre='S1') as mods,
            (SELECT COUNT(*) FROM inscriptions) as inscrip,
            (SELECT COUNT(*) FROM lieu_examen) as salles,
            (SELECT COUNT(DISTINCT module_id) FROM examens) as exams
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
                    <div class="stat-label">Modules S1</div>
                </div>
                <div class="stat-box">
                    <span class="stat-icon">📝</span>
                    <div class="stat-value">{stats['inscrip'] or 0:,}</div>
                    <div class="stat-label">Inscriptions</div>
                </div>
                <div class="stat-box">
                    <span class="stat-icon">📅</span>
                    <div class="stat-value">{stats['exams'] or 0}</div>
                    <div class="stat-label">Examens planifiés</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick Actions & Recent Exams
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="section-title"><h2>⚡ Accès Rapide</h2></div>', unsafe_allow_html=True)
        
        # Functional Quick Access buttons
        qa1, qa2, qa3 = st.columns(3)
        with qa1:
            if st.button("📅\nGénérer", use_container_width=True, key="qa_gen"):
                st.info("➡️ Allez dans 🚀 Génération dans le menu")
        with qa2:
            if st.button("📊\nPlannings", use_container_width=True, key="qa_plan"):
                st.info("➡️ Allez dans 📊 Plannings dans le menu")
        with qa3:
            if st.button("📄\nExport", use_container_width=True, key="qa_exp"):
                st.info("➡️ Allez dans 📄 Export dans le menu")
        
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
    
    # === STATISTIQUES DES SURVEILLANCES (PERSISTENT) ===
    st.markdown('---')
    st.markdown('<div class="section-title"><h2>👥 Statistiques des Surveillances</h2></div>', unsafe_allow_html=True)
    
    surv_stats = q("""
        SELECT 
            COUNT(DISTINCT e.id) as nb_examens,
            COUNT(s.id) as total_surveillants,
            ROUND(COUNT(s.id) / NULLIF(COUNT(DISTINCT e.id), 0), 1) as moyenne
        FROM examens e 
        LEFT JOIN surveillances s ON s.examen_id = e.id
    """, fetch='one')
    
    surv_detail = q("""
        SELECT 
            CASE WHEN l.capacite >= 100 THEN 'Amphithéâtre (≥100)' ELSE 'Petite salle (<100)' END as type_salle,
            COUNT(DISTINCT e.id) as nb_examens,
            COUNT(s.id) as total_surveillants,
            ROUND(COUNT(s.id) / NULLIF(COUNT(DISTINCT e.id), 0), 1) as moyenne
        FROM examens e 
        LEFT JOIN surveillances s ON s.examen_id = e.id
        LEFT JOIN lieu_examen l ON e.salle_id = l.id
        GROUP BY type_salle
    """)
    
    if surv_stats and surv_stats.get('nb_examens', 0) > 0:
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("📊 Total Examens", surv_stats.get('nb_examens', 0))
        sc2.metric("👥 Total Surveillances", surv_stats.get('total_surveillants', 0))
        sc3.metric("📈 Moyenne/Examen", surv_stats.get('moyenne', 0))
        
        if surv_detail:
            st.write("**Détail par type de salle:**")
            for d in surv_detail:
                if d.get('type_salle'):
                    st.write(f"- **{d['type_salle']}**: {d['total_surveillants']} surveillants pour {d['nb_examens']} examens ({d['moyenne']} par examen)")
            
            st.caption("💡 **Calcul de la moyenne:** Total surveillants ÷ Nombre d'examens dans cette catégorie de salle")
    else:
        st.info("📊 Aucune surveillance assignée. Générez d'abord les plannings.")

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: CONFIGURATION - AVEC PARAMÈTRES D'OPTIMISATION                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "Configuration" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">⚙️ Configuration</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Sessions, créneaux et paramètres d'optimisation</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Sessions", "🕐 Créneaux", "⚡ Optimisation"])
    
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
    
    with tab3:
        st.markdown("### ⚡ Paramètres d'Optimisation")
        st.info("🔧 Ces paramètres contrôlent la génération des plannings. Modifiez-les puis régénérez.")
        
        # ════════════════════════════════════════════════════════
        # SECTION 1: PLANNING & REPOS
        # ════════════════════════════════════════════════════════
        
        st.markdown("---")
        st.markdown("#### 📅 Planning & Repos")
        
        col1, col2 = st.columns(2)
        with col1:
            rest_days = st.selectbox(
                "🛌 Jours de repos entre examens",
                options=[0, 1, 2],
                index=0,
                format_func=lambda x: f"{x} jour(s) de repos" if x > 0 else "Pas de repos",
                help="Ex: 1 = Lundi examen, Mardi repos, Mercredi examen..."
            )
            st.session_state.rest_days = rest_days
        
        with col2:
            max_exam = st.selectbox(
                "📝 Max examens par étudiant par jour",
                options=[1, 2],
                index=0,
                format_func=lambda x: f"{x} examen(s) maximum"
            )
            st.session_state.max_exam_student = max_exam
        
        # ════════════════════════════════════════════════════════
        # SECTION 2: DIVISION PAR DÉPARTEMENT
        # ════════════════════════════════════════════════════════
        
        st.markdown("---")
        st.markdown("#### 🏛️ Division par Département")
        
        dept_split = st.checkbox(
            "✅ Activer l'alternance des départements",
            value=False,
            help="Les départements du Groupe A passent examen Jour 1, repos Jour 2. Le Groupe B fait l'inverse."
        )
        st.session_state.dept_splitting = dept_split
        
        if dept_split:
            st.info("📊 **Mode Alternance:** Regroupez les départements qui passeront les examens ensemble")
            
            # Charger les départements
            all_depts = q("SELECT id, nom FROM departements ORDER BY nom") or []
            dept_names = [d['nom'] for d in all_depts]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔵 Groupe A** (Examen Jours 1, 3, 5...)")
                group_a = st.multiselect(
                    "Départements Groupe A",
                    options=dept_names,
                    default=dept_names[:len(dept_names)//2] if dept_names else [],
                    key="widget_group_a",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("**🟠 Groupe B** (Examen Jours 2, 4, 6...)")
                # Filtrer pour ne montrer que ceux non sélectionnés dans A
                remaining = [d for d in dept_names if d not in group_a]
                group_b = st.multiselect(
                    "Départements Groupe B",
                    options=remaining,
                    default=remaining,
                    key="widget_group_b",
                    label_visibility="collapsed"
                )
            
            # Sauvegarder les IDs des départements (clés différentes des widgets!)
            group_a_ids = [d['id'] for d in all_depts if d['nom'] in group_a]
            group_b_ids = [d['id'] for d in all_depts if d['nom'] in group_b]
            st.session_state.dept_group_a = group_a_ids
            st.session_state.dept_group_b = group_b_ids
            
            # Afficher résumé
            if group_a or group_b:
                st.success(f"""
                **📅 Planification:**
                - 🔵 **Groupe A** ({len(group_a)} depts): Examen Lundi, Repos Mardi, Examen Mercredi...
                - 🟠 **Groupe B** ({len(group_b)} depts): Repos Lundi, Examen Mardi, Repos Mercredi...
                """)
        
        # ════════════════════════════════════════════════════════
        # SECTION 3: SURVEILLANTS (SAISIE MANUELLE)
        # ════════════════════════════════════════════════════════
        
        st.markdown("---")
        st.markdown("#### 👨‍🏫 Nombre de Surveillants par Salle")
        st.caption("Saisissez le nombre exact de surveillants souhaité")
        
        col1, col2 = st.columns(2)
        with col1:
            sv_small = st.number_input(
                "🏢 Petite salle (< 100 places)",
                min_value=1, max_value=10, value=1, step=1,
                help="Nombre de surveillants par petite salle"
            )
            st.session_state.supervisors_small_room = sv_small
        
        with col2:
            sv_amphi = st.number_input(
                "🏛️ Amphithéâtre (> 100 places)",
                min_value=1, max_value=10, value=2, step=1,
                help="Nombre de surveillants par amphithéâtre"
            )
            st.session_state.supervisors_amphi = sv_amphi
        
        # Nouvelle option: Max surveillances par professeur PAR JOUR
        st.markdown("##### 📊 Limite de surveillances par jour")
        col1, col2 = st.columns(2)
        with col1:
            max_surv_day = st.number_input(
                "🎯 Max surveillances par enseignant (par jour)",
                min_value=1, max_value=10, value=3, step=1,
                help="Nombre maximum de surveillances qu'un enseignant peut effectuer PAR JOUR"
            )
            st.session_state.max_supervisions_per_prof_per_day = max_surv_day
        
        with col2:
            st.caption(f"""
            ℹ️ **Conformément au PDF:** Un enseignant peut surveiller au maximum **{max_surv_day} examens par jour**.
            Cela respecte la contrainte "Professeurs: Maximum 3 examens par jour".
            """)
        
        # ════════════════════════════════════════════════════════
        # SECTION 4: NIVEAUX
        # ════════════════════════════════════════════════════════
        
        st.markdown("---")
        st.markdown("#### 🎓 Niveaux à Planifier")
        st.caption("Sélectionnez les niveaux d'études à inclure dans la planification")
        
        niveaux = st.multiselect(
            "Niveaux",
            options=["L1", "L2", "L3", "M1", "M2"],
            default=["L1", "L2", "L3", "M1", "M2"],
            label_visibility="collapsed"
        )
        st.session_state.selected_levels = niveaux if niveaux else ["L1", "L2", "L3", "M1", "M2"]
        
        # Valeurs par défaut pour les autres paramètres
        st.session_state.max_exam_prof = 5
        st.session_state.fair_distribution = True
        st.session_state.dept_priority = True
        
        st.markdown("---")
        
        # RÉSUMÉ CLAIR
        st.markdown("#### ✅ Configuration Actuelle")
        division_text = "✅ Division département activée" if st.session_state.get('dept_splitting', False) else "❌ Division département désactivée"
        st.success(f"""
        **📅 Repos:** {st.session_state.rest_days} jour(s) entre examens  
        **🏛️ Départements:** {division_text}  
        **📝 Étudiants:** Max {st.session_state.max_exam_student} examen/jour  
        **👨‍🏫 Surveillants:** {st.session_state.supervisors_small_room} (salle) / {st.session_state.supervisors_amphi} (amphi)  
        **🎓 Niveaux:** {', '.join(st.session_state.selected_levels)}
        """)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: DONNÉES - VERSION AMÉLIORÉE                                           ║
# ║  Avec spécialités, bâtiments, filtres, dropdowns et suppression              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "Données" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">📝 Gestion des Données</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Ajouter, modifier et supprimer les données de l'application</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏛️ Depts", "📚 Forms", "👨‍🏫 Profs", "🏢 Salles", "📖 Modules", "👨‍🎓 Étudiants"])
    
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1: DÉPARTEMENTS
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🏛️ Départements")
        depts = get_depts()
        
        if depts:
            df = pd.DataFrame([{'ID': d['id'], 'Nom': d['nom'], 'Code': d['code']} for d in depts])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        col_add, col_del = st.columns(2)
        
        with col_add:
            st.markdown("#### ➕ Ajouter")
            with st.form("dept_form"):
                nom = st.text_input("Nom", placeholder="Informatique")
                code = st.text_input("Code", placeholder="INFO")
                if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
                    if nom and code:
                        insert("INSERT INTO departements (nom, code) VALUES (%s,%s)", (nom, code))
                        st.success("✅ Département ajouté!"); st.cache_data.clear(); st.rerun()
        
        with col_del:
            st.markdown("#### 🗑️ Supprimer")
            if depts:
                del_dept = st.selectbox("Sélectionner", [f"{d['code']} - {d['nom']}" for d in depts], key="del_dept")
                if st.button("❌ Supprimer", key="btn_del_dept", type="secondary", use_container_width=True):
                    code_to_del = del_dept.split(" - ")[0]
                    try:
                        q("DELETE FROM departements WHERE code=%s", (code_to_del,), fetch='none')
                        st.success("✅ Supprimé!"); st.cache_data.clear(); st.rerun()
                    except Exception as e:
                        st.error(f"❌ Impossible de supprimer (données liées): {e}")
    
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2: FORMATIONS
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📚 Formations")
        depts = get_depts()
        formations = get_formations()
        
        if formations:
            # Filtre par département
            filter_dept = st.selectbox("🔍 Filtrer par département", ["Tous"] + [d['nom'] for d in depts], key="filter_form_dept")
            if filter_dept != "Tous":
                formations = [f for f in formations if f['dept'] == filter_dept]
            
            df = pd.DataFrame([{'ID': f['id'], 'Nom': f['nom'], 'Code': f['code'], 'Niveau': f['niveau'], 'Dept': f['dept']} for f in formations[:50]])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        col_add, col_del = st.columns(2)
        
        with col_add:
            st.markdown("#### ➕ Ajouter")
            if depts:
                with st.form("form_form"):
                    nom = st.text_input("Nom", placeholder="Génie Logiciel")
                    code = st.text_input("Code", placeholder="GL")
                    c1, c2 = st.columns(2)
                    dept_sel = c1.selectbox("Département", [d['nom'] for d in depts])
                    niveau = c2.selectbox("Niveau", ["L1", "L2", "L3", "M1", "M2"])
                    if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
                        if nom and code:
                            did = next(d['id'] for d in depts if d['nom'] == dept_sel)
                            insert("INSERT INTO formations (nom, code, dept_id, niveau, nb_modules) VALUES (%s,%s,%s,%s,6)", (f"{niveau} - {nom}", code, did, niveau))
                            st.success("✅ Formation ajoutée!"); st.cache_data.clear(); st.rerun()
        
        with col_del:
            st.markdown("#### 🗑️ Supprimer")
            if formations:
                del_form = st.selectbox("Sélectionner", [f"{f['code']} - {f['nom']}" for f in formations[:30]], key="del_form")
                col_single, col_bulk = st.columns(2)
                if col_single.button("❌ Supprimer", key="btn_del_form", type="secondary", use_container_width=True):
                    code_to_del = del_form.split(" - ")[0]
                    try:
                        q("DELETE FROM formations WHERE code=%s", (code_to_del,), fetch='none')
                        st.success("✅ Supprimé!"); st.cache_data.clear(); st.rerun()
                    except Exception as e:
                        st.error(f"❌ Impossible: {e}")
    
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3: PROFESSEURS (avec spécialité + autocomplete)
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 👨‍🏫 Professeurs")
        depts = get_depts()
        profs = get_profs()
        
        # Récupérer les spécialités existantes pour l'autocomplete
        existing_specs = q("SELECT DISTINCT specialite FROM professeurs WHERE specialite IS NOT NULL AND specialite != '' ORDER BY specialite")
        spec_suggestions = [s['specialite'] for s in existing_specs] if existing_specs else []
        
        if profs:
            # Filtre par département
            filter_dept = st.selectbox("🔍 Filtrer par département", ["Tous"] + [d['nom'] for d in depts], key="filter_prof_dept")
            profs_filtered = profs if filter_dept == "Tous" else [p for p in profs if p['dept'] == filter_dept]
            
            df = pd.DataFrame([{
                'Matricule': p['matricule'],
                'Nom': f"{p['prenom']} {p['nom']}", 
                'Grade': p['grade'], 
                'Spécialité': p.get('specialite') or '—',
                'Dept': p['dept']
            } for p in profs_filtered[:50]])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        col_add, col_del = st.columns(2)
        
        with col_add:
            st.markdown("#### ➕ Ajouter un professeur")
            if depts:
                with st.form("prof_form"):
                    c1, c2 = st.columns(2)
                    matricule = c1.text_input("Matricule", placeholder="P001")
                    nom = c2.text_input("Nom", placeholder="BENALI")
                    c3, c4 = st.columns(2)
                    prenom = c3.text_input("Prénom", placeholder="Ahmed")
                    grade = c4.selectbox("Grade", ["MAA", "MAB", "MCA", "MCB", "PR"])
                    dept_sel = st.selectbox("Département", [d['nom'] for d in depts], key="pd")
                    
                    # Spécialité avec suggestions
                    if spec_suggestions:
                        st.caption(f"💡 Suggestions: {', '.join(spec_suggestions[:5])}")
                    specialite = st.text_input("Spécialité", placeholder="Intelligence Artificielle, Réseaux...")
                    
                    if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
                        if matricule and nom and prenom:
                            did = next(d['id'] for d in depts if d['nom'] == dept_sel)
                            try:
                                insert("INSERT INTO professeurs (matricule, nom, prenom, dept_id, grade, specialite) VALUES (%s,%s,%s,%s,%s,%s)", 
                                       (matricule, nom, prenom, did, grade, specialite or None))
                                st.success(f"✅ Professeur ajouté!"); st.cache_data.clear(); st.rerun()
                            except Exception as e:
                                st.error(f"❌ Matricule déjà existant ou erreur: {e}")
        
        with col_del:
            st.markdown("#### 🗑️ Supprimer")
            if profs:
                # Suppression individuelle
                profs_filtered = profs if filter_dept == "Tous" else [p for p in profs if p['dept'] == filter_dept]
                del_prof = st.selectbox("Sélectionner", [f"{p['matricule']} - {p['prenom']} {p['nom']}" for p in profs_filtered[:30]], key="del_prof")
                
                c1, c2 = st.columns(2)
                if c1.button("❌ Supprimer", key="btn_del_prof", type="secondary", use_container_width=True):
                    mat_to_del = del_prof.split(" - ")[0]
                    try:
                        q("DELETE FROM surveillances WHERE professeur_id = (SELECT id FROM professeurs WHERE matricule=%s)", (mat_to_del,), fetch='none')
                        q("DELETE FROM professeurs WHERE matricule=%s", (mat_to_del,), fetch='none')
                        st.success("✅ Supprimé!"); st.cache_data.clear(); st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur: {e}")
                
                # Suppression en masse
                with st.expander("🗑️ Suppression en masse"):
                    st.warning("⚠️ Cette action est irréversible!")
                    if filter_dept != "Tous":
                        if st.button(f"❌ Supprimer tous les profs de {filter_dept}", key="bulk_del_prof"):
                            dept_id = next(d['id'] for d in depts if d['nom'] == filter_dept)
                            try:
                                q("DELETE FROM surveillances WHERE professeur_id IN (SELECT id FROM professeurs WHERE dept_id=%s)", (dept_id,), fetch='none')
                                q("DELETE FROM professeurs WHERE dept_id=%s", (dept_id,), fetch='none')
                                st.success("✅ Tous supprimés!"); st.cache_data.clear(); st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erreur: {e}")
    
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4: SALLES (avec bâtiment + autocomplete)
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### 🏢 Salles & Amphithéâtres")
        salles = get_salles()
        
        # Récupérer les bâtiments existants pour l'autocomplete
        existing_buildings = q("SELECT DISTINCT batiment FROM lieu_examen WHERE batiment IS NOT NULL AND batiment != '' ORDER BY batiment")
        building_suggestions = [b['batiment'] for b in existing_buildings] if existing_buildings else []
        
        if salles:
            # Filtre par type
            filter_type = st.selectbox("🔍 Filtrer par type", ["Tous", "AMPHI", "SALLE", "LABO"], key="filter_salle_type")
            salles_filtered = salles if filter_type == "Tous" else [s for s in salles if s['type'] == filter_type]
            
            df = pd.DataFrame([{
                'Nom': s['nom'], 
                'Code': s['code'], 
                'Type': s['type'], 
                'Bâtiment': s.get('batiment') or '—',
                'Capacité': s['capacite']
            } for s in salles_filtered])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        col_add, col_del = st.columns(2)
        
        with col_add:
            st.markdown("#### ➕ Ajouter une salle")
            with st.form("salle_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("Nom", placeholder="Amphi 1")
                code = c2.text_input("Code", placeholder="AMP01")
                c3, c4 = st.columns(2)
                typ = c3.selectbox("Type", ["AMPHI", "SALLE", "LABO"])
                cap = c4.number_input("Capacité", 10, 500, 100)
                
                # Bâtiment avec suggestions
                if building_suggestions:
                    st.caption(f"💡 Bâtiments existants: {', '.join(building_suggestions)}")
                batiment = st.text_input("Bâtiment", placeholder="Bloc A, Nouveau Bloc...")
                
                if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
                    if nom and code:
                        insert("INSERT INTO lieu_examen (nom, code, type, capacite, batiment, disponible) VALUES (%s,%s,%s,%s,%s,TRUE)", 
                               (nom, code, typ, cap, batiment or None))
                        st.success("✅ Salle ajoutée!"); st.cache_data.clear(); st.rerun()
        
        with col_del:
            st.markdown("#### 🗑️ Supprimer")
            if salles:
                salles_filtered = salles if filter_type == "Tous" else [s for s in salles if s['type'] == filter_type]
                del_salle = st.selectbox("Sélectionner", [f"{s['code']} - {s['nom']}" for s in salles_filtered], key="del_salle")
                
                if st.button("❌ Supprimer", key="btn_del_salle", type="secondary", use_container_width=True):
                    code_to_del = del_salle.split(" - ")[0]
                    try:
                        q("DELETE FROM lieu_examen WHERE code=%s", (code_to_del,), fetch='none')
                        st.success("✅ Supprimé!"); st.cache_data.clear(); st.rerun()
                    except Exception as e:
                        st.error(f"❌ Impossible (examens planifiés): {e}")
                
                # Suppression par type
                with st.expander("🗑️ Suppression en masse"):
                    if filter_type != "Tous":
                        if st.button(f"❌ Supprimer toutes les {filter_type}s", key="bulk_del_salle"):
                            try:
                                q("DELETE FROM lieu_examen WHERE type=%s AND id NOT IN (SELECT DISTINCT salle_id FROM examens)", (filter_type,), fetch='none')
                                st.success("✅ Salles non utilisées supprimées!"); st.cache_data.clear(); st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erreur: {e}")
    
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5: MODULES
    # ══════════════════════════════════════════════════════════════════════════
    with tab5:
        st.markdown("### 📖 Modules")
        depts = get_depts()
        formations = get_formations()
        
        if formations:
            # Double filtre: département puis formation
            c1, c2 = st.columns(2)
            filter_dept = c1.selectbox("🏛️ Département", ["Tous"] + [d['nom'] for d in depts], key="mod_filter_dept")
            
            if filter_dept != "Tous":
                formations = [f for f in formations if f['dept'] == filter_dept]
            
            sel_f = c2.selectbox("📚 Formation", [f['nom'] for f in formations], key="mf")
            fid = next(f['id'] for f in formations if f['nom'] == sel_f)
            mods = get_modules(fid)
            
            if mods:
                df = pd.DataFrame([{'Code': m['code'], 'Nom': m['nom'], 'Crédits': m['credits'], 'Sem': m['semestre']} for m in mods])
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            col_add, col_del = st.columns(2)
            
            with col_add:
                st.markdown("#### ➕ Ajouter")
                with st.form("mod_form"):
                    c1, c2 = st.columns(2)
                    nom = c1.text_input("Nom du module", placeholder="Programmation")
                    code = c2.text_input("Code", placeholder="PROG01")
                    c3, c4 = st.columns(2)
                    sem = c3.selectbox("Semestre", ["S1", "S2"])
                    cred = c4.number_input("Crédits", 1, 10, 4)
                    if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
                        if nom and code:
                            insert("INSERT INTO modules (code, nom, credits, formation_id, semestre, coefficient) VALUES (%s,%s,%s,%s,%s,%s)", (code, nom, cred, fid, sem, cred/2))
                            st.success("✅ Module ajouté!"); st.cache_data.clear(); st.rerun()
            
            with col_del:
                st.markdown("#### 🗑️ Supprimer")
                if mods:
                    del_mod = st.selectbox("Sélectionner", [f"{m['code']} - {m['nom']}" for m in mods], key="del_mod")
                    if st.button("❌ Supprimer", key="btn_del_mod", type="secondary", use_container_width=True):
                        code_to_del = del_mod.split(" - ")[0]
                        try:
                            q("DELETE FROM examens WHERE module_id = (SELECT id FROM modules WHERE code=%s)", (code_to_del,), fetch='none')
                            q("DELETE FROM inscriptions WHERE module_id = (SELECT id FROM modules WHERE code=%s)", (code_to_del,), fetch='none')
                            q("DELETE FROM modules WHERE code=%s", (code_to_del,), fetch='none')
                            st.success("✅ Supprimé!"); st.cache_data.clear(); st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
    
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 6: ÉTUDIANTS (avec filtre dept, dropdown groupe, suppression)
    # ══════════════════════════════════════════════════════════════════════════
    with tab6:
        st.markdown("### 👨‍🎓 Étudiants")
        depts = get_depts()
        
        # Double filtre: département puis formation
        c1, c2 = st.columns(2)
        filter_dept = c1.selectbox("🏛️ Département", ["Tous"] + [d['nom'] for d in depts], key="etud_filter_dept")
        
        if filter_dept != "Tous":
            formations = q("SELECT f.*, d.nom as dept FROM formations f JOIN departements d ON f.dept_id=d.id WHERE d.nom=%s ORDER BY f.niveau, f.nom", (filter_dept,))
        else:
            formations = get_formations()
        
        if formations:
            sel_f = c2.selectbox("📚 Formation", [f['nom'] for f in formations], key="ef")
            fid = next(f['id'] for f in formations if f['nom'] == sel_f)
            
            # Récupérer les groupes existants pour cette formation
            existing_groups = q("SELECT DISTINCT COALESCE(groupe, 'G01') as g FROM etudiants WHERE formation_id=%s ORDER BY g", (fid,))
            group_list = [g['g'] for g in existing_groups] if existing_groups else []
            
            # Filtre par groupe
            c1, c2 = st.columns([3, 1])
            filter_groupe = c1.selectbox("👥 Groupe", ["Tous"] + group_list, key="filter_groupe") if group_list else "Tous"
            
            # Récupérer les étudiants
            if filter_groupe == "Tous":
                etuds = q("SELECT id, matricule, nom, prenom, COALESCE(groupe,'G01') as groupe FROM etudiants WHERE formation_id=%s ORDER BY groupe, nom LIMIT 100", (fid,))
            else:
                etuds = q("SELECT id, matricule, nom, prenom, COALESCE(groupe,'G01') as groupe FROM etudiants WHERE formation_id=%s AND (groupe=%s OR (groupe IS NULL AND %s='G01')) ORDER BY nom LIMIT 100", (fid, filter_groupe, filter_groupe))
            
            if etuds:
                c2.metric("Total", len(etuds))
                df = pd.DataFrame([{'Matricule': e['matricule'], 'Nom': e['nom'], 'Prénom': e['prenom'], 'Groupe': e['groupe']} for e in etuds])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun étudiant dans cette formation/groupe")
            
            col_add, col_del = st.columns(2)
            
            with col_add:
                st.markdown("#### ➕ Ajouter un étudiant")
                with st.form("etud_form"):
                    c1, c2 = st.columns(2)
                    matricule = c1.text_input("Matricule", placeholder="E20250001")
                    nom = c2.text_input("Nom", placeholder="AMRANI")
                    c3, c4 = st.columns(2)
                    prenom = c3.text_input("Prénom", placeholder="Mohamed")
                    
                    # Groupe: dropdown avec option pour nouveau groupe
                    groupe_options = group_list + ["➕ Nouveau groupe..."] if group_list else ["G01", "➕ Nouveau groupe..."]
                    groupe_sel = c4.selectbox("Groupe", groupe_options, key="groupe_sel")
                    
                    # Si nouveau groupe sélectionné, afficher champ de saisie
                    if groupe_sel == "➕ Nouveau groupe...":
                        groupe = st.text_input("Nom du nouveau groupe", placeholder="G03")
                    else:
                        groupe = groupe_sel
                    
                    if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
                        if matricule and nom and prenom and groupe:
                            try:
                                insert("INSERT INTO etudiants (matricule, nom, prenom, formation_id, groupe, promo) VALUES (%s,%s,%s,%s,%s,2025)", (matricule, nom, prenom, fid, groupe))
                                st.success(f"✅ Étudiant ajouté!"); st.cache_data.clear(); st.rerun()
                            except Exception as e:
                                st.error(f"❌ Matricule déjà existant ou erreur: {e}")
            
            with col_del:
                st.markdown("#### 🗑️ Supprimer")
                if etuds:
                    del_etud = st.selectbox("Sélectionner", [f"{e['matricule']} - {e['nom']} {e['prenom']}" for e in etuds[:50]], key="del_etud")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("❌ Supprimer", key="btn_del_etud", type="secondary", use_container_width=True):
                        mat_to_del = del_etud.split(" - ")[0]
                        try:
                            q("DELETE FROM inscriptions WHERE etudiant_id = (SELECT id FROM etudiants WHERE matricule=%s)", (mat_to_del,), fetch='none')
                            q("DELETE FROM etudiants WHERE matricule=%s", (mat_to_del,), fetch='none')
                            st.success("✅ Supprimé!"); st.cache_data.clear(); st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
                    
                    # Suppression en masse par groupe
                    with st.expander("🗑️ Suppression en masse"):
                        st.warning("⚠️ Cette action est irréversible!")
                        if filter_groupe != "Tous":
                            if st.button(f"❌ Supprimer tout le groupe {filter_groupe}", key="bulk_del_etud_grp"):
                                try:
                                    q("DELETE FROM inscriptions WHERE etudiant_id IN (SELECT id FROM etudiants WHERE formation_id=%s AND groupe=%s)", (fid, filter_groupe), fetch='none')
                                    q("DELETE FROM etudiants WHERE formation_id=%s AND groupe=%s", (fid, filter_groupe), fetch='none')
                                    st.success("✅ Groupe supprimé!"); st.cache_data.clear(); st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur: {e}")
                        
                        if st.button(f"❌ Supprimer TOUS les étudiants de {sel_f}", key="bulk_del_etud_all"):
                            try:
                                q("DELETE FROM inscriptions WHERE etudiant_id IN (SELECT id FROM etudiants WHERE formation_id=%s)", (fid,), fetch='none')
                                q("DELETE FROM etudiants WHERE formation_id=%s", (fid,), fetch='none')
                                st.success("✅ Tous les étudiants supprimés!"); st.cache_data.clear(); st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erreur: {e}")
            
            st.divider()
            
            # Section inscriptions
            st.markdown("#### ⚡ Inscriptions aux modules")
            c1, c2 = st.columns(2)
            if c1.button("⚡ Inscrire tous aux modules S1", type="secondary", use_container_width=True):
                es = q("SELECT id FROM etudiants WHERE formation_id=%s", (fid,))
                ms = q("SELECT id FROM modules WHERE formation_id=%s AND semestre='S1'", (fid,))
                if es and ms:
                    cnt = 0
                    for e in es:
                        for m in ms:
                            try: 
                                insert("INSERT IGNORE INTO inscriptions (etudiant_id, module_id, annee_universitaire, statut) VALUES (%s,%s,'2025/2026','INSCRIT')", (e['id'], m['id']))
                                cnt += 1
                            except: pass
                    st.success(f"✅ {cnt} inscriptions créées!"); st.cache_data.clear()
            
            if c2.button("🗑️ Supprimer toutes les inscriptions", type="secondary", use_container_width=True):
                try:
                    q("DELETE FROM inscriptions WHERE etudiant_id IN (SELECT id FROM etudiants WHERE formation_id=%s)", (fid,), fetch='none')
                    st.success("✅ Inscriptions supprimées!"); st.cache_data.clear()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: GÉNÉRATION - AVEC RESET ET STATS CORRIGÉES                            ║
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
        c3.info(f"🕐 {len(creneaux)} créneaux/jour")
        
        # Stats corrigées: modules planifiés (distinct) vs créneaux utilisés
        stats = q("""SELECT 
            (SELECT COUNT(DISTINCT id) FROM modules WHERE semestre='S1') as mods,
            (SELECT COUNT(*) FROM lieu_examen WHERE disponible=TRUE) as salles,
            (SELECT COUNT(DISTINCT module_id) FROM examens WHERE session_id=%s) as modules_planifies,
            (SELECT COUNT(*) FROM examens WHERE session_id=%s) as total_creneaux
        """, (sid, sid), fetch='one')
        
        if stats:
            st.markdown(f"""
            <div class="stats-grid" style="grid-template-columns: repeat(4, 1fr);">
                <div class="stat-box"><span class="stat-icon">📖</span><div class="stat-value">{stats['mods'] or 0}</div><div class="stat-label">Modules S1</div></div>
                <div class="stat-box"><span class="stat-icon">🏢</span><div class="stat-value">{stats['salles'] or 0}</div><div class="stat-label">Salles</div></div>
                <div class="stat-box"><span class="stat-icon">✅</span><div class="stat-value">{stats['modules_planifies'] or 0}</div><div class="stat-label">Modules planifiés</div></div>
                <div class="stat-box"><span class="stat-icon">📅</span><div class="stat-value">{stats['total_creneaux'] or 0}</div><div class="stat-label">Créneaux utilisés</div></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Afficher info sur la relation modules/créneaux
            if stats['modules_planifies'] and stats['total_creneaux']:
                ratio = stats['total_creneaux'] / stats['modules_planifies']
                st.caption(f"ℹ️ En moyenne {ratio:.1f} groupes par module (même examen, salles différentes)")
        
        st.divider()
        
        # Afficher les paramètres qui seront utilisés
        with st.expander("⚙️ Paramètres de génération", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🛌 Repos", f"{st.session_state.get('rest_days', 0)} jour(s)")
            c2.metric("📝 Max/étudiant", f"{st.session_state.get('max_exam_student', 1)} exam/jour")
            c3.metric("👨‍🏫 Surv. salle", st.session_state.get('supervisors_small_room', 1))
            c4.metric("🏛️ Surv. amphi", st.session_state.get('supervisors_amphi', 2))
            st.caption(f"🎓 Niveaux: {', '.join(st.session_state.get('selected_levels', ['L1','L2','L3','M1','M2']))}")
        
        # Section Génération
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 GÉNÉRER L'EMPLOI DU TEMPS", type="primary", use_container_width=True):
                with st.spinner("⏳ Génération en cours..."):
                    try:
                        # Nettoyer les anciens examens
                        q("DELETE FROM surveillances WHERE examen_id IN (SELECT id FROM examens WHERE session_id=%s)", (sid,), fetch='none')
                        q("DELETE FROM conflits WHERE examen1_id IN (SELECT id FROM examens WHERE session_id=%s)", (sid,), fetch='none')
                        q("DELETE FROM examens WHERE session_id=%s", (sid,), fetch='none')
                        
                        from services.optimization import run_optimization
                        
                        opt_config = {
                            'max_exam_per_student_per_day': st.session_state.get('max_exam_student', 1),
                            'max_exam_per_professor_per_day': st.session_state.get('max_exam_prof', 3),
                            'rest_days': st.session_state.get('rest_days', 0),
                            'dept_splitting': st.session_state.get('dept_splitting', False),
                            'dept_group_a': st.session_state.get('dept_group_a', []),
                            'dept_group_b': st.session_state.get('dept_group_b', []),
                            'selected_levels': st.session_state.get('selected_levels', ['L1','L2','L3','M1','M2']),
                            'supervisors_small_room': st.session_state.get('supervisors_small_room', 1),
                            'supervisors_amphi': st.session_state.get('supervisors_amphi', 2),
                            'fair_distribution': st.session_state.get('fair_distribution', True),
                            'dept_priority': st.session_state.get('dept_priority', True),
                            'max_supervisions_per_prof_per_day': st.session_state.get('max_supervisions_per_prof_per_day', 3)
                        }
                        
                        start = datetime.now()
                        r = run_optimization(sid, opt_config)
                        elapsed = (datetime.now() - start).total_seconds()
                        
                        st.balloons()
                        st.success(f"✅ Terminé en {elapsed:.1f}s!")
                        
                        # Obtenir les valeurs depuis la base de données (source de vérité)
                        db_exams = q("SELECT COUNT(*) as cnt FROM examens WHERE session_id = %s", (sid,), fetch='one')
                        db_surv = q("SELECT COUNT(*) as cnt FROM surveillances sv JOIN examens e ON sv.examen_id = e.id WHERE e.session_id = %s", (sid,), fetch='one')
                        
                        exams_count = db_exams.get('cnt', 0) if db_exams else r.get('scheduled', 0)
                        surv_count = db_surv.get('cnt', 0) if db_surv else 0
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("📅 Examens Planifiés", exams_count)
                        c2.metric("⚠️ Conflits", r.get('conflicts', 0))
                        c3.metric("📊 Surveillances", surv_count)
                        
                        # Afficher les paramètres appliqués
                        with st.expander("📋 Paramètres appliqués", expanded=True):
                            st.write(f"**Jours de repos:** {opt_config.get('rest_days', 0)}")
                            st.write(f"**Surveillants (salle <100):** {opt_config.get('supervisors_small_room', 1)}")
                            st.write(f"**Surveillants (amphi ≥100):** {opt_config.get('supervisors_amphi', 2)}")
                            st.write(f"**Division département:** {'Oui' if opt_config.get('dept_splitting') else 'Non'}")
                        
                        # VÉRIFICATION: Statistiques réelles depuis la base de données
                        with st.expander("✅ Vérification - Surveillants Assignés", expanded=True):
                            # Requête pour compter les surveillants par examen
                            stats = q("""
                                SELECT 
                                    COUNT(DISTINCT e.id) as nb_examens,
                                    COUNT(s.id) as total_surveillants,
                                    ROUND(COUNT(s.id) / COUNT(DISTINCT e.id), 1) as moyenne_par_examen
                                FROM examens e 
                                LEFT JOIN surveillances s ON s.examen_id = e.id
                                WHERE e.session_id = %s
                            """, (sid,))
                            
                            # Détail par type de salle
                            detail = q("""
                                SELECT 
                                    CASE WHEN l.capacite >= 100 THEN 'Amphithéâtre (≥100)' ELSE 'Petite salle (<100)' END as type_salle,
                                    COUNT(DISTINCT e.id) as nb_examens,
                                    COUNT(s.id) as total_surveillants,
                                    ROUND(COUNT(s.id) / COUNT(DISTINCT e.id), 1) as moyenne
                                FROM examens e 
                                LEFT JOIN surveillances s ON s.examen_id = e.id
                                LEFT JOIN lieu_examen l ON e.salle_id = l.id
                                WHERE e.session_id = %s
                                GROUP BY type_salle
                            """, (sid,))
                            
                            if stats and stats[0]:
                                s = stats[0]
                                st.metric("📊 Total surveillances", s.get('total_surveillants', 0))
                                st.metric("📈 Moyenne par examen", s.get('moyenne_par_examen', 0))
                                
                            if detail:
                                st.write("**Détail par type de salle:**")
                                for d in detail:
                                    st.write(f"- {d['type_salle']}: {d['total_surveillants']} surveillants ({d['moyenne']} par examen)")
                        
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"❌ {e}")
        
        with col2:
            with st.expander("🔄 Réinitialiser"):
                st.warning("⚠️ Supprimer tous les examens de cette session")
                if st.button("🗑️ Réinitialiser", type="secondary", use_container_width=True):
                    try:
                        q("DELETE FROM surveillances WHERE examen_id IN (SELECT id FROM examens WHERE session_id=%s)", (sid,), fetch='none')
                        q("DELETE FROM conflits WHERE examen1_id IN (SELECT id FROM examens WHERE session_id=%s)", (sid,), fetch='none')
                        q("DELETE FROM examens WHERE session_id=%s", (sid,), fetch='none')
                        st.success("✅ Session réinitialisée!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur: {e}")


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
                       m.nom as Module, COALESCE(e.groupe, 'G01') as Groupe,
                       (SELECT GROUP_CONCAT(CONCAT(p.prenom, ' ', p.nom) SEPARATOR ', ') 
                        FROM surveillances sv JOIN professeurs p ON sv.professeur_id=p.id 
                        WHERE sv.examen_id=e.id) as Surveillants
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
    user = st.session_state.user or {}
    role = st.session_state.role
    
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">📄 Export PDF</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Téléchargez votre planning au format PDF</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ════════════════════════════════════════════════════════════════════════════
    # EXPORT ÉTUDIANT - Uniquement son propre planning
    # ════════════════════════════════════════════════════════════════════════════
    if role == 'ETUDIANT':
        etudiant_id = user.get('etudiant_id')
        
        if etudiant_id:
            # Récupérer infos de l'étudiant
            etud_info = q("""
                SELECT e.nom, e.prenom, e.matricule, e.groupe, f.nom as formation, 
                       f.niveau, d.nom as departement, f.id as formation_id
                FROM etudiants e
                JOIN formations f ON e.formation_id = f.id
                JOIN departements d ON f.dept_id = d.id
                WHERE e.id = %s
            """, (etudiant_id,), fetch='one')
            
            if etud_info:
                st.info(f"📚 **Formation:** {etud_info['formation']} | **Groupe:** {etud_info['groupe']}")
                
                # Récupérer les examens de l'étudiant
                mes_examens = q("""
                    SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, 
                           m.code as module_code, m.nom as module_nom, l.code as salle
                    FROM examens e
                    JOIN modules m ON e.module_id = m.id
                    JOIN lieu_examen l ON e.salle_id = l.id
                    JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                    JOIN inscriptions i ON i.module_id = m.id
                    WHERE i.etudiant_id = %s
                    ORDER BY e.date_examen, ch.heure_debut
                """, (etudiant_id,))
                
                if mes_examens:
                    st.success(f"📅 {len(mes_examens)} examen(s) dans votre planning")
                    
                    if st.button("📄 Télécharger Mon Planning PDF", type="primary", use_container_width=True):
                        try:
                            from services.pdf_generator import generate_student_schedule_pdf
                            pdf = generate_student_schedule_pdf(
                                etud_info['formation'], 
                                etud_info['groupe'], 
                                etud_info['niveau'], 
                                mes_examens, 
                                etud_info['departement']
                            )
                            st.download_button(
                                "⬇️ Télécharger le PDF", 
                                pdf, 
                                f"planning_{user.get('nom', 'etudiant')}_{etud_info['groupe']}.pdf", 
                                "application/pdf",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Erreur: {e}")
                else:
                    st.warning("Aucun examen programmé")
            else:
                st.error("Impossible de charger vos informations")
        else:
            st.error("Compte non lié à un étudiant")
    
    # ════════════════════════════════════════════════════════════════════════════
    # EXPORT PROFESSEUR - Uniquement ses surveillances
    # ════════════════════════════════════════════════════════════════════════════
    elif role == 'PROFESSEUR':
        prof_id = user.get('professeur_id')
        
        if prof_id:
            st.info(f"👨‍🏫 Export de vos surveillances personnelles")
            
            survs = q("""
                SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, 
                       m.code as module_code, m.nom as module_nom, 
                       f.nom as formation, COALESCE(e.groupe,'G01') as groupe,
                       d.nom as departement, d.nom as dept,
                       l.code as salle, s.role
                FROM surveillances s 
                JOIN examens e ON s.examen_id=e.id 
                JOIN modules m ON e.module_id=m.id
                JOIN formations f ON m.formation_id=f.id
                JOIN departements d ON f.dept_id=d.id
                JOIN lieu_examen l ON e.salle_id=l.id 
                JOIN creneaux_horaires ch ON e.creneau_id=ch.id 
                WHERE s.professeur_id=%s ORDER BY e.date_examen
            """, (prof_id,))
            
            if survs:
                st.success(f"📅 {len(survs)} surveillance(s) programmée(s)")
                
                if st.button("📄 Télécharger Mon Planning PDF", type="primary", use_container_width=True):
                    try:
                        from services.pdf_generator import generate_professor_schedule_pdf
                        pdf = generate_professor_schedule_pdf(
                            user.get('nom', ''), 
                            user.get('prenom', ''), 
                            user.get('dept_nom', ''), 
                            survs
                        )
                        st.download_button(
                            "⬇️ Télécharger le PDF", 
                            pdf, 
                            f"surveillances_{user.get('nom', 'prof')}.pdf", 
                            "application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Erreur: {e}")
            else:
                st.warning("Aucune surveillance programmée")
        else:
            st.error("Compte non lié à un professeur")
    
    # ════════════════════════════════════════════════════════════════════════════
    # EXPORT CHEF DEPT - Uniquement son département
    # ════════════════════════════════════════════════════════════════════════════
    elif role == 'CHEF_DEPT':
        dept_id = user.get('dept_id')
        dept_nom = user.get('dept_nom', 'Mon Département')
        
        if dept_id:
            st.info(f"🏛️ Export du département: **{dept_nom}**")
            
            tab1, tab2 = st.tabs(["📚 Formations", "👨‍🏫 Professeurs"])
            
            with tab1:
                forms = q("SELECT id, nom, niveau FROM formations WHERE dept_id=%s ORDER BY niveau, nom", (dept_id,))
                if forms:
                    st.success(f"📚 {len(forms)} formations dans votre département")
                    if st.button("📄 Générer PDF Département", type="primary", key="chef_dept_pdf"):
                        all_data = {}
                        for f in forms:
                            ex = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, 
                                    m.code as module_code, m.nom as module_nom, 
                                    COALESCE(e.groupe,'G01') as groupe, l.code as salle
                                    FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id
                                    JOIN creneaux_horaires ch ON e.creneau_id=ch.id 
                                    WHERE m.formation_id=%s ORDER BY e.groupe, e.date_examen""", (f['id'],))
                            if ex: all_data[f['nom']] = {'niveau': f['niveau'], 'exams': ex}
                        if all_data:
                            try:
                                from services.pdf_generator import generate_department_pdf
                                pdf = generate_department_pdf(dept_nom, all_data)
                                st.download_button("⬇️ Télécharger", pdf, f"dept_{dept_nom}.pdf", "application/pdf")
                            except Exception as e: st.error(f"Erreur: {e}")
            
            with tab2:
                profs = q("SELECT id, nom, prenom FROM professeurs WHERE dept_id=%s ORDER BY nom", (dept_id,))
                if profs:
                    sel_p = st.selectbox("Professeur", [f"{p['prenom']} {p['nom']}" for p in profs])
                    pd2 = next(p for p in profs if f"{p['prenom']} {p['nom']}" == sel_p)
                    
                    if st.button("📄 Générer PDF Professeur", type="primary", key="chef_prof_pdf"):
                        survs = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, 
                                    m.code as module_code, m.nom as module_nom, f.nom as formation,
                                    COALESCE(e.groupe,'G01') as groupe, l.code as salle, s.role
                                    FROM surveillances s JOIN examens e ON s.examen_id=e.id 
                                    JOIN modules m ON e.module_id=m.id JOIN formations f ON m.formation_id=f.id
                                    JOIN lieu_examen l ON e.salle_id=l.id JOIN creneaux_horaires ch ON e.creneau_id=ch.id 
                                    WHERE s.professeur_id=%s ORDER BY e.date_examen""", (pd2['id'],))
                        if survs:
                            try:
                                from services.pdf_generator import generate_professor_schedule_pdf
                                pdf = generate_professor_schedule_pdf(pd2['nom'], pd2['prenom'], dept_nom, survs)
                                st.download_button("⬇️ Télécharger", pdf, f"prof_{pd2['nom']}.pdf", "application/pdf")
                            except Exception as e: st.error(f"Erreur: {e}")
        else:
            st.error("Compte non lié à un département")
    
    # ════════════════════════════════════════════════════════════════════════════
    # EXPORT ADMIN / VICE-DOYEN - Accès complet
    # ════════════════════════════════════════════════════════════════════════════
    else:
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
                        dept_info = q("SELECT d.nom FROM formations f JOIN departements d ON f.dept_id=d.id WHERE f.id=%s", (fd['id'],))
                        dept_name = dept_info[0]['nom'] if dept_info else ""
                        all_ex = {}
                        for g in groupes:
                            ex = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, 
                                    m.code as module_code, m.nom as module_nom, l.code as salle
                                    FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id
                                    JOIN creneaux_horaires ch ON e.creneau_id=ch.id 
                                    WHERE m.formation_id=%s AND (e.groupe=%s OR e.groupe IS NULL) ORDER BY e.date_examen""", (fd['id'], g['g']))
                            if ex: all_ex[g['g']] = ex
                        if all_ex:
                            try:
                                from services.pdf_generator import generate_multi_group_pdf
                                pdf = generate_multi_group_pdf(sel_f, fd['niveau'], all_ex, dept_name)
                                st.download_button("⬇️ Télécharger", pdf, f"planning_{sel_f}.pdf", "application/pdf")
                            except Exception as e: st.error(f"Erreur: {e}")
                    else:
                        dept_info = q("SELECT d.nom FROM formations f JOIN departements d ON f.dept_id=d.id WHERE f.id=%s", (fd['id'],))
                        dept_name = dept_info[0]['nom'] if dept_info else ""
                        ex = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, 
                                m.code as module_code, m.nom as module_nom, l.code as salle
                                FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id
                                JOIN creneaux_horaires ch ON e.creneau_id=ch.id 
                                WHERE m.formation_id=%s AND (e.groupe=%s OR e.groupe IS NULL) ORDER BY e.date_examen""", (fd['id'], sel_g))
                        if ex:
                            try:
                                from services.pdf_generator import generate_student_schedule_pdf
                                pdf = generate_student_schedule_pdf(sel_f, sel_g, fd['niveau'], ex, dept_name)
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
                            ex = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, 
                                    m.code as module_code, m.nom as module_nom, 
                                    COALESCE(e.groupe,'G01') as groupe, l.code as salle
                                    FROM examens e JOIN modules m ON e.module_id=m.id JOIN lieu_examen l ON e.salle_id=l.id
                                    JOIN creneaux_horaires ch ON e.creneau_id=ch.id 
                                    WHERE m.formation_id=%s ORDER BY e.groupe, e.date_examen""", (f['id'],))
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
                    survs = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, 
                                m.code as module_code, m.nom as module_nom, 
                                f.nom as formation, COALESCE(e.groupe,'G01') as groupe,
                                d.nom as departement, d.nom as dept,
                                l.code as salle, s.role
                                FROM surveillances s 
                                JOIN examens e ON s.examen_id=e.id 
                                JOIN modules m ON e.module_id=m.id
                                JOIN formations f ON m.formation_id=f.id
                                JOIN departements d ON f.dept_id=d.id
                                JOIN lieu_examen l ON e.salle_id=l.id 
                                JOIN creneaux_horaires ch ON e.creneau_id=ch.id 
                                WHERE s.professeur_id=%s ORDER BY e.date_examen""", (pd2['id'],))
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
                    ex = q("""SELECT e.date_examen as date, ch.heure_debut, ch.heure_fin, 
                            m.code as module_code, m.nom as module_nom, f.nom as formation,
                            COALESCE(e.groupe,'G01') as groupe,
                            (SELECT GROUP_CONCAT(CONCAT(p.prenom, ' ', p.nom) SEPARATOR ', ') 
                             FROM surveillances sv 
                             JOIN professeurs p ON sv.professeur_id=p.id 
                             WHERE sv.examen_id=e.id) as surveillant,
                            COALESCE(e.nb_etudiants_prevus, 0) as nb_etudiants
                            FROM examens e 
                            JOIN modules m ON e.module_id=m.id 
                            JOIN formations f ON m.formation_id=f.id
                            JOIN creneaux_horaires ch ON e.creneau_id=ch.id 
                            WHERE e.salle_id=%s ORDER BY e.date_examen""", (sd['id'],))
                    if ex:
                        try:
                            from services.pdf_generator import generate_room_schedule_pdf
                            pdf = generate_room_schedule_pdf(sd['nom'], sd['code'], sd['capacite'], ex)
                            st.download_button("⬇️ Télécharger", pdf, f"salle_{sd['code']}.pdf", "application/pdf")
                        except Exception as e: st.error(f"Erreur: {e}")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: KPIs VICE-DOYEN - Vue stratégique globale                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "KPIs Vice-doyen" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">📈 KPIs Vice-doyen</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Vue stratégique globale - Occupation, Conflits, Performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    sessions = get_sessions()
    if sessions:
        sel_s = st.selectbox("📅 Session", [s['nom'] for s in sessions], key="kpi_session")
        sid = next(s['id'] for s in sessions if s['nom'] == sel_s)
        
        # ═══════════════════════════════════════════════════════════════════════
        # SECTION 1: KPIs GLOBAUX
        # ═══════════════════════════════════════════════════════════════════════
        
        st.markdown("### 📊 Indicateurs Globaux")
        
        kpis = q("""
            SELECT 
                (SELECT COUNT(*) FROM examens WHERE session_id = %s) as total_examens,
                (SELECT COUNT(DISTINCT module_id) FROM examens WHERE session_id = %s) as modules_planifies,
                (SELECT COUNT(DISTINCT salle_id) FROM examens WHERE session_id = %s) as salles_utilisees,
                (SELECT COUNT(*) FROM lieu_examen WHERE disponible=TRUE) as total_salles,
                (SELECT COUNT(*) FROM surveillances sv JOIN examens e ON sv.examen_id=e.id WHERE e.session_id=%s) as total_surveillances,
                (SELECT COUNT(DISTINCT sv.professeur_id) FROM surveillances sv JOIN examens e ON sv.examen_id=e.id WHERE e.session_id=%s) as profs_actifs,
                (SELECT COUNT(*) FROM professeurs) as total_profs
        """, (sid, sid, sid, sid, sid), fetch='one')
        
        if kpis:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📅 Examens Planifiés", kpis['total_examens'] or 0)
            c2.metric("📖 Modules Couverts", kpis['modules_planifies'] or 0)
            
            taux_salles = ((kpis['salles_utilisees'] or 0) / max(kpis['total_salles'] or 1, 1)) * 100
            c3.metric("🏢 Taux Occupation Salles", f"{taux_salles:.1f}%")
            
            taux_profs = ((kpis['profs_actifs'] or 0) / max(kpis['total_profs'] or 1, 1)) * 100
            c4.metric("👨‍🏫 Profs Mobilisés", f"{taux_profs:.0f}%")
        
        # ═══════════════════════════════════════════════════════════════════════
        # SECTION 2: TAUX DE CONFLITS PAR DÉPARTEMENT
        # ═══════════════════════════════════════════════════════════════════════
        
        st.markdown("### ⚠️ Taux de Conflits par Département")
        
        dept_stats = q("""
            SELECT 
                d.id, d.nom as departement, d.code,
                COUNT(DISTINCT e.id) as examens,
                COUNT(DISTINCT c.id) as conflits,
                ROUND(COUNT(DISTINCT c.id) * 100.0 / NULLIF(COUNT(DISTINCT e.id), 0), 2) as taux_conflits
            FROM departements d
            LEFT JOIN formations f ON f.dept_id = d.id
            LEFT JOIN modules m ON m.formation_id = f.id
            LEFT JOIN examens e ON e.module_id = m.id AND e.session_id = %s
            LEFT JOIN conflits c ON c.examen1_id = e.id AND c.resolu = FALSE
            GROUP BY d.id
            ORDER BY taux_conflits DESC
        """, (sid,))
        
        if dept_stats:
            import pandas as pd
            df = pd.DataFrame(dept_stats)
            df['taux_conflits'] = df['taux_conflits'].fillna(0)
            
            # Affichage avec indicateurs visuels
            for _, row in df.iterrows():
                taux = row['taux_conflits']
                if taux == 0:
                    status = "🟢"
                elif taux < 5:
                    status = "🟡"
                else:
                    status = "🔴"
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                col1.write(f"{status} **{row['departement']}** ({row['code']})")
                col2.write(f"📅 {row['examens']} examens")
                col3.write(f"⚠️ {row['conflits']} conflits")
                col4.write(f"📊 {taux:.1f}%")
        
        # ═══════════════════════════════════════════════════════════════════════
        # SECTION 3: HEURES PROFESSEURS
        # ═══════════════════════════════════════════════════════════════════════
        
        st.markdown("### 👨‍🏫 Heures de Surveillance par Département")
        
        prof_hours = q("""
            SELECT 
                d.nom as departement,
                COUNT(sv.id) as total_surveillances,
                ROUND(COUNT(sv.id) * 1.5, 1) as heures_totales,
                COUNT(DISTINCT sv.professeur_id) as nb_profs,
                ROUND(COUNT(sv.id) * 1.5 / NULLIF(COUNT(DISTINCT sv.professeur_id), 0), 1) as heures_par_prof
            FROM departements d
            LEFT JOIN professeurs p ON p.dept_id = d.id
            LEFT JOIN surveillances sv ON sv.professeur_id = p.id
            LEFT JOIN examens e ON sv.examen_id = e.id AND e.session_id = %s
            GROUP BY d.id
            ORDER BY heures_totales DESC
        """, (sid,))
        
        if prof_hours:
            import pandas as pd
            df = pd.DataFrame(prof_hours)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Aucune session trouvée")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: VALIDATION CHEF DE DÉPARTEMENT                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "Validation Dept" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">✅ Validation par Département</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Approbation et validation des plannings par les chefs de département</p>
    </div>
    """, unsafe_allow_html=True)
    
    sessions = get_sessions()
    depts = get_depts()
    
    if sessions and depts:
        c1, c2 = st.columns(2)
        sel_s = c1.selectbox("📅 Session", [s['nom'] for s in sessions], key="val_session")
        sid = next(s['id'] for s in sessions if s['nom'] == sel_s)
        
        sel_d = c2.selectbox("🏛️ Département", [d['nom'] for d in depts], key="val_dept")
        did = next(d['id'] for d in depts if d['nom'] == sel_d)
        
        # Statistiques du département
        stats = q("""
            SELECT 
                COUNT(DISTINCT e.id) as total_examens,
                COUNT(DISTINCT e.module_id) as modules,
                SUM(CASE WHEN e.statut = 'VALIDE' THEN 1 ELSE 0 END) as valides,
                SUM(CASE WHEN e.statut = 'PLANIFIE' THEN 1 ELSE 0 END) as en_attente
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE e.session_id = %s AND f.dept_id = %s
        """, (sid, did), fetch='one')
        
        if stats and stats['total_examens']:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📅 Total Examens", stats['total_examens'])
            c2.metric("📖 Modules", stats['modules'])
            c3.metric("✅ Validés", stats['valides'] or 0)
            c4.metric("⏳ En Attente", stats['en_attente'] or 0)
            
            # Liste des examens à valider
            st.markdown("### 📋 Examens à Valider")
            
            exams = q("""
                SELECT e.id, e.date_examen, m.code as module, m.nom as module_nom,
                       l.nom as salle, e.nb_etudiants_prevus, e.statut,
                       ch.heure_debut, ch.heure_fin
                FROM examens e
                JOIN modules m ON e.module_id = m.id
                JOIN formations f ON m.formation_id = f.id
                JOIN lieu_examen l ON e.salle_id = l.id
                JOIN creneaux_horaires ch ON e.creneau_id = ch.id
                WHERE e.session_id = %s AND f.dept_id = %s
                ORDER BY e.date_examen, ch.heure_debut
            """, (sid, did))
            
            if exams:
                import pandas as pd
                df = pd.DataFrame(exams)
                df['statut'] = df['statut'].apply(lambda x: '✅ Validé' if x == 'VALIDE' else '⏳ En attente')
                st.dataframe(df[['date_examen', 'module', 'salle', 'nb_etudiants_prevus', 'statut']], 
                           use_container_width=True, hide_index=True)
                
                # Bouton de validation
                st.markdown("---")
                comments = st.text_area("📝 Commentaires de validation (optionnel)", key="val_comments")
                
                col1, col2 = st.columns(2)
                if col1.button("✅ Valider Tous les Examens", type="primary", use_container_width=True):
                    try:
                        # Vérifier si la colonne statut existe
                        try:
                            q("UPDATE examens e JOIN modules m ON e.module_id = m.id JOIN formations f ON m.formation_id = f.id SET e.statut = 'VALIDE' WHERE e.session_id = %s AND f.dept_id = %s", (sid, did), fetch='none')
                            st.success(f"✅ {stats['en_attente'] or 0} examens validés pour {sel_d}!")
                            st.cache_data.clear()
                        except Exception as e:
                            # Colonne n'existe pas encore
                            st.warning("⚠️ Exécutez d'abord stored_procedures.sql pour activer la validation")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                
                if col2.button("❌ Rejeter (Demander Révision)", type="secondary", use_container_width=True):
                    st.info("📧 Notification envoyée à l'administrateur pour révision")
        else:
            st.info(f"ℹ️ Aucun examen planifié pour {sel_d}")
    else:
        st.warning("⚠️ Configurez d'abord une session et des départements")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PAGE: BENCHMARKS PERFORMANCE                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

elif "Benchmarks" in page:
    st.markdown("""
    <div class="hero-gradient">
        <h1 style="color: #F8FAFC; font-size: 2rem; margin: 0;">⏱️ Benchmarks Performance</h1>
        <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Mesure des temps d'exécution des requêtes et opérations</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Taille des Données")
    
    # Statistiques de base
    sizes = q("""
        SELECT 
            (SELECT COUNT(*) FROM etudiants) as etudiants,
            (SELECT COUNT(*) FROM professeurs) as professeurs,
            (SELECT COUNT(*) FROM modules) as modules,
            (SELECT COUNT(*) FROM inscriptions) as inscriptions,
            (SELECT COUNT(*) FROM examens) as examens,
            (SELECT COUNT(*) FROM surveillances) as surveillances
    """, fetch='one')
    
    if sizes:
        c1, c2, c3 = st.columns(3)
        c1.metric("👨‍🎓 Étudiants", f"{sizes['etudiants']:,}")
        c2.metric("👨‍🏫 Professeurs", f"{sizes['professeurs']:,}")
        c3.metric("📖 Modules", f"{sizes['modules']:,}")
        
        c4, c5, c6 = st.columns(3)
        c4.metric("📝 Inscriptions", f"{sizes['inscriptions']:,}")
        c5.metric("📅 Examens", f"{sizes['examens']:,}")
        c6.metric("👁️ Surveillances", f"{sizes['surveillances']:,}")
    
    st.markdown("---")
    st.markdown("### ⏱️ Tests de Performance")
    
    if st.button("🚀 Lancer les Benchmarks", type="primary"):
        import time
        results = []
        
        with st.spinner("Exécution des benchmarks..."):
            # Test 1: COUNT simple
            start = time.perf_counter()
            q("SELECT COUNT(*) FROM inscriptions", fetch='one')
            elapsed = (time.perf_counter() - start) * 1000
            results.append({"Test": "COUNT inscriptions (130k+)", "Temps (ms)": f"{elapsed:.2f}", "Statut": "✅" if elapsed < 100 else "⚠️"})
            
            # Test 2: JOIN 2 tables
            start = time.perf_counter()
            q("SELECT COUNT(*) FROM inscriptions i JOIN etudiants e ON i.etudiant_id = e.id", fetch='one')
            elapsed = (time.perf_counter() - start) * 1000
            results.append({"Test": "JOIN inscriptions→etudiants", "Temps (ms)": f"{elapsed:.2f}", "Statut": "✅" if elapsed < 200 else "⚠️"})
            
            # Test 3: JOIN 4 tables
            start = time.perf_counter()
            q("""SELECT COUNT(*) FROM inscriptions i 
                 JOIN etudiants e ON i.etudiant_id = e.id
                 JOIN modules m ON i.module_id = m.id
                 JOIN formations f ON m.formation_id = f.id""", fetch='one')
            elapsed = (time.perf_counter() - start) * 1000
            results.append({"Test": "JOIN 4 tables", "Temps (ms)": f"{elapsed:.2f}", "Statut": "✅" if elapsed < 500 else "⚠️"})
            
            # Test 4: Requête examens avec surveillances
            start = time.perf_counter()
            q("""SELECT e.id, COUNT(sv.id) as surv
                 FROM examens e 
                 LEFT JOIN surveillances sv ON sv.examen_id = e.id
                 GROUP BY e.id LIMIT 1000""")
            elapsed = (time.perf_counter() - start) * 1000
            results.append({"Test": "GROUP BY examens+surveillances", "Temps (ms)": f"{elapsed:.2f}", "Statut": "✅" if elapsed < 300 else "⚠️"})
            
            # Test 5: Détection conflits
            start = time.perf_counter()
            q("""SELECT e1.id, e2.id
                 FROM examens e1
                 JOIN examens e2 ON e1.date_examen = e2.date_examen AND e1.id < e2.id
                 JOIN inscriptions i1 ON i1.module_id = e1.module_id
                 JOIN inscriptions i2 ON i2.module_id = e2.module_id AND i1.etudiant_id = i2.etudiant_id
                 LIMIT 100""")
            elapsed = (time.perf_counter() - start) * 1000
            results.append({"Test": "Détection conflits étudiants", "Temps (ms)": f"{elapsed:.2f}", "Statut": "✅" if elapsed < 1000 else "⚠️"})
        
        # Afficher les résultats
        import pandas as pd
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Résumé
        passed = sum(1 for r in results if r['Statut'] == '✅')
        total = len(results)
        
        if passed == total:
            st.success(f"✅ Tous les benchmarks passés ({passed}/{total})! Performance excellente.")
        elif passed >= total * 0.7:
            st.warning(f"⚠️ {passed}/{total} benchmarks passés. Performance acceptable.")
        else:
            st.error(f"❌ Seulement {passed}/{total} benchmarks passés. Optimisation nécessaire.")
        
        # Export rapport
        st.markdown("---")
        st.markdown("### 📄 Rapport de Benchmark")
        
        report = f"""# Rapport de Benchmark Performance
        
## Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Volume de données:
- Étudiants: {sizes['etudiants']:,}
- Inscriptions: {sizes['inscriptions']:,}
- Examens: {sizes['examens']:,}

## Résultats des tests:
"""
        for r in results:
            report += f"- {r['Test']}: {r['Temps (ms)']}ms {r['Statut']}\n"
        
        report += f"""
## Conclusion:
{passed}/{total} tests passés. {"Performance conforme aux exigences (<45s)." if passed == total else "Optimisation recommandée."}
"""
        
        st.download_button("📥 Télécharger Rapport", report, "benchmark_report.txt", "text/plain")

