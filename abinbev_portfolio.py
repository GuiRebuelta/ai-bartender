COUNTRY_PORTFOLIOS = {
    "Argentina": ["Quilmes", "Patagonia", "Corona", "Stella Artois", "Budweiser"],
    "Belgium": ["Stella Artois", "Jupiler", "Leffe", "Hoegaarden", "Corona"],
    "Brazil": ["Brahma", "Skol", "Antarctica", "Original", "Spaten", "Budweiser", "Stella Artois", "Corona", "Beck's"],
    "Canada": ["Budweiser", "Bud Light", "Michelob Ultra", "Stella Artois", "Corona"],
    "Chile": ["Corona", "Stella Artois", "Budweiser", "Beck's"],
    "China": ["Budweiser", "Harbin", "Corona", "Hoegaarden", "Stella Artois"],
    "Colombia": ["Aguila", "Poker", "Club Colombia", "Corona", "Budweiser", "Stella Artois"],
    "Dominican Republic": ["Presidente", "Corona", "Budweiser", "Stella Artois"],
    "Ecuador": ["Pilsener", "Club Premium", "Budweiser", "Corona", "Stella Artois"],
    "Germany": ["Beck's", "Spaten", "Franziskaner", "Corona", "Stella Artois"],
    "India": ["Budweiser", "Corona", "Hoegaarden", "Stella Artois"],
    "Mexico": ["Corona", "Victoria", "Modelo Especial", "Negra Modelo", "Michelob Ultra", "Stella Artois"],
    "Paraguay": ["Pilsen", "Brahma", "Budweiser", "Corona", "Stella Artois"],
    "Peru": ["Cristal", "Pilsen Callao", "Cusqueña", "Corona", "Budweiser", "Stella Artois"],
    "South Africa": ["Castle Lager", "Castle Lite", "Carling Black Label", "Corona", "Stella Artois"],
    "South Korea": ["Cass", "Budweiser", "Hoegaarden", "Stella Artois", "Corona"],
    "United Kingdom": ["Budweiser", "Stella Artois", "Corona", "Camden Hells", "Leffe"],
    "United States": ["Budweiser", "Bud Light", "Michelob Ultra", "Busch", "Natural Light", "Stella Artois", "Corona"],
    "Uruguay": ["Pilsen", "Patricia", "Budweiser", "Corona", "Stella Artois"],
}


def get_countries() -> list[str]:
    return sorted(COUNTRY_PORTFOLIOS.keys())


def get_brands_for_country(country: str) -> list[str]:
    return COUNTRY_PORTFOLIOS.get(country, [])
