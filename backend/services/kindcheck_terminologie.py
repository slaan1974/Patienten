TERMINOLOGIE = {
    "herkomst": [
        {"waarde": "thuis", "label": "Thuis"},
        {"waarde": "pleeggezin", "label": "Pleeggezin"},
        {"waarde": "instelling", "label": "Instelling"},
        {"waarde": "netwerk", "label": "Netwerk"},
        {"waarde": "anders", "label": "Anders"},
    ],
    "kleinstiefpleeg": [
        {"waarde": "klein", "label": "Klein"},
        {"waarde": "stief", "label": "Stief"},
        {"waarde": "pleeg", "label": "Pleeg"},
    ],
    "kind_soort": [
        {"waarde": "eigen", "label": "Eigen"},
        {"waarde": "stief", "label": "Stief"},
        {"waarde": "pleeg", "label": "Pleeg"},
        {"waarde": "adoptie", "label": "Adoptie"},
        {"waarde": "overig", "label": "Overig"},
    ],
    "kind_zorg": [
        {"waarde": "gedeelde_zorg", "label": "Gedeelde zorg"},
        {"waarde": "alleen_zorg", "label": "Alleen zorg"},
        {"waarde": "geen_zorg", "label": "Geen zorg"},
    ],
}


def get_terminologie() -> dict:
    return TERMINOLOGIE
