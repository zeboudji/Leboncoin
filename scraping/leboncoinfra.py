# scraping/leboncoinfra.py

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

def scrape_france(
    prix_min, prix_max, marque, modele, annee_min, annee_max,
    doors, seats, owner_type, mileage_min, mileage_max, sort_by,
    order, vehicle_type, cv_min, cv_max
):
    # Initialisation du driver Chrome avec webdriver-manager
    options = Options()
    options.add_argument("--headless")  # Exécuter en mode headless pour le serveur
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    # Construction de l'URL
    params = {
        "category": "2",
        "u_car_brand": marque,
        "u_car_model": f"{marque}_{modele}",
        "price": f"{prix_min}-{prix_max}",
        "regdate": f"{annee_min}-{annee_max}",
        "doors": doors,
        "seats": seats,
        "mileage": f"{mileage_min}-{mileage_max}",
        "owner_type": owner_type,
        "sort": sort_by.lower(),
        "order": order.lower(),
        "vehicle_type": vehicle_type,
        "vehicle_vsp": "avecpermis"
    }

    if cv_min and cv_max:
        params["horsepower"] = f"{cv_min}-{cv_max}"

    base_url = "https://www.leboncoin.fr/recherche"
    query_string = "&".join([f"{key}={quote(str(value))}" for key, value in params.items()])
    url = f"{base_url}?{query_string}"

    driver.get(url)
    time.sleep(2)  # Attendre le chargement de la page

    # Scraping
    data = []
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    annonces = soup.find_all("p", {"data-qa-id": "aditem_title"})

    for annonce in annonces:
        try:
            titre = annonce.text.strip()
            parent = annonce.find_parent("a")
            lien = parent['href']
            if not lien.startswith("http"):
                lien = "https://www.leboncoin.fr" + lien

            prix_text = parent.find("span", {"data-qa-id": "aditem_price"}).text
            prix = int(re.sub(r'\D', '', prix_text))

            localisation = parent.find("p", {"class": "text-caption text-neutral"}).text.strip()

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
            print(f"Erreur lors de l'extraction des données : {e}")

    driver.quit()

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    # Exemple d'utilisation
    df = scrape_france(
        prix_min=5000, prix_max=15000, marque="BMW", modele="Série 1", annee_min=2010, annee_max=2020,
        doors="5", seats="5", owner_type="all", mileage_min=0, mileage_max=150000, sort_by="Prix",
        order="Ascendant", vehicle_type="berline", cv_min=0, cv_max=0
    )
    print(df)
