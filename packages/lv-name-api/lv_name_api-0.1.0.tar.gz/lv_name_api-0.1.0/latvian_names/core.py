import requests
from bs4 import BeautifulSoup

BASE_URL = "https://personvardi.pmlp.gov.lv/index.php"

def search_names(*names):
    """Query the Latvian names database and return a list of results."""
    query = "+".join(names)
    response = requests.get(BASE_URL, params={"name": query})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    results = []

    if not table:
        return results

    for row in table.find_all("tr")[1:]:  # skip header
        cols = row.find_all("td")
        if not cols:
            continue

        results.append({
            "name": cols[0].get_text(strip=True),
            "count": cols[1].get_text(strip=True) if len(cols) > 1 else None,
            "nameday": cols[2].get_text(strip=True) if len(cols) > 2 else None
        })

    return results
