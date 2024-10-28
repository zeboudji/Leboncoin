# processing/data_processing.py

import pandas as pd
from utils.helpers import (
    extraire_informations_titre,
    convertir_generation_en_nombre,
    extraire_modele_sans_generation
)

def compare_data(df_occitanie, df_france):
    # Extraire les informations du titre
    df_occitanie[['Base_Model', 'Generation', 'Carrosserie']] = df_occitanie.apply(
        lambda row: extraire_informations_titre(row['Titre'], row['Marque']), axis=1)

    df_france[['Base_Model', 'Generation', 'Carrosserie']] = df_france.apply(
        lambda row: extraire_informations_titre(row['Titre'], row['Marque']), axis=1)

    # Extraire le 'Modele' sans génération
    df_occitanie['Modele'] = df_occitanie.apply(
        lambda row: extraire_modele_sans_generation(row['Titre'], row['Marque']), axis=1)
    df_france['Modele'] = df_france.apply(
        lambda row: extraire_modele_sans_generation(row['Titre'], row['Marque']), axis=1)

    # Convertir les générations en nombres
    df_occitanie['Generation_num'] = df_occitanie['Generation'].apply(convertir_generation_en_nombre)
    df_france['Generation_num'] = df_france['Generation'].apply(convertir_generation_en_nombre)

    # Mettre à jour la colonne 'Generation' avec les valeurs numériques, convertir en chaîne
    df_france['Generation'] = df_france['Generation_num'].apply(lambda x: str(int(x)) if pd.notna(x) else None)
    df_occitanie['Generation'] = df_occitanie['Generation_num'].apply(lambda x: str(int(x)) if pd.notna(x) else None)

    # Nettoyage des colonnes critiques pour la fusion
    columns_to_strip = ['Marque', 'Modele', 'Carburant', 'Transmission', 'Carrosserie']
    for col in columns_to_strip:
        df_france[col] = df_france[col].astype(str).str.strip().str.lower()
        df_occitanie[col] = df_occitanie[col].astype(str).str.strip().str.lower()

    # Clés de fusion sans la génération
    keys_without_generation = ['Marque', 'Modele', 'Carburant', 'Transmission', 'Carrosserie']

    # Fusionner les deux DataFrames sans le critère de génération
    df_comparaison = pd.merge(
        df_occitanie,
        df_france,
        how='left',
        on=keys_without_generation,
        suffixes=('_occitanie', '_france')
    )

    # Ajouter une colonne pour vérifier la différence d'années
    df_comparaison['Différence_Année'] = df_comparaison['Année_occitanie'] - df_comparaison['Année_france']

    # Ajouter une colonne pour calculer la différence de prix et de kilométrage
    df_comparaison['Différence_Prix (€)'] = df_comparaison['Prix_occitanie'] - df_comparaison['Prix_france']
    df_comparaison['Différence_Kilométrage (km)'] = df_comparaison['Kilométrage_occitanie'] - df_comparaison['Kilométrage_france']

    return df_comparaison

