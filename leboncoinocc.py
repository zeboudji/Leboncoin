import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import re

def scrape_leboncoin_occ(prix_min, prix_max, marque, modele, annee_min, annee_max, doors, seats, owner_type,
                         mileage_min, mileage_max, sort_by, order, vehicle_type, cv_min, cv_max, cv_din_min, cv_din_max, region_code):

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

    # Construction de l'URL
    base_url = "https://www.leboncoin.fr/recherche"
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    url = f"{base_url}?{query_string}"

    st.write("URL générée:", url)  # Pour affichage dans Streamlit

    # Récupération de la page avec requests
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)

    # Vérifier si la requête a été réussie
    if response.status_code != 200:
        st.write(f"Erreur lors de la récupération des données: {response.status_code}")
        return pd.DataFrame()

    # Analyser le contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    data = []
    annonces = soup.find_all("p", {"data-qa-id": "aditem_title"})
    
    for annonce in annonces:
        try:
            titre = annonce.text
            parent = annonce.find_parent("a")
            
            # Lien
            lien = parent['href']
            if not lien.startswith("http"):
                lien = "https://www.leboncoin.fr" + lien

            # Prix
            prix = parent.find("span", {"data-qa-id": "aditem_price"}).text
            prix = int(re.sub(r'\D', '', prix))  # Nettoyer et convertir le prix en nombre
            
            # Localisation
            localisation = parent.find("p", {"class": "text-caption text-neutral"}).text
            
            # Détails (année, kilométrage, carburant, transmission)
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
            st.write(f"Erreur lors de l'extraction des données pour une annonce: {e}")

    # Retourner les résultats sous forme de DataFrame pour Streamlit
    if not data:
        st.write("Aucune donnée n'a été extraite.")
        return pd.DataFrame()

    return pd.DataFrame(data)
