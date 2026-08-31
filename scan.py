# scan.py

def scanner_emploi_du_temps(image_path):
    """
    Mode démo : simule l'extraction OCR de l'emploi du temps.
    """
    print(f"[scan.py] Traitement de l'image : {image_path}")

    cours_ecole = {
        "Lundi": ["Mathématiques", "Physique"],
        "Mardi": ["Français", "Histoire-Géo"],
        "Mercredi": ["Mathématiques", "Anglais"],
        "Jeudi": ["SVT", "Physique"],
        "Vendredi": ["Philosophie", "Espagnol"]
    }

    jours_detectes = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

    matieres_uniques = [
        "Mathématiques", "Physique", "Français", 
        "Histoire-Géo", "Anglais", "SVT", "Philosophie", "Espagnol"
    ]

    return cours_ecole, jours_detectes, matieres_uniques
