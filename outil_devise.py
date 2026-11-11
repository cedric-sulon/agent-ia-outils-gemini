import requests


def convertir_devise(montant: float, de: str, vers: str) -> dict:
    """Convertit un montant d'une monnaie à une autre, au taux du jour."""
    print(f"   [OUTIL] convertir_devise appelé : {montant} {de} -> {vers}")

    try:
        reponse = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": de, "symbols": vers},
            timeout=10,
        )
        reponse.raise_for_status()
        donnees = reponse.json()
        taux = donnees["rates"][vers]
    except requests.RequestException:
        return {"erreur": "Service de change indisponible, réessayer plus tard"}

    return {"montant": montant, "de": de, "vers": vers, "taux": taux, "resultat": round(montant * taux, 2)}


if __name__ == "__main__":
    print(convertir_devise(100, "EUR", "USD"))