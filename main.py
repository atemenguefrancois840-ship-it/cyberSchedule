import flet as ft
import time
import threading
from collections import defaultdict
from engine import calculer_planning_revision
from scan import scanner_emploi_du_temps
from storage import sauvegarder_donnees, charger_donnees


import requests

def envoyer_photo_a_l_api(chemin_image_locale):
    url = "http://127.0.0.1:8000/scan-schedule"
    files = {'file': open(chemin_image_locale, 'rb')}
    
    response = requests.post(url, files=files)
    resultat = response.json()
    
    # Récupération directe des résultats nettoyés par engine.py
    cours = resultat["cours_par_jour"]
    return cours


def main(page: ft.Page):
    page.title = "CyberSchedule"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 480
    page.window_height = 800
    page.padding = 0

    colonne_agenda = ft.Column(expand=True)
    colonne_ecole = ft.Column(expand=True)

    # Variables globales
    heures_revision_var = [3.0]
    donnees_scan_cache = {"cours": []}

    def obtenir_couleur_coeff(coeff):
        if coeff >= 3:
            return "red400"
        elif coeff == 2:
            return "orange400"
        return "blue400"

    def aller_a(vue):
        page.views.clear()
        page.views.append(vue)
        page.update()

    # --- RECONSTRUCTION & SAUVEGARDE ---
    def reconstruire_planning(e=None):
        if e:
            heures_revision_var[0] = float(e.control.value)
        
        cours_ecole = donnees_scan_cache["cours"]
        
        # Sauvegarde automatique des nouvelles préférences
        sauvegarder_donnees(cours_ecole, heures_revision_var[0])

        planning_final = calculer_planning_revision(
            daily_hours_budget=heures_revision_var[0],
            raw_schedule_events=cours_ecole
        )
        construire_dashboard(cours_ecole, planning_final)

    # --- 3. VUE DASHBOARD ---
    def construire_dashboard(cours_ecole, planning_final):
        colonne_agenda.controls.clear()
        colonne_ecole.controls.clear()

        # En-tête avec réglage des heures
        colonne_agenda.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("📅 Agenda de Révision (Soirée)", size=16, weight=ft.FontWeight.BOLD, color="blue200"),
                    ft.Row([
                        ft.Text(f"Budget révision : {heures_revision_var[0]}h / soir", size=13, weight=ft.FontWeight.W_500),
                    ]),
                    ft.Slider(
                        min=1.0, max=6.0, divisions=10,
                        value=heures_revision_var[0],
                        label="{value}h/soir",
                        on_change=reconstruire_planning
                    )
                ]),
                padding=10,
                bgcolor="#1E293B",
                border_radius=10
            )
        )

        if isinstance(planning_final, dict):
            for jour, crenaux in planning_final.items():
                items_jour = []
                if isinstance(crenaux, list):
                    for c in crenaux:
                        if isinstance(c, dict):
                            nom_m = c.get("matiere", "Matière")
                            coeff = c.get("coeff", 1)
                            duree = c.get("duree", "30min")
                            action = c.get("action", "")
                        else:
                            nom_m = str(c)
                            coeff = 1
                            duree = ""
                            action = "Révision"

                        couleur = obtenir_couleur_coeff(coeff)
                        subtitle_text = f"Durée : {duree} | {action}" if duree else action

                        items_jour.append(
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.TIMER, color=couleur),
                                title=ft.Text(f"{nom_m} (Coeff {coeff})", weight=ft.FontWeight.W_500),
                                subtitle=ft.Text(subtitle_text, size=12)
                            )
                        )

                colonne_agenda.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(str(jour).capitalize(), size=15, weight=ft.FontWeight.BOLD),
                                ft.Divider(height=1),
                                *items_jour
                            ]),
                            padding=10
                        )
                    )
                )

        # Emploi du Temps École
        colonne_ecole.controls.append(
            ft.Text("🏫 Emploi du Temps École", size=16, weight=ft.FontWeight.BOLD, color="blue200")
        )

        cours_par_jour = defaultdict(list)
        for event in cours_ecole:
            if isinstance(event, dict):
                j = str(event.get("day", "Lundi")).capitalize()
                m = str(event.get("subject", "Matière"))
                h_start = event.get("start", "")
                h_end = event.get("end", "")
                horaire = f" ({h_start}-{h_end})" if h_start else ""
                cours_par_jour[j].append(f"{m}{horaire}")
            elif isinstance(event, str):
                cours_par_jour["Lundi"].append(event)

        for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]:
            matieres = cours_par_jour.get(jour, [])
            items_cours = [ft.Text(f"• {m}", size=13) for m in matieres] if matieres else [ft.Text("Aucun cours", italic=True, size=12)]

            colonne_ecole.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(jour, size=14, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=1),
                            *items_cours
                        ]),
                        padding=10
                    )
                )
            )

        vue_dashboard = ft.View(
            "/dashboard",
            [
                ft.AppBar(
                    leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: aller_a(vue_scan)),
                    title=ft.Text("CyberSchedule - Tableau de Bord")
                ),
                ft.Container(
                    content=ft.Row([
                        colonne_agenda,
                        colonne_ecole
                    ], vertical_alignment=ft.CrossAxisAlignment.START),
                    padding=15
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )
        aller_a(vue_dashboard)

    # --- 2. VUE SCANNER ---
    texte_statut = ft.Text("Prêt pour l'analyse", size=14, weight=ft.FontWeight.W_500)
    cercle_chargement = ft.ProgressRing(width=50, height=50, stroke_width=4, visible=False, color="blue400")

    def quand_image_selectionnee(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            chemin_image = e.files[0].path
            cercle_chargement.visible = True
            cercle_chargement.color = "blue400"
            texte_statut.value = "🔍 Extraction OCR de l'emploi du temps..."
            page.update()

            def lancer_traitement():
                try:
                    cours_ecole, jours_ecole, matieres = scanner_emploi_du_temps(chemin_image)
                    donnees_scan_cache["cours"] = cours_ecole

                    cercle_chargement.color = "purple400"
                    texte_statut.value = "⚡ Analyse algorithmique & coefficients..."
                    page.update()
                    time.sleep(0.8)

                    cercle_chargement.color = "green400"
                    texte_statut.value = "🧠 Sauvegarde et génération..."
                    page.update()

                    # Sauvegarde locale automatique
                    sauvegarder_donnees(cours_ecole, heures_revision_var[0])

                    planning_final = calculer_planning_revision(
                        daily_hours_budget=heures_revision_var[0],
                        raw_schedule_events=cours_ecole
                    )
                    time.sleep(0.6)

                    cercle_chargement.visible = False
                    construire_dashboard(cours_ecole, planning_final)

                except Exception as err:
                    cercle_chargement.visible = False
                    texte_statut.value = f"❌ Erreur : {str(err)}"
                    page.update()

            threading.Thread(target=lancer_traitement, daemon=True).start()

    selecteur_media = ft.FilePicker(on_result=quand_image_selectionnee)
    page.overlay.append(selecteur_media)

    vue_scan = ft.View(
        "/scan",
        [
            ft.AppBar(
                leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: aller_a(vue_accueil)),
                title=ft.Text("CyberSchedule - Scanner")
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Combien d'heures peux-tu réviser par soir ?", size=15, weight=ft.FontWeight.W_500),
                    ft.Slider(
                        min=1.0, max=6.0, divisions=10,
                        value=heures_revision_var[0],
                        label="{value}h/soir",
                        on_change=lambda e: heures_revision_var.__setitem__(0, float(e.control.value))
                    ),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Scanner mon planning",
                        icon=ft.icons.CAMERA_ALT,
                        on_click=lambda _: selecteur_media.pick_files(allow_multiple=False),
                        style=ft.ButtonStyle(padding=20)
                    ),
                    ft.Container(height=30),
                    cercle_chargement,
                    ft.Container(height=10),
                    texte_statut
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )

    # --- 1. VUE ACCUEIL ---
    vue_accueil = ft.View(
        "/",
        [
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.HEXAGON_OUTLINED, size=80, color="blue400"),
                            ft.Text("CS", size=32, weight=ft.FontWeight.BOLD, color="blue400")
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=30,
                        bgcolor="#151C28",
                        border_radius=20
                    ),
                    ft.Container(height=30),
                    ft.Text("Bienvenue sur CyberSchedule", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    ft.Text("Votre assistant intelligent de gestion d'emploi du temps.", size=14, color="grey", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=40),
                    ft.ElevatedButton(
                        "Commencer",
                        icon=ft.icons.ARROW_FORWARD,
                        on_click=lambda _: aller_a(vue_scan)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )

    # --- CHARGEMENT AUTOMATIQUE AU DÉMARRAGE ---
    donnees_sauvegardees = charger_donnees()
    if donnees_sauvegardees and donnees_sauvegardees.get("cours_ecole"):
        heures_revision_var[0] = donnees_sauvegardees.get("heures_revision", 3.0)
        donnees_scan_cache["cours"] = donnees_sauvegardees.get("cours_ecole")
        
        planning_initial = calculer_planning_revision(
            daily_hours_budget=heures_revision_var[0],
            raw_schedule_events=donnees_scan_cache["cours"]
        )
        construire_dashboard(donnees_scan_cache["cours"], planning_initial)
    else:
        aller_a(vue_accueil)


if __name__ == "__main__":
    ft.app(target=main)
