# comparaison.py

import pandas as pd
import re
import unicodedata

# Fonction pour créer un lien Google Maps
def create_google_maps_link(destination, origin):
    base_url = "https://www.google.com/maps/dir/?api=1"
    if pd.notna(destination) and pd.notna(origin):
        return f"{base_url}&origin={origin.replace(' ', '+')}&destination={destination.replace(' ', '+')}"
    return None

# Fonction pour catégoriser l'indicateur de vigilance
def categoriser_vigilance(diff_prix):
    if 800 < diff_prix <= 2000:
        return 'Top affaire'
    elif 2000 < diff_prix <= 2500:
        return 'Vérification recommandée'
    else:  # diff_prix > 2500
        return 'À vérifier!'

# Fonction pour nettoyer le nom du modèle
def clean_model_name(model_name):
    if pd.isna(model_name):
        return None
    # Supprimer les accents
    model_name_clean = ''.join(
        (c for c in unicodedata.normalize('NFD', model_name) if unicodedata.category(c) != 'Mn')
    )
    # Convertir en minuscules et supprimer les espaces inutiles
    model_name_clean = model_name_clean.lower().strip()
    # Supprimer les doubles espaces
    model_name_clean = re.sub(r'\s+', ' ', model_name_clean)
    return model_name_clean

def comparer_annonces(df_occ, df_fra, adresse_depart, ecart_annee_max, diff_prix_min, diff_kilometrage_max):
    """
    Compare les annonces entre la région d'origine (Occitanie) et d'autres régions (France).

    Parameters:
    - df_occ (pd.DataFrame): DataFrame des annonces de la région d'origine
    - df_fra (pd.DataFrame): DataFrame des annonces des autres régions
    - adresse_depart (str): Adresse de départ pour les liens Google Maps
    - ecart_annee_max (int): Écart d'années maximum autorisé
    - diff_prix_min (int): Différence de prix minimum
    - diff_kilometrage_max (int): Écart de kilométrage maximum autorisé

    Returns:
    - pd.DataFrame: DataFrame contenant les annonces filtrées et comparées
    """
    # Nettoyage des colonnes critiques pour la fusion
    columns_to_strip = ['Marque', 'Modèle', 'Carburant', 'Transmission']
    df_occ[columns_to_strip] = df_occ[columns_to_strip].apply(lambda x: x.str.strip().str.lower())
    df_fra[columns_to_strip] = df_fra[columns_to_strip].apply(lambda x: x.str.strip().str.lower())
    
    # Créer la colonne Base_Model à partir de Modèle après nettoyage
    df_occ['Base_Model'] = df_occ['Modèle'].apply(clean_model_name)
    df_fra['Base_Model'] = df_fra['Modèle'].apply(clean_model_name)
    
    # Fusionner les deux DataFrames sur Marque, Base_Model, Carburant et Transmission
    df_comparaison = pd.merge(
        df_occ,
        df_fra,
        how='left',
        on=['Marque', 'Base_Model', 'Carburant', 'Transmission'],
        suffixes=('_occitanie', '_france')
    )
    
    # Calcul des différences
    df_comparaison['Différence_Année'] = df_comparaison['Année_occitanie'] - df_comparaison['Année_france']
    df_comparaison['Différence_Prix (€)'] = df_comparaison['Prix_occitanie'] - df_comparaison['Prix_france']
    df_comparaison['Différence_Kilométrage (km)'] = df_comparaison['Kilométrage_occitanie'] - df_comparaison['Kilométrage_france']
    
    # Appliquer les filtres basés sur les valeurs entrées
    resultats_filtres = df_comparaison[
        (df_comparaison['Différence_Année'].abs() <= ecart_annee_max) &
        ((df_comparaison['Différence_Prix (€)'] >= diff_prix_min) | (df_comparaison['Différence_Prix (€)'] <= 0)) &
        (df_comparaison['Différence_Kilométrage (km)'].abs() <= diff_kilometrage_max)
    ]
    
    # Vérifier si le DataFrame n'est pas vide
    if resultats_filtres.empty:
        return resultats_filtres  # Retourner un DataFrame vide
    
    # Calcul du ROI estimé
    cout_supplementaire = 500
    resultats_filtres['ROI_estimé (€)'] = resultats_filtres['Différence_Prix (€)'] - cout_supplementaire
    
    # Ajout de l'Indicateur de Vigilance
    resultats_filtres['Indicateur de Vigilance'] = resultats_filtres['Différence_Prix (€)'].apply(categoriser_vigilance)
    
    # Trier les résultats par Indicateur de Vigilance et ROI estimé décroissant
    resultats_filtres = resultats_filtres.sort_values(by=['Indicateur de Vigilance', 'ROI_estimé (€)'], ascending=[True, False])
    
    # Ajouter les liens Google Maps pour les localisations
    resultats_filtres['Localisation_occitanie_link'] = resultats_filtres.apply(
        lambda row: create_google_maps_link(row["Localisation_occitanie"], adresse_depart) if pd.notna(row['Localisation_occitanie']) else None, axis=1
    )
    resultats_filtres['Localisation_france_link'] = resultats_filtres.apply(
        lambda row: create_google_maps_link(row["Localisation_france"], adresse_depart) if pd.notna(row['Localisation_france']) else None, axis=1
    )
    
    # Ajouter les liens des titres des véhicules
    resultats_filtres['Titre_occitanie_link'] = resultats_filtres.apply(
        lambda row: row["Lien_occitanie"] if pd.notna(row["Lien_occitanie"]) else None, axis=1
    )
    resultats_filtres['Titre_france_link'] = resultats_filtres.apply(
        lambda row: row["Lien_france"] if pd.notna(row["Lien_france"]) else None, axis=1
    )
    
    # Réorganiser les colonnes pour inclure les colonnes manquantes
    resultats_filtres = resultats_filtres[[
        'Titre_occitanie', 'Titre_france',
        'Prix_occitanie', 'Prix_france', 'Différence_Prix (€)',
        'Kilométrage_occitanie', 'Kilométrage_france', 'Indicateur de Vigilance',
        'Différence_Kilométrage (km)', 'ROI_estimé (€)',
        'Localisation_occitanie', 'Localisation_france',
        'Carburant', 'Année_occitanie', 'Année_france', 'Transmission',
        'Marque', 'Base_Model',
        'Localisation_occitanie_link', 'Localisation_france_link',
        'Titre_occitanie_link', 'Titre_france_link'
    ]]
    
    return resultats_filtres
