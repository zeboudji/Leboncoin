# scraping/leboncoinocc.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import quote

def scrape_occitanie(
    prix_min, prix_max, marque, modele, annee_min, annee_max,
    doors, seats, owner_type, mileage_min, mileage_max, sort_by,
    order, vehicle_type, cv_min, cv_max, cv_din_min, cv_din_max, region_code
):
    params = {
        "category": "2",
        "locations": region_code,
        "brand": marque.lower(),
        "model": modele.lower(),
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
    if cv_din_min and cv_din_max:
        params["horse_power_din"] = f"{cv_din_min}-{cv_din_max}"

    base_url = "https://www.leboncoin.fr/recherche"
    query_string = "&".join([f"{key}={quote(str(value))}" for key, value in params.items() if value])
    url = f"{base_url}?{query_string}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = []
    annonces = soup.find_all("a", {"data-qa-id": "aditem_container"})

    for annonce in annonces:
        try:
            titre = annonce.find("p", {"data-qa-id": "aditem_title"}).text.strip()
            lien = annonce['href']
            if not lien.startswith("http"):
                lien = "https://www.leboncoin.fr" + lien

            prix_text = annonce.find("span", {"data-qa-id": "aditem_price"}).text
            prix = int(re.sub(r'\D', '', prix_text))

            localisation = annonce.find("p", {"data-qa-id": "aditem_location"}).text.strip()

            details_container = annonce.find("div", {"data-qa-id": "aditem_details_container"})
            details_text = details_container.text.strip().split('·') if details_container else []

            annee = next((detail.strip() for detail in details_text if detail.strip().isdigit() and len(detail.strip()) == 4), None)
            annee = int(annee) if annee else None

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

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    pass
