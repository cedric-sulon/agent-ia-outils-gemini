import os
from typing import Literal
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=60_000),
)
MODELE = "gemini-3.1-flash-lite"


# ---------- LE FORMULAIRE QUE L'IA DOIT REMPLIR ----------

class DemandeClient(BaseModel):
    categorie: Literal["reclamation", "information", "commande", "autre"]
    urgence: Literal["basse", "moyenne", "haute"]
    nom_client: str | None = Field(description="Nom du client s'il est mentionné, sinon null")
    resume: str = Field(description="Résumé de la demande en une phrase")
    infos_manquantes: list[str] = Field(
        description="Informations nécessaires pour traiter la demande, mais absentes du message"
    )


# ---------- L'APPEL À L'IA ----------

def classer_demande(message: str) -> DemandeClient:
    """Envoie une demande client à l'IA et récupère une fiche structurée et vérifiée."""
    reponse = client.models.generate_content(
        model=MODELE,
        contents=f"Analyse cette demande client :\n\n{message}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DemandeClient,
        ),
    )
    return reponse.parsed


# ---------- DÉMONSTRATION ----------

if __name__ == "__main__":
    messages = [
        "Bonjour, je suis Mme Dupont. Ma commande est arrivée cassée, c'est la deuxième fois ! Je veux un remboursement immédiat.",
        "Bonjour, quels sont vos horaires d'ouverture le samedi ?",
        "Je souhaite commander 50 unités de votre produit pour mon entreprise. Pouvez-vous me faire un devis ?",
    ]

    for message in messages:
        print(f"\nMESSAGE : {message}")
        demande = classer_demande(message)
        print(demande.model_dump_json(indent=2))