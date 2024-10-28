import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
import os
from urllib.parse import quote

def scrape_occitanie(prix_min, prix_max, marque, modele, annee_min, annee_max, doors, seats,
                    owner_type, mileage_min, mileage_max, sort_by, order, vehicle_type,
                    cv_min, cv_max, cv_din_min, cv_din_max, region_code):

    # Initialisation du driver Edge
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")  # Exécuter en mode headless pour le serveur
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")

    driver = webdriver.Edge(options=options)

    # Construction de l'URL (similaire à votre script)
    # ...

    driver.get(url)
    time.sleep(2)

    # Extraction des données
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = []
    annonces = soup.find_all("p", {"data-qa-id": "aditem_title"})

    for annonce in annonces:
        try:
            titre = annonce.text
            parent = annonce.find_parent("a")
            lien = parent['href']
            if not lien.startswith("http"):
                lien = "https://www.leboncoin.fr" + lien

            prix = parent.find("span", {"data-qa-id": "aditem_price"}).text
            prix = int(re.sub(r'\D', '', prix))

            localisation = parent.find("p", {"class": "text-caption text-neutral"}).text

            details_container = parent.find("div", {"data-test-id": "ad-params-light"})
            details_text = details_container.text.strip().split('·')

            annee = next((detail.strip() for detail in details_text if detail.strip().isdigit() and len(detail.strip()) == 4), None)
            annee = int(re.sub(r'\D', '', annee)) if annee else None

            kilometrage = next((detail.strip() for detail in details_text if "km" in detail.strip()), None)
            kilometrage = int(re.sub(r'\D', '', kilometrage)) if kilometrage else None

            carburant = next((detail.strip() for detail in details_text if detail.strip().lower() in ["essence", "diesel", "électrique", "hybride"]), None)
            transmission = next((detail.strip() for detail in details_text if detail.strip().lower() in ["automatique", "manuelle"]), None)

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

    driver.quit()

    # Exporter les données
    df = pd.DataFrame(data)
    output_file = "resultats_occitanie.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Les données ont été exportées dans '{output_file}'.")

    return df

# Si exécuté en tant que script
if __name__ == "__main__":
    # Récupérer les arguments
    if len(sys.argv) != 20:
        print("Usage: python leboncoinocc.py <args>")
        sys.exit(1)
    # Appeler la fonction avec les arguments
    df = scrape_occitanie(*sys.argv[1:])

