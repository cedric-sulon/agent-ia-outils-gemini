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