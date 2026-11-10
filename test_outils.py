import requests

from premier_agent import statut_ticket, obtenir_meteo


# ---------- Outil ticket ----------

def test_ticket_existant():
    resultat = statut_ticket("QA-101")
    assert resultat == {"ticket": "QA-101", "statut": "En cours"}


def test_ticket_en_minuscules():
    resultat = statut_ticket("qa-102")
    assert resultat["statut"] == "Terminé"


def test_ticket_inconnu():
    resultat = statut_ticket("QA-999")
    assert "erreur" in resultat


# ---------- Outil météo ----------

def test_meteo_ville_connue():
    resultat = obtenir_meteo("Lyon")
    assert resultat["pays"] == "France"
    assert isinstance(resultat["temperature_celsius"], (int, float))


def test_meteo_ville_inconnue():
    resultat = obtenir_meteo("Zxqwville")
    assert "erreur" in resultat

    

def test_meteo_service_en_panne(monkeypatch):
    def fausse_panne(*args, **kwargs):
        raise requests.ConnectionError("API météo injoignable")

    monkeypatch.setattr(requests, "get", fausse_panne)
    resultat = obtenir_meteo("Lyon")
    assert "erreur" in resultat


def test_ticket_bloque():
    resultat = statut_ticket("QA-103")
    assert resultat["statut"] == "Bloqué"