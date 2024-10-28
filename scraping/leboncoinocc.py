# scraping/leboncoinocc.py

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import quote

def scrape_occitanie(prix_min, prix_max, marques, modeles, annee_min, annee_max, doors, seats,
                    owner_type, mileage_min, mileage_max, sort_by, order, vehicle_type,
                    cv_min, cv_max, cv_din_min, cv_din_max, region_code):
    # Initialisation du driver Edge en mode headless
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    
    driver = webdriver.Edge(options=options)
    
    data = []
    
    # Générer les paires marque-modèle
    marque_modele_paires = []
    for marque in marques:
        # Récupérer les modèles correspondant à la marque sélectionnée
        modeles_associes = [modele for modele in modeles if modele in get_marques_modeles()[marque]]
        # Ajouter chaque paire marque-modèle à une liste
        for modele in modeles_associes:
            marque_modele_paires.append((marque, modele))
    
    for marque, modele in marque_modele_paires:
        modele_str = modele.replace(" ", "%20")  # Encodage des espaces
        
        # Construction des paramètres
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
            "vehicle_vsp": "avecpermis"
        }
        
        if cv_min and cv_max:
            params["horsepower"] = f"{cv_min}-{cv_max}"
        
        if cv_din_min and cv_din_max:
            params["horse_power_din"] = f"{cv_din_min}-{cv_din_max}"
        
        # Encodage des paramètres
        encoded_params = {key: quote(str(value)) for key, value in params.items()}
        query_string = "&".join([f"{key}={value}" for key, value in encoded_params.items()])
        base_url = "https://www.leboncoin.fr/recherche"
        url = f"{base_url}?{query_string}"
        
        print(f"Scraping Occitanie - Marque: {marque}, Modèle: {modele}")
        print(f"URL: {url}")  # Pour débogage
        
        driver.get(url)
        time.sleep(2)  # Attendre le chargement de la page
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        annonces = soup.find_all("p", {"data-qa-id": "aditem_title"})
        if not annonces:
            print(f"Aucune annonce trouvée pour {marque} {modele}.")
            continue
        
        for annonce in annonces:
            try:
                titre = annonce.text
                parent = annonce.find_parent("a")
                
                # Lien
                try:
                    lien = parent['href']
                    if not lien.startswith("http"):
                        lien = "https://www.leboncoin.fr" + lien
                except:
                    lien = "Lien non disponible"
                
                # Prix
                try:
                    prix = parent.find("span", {"data-qa-id": "aditem_price"}).text
                    prix = int(re.sub(r'\D', '', prix))
                except:
                    prix = None
                
                # Localisation
                try:
                    localisation = parent.find("p", {"class": "text-caption text-neutral"}).text
                except:
                    localisation = "Localisation non disponible"
                
                # Détails (année, kilométrage, carburant, transmission)
                try:
                    details_container = parent.find("div", {"data-test-id": "ad-params-light"})
                    details_text = details_container.text.strip().split('·')
                    
                    # Année
                    annee = next((detail.strip() for detail in details_text if detail.strip().isdigit() and len(detail.strip()) == 4), None)
                    annee = int(re.sub(r'\D', '', annee)) if annee else None
                    
                    # Kilométrage
                    kilometrage = next((detail.strip() for detail in details_text if "km" in detail.strip()), None)
                    kilometrage = int(re.sub(r'\D', '', kilometrage)) if kilometrage else None
                    
                    # Carburant
                    carburant = next((detail.strip() for detail in details_text if detail.strip().lower() in ["essence", "diesel", "électrique", "hybride"]), None)
                    
                    # Transmission
                    transmission = next((detail.strip() for detail in details_text if detail.strip().lower() in ["automatique", "manuelle"]), None)
                
                except:
                    annee = None
                    kilometrage = None
                    carburant = "Carburant non disponible"
                    transmission = "Transmission non disponible"
                
                data.append({
                    "Marque": marque,
                    "Modèle": modele,
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
    
    # Fermer le navigateur
    driver.quit()
    
    # Exporter les données dans un DataFrame
    df = pd.DataFrame(data)
    output_file = "resultats_occitanie.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Les données ont été exportées dans '{output_file}'.")
    
    return df

def get_marques_modeles():
    # Dictionnaire des marques et des modèles disponibles
    marques_modeles = {
        "BMW": ["Série 1", "Série 2", "Série 3", "Série 4", "Série 5", "X1", "X3", "X5", "X6"],
        "AUDI": ["A1", "A3", "A4", "A6", "Q3", "Q5", "Q7", "Q8"],
        "MERCEDES-BENZ": ["Classe A", "Classe B", "Classe C", "Classe E", "GLE", "GLA", "GLC", "CLS"],
        "RENAULT": ["Clio", "Megane", "Espace", "Kadjar", "Captur", "Twingo", "Scénic", "Koleos", "Zoe"],
        "PEUGEOT": ["208", "2008", "308", "3008", "508", "5008", "Rifter"],
        "VOLKSWAGEN": ["Golf", "Polo", "Tiguan", "Passat", "T-Cross", "T-Roc", "Touareg"],
        "TOYOTA": ["Yaris", "Corolla", "RAV4", "C-HR", "Auris", "Camry", "Land Cruiser"],
        "FORD": ["Fiesta", "Focus", "Mondeo", "Kuga", "Puma", "Mustang", "Edge"],
        "NISSAN": ["Micra", "Juke", "Qashqai", "X-Trail", "Leaf", "Navara"],
        "HYUNDAI": ["i10", "i20", "i30", "Tucson", "Kona", "Santa Fe", "Ioniq"],
        "KIA": ["Picanto", "Rio", "Ceed", "Sportage", "Sorento", "Stinger"],
        "HONDA": ["Civic", "Jazz", "CR-V", "HR-V", "Accord"],
        "VOLVO": ["XC40", "XC60", "XC90", "S60", "S90", "V40", "V60"],
        "FIAT": ["500", "Panda", "Tipo", "500X", "500L"],
        "CITROEN": ["C1", "C3", "C4", "C5 Aircross", "Berlingo"],
        "OPEL": ["Corsa", "Astra", "Insignia", "Crossland", "Grandland"],
        "SEAT": ["Ibiza", "Leon", "Arona", "Ateca", "Tarraco"],
        "SKODA": ["Fabia", "Octavia", "Karoq", "Kodiaq", "Superb"],
        "TESLA": ["Model 3", "Model S", "Model X", "Model Y"],
        "JEEP": ["Renegade", "Compass", "Cherokee", "Wrangler", "Grand Cherokee"],
        "LAND ROVER": ["Range Rover", "Evoque", "Discovery", "Defender"]
    }
    return marques_modeles
