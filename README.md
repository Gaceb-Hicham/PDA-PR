# Plateforme d'Optimisation des Emplois du Temps d'Examens Universitaires

## 🎓 Université M'Hamed Bougara - Faculté des Sciences

### 📋 Description

Plateforme web complète pour l'optimisation automatique des emplois du temps d'examens universitaires. Le système gère plus de 13 000 étudiants, 7 départements, et plus de 200 formations avec un algorithme de planification qui respecte toutes les contraintes académiques.

### 🚀 Fonctionnalités

- **Génération automatique EDT** en moins de 45 secondes
- **Détection de conflits** (étudiants, salles, professeurs)
- **Tableaux de bord** pour chaque rôle (Doyen, Admin, Chef Dept, Étudiant, Prof)
- **KPIs et statistiques** en temps réel
- **Export des plannings** (CSV)

### 🔧 Technologies

- **Base de données:** MySQL 8.0
- **Backend:** Python 3.10+
- **Frontend:** Streamlit + Bootstrap
- **Optimisation:** Algorithme de satisfaction de contraintes

### 📦 Installation

1. **Cloner le projet**
```bash
cd "c:\Users\PCSAT\Desktop\Project PDA"
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Créer la base de données**
```bash
mysql -u root -p < database/schema.sql
```

5. **Générer les données**
```bash
cd backend
python seed_data.py
```

6. **Lancer l'application**
```bash
cd frontend
streamlit run app.py
```

### 📊 Structure du Projet

```
Project PDA/
├── database/
│   └── schema.sql          # Schéma complet de la BD
├── backend/
│   ├── config.py           # Configuration
│   ├── database.py         # Connexion MySQL
│   ├── seed_data.py        # Génération de données
│   └── services/
│       ├── optimization.py # Algorithme EDT
│       ├── statistics.py   # KPIs
│       └── conflicts.py    # Détection conflits
├── frontend/
│   ├── app.py              # Application principale
│   └── pages/
│       ├── dashboard_doyen.py
│       ├── admin_planning.py
│       ├── conflits.py
│       ├── statistiques.py
│       ├── departements.py
│       └── consultation.py
├── benchmarks/
│   └── run_benchmarks.py
└── requirements.txt
```

### 📈 Contraintes Respectées

- ✅ Maximum 1 examen par jour par étudiant
- ✅ Maximum 3 surveillances par jour par professeur
- ✅ Respect de la capacité des salles
- ✅ Priorité aux surveillants du département
- ✅ Équilibrage des charges

### 👥 Auteurs

- Projet académique - Année 2025/2026

### 📄 Licence

Projet académique - Université M'Hamed Bougara
