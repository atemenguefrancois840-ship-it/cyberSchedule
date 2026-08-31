import flet as ft
import time
import threading
from scan import scanner_emploi_du_temps
from engine import calculer_planning_revision

SVG_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="120" height="120">
  <defs>
    <linearGradient id="cyberGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00E5FF"/>
      <stop offset="100%" stop-color="#2196F3"/>
    </linearGradient>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1E222D"/>
      <stop offset="100%" stop-color="#10121A"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="100" fill="url(#bgGrad)"/>
  <polygon points="256,50 420,145 420,335 256,430 92,335 92,145" fill="none" stroke="url(#cyberGrad)" stroke-width="12" stroke-linejoin="round"/>
  <circle cx="256" cy="240" r="110" fill="none" stroke="#2A3142" stroke-width="8" stroke-dasharray="10 15"/>
  <g transform="translate(145, 140) scale(0.9)">
    <path d="M 120 40 A 70 70 0 1 0 120 180" fill="none" stroke="url(#cyberGrad)" stroke-width="26" stroke-linecap="round"/>
    <path d="M 190 50 C 140 30, 110 90, 150 110 C 190 130, 160 190, 100 170" fill="none" stroke="#FFFFFF" stroke-width="24" stroke-linecap="round"/>
  </g>
  <circle cx="256" cy="120" r="10" fill="#00E5FF"/>
  <circle cx="340" cy="270" r="8" fill="#2196F3"/>
</svg>
"""

def main(page: ft.Page):
    page.title = "CyberSchedule"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- COMPOSANTS REUTILISABLES ---
    texte_statut = ft.Text("Statut : En attente d'une image", size=13, color=ft.colors.GREY_400)
    colonne_agenda = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
    colonne_ecole = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    def obtenir_couleur_coeff(coeff):
        try:
            c = float(coeff)
            if c >= 4:
                return ft.colors.RED_400
            elif c >= 2:
                return ft.colors.ORANGE_400
            return ft.colors.GREEN_400
        except Exception:
            return ft.colors.BLUE_400

    def construire_dashboard(cours_ecole, planning_final):
        colonne_agenda.controls.clear()
        colonne_ecole.controls.clear()

        # Agenda
        colonne_agenda.controls.append(
            ft.Text("📅 Agenda de Révision (Soirée)", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400)
        )
        if isinstance(planning_final, dict):
            for jour, crenaux in planning_final.items():
                items_jour = []
                if isinstance(crenaux, list):
                    for c in crenaux:
                        nom_m = c.get("matiere", "Matière")
                        coeff = c.get("coeff", 1)
                        duree = c.get("duree", "30min")
                        action = c.get("action", "")
                        couleur = obtenir_couleur_coeff(coeff)

                        items_jour.append(
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.TIMER, color=couleur),
                                title=ft.Text(f"{nom_m} (Coeff {coeff})", weight=ft.FontWeight.BOLD, size=14),
                                subtitle=ft.Text(f"Durée : {duree} | {action}", size=12, color=ft.colors.GREY_300),
                            )
                        )
                colonne_agenda.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(str(jour).capitalize(), size=15, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_200),
                                ft.Divider(height=1),
                                *items_jour
                            ]),
                            padding=10
                        )
                    )
                )

        # Emploi du Temps École
        colonne_ecole.controls.append(
            ft.Text("🏫 Emploi du Temps École", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN_400)
        )
        if isinstance(cours_ecole, dict):
            for jour, matieres in cours_ecole.items():
                list_items = [ft.Text(f"• {m}", size=13) for m in matieres] if isinstance(matieres, list) else []
                colonne_ecole.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(jour).capitalize(), weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_200),
                            *list_items
                        ]),
                        padding=10, border=ft.border.all(1, ft.colors.WHITE10), border_radius=8
                    )
                )
        elif isinstance(cours_ecole, list):
            for c in cours_ecole:
                nom = c.get("matiere", str(c)) if isinstance(c, dict) else str(c)
                horaire = c.get("horaire", "") if isinstance(c, dict) else ""
                jour_c = c.get("jour", "") if isinstance(c, dict) else ""

                colonne_ecole.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.SCHOOL, color=ft.colors.GREY_400, size=18),
                            ft.Column([
                                ft.Text(f"{nom} ({jour_c})", weight=ft.FontWeight.BOLD, size=13),
                                ft.Text(horaire, size=11, color=ft.colors.GREY_400)
                            ])
                        ]),
                        padding=8, border=ft.border.all(1, ft.colors.WHITE10), border_radius=8
                    )
                )

        # Masquer l'écran de scan simple et afficher le dashboard
        boite_scan_simple.visible = False
        zone_dashboard.visible = True
        page.update()

    def quand_image_selectionnee(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            chemin_image = e.files[0].path
            texte_statut.value = "Statut : OCR en cours..."
            page.update()

            def lancer_traitement():
                try:
                    cours_ecole, jours_ecole, matieres = scanner_emploi_du_temps(chemin_image)
                    texte_statut.value = "Statut : Calcul du planning personnalisé..."
                    page.update()

                    coefficients_defaut = {m: 2 for m in matieres}
                    quota_soir = 3.0

                    planning_final = calculer_planning_revision(
                        cours_ecole=cours_ecole,
                        jours_ecole=jours_ecole,
                        coefficients=coefficients_defaut,
                        quota_du_soir=quota_soir
                    )

                    construire_dashboard(cours_ecole, planning_final)
                    texte_statut.value = "Statut : Traitement terminé !"
                except Exception as err:
                    texte_statut.value = f"Statut : Erreur ({str(err)})"

                page.update()

            threading.Thread(target=lancer_traitement, daemon=True).start()

    selecteur_media = ft.FilePicker(on_result=quand_image_selectionnee)
    page.overlay.append(selecteur_media)

    # --- VUE 1 : ACCUEIL + ANIMATION ---
    logo_image = ft.Image(src=SVG_LOGO, width=120, height=120, fit=ft.ImageFit.CONTAIN)
    conteneur_logo = ft.Container(
        content=logo_image, scale=ft.Scale(1.0),
        animate_scale=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    )

    animer_logo = True
    def boucle_animation():
        while animer_logo:
            try:
                conteneur_logo.scale = ft.Scale(1.1)
                page.update()
                time.sleep(1.0)
                if not animer_logo: break
                conteneur_logo.scale = ft.Scale(1.0)
                page.update()
                time.sleep(1.0)
            except Exception: break

    threading.Thread(target=boucle_animation, daemon=True).start()

    barre_chargement = ft.ProgressRing(width=30, height=30, stroke_width=3, visible=False)
    texte_chargement = ft.Text("Chargement des modules...", size=13, color=ft.colors.BLUE_200, visible=False)

    def demarrer_chargement(e):
        nonlocal animer_logo
        animer_logo = False
        bouton_demarrer.visible = False
        barre_chargement.visible = True
        texte_chargement.visible = True
        page.update()

        def simuler():
            time.sleep(1.2)
            vue_accueil.visible = False
            vue_scanner.visible = True
            page.update()

        threading.Thread(target=simuler, daemon=True).start()

    bouton_demarrer = ft.ElevatedButton(
        text="Commencer", icon=ft.icons.ARROW_FORWARD, on_click=demarrer_chargement
    )

    vue_accueil = ft.Column(
        controls=[
            conteneur_logo,
            ft.Container(height=10),
            ft.Text("Bienvenue sur CyberSchedule", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400),
            ft.Text("Votre assistant intelligent de gestion d'emploi du temps.", size=14, color=ft.colors.GREY_400),
            ft.Container(height=30),
            bouton_demarrer,
            barre_chargement,
            ft.Container(height=8),
            texte_chargement
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        visible=True
    )

    # --- VUE 2 : SCANNER & DASHBOARD ---
    def clic_bouton_scan(e):
        selecteur_media.pick_files(
            dialog_title="Choisir une image de l'emploi du temps",
            file_type=ft.FilePickerFileType.IMAGE
        )

    bouton_scan = ft.ElevatedButton(
        text="Scanner mon planning", icon=ft.icons.CAMERA_ALT, on_click=clic_bouton_scan
    )

    def retour_accueil(e):
        vue_scanner.visible = False
        zone_dashboard.visible = False
        boite_scan_simple.visible = True
        vue_accueil.visible = True
        bouton_demarrer.visible = True
        barre_chargement.visible = False
        texte_chargement.visible = False
        texte_statut.value = "Statut : En attente d'une image"
        page.update()

    boite_scan_simple = ft.Column([
        ft.Container(height=40),
        bouton_scan,
        ft.Container(height=20),
        texte_statut
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=True)

    zone_dashboard = ft.Row([colonne_agenda, colonne_ecole], expand=True, spacing=20, visible=False)

    vue_scanner = ft.Column(
        controls=[
            ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=retour_accueil),
                ft.Text("CyberSchedule - Tableau de Bord", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400)
            ], alignment=ft.MainAxisAlignment.START),
            boite_scan_simple,
            zone_dashboard
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False,
        expand=True
    )

    page.add(vue_accueil, vue_scanner)

if __name__ == "__main__":
    ft.app(target=main)
