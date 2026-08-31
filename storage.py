import json
import os

FILENAME = "user_schedule_data.json"

def sauvegarder_donnees(cours_ecole, heures_revision):
    """Sauvegarde l'emploi du temps scanné et les préférences d'heures dans un fichier JSON local."""
    data = {
        "heures_revision": heures_revision,
        "cours_ecole": cours_ecole
    }
    try:
        with open(FILENAME, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Erreur de sauvegarde : {e}")
        return False

def charger_donnees():
    """Charge les données sauvegardées si le fichier existe."""
    if not os.path.exists(FILENAME):
        return None
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Erreur de chargement : {e}")
        return None
