import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re
from urllib.parse import quote
import os
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Vérification des arguments en ligne de commande
if len(sys.argv) != 20:
    print("Usage: python script.py <prix_min> <prix_max> <marque> <modèle> <annee_min> <annee_max> "
          "<doors> <seats> <owner_type> <mileage_min> <mileage_max> <sort_by> <order> <vehicle_type> "
          "<cv_min> <cv_max> <cv_din_min> <cv_din_max> <region_code>")
    sys.exit(1)

# Récupération des arguments
prix_min = sys.argv[1]
prix_max = sys.argv[2]
marque = sys.argv[3]
modele = sys.argv[4]
annee_min = sys.argv[5]
annee_max = sys.argv[6]
doors = sys.argv[7]
seats = sys.argv[8]
owner_type = sys.argv[9]
mileage_min = sys.argv[10]
mileage_max = sys.argv[11]
sort_by = sys.argv[12]
order = sys.argv[13]
vehicle_type = sys.argv[14]
cv_min = sys.argv[15]
cv_max = sys.argv[16]
cv_din_min = sys.argv[17]
cv_din_max = sys.argv[18]
region_code = sys.argv[19]  # Doit être au format 'r_76'

# En-têtes HTTP pour simuler un navigateur réel
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.leboncoin.fr/"
}

# Initialisation du driver Edge
options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")
options.add_argument("--incognito")
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

# Construction du dictionnaire des paramètres
params = {
    "category": "2",
    "locations": region_code,
    "u_car_brand": marque,
    "u_car_model": f"{marque}_{modele}",
    "price": f"{prix_min}-{prix_max}",
    "regdate": f"{annee_min}-{annee_max}",
    "doors": doors,
    "seats": seats,
    "mileage": f"{mileage_min}-{mileage_max}",
    "owner_type": owner_type,
    "sort": sort_by,
    "order": order,
    "vehicle_type": vehicle_type,
    "vehicle_damage": "undamaged",
    "vehicle_vsp": "avecpermis"
}

# Ajouter les CV fiscaux si fournis
if cv_min and cv_max:
    params["horsepower"] = f"{cv_min}-{cv_max}"

# Ajouter les CV DIN si fournis
if cv_din_min and cv_din_max:
    params["horse_power_din"] = f"{cv_din_min}-{cv_din_max}"

# Encoder les paramètres
encoded_params = {key: quote(str(value)) for key, value in params.items()}

# Construction de l'URL
base_url = "https://www.leboncoin.fr/recherche"
query_string = "&".join([f"{key}={value}" for key, value in encoded_params.items()])
url = f"{base_url}?{query_string}"

print("URL générée:", url)  # Pour débogage

# Simuler la navigation sur la page en utilisant Selenium
driver.get(url)

# Attendre suffisamment longtemps pour que le contenu se charge
time.sleep(2)  # Ajuster si nécessaire

# Capturer le contenu HTML de la page après le chargement
page_source = driver.page_source

# Fermer le navigateur après avoir capturé le HTML
driver.quit()

# Analyser le contenu HTML avec BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Initialiser une liste pour stocker les annonces
data = []

try:
    annonces = soup.find_all("p", {"data-qa-id": "aditem_title"})  # Récupère les titres des annonces
    if not annonces:
        print("Aucune annonce trouvée sur la page.")
    for annonce in annonces:
        try:
            titre = annonce.text
            parent = annonce.find_parent("a")
            
            # Lien
            try:
                lien = parent['href']
                if not lien.startswith("http"):
                    lien = "https://www.leboncoin.fr" + lien
            except Exception:
                lien = "Lien non disponible"
            
            # Prix
            try:
                prix = parent.find("span", {"data-qa-id": "aditem_price"}).text
                prix = int(re.sub(r'\D', '', prix))  # Nettoyer et convertir le prix en nombre
            except Exception:
                prix = None  # Utilisez None pour indiquer l'absence de prix
            
            # Localisation
            try:
                localisation = parent.find("p", {"class": "text-caption text-neutral"}).text
            except Exception:
                localisation = "Localisation non disponible"
            
            # Détails (année, kilométrage, carburant, transmission)
            try:
                details_container = parent.find("div", {"data-test-id": "ad-params-light"})
                details_text = details_container.text.strip().split('·')
                
                # Année
                annee = next((detail.strip() for detail in details_text if detail.strip().isdigit() and len(detail.strip()) == 4), None)
                annee = int(annee) if annee else None
                
                # Kilométrage
                kilometrage = next((detail.strip() for detail in details_text if "km" in detail.strip()), None)
                kilometrage = int(re.sub(r'\D', '', kilometrage)) if kilometrage else None
                
                # Carburant
                carburant_options = ["essence", "diesel", "électrique", "hybride", "gpl", "gaz naturel (cng)", "autre"]
                carburant = next((detail.strip() for detail in details_text if detail.strip().lower() in carburant_options), "Non spécifié")
                
                # Transmission
                transmission = next((detail.strip() for detail in details_text if detail.strip().lower() in ["automatique", "manuelle"]), "Non spécifié")
            
            except Exception:
                annee = None
                kilometrage = None
                carburant = "Non spécifié"
                transmission = "Non spécifié"
            
            # Ajouter les informations de l'annonce à la liste
            data.append({
                "Titre": titre,
                "Lien": lien,
                "Prix": prix,
                "Localisation": localisation,
                "Année": annee,
                "Kilométrage": kilometrage,
                "Carburant": carburant,
                "Transmission": transmission
            })
        except Exception as e:
            print(f"Erreur lors de l'extraction des données pour une annonce: {e}")
except Exception as e:
    print(f"Erreur lors de l'extraction des annonces: {e}")

# Vérifier si des données ont été extraites
if not data:
    print("Aucune donnée n'a été extraite.")
else:
    print(f"{len(data)} annonces ont été extraites.")

# Conversion des résultats en DataFrame pour l'utilisation dans Streamlit
df = pd.DataFrame(data)

# Si tu veux retourner les données sans utiliser Excel
df
