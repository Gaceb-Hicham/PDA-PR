"""
ExamPro - Module de Design Premium
Fournit les styles CSS et composants pour toutes les pages
Optimisé pour éviter le flash noir lors de la navigation
"""
import streamlit as st
import os

# Cache CSS content at module level to avoid re-reading file
_CSS_CACHE = None

def _get_css_content():
    """Cache le contenu CSS pour éviter la lecture répétée du fichier"""
    global _CSS_CACHE
    if _CSS_CACHE is None:
        css_path = os.path.join(os.path.dirname(__file__), 'style.css')
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                _CSS_CACHE = f.read()
        else:
            _CSS_CACHE = ""
    return _CSS_CACHE


def inject_premium_css():
    """Injecte le CSS premium dans n'importe quelle page Streamlit"""
    
    css_content = _get_css_content()
    
    # Critical: Set background immediately to prevent white/black flash
    st.markdown(f"""
    <style>
        /* CRITICAL: Instant background to prevent flash */
        .stApp {{
            background: #0F0F1A !important;
        }}
        
        {css_content}
        
        /* Additional styles for sub-pages */
        .page-hero {{
            background: linear-gradient(135deg, 
                rgba(99, 102, 241, 0.15) 0%, 
                rgba(236, 72, 153, 0.1) 50%,
                rgba(16, 185, 129, 0.1) 100%);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }}
        
        .page-hero::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #6366F1, #EC4899, #10B981);
        }}
        
        .page-hero h1 {{
            color: #F8FAFC;
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .page-hero p {{
            color: #94A3B8;
            margin: 0.5rem 0 0 0;
            font-size: 0.95rem;
        }}
        
        /* Stats row */
        .stats-row {{
            display: flex;
            gap: 1rem;
            margin: 1.5rem 0;
            flex-wrap: wrap;
        }}
        
        .stat-pill {{
            background: linear-gradient(145deg, rgba(30,30,50,0.9) 0%, rgba(20,20,35,0.95) 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            flex: 1;
            min-width: 120px;
        }}
        
        .stat-pill:hover {{
            transform: translateY(-3px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15);
        }}
        
        .stat-pill .icon {{
            font-size: 1.5rem;
            margin-bottom: 0.25rem;
        }}
        
        .stat-pill .value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #F8FAFC;
            line-height: 1.2;
        }}
        
        .stat-pill .label {{
            font-size: 0.7rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Info cards */
        .info-card {{
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            padding: 1rem;
            color: #93C5FD;
        }}
        
        .success-card {{
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 12px;
            padding: 1rem;
            color: #6EE7B7;
        }}
        
        .warning-card {{
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: 12px;
            padding: 1rem;
            color: #FCD34D;
        }}
        
        /* Tabs enhancement */
        .stTabs [data-baseweb="tab-list"] {{
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            padding: 0.5rem;
            gap: 0.5rem;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent !important;
            border-radius: 12px !important;
            color: #94A3B8 !important;
            font-weight: 500 !important;
            padding: 0.75rem 1.25rem !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
            color: white !important;
        }}
        
        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] {{
            display: none !important;
        }}
        
        /* Data tables */
        .stDataFrame {{
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid rgba(255,255,255,0.06) !important;
        }}
        
        /* Form styling */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stNumberInput > div > div > input {{
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 10px !important;
            color: #F8FAFC !important;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
            border: none !important;
            border-radius: 10px !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.5rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 18px rgba(99, 102, 241, 0.4) !important;
        }}
        
        /* Hide streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.06) !important;
            border-radius: 10px !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    """Affiche un header premium pour une page"""
    st.markdown(f"""
    <div class="page-hero">
        <h1>{icon} {title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def stats_row(stats: list):
    """
    Affiche une rangée de statistiques
    stats = [{"icon": "📅", "value": 42, "label": "Examens"}, ...]
    """
    stats_html = '<div class="stats-row">'
    for s in stats:
        stats_html += f'''
        <div class="stat-pill">
            <div class="icon">{s.get("icon", "📊")}</div>
            <div class="value">{s.get("value", 0)}</div>
            <div class="label">{s.get("label", "")}</div>
        </div>
        '''
    stats_html += '</div>'
    st.markdown(stats_html, unsafe_allow_html=True)


def info_card(text: str, card_type: str = "info"):
    """Affiche une carte d'information stylisée"""
    st.markdown(f'<div class="{card_type}-card">{text}</div>', unsafe_allow_html=True)
