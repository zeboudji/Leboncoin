def create_google_maps_link(destination, origin):
    base_url = "https://www.google.com/maps/dir/?api=1"
    if pd.notna(destination):
        return f"{base_url}&origin={origin.replace(' ', '+')}&destination={destination.replace(' ', '+')}"
    return None

def categoriser_vigilance(diff_prix):
    if 800 < diff_prix <= 2000:
        return 'Top affaire'
    elif 2000 < diff_prix <= 2500:
        return 'Vérification recommandée'
    else:
        return 'À vérifier!'

def convertir_generation_en_nombre(s):
    romain = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}
    s = s.lower()
    total = 0
    prev_value = 0
    for char in reversed(s):
        if char in romain:
            value = romain[char]
            if value < prev_value:
                total -= value
            else:
                total += value
                prev_value = value
        else:
            return None
    return total

