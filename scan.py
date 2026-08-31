def scanner_emploi_du_temps(image_path):
    print(f"[scan.py] Traitement de l'image : {image_path}")

    cours_ecole = [
        # Lundi
        {"day": "Lundi", "subject": "Mathématiques", "start": "08:00", "end": "09:00"},
        {"day": "Lundi", "subject": "Histoire-Géo", "start": "09:00", "end": "11:00"},
        {"day": "Lundi", "subject": "Physique-Chimie", "start": "10:00", "end": "11:00"},
        {"day": "Lundi", "subject": "Anglais", "start": "11:00", "end": "12:00"},
        {"day": "Lundi", "subject": "Déjeuner", "start": "12:00", "end": "13:00"},
        {"day": "Lundi", "subject": "Informatique", "start": "13:00", "end": "14:00"},
        {"day": "Lundi", "subject": "Éducation Civique", "start": "15:00", "end": "16:00"},
        {"day": "Lundi", "subject": "EPS", "start": "16:00", "end": "17:00"},

        # Mardi
        {"day": "Mardi", "subject": "Français", "start": "08:00", "end": "09:00"},
        {"day": "Mardi", "subject": "SVT", "start": "09:00", "end": "11:00"},
        {"day": "Mardi", "subject": "Informatique", "start": "10:00", "end": "11:00"},
        {"day": "Mardi", "subject": "Mathématiques", "start": "11:00", "end": "12:00"},
        {"day": "Mardi", "subject": "Déjeuner", "start": "12:00", "end": "13:00"},
        {"day": "Mardi", "subject": "Arts Plastiques", "start": "13:00", "end": "14:00"},
        {"day": "Mardi", "subject": "Anglais", "start": "15:00", "end": "16:00"},
        {"day": "Mardi", "subject": "EPS", "start": "16:00", "end": "17:00"},

        # Mercredi
        {"day": "Mercredi", "subject": "Histoire-Géo", "start": "08:00", "end": "09:00"},
        {"day": "Mercredi", "subject": "EPS", "start": "09:00", "end": "11:00"},
        {"day": "Mercredi", "subject": "Physique-Chimie", "start": "10:00", "end": "11:00"},
        {"day": "Mercredi", "subject": "Informatique", "start": "11:00", "end": "12:00"},
        {"day": "Mercredi", "subject": "Déjeuner", "start": "12:00", "end": "13:00"},
        {"day": "Mercredi", "subject": "Arts Plastiques", "start": "13:00", "end": "14:00"},
        {"day": "Mercredi", "subject": "Anglais", "start": "15:00", "end": "16:00"},
        {"day": "Mercredi", "subject": "Technologies", "start": "16:00", "end": "17:00"},

        # Jeudi
        {"day": "Jeudi", "subject": "Mathématiques", "start": "08:00", "end": "09:00"},
        {"day": "Jeudi", "subject": "Français", "start": "09:00", "end": "11:00"},
        {"day": "Jeudi", "subject": "Technologie", "start": "10:00", "end": "11:00"},
        {"day": "Jeudi", "subject": "Histoire-Géo", "start": "11:00", "end": "12:00"},
        {"day": "Jeudi", "subject": "Déjeuner", "start": "12:00", "end": "13:00"},
        {"day": "Jeudi", "subject": "Anglais", "start": "13:00", "end": "14:00"},
        {"day": "Jeudi", "subject": "Physique-Chimie", "start": "15:00", "end": "16:00"},
        {"day": "Jeudi", "subject": "Arts Plastiques", "start": "16:00", "end": "17:00"},

        # Vendredi
        {"day": "Vendredi", "subject": "SVT", "start": "08:00", "end": "09:00"},
        {"day": "Vendredi", "subject": "Informatique", "start": "09:00", "end": "11:00"},
        {"day": "Vendredi", "subject": "Français", "start": "10:00", "end": "11:00"},
        {"day": "Vendredi", "subject": "Mathématiques", "start": "11:00", "end": "12:00"},
        {"day": "Vendredi", "subject": "Déjeuner", "start": "12:00", "end": "13:00"},
        {"day": "Vendredi", "subject": "EPS", "start": "13:00", "end": "14:00"},
        {"day": "Vendredi", "subject": "Technologie", "start": "15:00", "end": "16:00"},
        {"day": "Vendredi", "subject": "Anglais", "start": "16:00", "end": "17:00"},
    ]

    jours_detectes = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    
    # Extraction dynamique des matières sans doublons
    matieres_uniques = list(set(
        c["subject"] for c in cours_ecole if c["subject"] not in ["Déjeuner", "EPS"]
    ))

    return cours_ecole, jours_detectes, matieres_uniques
