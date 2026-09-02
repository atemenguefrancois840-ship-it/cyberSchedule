import requests

def scanner_emploi_du_temps(chemin_image):
    url = "https://groggy-darwinism-gluten.ngrok-free.dev/scan-schedule"
    files = {'file': open(chemin_image, 'rb')}
    
    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            resultat = response.json()
            return resultat["cours_par_jour"]
        else:
            print(f"Erreur API ({response.status_code}): {response.text}")
            return {}
    except Exception as e:
        print(f"Impossible de contacter l'API Titan OCR : {e}")
        return {}
