from premier_agent import lancer_agent


def test_question_meteo_utilise_outil_meteo():
    outils = []
    reponse = lancer_agent("Quelle température fait-il à Lyon ?", outils)
    assert outils == ["obtenir_meteo"]
    assert "Lyon" in reponse


def test_question_ticket_utilise_outil_ticket():
    outils = []
    lancer_agent("Où en est le ticket QA-101 ?", outils)
    assert outils == ["statut_ticket"]


def test_question_generale_sans_outil():
    outils = []
    reponse = lancer_agent("Quelle est la capitale de l'Italie ?", outils)
    assert outils == []
    assert "Rome" in reponse


def test_ville_inexistante_pas_de_temperature_inventee():
    outils = []
    reponse = lancer_agent("Quelle température fait-il à Zxqwville ?", outils)
    assert outils == ["obtenir_meteo"]
    assert "°C" not in reponse