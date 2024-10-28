# processing/data_processing.py

from utils.helpers import (
    extraire_informations_titre,
    convertir_generation_en_nombre,
    extraire_modele_sans_generation
)
import pandas as pd

def compare_data(df_occitanie, df_france):
    df_occitanie[['Base_Model', 'Generation', 'Carrosserie']] = df_occitanie.apply(
        lambda row: extraire_informations_titre(row['Titre'], row['Marque']), axis=1)

    df_france[['Base_Model', 'Generation', 'Carrosserie']] = df_france.apply(
        lambda row: extraire_informations_titre(row['Titre'], row['Marque']), axis=1)

    df_occitanie['Modele'] = df_occitanie.apply(
        lambda row: extraire_modele_sans_generation(row['Titre'], row['Marque']), axis=1)
    df_france['Modele'] = df_france.apply(
        lambda row: extraire_modele_sans_generation(row['Titre'], row['Marque']), axis=1)

    df_occitanie['Generation_num'] = df_occitanie['Generation'].apply(convertir_generation_en_nombre)
    df_france['Generation_num'] = df_france['Generation'].apply(convertir_generation_en_nombre)

    df_france['Generation'] = df_france['Generation_num'].apply(lambda x: str(int(x)) if pd.notna(x) else None)
    df_occitanie['Generation'] = df_occitanie['Generation_num'].apply(lambda x: str(int(x)) if pd.notna(x) else None)

    columns_to_strip = ['Marque', 'Modele', 'Carburant', 'Transmission', 'Carrosserie']
    for col in columns_to_strip:
        df_france[col] = df_france[col].astype(str).str.strip().str.lower()
        df_occitanie[col] = df_occitanie[col].astype(str).str.strip().str.lower()

    keys_without_generation = ['Marque', 'Modele', 'Carburant', 'Transmission', 'Carrosserie']

    df_comparaison = pd.merge(
        df_occitanie,
        df_france,
        how='left',
        on=keys_without_generation,
        suffixes=('_occitanie', '_france')
    )

    df_comparaison['Différence_Année'] = df_comparaison['Année_occitanie'] - df_comparaison['Année_france']
    df_comparaison['Différence_Prix (€)'] = df_comparaison['Prix_occitanie'] - df_comparaison['Prix_france']
    df_comparaison['Différence_Kilométrage (km)'] = df_comparaison['Kilométrage_occitanie'] - df_comparaison['Kilométrage_france']

    return df_comparaison
