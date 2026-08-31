def calculer_planning_revision(cours_ecole, jours_ecole, coefficients, quota_du_soir):
    """
    Calcule la répartition du temps de révision par matière pour chaque soir,
    au prorata des coefficients attribués.
    """
    planning_final = {}

    # Liste par défaut des jours si non fournis
    jours = jours_ecole if jours_ecole else ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

    for i, jour_actuel in enumerate(jours):
        # 1. Identifier les matières vues le jour même
        cours_aujourdhui = []
        if isinstance(cours_ecole, dict):
            cours_aujourdhui = cours_ecole.get(jour_actuel, [])
        elif isinstance(cours_ecole, list):
            cours_aujourdhui = [
                c.get("matiere") for c in cours_ecole 
                if isinstance(c, dict) and c.get("jour") == jour_actuel
            ]

        # 2. Matières à réviser ce soir (matières du jour ou de la semaine)
        matieres_du_soir = list(coefficients.keys())

        if not matieres_du_soir:
            continue

        # 3. Calcul du total des coefficients pour la soirée
        total_coeffs = sum(coefficients.get(m, 1) for m in matieres_du_soir)

        creneaux_soir = []
        
        # Jour suivant pour la mention "Préparer (jour)"
        jour_suivant = jours[(i + 1) % len(jours)]

        for m in matieres_du_soir:
            coeff = coefficients.get(m, 1)

            # Formule au prorata : (Quota x Coeff) / Total_Coeffs
            if total_coeffs > 0:
                temps_heures = (quota_du_soir * coeff) / total_coeffs
            else:
                temps_heures = 0

            minutes_totales = int(temps_heures * 60)

            # Conversion en heures et minutes
            heures = minutes_totales // 60
            minutes_restantes = minutes_totales % 60

            if heures > 0:
                duree_str = f"{heures}h {minutes_restantes:02d}m"
            else:
                duree_str = f"{minutes_restantes} min"

            # Identification du type d'action
            if m in cours_aujourdhui:
                statut = "Revoir (Aujourd'hui)"
            else:
                statut = f"Préparer ({jour_suivant})"

            creneaux_soir.append({
                "matiere": m,
                "coeff": coeff,
                "duree": duree_str,
                "duree_minutes": minutes_totales,
                "action": statut
            })

        planning_final[jour_actuel] = creneaux_soir

    return planning_final
