# app.py

import streamlit as st
import pandas as pd
from leboncoinocc import scrape_leboncoin_occ
from leboncoinfra import scrape_leboncoin_fra
from comparaison import comparer_annonces

# Configuration de la page
st.set_page_config(
    page_title="Comparateur de Véhicules d'Occasion",
    page_icon="🚗",
    layout="wide"
)

# Titre de l'application
st.title("Comparateur de Véhicules d'Occasion 🚗")

# Description
st.markdown("""
Bienvenue dans le **Comparateur de Véhicules d'Occasion**.  
Ce tool vous permet de comparer les prix des véhicules d'occasion entre différentes régions de France.
""")

# Collecte des critères de recherche
st.header("Critères de Recherche")

with st.form("recherche_form"):
    # Prix
    prix_min = st.number_input("Prix Minimum (€)", min_value=0, value=2000, step=100)
    prix_max = st.number_input("Prix Maximum (€)", min_value=0, value=50000, step=100)
    
    # Années
    annee_min = st.slider("Année Minimum", min_value=1990, max_value=2023, value=2010, step=1)
    annee_max = st.slider("Année Maximum", min_value=1990, max_value=2023, value=2023, step=1)
    
    # Kilométrage
    mileage_min = st.number_input("Kilométrage Minimum (km)", min_value=0, value=0, step=1000)
    mileage_max = st.number_input("Kilométrage Maximum (km)", min_value=0, value=500000, step=1000)
    
    # Marques et Modèles
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
    
    marque = st.selectbox("Marque", list(marques_modeles.keys()))
    modele = st.selectbox("Modèle", marques_modeles[marque])
    
    # Options Avancées
    st.subheader("Options Avancées")
    
    # Chevaux Fiscaux (CV)
    cv_min = st.number_input("Chevaux Fiscaux (CV) Minimum", min_value=0, value=5, step=1)
    cv_max = st.number_input("Chevaux Fiscaux (CV) Maximum", min_value=0, value=5, step=1)
    
    # Puissance DIN (CV)
    cv_din_min = st.number_input("Puissance DIN (CV) Minimum", min_value=0, value=0, step=1)
    cv_din_max = st.number_input("Puissance DIN (CV) Maximum", min_value=0, value=0, step=1)
    
    # Portes et Sièges
    doors = st.number_input("Nombre de Portes", min_value=0, value=5, step=1)
    seats = st.number_input("Nombre de Sièges", min_value=0, value=5, step=1)
    
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
    selected_carburants = st.multiselect("Type de Carburant", list(carburants.keys()), default=["Essence"])
    
    # Type de véhicule
    types_vehicule = ["4x4", "berline", "break", "cabriolet", "citadine", "coupé", "monospace"]
    selected_vehicle_types = st.multiselect("Type de Véhicule", types_vehicule, default=types_vehicule)
    
    # Propriétaire
    st.subheader("Propriétaire")
    owner_private = st.checkbox("Particulier", value=True)
    owner_pro = st.checkbox("Professionnel", value=True)
    
    # Tri
    st.subheader("Tri")
    sort_by = st.radio("Trier par", ("Prix", "Kilométrage"), index=0)
    order = st.radio("Ordre", ("Ascendant", "Descendant"), index=0)
    
    # Région et Recherche
    st.subheader("Région & Recherche")
    region_list = [
        "Auvergne-Rhône-Alpes",
        "Bourgogne-Franche-Comté",
        "Bretagne",
        "Centre-Val de Loire",
        "Corse",
        "Grand Est",
        "Hauts-de-France",
        "Île-de-France",
        "Normandie",
        "Nouvelle-Aquitaine",
        "Occitanie",
        "Pays de la Loire",
        "Provence-Alpes-Côte d'Azur"
    ]
    
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
    
    selected_region = st.selectbox("Sélectionnez la région", region_list)
    search_area = st.radio("Zone de recherche", ("Région sélectionnée", "France", "Les deux"), index=2)
    
    # Bouton de soumission
    submit_button = st.form_submit_button("Lancer la recherche")
    
    if submit_button:
        st.info("Scrapping des annonces en cours...")
        
        # Déterminer le type de propriétaire
        if owner_private and owner_pro:
            owner_type = "all"
        elif owner_private:
            owner_type = "private"
        elif owner_pro:
            owner_type = "pro"
        else:
            owner_type = "all"
        
        # Convertir les carburants sélectionnés en index
        fuel_indexes = [carburants[carb] for carb in selected_carburants]
        fuel_params = ",".join(map(str, fuel_indexes))
        
        # Convertir les types de véhicules sélectionnés en chaîne de caractères
        vehicle_type = ",".join(selected_vehicle_types)
        
        # Récupérer le code de la région sélectionnée
        region_code = region_codes.get(selected_region, "r_36")  # Par défaut Occitanie
        
        # Scraping de la région d'origine
        df_occ = scrape_leboncoin_occ(
            prix_min, prix_max, marque, modele, annee_min, annee_max,
            doors, seats, owner_type, mileage_min, mileage_max,
            sort_by.lower(), order.lower(), vehicle_type,
            cv_min, cv_max, cv_din_min=0, cv_din_max=0, region_code=region_code
        )
        
        st.success(f"Scrapping de la région d'origine ({selected_region}) terminé. {len(df_occ)} annonces trouvées.")
        
        # Scraping des autres régions si nécessaire
        if search_area in ["France", "Les deux"]:
            df_fra = scrape_leboncoin_fra(
                prix_min, prix_max, marque, modele, annee_min, annee_max,
                doors, seats, owner_type, mileage_min, mileage_max,
                sort_by.lower(), order.lower(), vehicle_type,
                cv_min, cv_max
            )
            st.success(f"Scrapping des autres régions terminé. {len(df_fra)} annonces trouvées.")
        else:
            df_fra = pd.DataFrame()
        
        # Comparaison des annonces si les deux DataFrames ne sont pas vides
        if not df_occ.empty and not df_fra.empty:
            st.header("Filtres de Comparaison")
            with st.form("comparaison_form"):
                # Adresse de départ pour les liens Google Maps
                adresse_depart = st.text_input("Adresse de départ pour Google Maps", value="9 rue des chênes 31410 Le Fauga")
                
                # Filtres de comparaison
                ecart_annee_max = st.number_input("Écart d'années maximum", min_value=0, value=1, step=1)
                diff_prix_min = st.number_input("Différence de prix minimum (€)", min_value=0, value=1000, step=100)
                diff_kilometrage_max = st.number_input("Écart de kilométrage maximum (km)", min_value=0, value=10000, step=1000)
                
                comparer_button = st.form_submit_button("Appliquer les filtres et Comparer")
            
            if comparer_button:
                st.info("Comparaison en cours...")
                comparison_df = comparer_annonces(
                    df_occ, df_fra,
                    adresse_depart,
                    ecart_annee_max,
                    diff_prix_min,
                    diff_kilometrage_max
                )
                
                if comparison_df.empty:
                    st.warning("Aucun résultat ne correspond aux filtres appliqués.")
                else:
                    st.success("Comparaison terminée.")
                    st.write("### Résultats de la comparaison")
                    
                    # Préparer les liens pour Streamlit
                    def make_clickable(val, link=None):
                        if pd.notna(link) and link != "Lien non disponible":
                            return f'<a href="{link}" target="_blank">{val}</a>'
                        return val
                    
                    comparison_df['Localisation_occitanie'] = comparison_df.apply(
                        lambda row: make_clickable(row['Localisation_occitanie'], row['Localisation_occitanie_link']), axis=1
                    )
                    comparison_df['Localisation_france'] = comparison_df.apply(
                        lambda row: make_clickable(row['Localisation_france'], row['Localisation_france_link']), axis=1
                    )
                    comparison_df['Titre_occitanie'] = comparison_df.apply(
                        lambda row: make_clickable(row['Titre_occitanie'], row['Titre_occitanie_link']), axis=1
                    )
                    comparison_df['Titre_france'] = comparison_df.apply(
                        lambda row: make_clickable(row['Titre_france'], row['Titre_france_link']), axis=1
                    )
                    
                    # Supprimer les colonnes de liens
                    comparison_display = comparison_df.drop([
                        'Localisation_occitanie_link', 'Localisation_france_link',
                        'Titre_occitanie_link', 'Titre_france_link'
                    ], axis=1)
                    
                    # Convertir le DataFrame en HTML pour afficher les liens cliquables
                    comparison_display = comparison_display.to_html(escape=False, index=False)
                    st.markdown(comparison_display, unsafe_allow_html=True)
                    
                    # Optionnel : Permettre le téléchargement du fichier CSV
                    csv = comparison_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Télécharger les résultats",
                        data=csv,
                        file_name='comparaison_prix.csv',
                        mime='text/csv',
                    )
        else:
            st.warning("Aucune donnée disponible pour la comparaison.")
