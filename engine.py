from collections import defaultdict

COEFFS_PAR_DEFAUT = {
    "MATHEMATIQUES": 4, "MATHS": 4, "MATH": 4,
    "PHYSIQUE": 3, "CHIMIE": 3, "PHYSIQUE-CHIMIE": 3,
    "SVT": 3, "INFORMATIQUE": 3, "PYTHON": 3, "CYBERSECURITE": 4,
    "FRANCAIS": 2, "ANGLAIS": 2, "HISTOIRE": 2, "GEOGRAPHIE": 2,
    "PHILOSOPHIE": 2, "ESPAGNOL": 1, "ALLEMAND": 1, "EPS": 1, "ARTS": 1
}

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

def extraire_matieres_et_coeffs(raw_schedule_events):
    matieres_coeffs = {}
    cours_par_jour = defaultdict(list)
    
    for event in raw_schedule_events:
        if isinstance(event, dict):
            j = str(event.get("day", "Lundi")).capitalize()
            m = str(event.get("subject", "Matière")).strip()
            coeff = event.get("coeff")
        elif isinstance(event, str):
            j = "Lundi"
            m = event.strip()
            coeff = None
        else:
            continue
            
        m_upper = m.upper()
        if not coeff:
            coeff = COEFFS_PAR_DEFAUT.get(m_upper, 2)
            
        matieres_coeffs[m] = coeff
        if m not in cours_par_jour[j]:
            cours_par_jour[j].append(m)
            
    return matieres_coeffs, cours_par_jour

def calculer_planning_revision(daily_hours_budget=3.0, raw_schedule_events=None):
    """
    Moteur adaptatif de révision ultra-performant.
    - daily_hours_budget : Nombre d'heures que l'utilisateur souhaite réviser par soir (ex: 2.0, 3.0, 5.0).
    """
    if not raw_schedule_events:
        return {}

    matieres_coeffs, cours_par_jour = extraire_matieres_et_coeffs(raw_schedule_events)
    planning_final = {}

    for index_jour, jour in enumerate(JOURS_SEMAINE):
        lendemain = JOURS_SEMAINE[(index_jour + 1) % len(JOURS_SEMAINE)]
        
        cours_aujourdhui = cours_par_jour.get(jour, [])
        cours_lendemain = cours_par_jour.get(lendemain, [])

        scores_matieres = defaultdict(float)

        # 1. Priorité aux cours du lendemain (Préparation active - Coeff * 2.5)
        for m in cours_lendemain:
            c = matieres_coeffs.get(m, 2)
            scores_matieres[m] += c * 2.5

        # 2. Priorité aux cours du jour même (Consolidation - Coeff * 1.5)
        for m in cours_aujourdhui:
            c = matieres_coeffs.get(m, 2)
            scores_matieres[m] += c * 1.5

        # Si pas de cours aujourd'hui/demain, ajouter d'autres matières
        if not scores_matieres:
            for m, c in matieres_coeffs.items():
                scores_matieres[m] = c * 1.0

        matieres_triees = sorted(scores_matieres.items(), key=lambda x: x[1], reverse=True)

        # Ajustement du nombre de matières selon le temps disponible
        if daily_hours_budget <= 2.5:
            nb_matieres_max = 2
        elif daily_hours_budget <= 4.0:
            nb_matieres_max = 3
        else:
            nb_matieres_max = 4

        matieres_selectionnees = matieres_triees[:nb_matieres_max]
        total_score = sum(score for _, score in matieres_selectionnees)

        crenaux_jour = []
        if total_score > 0:
            temps_restant = daily_hours_budget
            for i, (m, score) in enumerate(matieres_selectionnees):
                is_last = (i == len(matieres_selectionnees) - 1)
                
                if is_last:
                    duree_h = round(temps_restant, 1)
                else:
                    duree_h = round((score / total_score) * daily_hours_budget, 1)
                    duree_h = max(0.5, duree_h)
                    temps_restant -= duree_h

                if duree_h <= 0:
                    continue

                # Formater la durée (ex: 1h30min ou 45min)
                minutes_totales = int(duree_h * 60)
                heures = minutes_totales // 60
                mins = minutes_totales % 60
                
                if heures > 0 and mins > 0:
                    duree_str = f"{heures}h{mins}min"
                elif heures > 0:
                    duree_str = f"{heures}h"
                else:
                    duree_str = f"{mins}min"

                action = "Préparation cours du lendemain" if m in cours_lendemain else "Consolidation & Exercices"
                coeff = matieres_coeffs.get(m, 2)

                crenaux_jour.append({
                    "matiere": m,
                    "coeff": coeff,
                    "duree": duree_str,
                    "action": action
                })

        planning_final[jour] = crenaux_jour

    return planning_final
