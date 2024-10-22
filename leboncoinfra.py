# leboncoinfra.py

import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_leboncoin_fra(prix_min, prix_max, marque, modele, annee_min, annee_max, doors, seats,
                        owner_type, mileage_min, mileage_max, sort_by, order, vehicle_type,
                        cv_min, cv_max):
    """
    Scrape les annonces de véhicules d'occasion sur Leboncoin pour d'autres régions.
    Retourne un DataFrame pandas contenant les annonces.
    """
    url = f"https://www.leboncoin.fr/voitures/offres/"
    params = {
        # Ajouter les paramètres nécessaires pour le scrapping
        # Exemple :
        'category': '2',
        'price_min': prix_min,
        'price_max': prix_max,
        'brand': marque,
        'model': modele,
        'year_min': annee_min,
        'year_max': annee_max,
        'doors_min': doors,
        'seats_min': seats,
        'owner_type': owner_type,
        'mileage_min': mileage_min,
        'mileage_max': mileage_max,
        'sort_by': sort_by,
        'order': order,
        'vehicle_type': vehicle_type,
        'cv_min': cv_min,
        'cv_max': cv_max
    }
    
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extraction des données des annonces
    annonces = []
    for annonce in soup.find_all("div", class_="ad"):
        try:
            marque = annonce.find("span", class_="marque").text.strip()
            modele = annonce.find("span", class_="modele").text.strip()
            prix = int(annonce.find("span", class_="prix").text.replace("€", "").replace(" ", ""))
            kilometrage = int(annonce.find("span", class_="km").text.replace(" km", "").replace(" ", ""))
            annee = int(annonce.find("span", class_="annee").text.strip())
            # Ajouter d'autres champs si nécessaire
            
            annonces.append({
                'Marque': marque,
                'Modèle': modele,
                'Prix': prix,
                'Kilométrage': kilometrage,
                'Année': annee
            })
        except Exception as e:
            # Gérer les erreurs d'extraction
            continue
    
    df = pd.DataFrame(annonces)
    return df
