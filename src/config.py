# Dans la section target_countries, remplacez par :
target_countries: List[str] = Field(
    ["France", "Belgique", "Suisse", "Luxembourg", "Monaco", "Canada (Québec)"],
    env="TARGET_COUNTRIES"
)

# Dans la méthode get_google_dorks, modifiez les dorks :
def get_google_dorks(self) -> List[str]:
    """Génère les Google Dorks pour la recherche de prospects"""
    dorks = []
    
    # Dorks de base pour chaque pays
    country_dorks = {
        "France": [
            '"e-commerce" "témoignage" "France" -emploi -stage',
            '"boutique en ligne" "France" "croissance"',
            '"e-commerce" "France" "expert" "solution"',
            '"site e-commerce" "France" "performance"',
            '"vendre en ligne" "France" "conseil"'
        ],
        "Belgique": [
            '"e-commerce" "Belgique" "site"',
            '"boutique en ligne" "Belgique" "shop"',
            '"e-commerce" "Belgique" "expert"'
        ],
        "Suisse": [
            '"e-commerce" "Suisse" "shop"',
            '"boutique en ligne" "Suisse" "vente"',
            '"e-commerce" "Suisse" "solution"'
        ],
        "Luxembourg": [
            '"e-commerce" "Luxembourg" "business"',
            '"boutique en ligne" "Luxembourg"'
        ],
        "Monaco": [
            '"e-commerce" "Monaco" "luxe"',
            '"boutique en ligne" "Monaco"'
        ]
    }
    
    # Dorks pour le Québec
    quebec_dorks = [
        '"e-commerce" "Québec" "boutique en ligne"',
        '"vendre en ligne" "Québec" "conseil"',
        '"site e-commerce" "Québec" "expert"'
    ]
    
    # Dorks par secteur
    sector_dorks = {
        "Mode": [
            '"e-commerce mode" "boutique" "francophone"',
            '"vetements en ligne" "shop" "francophone"'
        ],
        "Électronique": [
            '"e-commerce électronique" "shop" "francophone"',
            '"high-tech en ligne" "boutique" "francophone"'
        ],
        "Services": [
            '"e-commerce services" "solution" "francophone"',
            '"services en ligne" "plateforme" "francophone"'
        ],
        "Digital": [
            '"e-commerce digital" "solution" "francophone"',
            '"digital shop" "francophone"'
        ],
        "Retail": [
            '"e-commerce retail" "shop" "francophone"',
            '"retail en ligne" "boutique" "francophone"'
        ]
    }
    
    # Combiner tous les dorks
    for country, country_dork_list in country_dorks.items():
        if country in self.target_countries:
            dorks.extend(country_dork_list)
    
    if "Canada (Québec)" in self.target_countries:
        dorks.extend(quebec_dorks)
    
    # Ajouter les dorks par secteur
    for sector in self.target_sectors:
        if sector in sector_dorks:
            dorks.extend(sector_dorks[sector])
    
    return list(set(dorks))  # Éliminer les doublons
