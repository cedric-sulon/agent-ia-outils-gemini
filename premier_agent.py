import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Délai max : si Google ne répond pas en 60 s, on arrête avec une erreur claire
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=60_000),
)
MODELE = "gemini-3.5-flash"


# ---------- LES OUTILS ----------

def obtenir_meteo(ville: str) -> dict:
    """Donne la température actuelle d'une ville."""
    print(f"   [OUTIL] obtenir_meteo appelé avec ville={ville}")
    fausses_donnees = {"paris": 12, "lyon": 9, "marseille": 17}
    temperature = fausses_donnees.get(ville.lower())
    if temperature is None:
        return {"erreur": f"Ville inconnue : {ville}"}
    return {"ville": ville, "temperature_celsius": temperature}


def statut_ticket(numero: str) -> dict:
    """Donne le statut d'un ticket Jira à partir de son numéro."""
    print(f"   [OUTIL] statut_ticket appelé avec numero={numero}")
    faux_tickets = {"QA-101": "En cours", "QA-102": "Terminé"}
    statut = faux_tickets.get(numero.upper())
    if statut is None:
        return {"erreur": f"Ticket introuvable : {numero}"}
    return {"ticket": numero, "statut": statut}


OUTILS = {"obtenir_meteo": obtenir_meteo, "statut_ticket": statut_ticket}

# On donne les outils à l'IA, mais c'est NOUS qui les exécutons (mode manuel)
config = types.GenerateContentConfig(
    tools=[obtenir_meteo, statut_ticket],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


# ---------- L'AGENT ----------

questions = [
    "Quelle température fait-il à Lyon ?",
    "Où en est le ticket QA-101 ?",
    "Quelle est la capitale de l'Italie ?",
]

for question in questions:
    print(f"\nQUESTION : {question}")
    historique = [types.Content(role="user", parts=[types.Part(text=question)])]

    # Aller-retour 1 : l'IA lit la question et décide
    print("   [IA] je réfléchis...")
    rep1 = client.models.generate_content(model=MODELE, contents=historique, config=config)

    if not rep1.function_calls:
        print(f"RÉPONSE  : {rep1.text}")
        continue

    # L'IA a demandé un outil : on l'exécute
    historique.append(rep1.candidates[0].content)
    resultats = []
    for appel in rep1.function_calls:
        resultat = OUTILS[appel.name](**appel.args)
        print(f"   [OUTIL] résultat : {resultat}")
        resultats.append(types.Part.from_function_response(name=appel.name, response=resultat))
    historique.append(types.Content(role="user", parts=resultats))

    # Aller-retour 2 : l'IA lit le résultat et rédige la réponse
    print("   [IA] je rédige la réponse...")
    rep2 = client.models.generate_content(model=MODELE, contents=historique, config=config)
    print(f"RÉPONSE  : {rep2.text}")