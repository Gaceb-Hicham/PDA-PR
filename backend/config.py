"""
Configuration du système de gestion des emplois du temps d'examens
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'pda_examens'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True
}

# Configuration de l'application
APP_CONFIG = {
    'name': "Plateforme d'Optimisation EDT Examens",
    'version': '1.0.0',
    'university': "Université M'Hamed Bougara",
    'faculty': "Faculté des Sciences",
    'annee_universitaire': '2025/2026'
}

# Paramètres d'optimisation
OPTIMIZATION_CONFIG = {
    'max_exam_per_student_per_day': 1,
    'max_exam_per_professor_per_day': 3,
    'default_exam_duration_minutes': 90,
    'time_slots': [
        ('08:00', '09:30'),
        ('09:45', '11:15'),
        ('11:30', '13:00'),
        ('13:45', '15:15'),
        ('15:30', '17:00')
    ],
    'optimization_timeout_seconds': 45,
    'prioritize_department_supervisors': True
}

# Créneaux horaires
TIME_SLOTS = {
    1: {'label': 'Matin 1', 'start': '08:00', 'end': '09:30'},
    2: {'label': 'Matin 2', 'start': '09:45', 'end': '11:15'},
    3: {'label': 'Matin 3', 'start': '11:30', 'end': '13:00'},
    4: {'label': 'Après-midi 1', 'start': '13:45', 'end': '15:15'},
    5: {'label': 'Après-midi 2', 'start': '15:30', 'end': '17:00'}
}

# Configuration des départements
DEPARTEMENTS = [
    {'code': 'INFO', 'nom': 'Informatique'},
    {'code': 'MATH', 'nom': 'Mathématiques'},
    {'code': 'PHYS', 'nom': 'Physique'},
    {'code': 'CHIM', 'nom': 'Chimie'},
    {'code': 'BIO', 'nom': 'Biologie'},
    {'code': 'GEO', 'nom': 'Géologie'},
    {'code': 'ELEC', 'nom': 'Électronique'}
]

# Configuration de l'interface
UI_CONFIG = {
    'theme': 'dark',
    'primary_color': '#FF6B35',
    'secondary_color': '#004E89',
    'success_color': '#2ECC71',
    'warning_color': '#F39C12',
    'danger_color': '#E74C3C',
    'page_icon': '🎓',
    'layout': 'wide'
}
