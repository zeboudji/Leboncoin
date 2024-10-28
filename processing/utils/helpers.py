# utils/helpers.py

import pandas as pd
import re

def extraire_informations_titre(titre, marque):
    if pd.isna(titre) or pd.isna(marque):
        return pd.Series({'Base_Model': '', 'Generation': None, 'Carrosserie': 'berline'})

    titre = titre.lower()
    marque = marque.lower()
    titre_sans_marque = titre.replace(marque.lower(), '').strip()
    titre_sans_marque = re.sub(r'[^\w\s]', '', titre_sans_marque)
    mots = titre_sans_marque.split()

    base_model = ''
    generation = None
    carrosserie = ''

    types_carrosserie = ['sw', 'break', 'estate', 'berline', 'coupé', 'hatchback', 'hatch', 'suv',
                         'monospace', 'cabriolet', 'roadster', 'fourgon', 'pickup', 'limousine',
                         'ludospace', 'tourer', 'touring', 'avant', 'sportback', 'fastback']

    pattern_generation = r'génération\s+(\d+|[ivx]+)\b'
    match = re.search(pattern_generation, titre_sans_marque)
    if match:
        potential_gen = match.group(1)
        if re.match(r'^\d+$', potential_gen) or re.match(r'^[ivx]+$', potential_gen):
            generation = potential_gen
    else:
        for i, mot in enumerate(mots):
            if mot == marque:
                continue
            if base_model == '':
                base_model = mot
                continue
            if generation is None and mot in ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',
                                              'xi', 'xii', 'xiii', 'xiv', 'xv',
                                              '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                generation = mot
            elif carrosserie == '' and mot in types_carrosserie:
                carrosserie = mot

    if generation:
        base_model_full = f"{base_model} {generation}"
    else:
        base_model_full = base_model

    if not carrosserie:
        carrosserie = 'berline'

    return pd.Series({'Base_Model': base_model_full.strip(), 'Generation': generation if generation else None, 'Carrosserie': carrosserie})

def convertir_generation_en_nombre(gen):
    try:
        gen = gen.lower()
        romain = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9, 'x': 10}
        if gen in romain:
            return romain[gen]
        else:
            return int(gen)
    except:
        return None

def extraire_modele_sans_generation(titre, marque):
    if pd.isna(titre) or pd.isna(marque):
        return ''
    titre = titre.lower()
    marque = marque.lower()
    titre_sans_marque = titre.replace(marque, '').strip()
    titre_sans_marque = re.sub(r'[^\w\s]', '', titre_sans_marque)
    mots = titre_sans_marque.split()
    if mots:
        return mots[0]
    else:
        return ''

def est_en_france_metropolitaine(localisation):
    if pd.isna(localisation):
        return False
    localisation = localisation.lower()
    dom_tom = [
        'guadeloupe', 'martinique', 'guyane', 'la réunion', 'mayotte',
        'saint-pierre-et-miquelon', 'saint-barthélemy', 'saint-martin',
        'wallis-et-futuna', 'polynésie française', 'nouvelle-calédonie',
        'terres australes et antarctiques françaises', 'taaf', 'clipperton'
    ]
    for region in dom_tom:
        if region in localisation:
            return False
    return True

def categoriser_vigilance(diff_prix):
    if 800 < diff_prix <= 2000:
        return 'Top affaire'
    elif 2000 < diff_prix <= 2500:
        return 'Vérification recommandée'
    else:
        return 'À vérifier!'

def create_google_maps_link(destination, origin):
    base_url = "https://www.google.com/maps/dir/?api=1"
    if pd.notna(destination):
        return f"{base_url}&origin={origin.replace(' ', '+')}&destination={destination.replace(' ', '+')}"
    return None

