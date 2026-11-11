import pytest
from pydantic import ValidationError
from classer_demande import DemandeClient, classer_demande


# ---------- Tests du formulaire (sans IA, rapides) ----------

def test_fiche_valide_acceptee():
    fiche = DemandeClient(categorie="commande", urgence="basse", nom_client=None,
                          resume="Demande de devis", infos_manquantes=[])
    assert fiche.categorie == "commande"


def test_categorie_inventee_refusee():
    with pytest.raises(ValidationError):
        DemandeClient(categorie="blabla", urgence="basse", nom_client=None,
                      resume="Test", infos_manquantes=[])


def test_urgence_inventee_refusee():
    with pytest.raises(ValidationError):
        DemandeClient(categorie="autre", urgence="critique", nom_client=None,
                      resume="Test", infos_manquantes=[])


# ---------- Tests de l'IA (appellent Gemini) ----------

def test_reclamation_bien_classee():
    fiche = classer_demande("Mon colis est arrivé abîmé, je veux être remboursé.")
    assert fiche.categorie == "reclamation"


def test_question_simple_sans_info_manquante():
    fiche = classer_demande("Quels sont vos horaires d'ouverture le samedi ?")
    assert fiche.categorie == "information"
    assert fiche.infos_manquantes == []