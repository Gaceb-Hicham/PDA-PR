"""
Script pour effacer toutes les données et permettre une saisie manuelle
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_cursor

def clear_all_data():
    """Efface toutes les données pour permettre une saisie fraîche"""
    
    print("🗑️ Suppression de toutes les données...")
    
    with get_cursor() as cursor:
        # Désactiver temporairement les contraintes FK
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Effacer dans l'ordre inverse des dépendances
        tables = [
            'logs_systeme',
            'conflits', 
            'surveillances',
            'examens',
            'sessions_examen',
            'inscriptions',
            'etudiants',
            'modules',
            'formations',
            'professeurs',
            'departements',
            'lieu_examen',
            'creneaux_horaires',
            'utilisateurs'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
                print(f"  ✓ {table} vidée")
            except Exception as e:
                print(f"  ⚠ {table}: {e}")
        
        # Réactiver les contraintes FK
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    print("\n✅ Toutes les données ont été supprimées!")
    print("   Vous pouvez maintenant saisir manuellement les données via l'interface web.")

if __name__ == "__main__":
    confirm = input("⚠️  ATTENTION: Ceci va SUPPRIMER TOUTES LES DONNÉES!\n   Tapez 'OUI' pour confirmer: ")
    if confirm == "OUI":
        clear_all_data()
    else:
        print("Annulé.")
