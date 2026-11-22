import json
import os
import datetime
import urllib.request

# Automatikus heti árfrissítő script (GitHub Actions futtatja)
# Lekéri a GVH Árfigyelő publikus végpontjait a SPAR, Lidl és Tesco üzletekre,
# és frissíti a data/prices.json fájlt a törzslista termékeire.

PRODUCTS = [
    {"id": "p1", "name": "Csirkemell filé (1 kg)", "category": "Hús & Felvágott", "unit": "kg", "query": "csirkemell filé", "prices": {"Lidl": 1899, "SPAR": 2190, "Tesco": 1999}, "promo": {"Lidl": True, "SPAR": False, "Tesco": True}},
    {"id": "p2", "name": "Mozzarella (125g)", "category": "Tejtermék", "unit": "db", "query": "mozzarella", "prices": {"Lidl": 349, "SPAR": 429, "Tesco": 389}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p3", "name": "Jázminrizs (1 kg)", "category": "Alapanyag", "unit": "csomag", "query": "jázminrizs", "prices": {"Lidl": 799, "SPAR": 899, "Tesco": 749}, "promo": {"Lidl": False, "SPAR": False, "Tesco": True}},
    {"id": "p4", "name": "Trappista sajt (1 kg)", "category": "Tejtermék", "unit": "kg", "query": "trappista sajt", "prices": {"Lidl": 2490, "SPAR": 2790, "Tesco": 2390}, "promo": {"Lidl": False, "SPAR": False, "Tesco": True}},
    {"id": "p5", "name": "Laktózmentes tejföl (330g)", "category": "Tejtermék", "unit": "db", "query": "laktózmentes tejföl", "prices": {"Lidl": 499, "SPAR": 549, "Tesco": 529}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p6", "name": "Laktózmentes tej 2,8% (1L)", "category": "Tejtermék", "unit": "liter", "query": "laktózmentes tej", "prices": {"Lidl": 439, "SPAR": 489, "Tesco": 459}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p7", "name": "Tojás M-es (10 db)", "category": "Tejtermék", "unit": "doboz", "query": "tojás", "prices": {"Lidl": 699, "SPAR": 799, "Tesco": 749}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p8", "name": "Tortilla lap (6 db)", "category": "Alapanyag", "unit": "csomag", "query": "tortilla", "prices": {"Lidl": 549, "SPAR": 699, "Tesco": 599}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p9", "name": "Light ketchup (450g)", "category": "Szószok", "unit": "flakon", "query": "ketchup", "prices": {"Lidl": 649, "SPAR": 799, "Tesco": 699}, "promo": {"Lidl": False, "SPAR": False, "Tesco": False}},
    {"id": "p10", "name": "Light majonéz (400g)", "category": "Szószok", "unit": "flakon", "query": "majonéz", "prices": {"Lidl": 699, "SPAR": 849, "Tesco": 729}, "promo": {"Lidl": False, "SPAR": False, "Tesco": True}},
    {"id": "p11", "name": "Csemege karaj felvágott (100g)", "category": "Hús & Felvágott", "unit": "csomag", "query": "csemege karaj", "prices": {"Lidl": 449, "SPAR": 499, "Tesco": 479}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p12", "name": "Szalámi (100g)", "category": "Hús & Felvágott", "unit": "csomag", "query": "szalámi", "prices": {"Lidl": 599, "SPAR": 689, "Tesco": 629}, "promo": {"Lidl": False, "SPAR": False, "Tesco": True}},
    {"id": "p13", "name": "Vaj (250g)", "category": "Tejtermék", "unit": "db", "query": "vaj", "prices": {"Lidl": 899, "SPAR": 1090, "Tesco": 949}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p14", "name": "Kávékapszula Dolce Gusto (16 db)", "category": "Kávé & Ital", "unit": "doboz", "query": "dolce gusto", "prices": {"Lidl": 1799, "SPAR": 1699, "Tesco": 1899}, "promo": {"Lidl": False, "SPAR": True, "Tesco": False}},
    {"id": "p15", "name": "Banán (1 kg)", "category": "Zöldség & Gyümölcs", "unit": "kg", "query": "banán", "prices": {"Lidl": 449, "SPAR": 529, "Tesco": 479}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p16", "name": "Alma (1 kg)", "category": "Zöldség & Gyümölcs", "unit": "kg", "query": "alma", "prices": {"Lidl": 399, "SPAR": 449, "Tesco": 379}, "promo": {"Lidl": False, "SPAR": False, "Tesco": True}},
    {"id": "p17", "name": "Fagyasztott zöldségkeverék (450g)", "category": "Fagyasztott", "unit": "csomag", "query": "fagyasztott zöldség", "prices": {"Lidl": 429, "SPAR": 549, "Tesco": 469}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p18", "name": "Leveszöldség csomag (500g)", "category": "Zöldség & Gyümölcs", "unit": "csomag", "query": "leveszöldség", "prices": {"Lidl": 499, "SPAR": 579, "Tesco": 529}, "promo": {"Lidl": False, "SPAR": False, "Tesco": False}},
    {"id": "p19", "name": "Paradicsom (1 kg)", "category": "Zöldség & Gyümölcs", "unit": "kg", "query": "paradicsom", "prices": {"Lidl": 699, "SPAR": 849, "Tesco": 749}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p20", "name": "TV Paprika (1 kg)", "category": "Zöldség & Gyümölcs", "unit": "kg", "query": "paprika", "prices": {"Lidl": 799, "SPAR": 899, "Tesco": 749}, "promo": {"Lidl": False, "SPAR": False, "Tesco": True}},
    {"id": "p21", "name": "Burgonya (1 kg)", "category": "Zöldség & Gyümölcs", "unit": "kg", "query": "burgonya", "prices": {"Lidl": 279, "SPAR": 349, "Tesco": 299}, "promo": {"Lidl": True, "SPAR": False, "Tesco": False}},
    {"id": "p22", "name": "Gourmet Savoury Cake paradicsommal", "category": "Készétel & Pékség", "unit": "db", "query": "savoury cake", "prices": {"Lidl": 649, "SPAR": 699, "Tesco": 599}, "promo": {"Lidl": False, "SPAR": False, "Tesco": True}},
    {"id": "p23", "name": "Gourmet Savoury Cake répával", "category": "Készétel & Pékség", "unit": "db", "query": "savoury cake", "prices": {"Lidl": 649, "SPAR": 699, "Tesco": 599}, "promo": {"Lidl": False, "SPAR": False, "Tesco": True}}
]

def fetch_arfigyelo_price(query):
    url = f"https://arfigyelo.gvh.hu/api/search?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            best = {}
            for item in data.get("products", []):
                for sp in item.get("prices", []):
                    chain = sp.get("chainName", "").upper()
                    price = sp.get("price")
                    if not price:
                        continue
                    for target in ["LIDL", "SPAR", "TESCO"]:
                        if target in chain:
                            key = "Lidl" if target == "LIDL" else ("SPAR" if target == "SPAR" else "Tesco")
                            if key not in best or price < best[key]:
                                best[key] = int(round(price))
            return best
    except Exception:
        return {}

def main():
    os.makedirs("data", exist_ok=True)
    for prod in PRODUCTS:
        live_prices = fetch_arfigyelo_price(prod["query"])
        for store, val in live_prices.items():
            if val > 50:
                prod["prices"][store] = val

    output = {
        "updatedAt": datetime.datetime.now().strftime("%Y. %m. %d."),
        "products": PRODUCTS
    }
    with open("data/prices.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
