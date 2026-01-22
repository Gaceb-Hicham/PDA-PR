"""
Script pour ajouter les colonnes manquantes à MariaDB Cloud
"""
import mysql.connector
import sys

# Configuration MariaDB Cloud
DB_CONFIG = {
    'host': 'serverless-europe-west2.sysp0000.db2.skysql.com',
    'port': 4057,
    'user': 'dbpgf25031469',
    'password': '9bx6PXBZ/b320{6XLMvs',
    'database': 'pda_examens',
    'charset': 'utf8mb4',
    'autocommit': True,
    'ssl_disabled': False
}

# Colonnes à ajouter à la table utilisateurs
ALTER_UTILISATEURS = [
    "ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS nom VARCHAR(100) AFTER dept_id",
    "ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS prenom VARCHAR(100) AFTER nom",
    "ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS niveau_acces INT DEFAULT 1 AFTER role",
    "ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS premiere_connexion BOOLEAN DEFAULT TRUE AFTER actif",
    "ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS last_login DATETIME DEFAULT NULL AFTER derniere_connexion",
]

def main():
    print("\n" + "=" * 60)
    print("  AJOUT DES COLONNES MANQUANTES")
    print("=" * 60)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)
        print("✅ Connecté à MariaDB Cloud")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    
    # Ajouter les colonnes à utilisateurs
    print("\n📋 Table: utilisateurs")
    for sql in ALTER_UTILISATEURS:
        try:
            cursor.execute(sql)
            col = sql.split('ADD COLUMN')[1].split()[2] if 'IF NOT EXISTS' in sql else sql.split('ADD COLUMN')[1].split()[0]
            print(f"  ✅ Colonne ajoutée: {col}")
        except mysql.connector.Error as e:
            if 'Duplicate column' in str(e) or 'already exists' in str(e).lower():
                print(f"  ⚠️  Colonne existe déjà")
            else:
                print(f"  ⚠️  {e}")
    
    # Vérifier la structure finale
    print("\n📊 Structure finale de utilisateurs:")
    cursor.execute("DESCRIBE utilisateurs")
    for row in cursor.fetchall():
        print(f"   • {row[0]}: {row[1]}")
    
    cursor.close()
    conn.close()
    print("\n✅ Terminé!")

if __name__ == "__main__":
    main()
