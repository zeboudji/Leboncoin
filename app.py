# app.py

import streamlit as st
import pandas as pd
import os
from scraping.leboncoinocc import scrape_occitanie
from scraping.leboncoinfra import scrape_france
from processing.data_processing import compare_data
from utils.helpers import (
    extraire_informations_titre,
    convertir_generation_en_nombre,
    extraire_modele_sans_generation,
    est_en_france_metropolitaine,
    categoriser_vigilance,
    create_google_maps_link
)
import datetime
import threading

def main():
    st.set_page_config(
        page_title="Recherche Leboncoin - Régions et France - By Youssef",
        layout="wide"
    )

    st.title("Recherche Leboncoin - Régions et France - By Youssef")

    # Barre latérale pour les critères de recherche
    st.sidebar.header("Critères de Recherche")

    # Sélection des marques et modèles
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

    # Sélection des marques
    selected_marques = st.sidebar.multiselect("Marques", list(marques_modeles.keys()))
    selected_modeles = []
    if selected_marques:
        # Récupérer les modèles correspondants aux marques sélectionnées
        for marque in selected_marques:
            selected_modeles.extend(marques_modeles[marque])
        selected_modeles = st.sidebar.multiselect("Modèles", sorted(set(selected_modeles)))
    else:
        # Si aucune marque n'est sélectionnée, afficher tous les modèles
        all_modeles = []
        for modeles in marques_modeles.values():
            all_modeles.extend(modeles)
        selected_modeles = st.sidebar.multiselect("Modèles", sorted(set(all_modeles)))

    # Prix
    prix_min = st.sidebar.number_input("Prix Min (€)", min_value=0, value=5000, step=1000)
    prix_max = st.sidebar.number_input("Prix Max (€)", min_value=0, value=15000, step=1000)

    # Année
    current_year = datetime.datetime.now().year
    annee_min = st.sidebar.number_input("Année Min", min_value=2000, max_value=current_year, value=2010, step=1)
    annee_max = st.sidebar.number_input("Année Max", min_value=2000, max_value=current_year, value=current_year, step=1)

    # Kilométrage
    mileage_min = st.sidebar.number_input("Kilométrage Min (km)", min_value=0, value=0, step=5000)
    mileage_max = st.sidebar.number_input("Kilométrage Max (km)", min_value=0, value=150000, step=5000)

    # Propriétaire
    owner_private = st.sidebar.checkbox("Particulier", value=True)
    owner_pro = st.sidebar.checkbox("Professionnel", value=True)

    # Tri
    sort_by = st.sidebar.selectbox("Trier par", ["Prix", "Kilométrage"])
    order = st.sidebar.selectbox("Ordre", ["Ascendant", "Descendant"])

    # Région
    region_codes = {
        "Auvergne-Rhône-Alpes": "r_30",
        "Bourgogne-Franche-Comté": "r_31",
        "Bretagne": "r_6",
        "Centre-Val de Loire": "r_37",
        "Corse": "r_9",
        "Grand Est": "r_33",
        "Hauts-de-France": "r_32",
        "Île-de-France": "r_12",
        "Normandie": "r_34",
        "Nouvelle-Aquitaine": "r_35",
        "Occitanie": "r_36",
        "Pays de la Loire": "r_18",
        "Provence-Alpes-Côte d'Azur": "r_21"
    }
    region_list = list(region_codes.keys())
    selected_region = st.sidebar.selectbox("Sélectionnez la région", region_list)
    region_code = region_codes[selected_region]

    # Zone de recherche
    search_area = st.sidebar.radio("Zone de recherche", ["Région sélectionnée", "France", "Les deux"])

    # Options avancées
    st.sidebar.header("Options Avancées")

    # Chevaux fiscaux
    cv_min = st.sidebar.number_input("CV Min", min_value=0, value=0, step=1)
    cv_max = st.sidebar.number_input("CV Max", min_value=0, value=0, step=1)

    # Chevaux DIN
    cv_din_min = st.sidebar.number_input("CV DIN Min", min_value=0, value=0, step=1)
    cv_din_max = st.sidebar.number_input("CV DIN Max", min_value=0, value=0, step=1)

    # Portes et sièges
    doors = st.sidebar.text_input("Nombre de portes", "5")
    seats = st.sidebar.text_input("Nombre de sièges", "5,4")

    # Carburant
    carburants = {
        "Essence": 1,
        "Diesel": 2,
        "Hybride": 3,
        "Électrique": 4,
        "GPL": 5,
        "Gaz naturel (CNG)": 6,
        "Autre": 7
    }
    selected_carburants = st.sidebar.multiselect("Carburant", list(carburants.keys()))

    # Type de véhicule
    types_vehicule = ["4x4", "berline", "break", "cabriolet", "citadine", "coupé", "monospace"]
    selected_vehicle_types = st.sidebar.multiselect("Type de véhicule", types_vehicule)

    # Bouton pour lancer la recherche
    if st.sidebar.button("Lancer la recherche"):
        # Validation des entrées
        if not owner_private and not owner_pro:
            st.error("Veuillez sélectionner au moins un type de propriétaire (Particulier ou Professionnel).")
        else:
            with st.spinner("Recherche en cours..."):
                lancer_recherche(
                    selected_marques, selected_modeles, prix_min, prix_max, annee_min, annee_max,
                    mileage_min, mileage_max, owner_private, owner_pro, sort_by, order,
                    region_code, search_area, cv_min, cv_max, cv_din_min, cv_din_max,
                    doors, seats, selected_carburants, selected_vehicle_types
                )

def lancer_recherche(
    selected_marques, selected_modeles, prix_min, prix_max, annee_min, annee_max,
    mileage_min, mileage_max, owner_private, owner_pro, sort_by, order,
    region_code, search_area, cv_min, cv_max, cv_din_min, cv_din_max,
    doors, seats, selected_carburants, selected_vehicle_types
):
    # Déterminer owner_type en fonction des cases cochées
    if owner_private and owner_pro:
        owner_type = "all"
    elif owner_private:
        owner_type = "private"
    elif owner_pro:
        owner_type = "pro"
    else:
        owner_type = "all"  # Par défaut si aucune case n'est cochée

    # Récupérer les index des carburants sélectionnés
    carburants = {
        "Essence": 1,
        "Diesel": 2,
        "Hybride": 3,
        "Électrique": 4,
        "GPL": 5,
        "Gaz naturel (CNG)": 6,
        "Autre": 7
    }
    fuel_indexes = [str(carburants[carburant]) for carburant in selected_carburants]
    fuel_params = ",".join(fuel_indexes)

    # Type de véhicule
    vehicle_type = ",".join(selected_vehicle_types) if selected_vehicle_types else ""

    # Si aucune marque ou modèle n'est sélectionné, utiliser tous
    if not selected_marques:
        selected_marques = list(marques_modeles.keys())
    if not selected_modeles:
        selected_modeles = []
        for marque in selected_marques:
            selected_modeles.extend(marques_modeles[marque])

    # Boucle pour chaque paire marque-modèle
    df_occ_total = pd.DataFrame()
    df_fra_total = pd.DataFrame()
    for marque in selected_marques:
        modeles = [modele for modele in selected_modeles if modele in marques_modeles[marque]]
        if not modeles:
            modeles = marques_modeles[marque]
        for modele in modeles:
            # Scraper la région sélectionnée
            if search_area in ["Région sélectionnée", "Les deux"]:
                df_occ = scrape_occitanie(
                    prix_min, prix_max, marque, modele, annee_min, annee_max,
                    doors, seats, owner_type, mileage_min, mileage_max, sort_by,
                    order, vehicle_type, cv_min, cv_max, cv_din_min, cv_din_max, region_code
                )
                df_occ['Marque'] = marque
                df_occ['Modèle'] = modele
                df_occ_total = pd.concat([df_occ_total, df_occ], ignore_index=True)

            # Scraper la France
            if search_area in ["France", "Les deux"]:
                df_fra = scrape_france(
                    prix_min, prix_max, marque, modele, annee_min, annee_max,
                    doors, seats, owner_type, mileage_min, mileage_max, sort_by,
                    order, vehicle_type, cv_min, cv_max
                )
                df_fra['Marque'] = marque
                df_fra['Modèle'] = modele
                df_fra_total = pd.concat([df_fra_total, df_fra], ignore_index=True)

    # Sauvegarder les résultats
    df_occ_total.to_excel("resultats_occitanie.xlsx", index=False)
    df_fra_total.to_excel("resultats_france.xlsx", index=False)

    # Comparaison des données
    df_comparaison = compare_data(df_occ_total, df_fra_total)

    st.success("Recherche terminée")

    # Afficher les résultats
    st.subheader("Résultats de la comparaison")
    st.dataframe(df_comparaison)

    # Bouton pour télécharger les résultats
    csv = df_comparaison.to_csv(index=False)
    st.download_button(
        label="Télécharger les résultats",
        data=csv,
        file_name='resultats_comparaison.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
