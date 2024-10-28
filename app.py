import streamlit as st
import pandas as pd
import subprocess
import os
from scraping import leboncoinocc, leboncoinfra
from processing import data_processing
from utils.helpers import create_google_maps_link, categoriser_vigilance, convertir_generation_en_nombre

# Titre de l'application
st.title("Recherche Leboncoin - Régions et France - By Youssef")

# Sidebar pour les critères de recherche
st.sidebar.header("Critères de Recherche")

# Prix
prix_min = st.sidebar.selectbox("Prix Min (€)", range(2000, 51000, 1000), index=3, key='prix_min')
prix_max = st.sidebar.selectbox("Prix Max (€)", range(2000, 51000, 1000), index=14, key='prix_max')

# Années
current_year = pd.Timestamp.now().year
annee_min = st.sidebar.selectbox("Année Min", list(range(2005, current_year + 1)), index=9, key='annee_min')
annee_max = st.sidebar.selectbox("Année Max", list(range(2005, current_year + 1)), index=current_year - 2005, key='annee_max')

# Kilométrage
mileage_min = st.sidebar.text_input("Kilométrage Min (km)", "0", key='mileage_min')
mileage_max = st.sidebar.text_input("Kilométrage Max (km)", "500000", key='mileage_max')

# Marques et Modèles
marques_modeles = leboncoinocc.get_marques_modeles()
selected_marques = st.sidebar.multiselect("Marques", list(marques_modeles.keys()))
selected_modeles = []
if selected_marques:
    modeles = [modele for marque in selected_marques for modele in marques_modeles[marque]]
    selected_modeles = st.sidebar.multiselect("Modèles", sorted(set(modeles)))

# Propriétaire
owner_private = st.sidebar.checkbox("Particulier", value=True)
owner_pro = st.sidebar.checkbox("Professionnel", value=True)

# Tri
sort_by = st.sidebar.radio("Trier par", ["Prix", "Kilométrage"])
order = st.sidebar.radio("Ordre", ["Ascendant", "Descendant"])

# Région et Recherche
st.sidebar.header("Région & Recherche")
selected_region = st.sidebar.selectbox("Sélectionnez la région", leboncoinocc.get_regions())
search_area = st.sidebar.radio("Zone de recherche", ["Région sélectionnée", "France", "Les deux"])

# Bouton de lancement
if st.sidebar.button("Lancer la recherche"):
    # Exécuter le processus de recherche
    # Cette partie nécessite l'adaptation de vos scripts de scraping pour être appelés depuis Streamlit
    # Par exemple, en utilisant subprocess ou en appelant directement les fonctions
    # Voici un exemple simplifié :
    with st.spinner("Recherche en cours..."):
        # Exécuter les scripts de scraping
        subprocess.run(['python', 'scraping/leboncoinocc.py', str(prix_min), str(prix_max), ...])
        subprocess.run(['python', 'scraping/leboncoinfra.py', str(prix_min), str(prix_max), ...])
        
        # Traitement des données
        df_occitanie = pd.read_excel("resultats_occitanie.xlsx")
        df_france = pd.read_excel("resultats_france.xlsx")
        df_comparaison = data_processing.compare_data(df_occitanie, df_france)
        
        st.success("Recherche terminée")
        st.write(df_comparaison)

        # Option pour télécharger le fichier Excel
        csv = df_comparaison.to_csv(index=False)
        st.download_button(
            label="Télécharger les résultats",
            data=csv,
            file_name='resultats_comparaison.csv',
            mime='text/csv',
        )
