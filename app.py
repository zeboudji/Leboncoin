# app.py

import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import datetime

from processing.data_processing import compare_data
from processing.helpers import (
    extraire_informations_titre,
    convertir_generation_en_nombre,
    extraire_modele_sans_generation,
    est_en_france_metropolitaine,
    categoriser_vigilance,
    create_google_maps_link
)
from scraping.leboncoinocc import scrape_occitanie
from scraping.leboncoinfra import scrape_france

# Définition de marques_modeles au niveau global
marques_modeles = {
    "BMW": ["Serie1", "Serie2", "Serie3", "Serie4", "Serie5", "X1", "X3", "X5", "X6"],
    "AUDI": ["A1", "A3", "A4", "A6", "Q3", "Q5", "Q7", "Q8"],
    "MERCEDES": ["ClasseA", "ClasseB", "ClasseC", "ClasseE", "GLE", "GLA", "GLC", "CLS"],
    "RENAULT": ["Clio", "Megane", "Espace", "Kadjar", "Captur", "Twingo", "Scenic", "Koleos", "Zoe"],
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

def main():
    st.set_page_config(
        page_title="Recherche Leboncoin - Régions et France - By Youssef",
        layout="wide"
    )

    st.title("Recherche Leboncoin - Régions et France - By Youssef")

    # Barre latérale pour les critères de recherche
    st.sidebar.header("Critères de Recherche")

    # Sélection des marques et modèles
    # marques_modeles est maintenant accessible ici

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

    # ... (le reste de votre code reste inchangé)

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
    # Vous pouvez maintenant accéder à marques_modeles ici
    # ... (le reste de la fonction reste inchangé)

    # Si aucune marque ou modèle n'est sélectionné, utiliser tous
    if not selected_marques:
        selected_marques = list(marques_modeles.keys())
    if not selected_modeles:
        selected_modeles = []
        for marque in selected_marques:
            selected_modeles.extend(marques_modeles[marque])

    # ... (le reste de votre code)

if __name__ == "__main__":
    main()
