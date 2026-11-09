import os
import time
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=60_000),
)
MODELE = "gemini-3.1-flash-lite"
MAX_TOURS = 5    # Sécurité : nombre max d'allers-retours avec l'IA
MAX_ESSAIS = 4   # Nombre d'essais en cas d'erreur passagère (429 ou 5xx)


# ---------- LES OUTILS ----------

def obtenir_meteo(ville: str) -> dict:
    """Donne la température actuelle d'une ville, n'importe où dans le monde."""
    print(f"      [OUTIL] obtenir_meteo appelé avec ville={ville}")

    rep_geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": ville, "count": 1, "language": "fr"},
        timeout=10,
    )
    rep_geo.raise_for_status()
    villes = rep_geo.json().get("results")
    if not villes:
        return {"erreur": f"Ville introuvable : {ville}"}
    lieu = villes[0]

    rep_meteo = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lieu["latitude"],
            "longitude": lieu["longitude"],
            "current": "temperature_2m",
        },
        timeout=10,
    )
    rep_meteo.raise_for_status()
    temperature = rep_meteo.json()["current"]["temperature_2m"]

    return {"ville": lieu["name"], "pays": lieu.get("country"), "temperature_celsius": temperature}


def statut_ticket(numero: str) -> dict:
    """Donne le statut d'un ticket Jira à partir de son numéro."""
    print(f"      [OUTIL] statut_ticket appelé avec numero={numero}")
    faux_tickets = {"QA-101": "En cours", "QA-102": "Terminé"}
    statut = faux_tickets.get(numero.upper())
    if statut is None:
        return {"erreur": f"Ticket introuvable : {numero}"}
    return {"ticket": numero, "statut": statut}


OUTILS = {"obtenir_meteo": obtenir_meteo, "statut_ticket": statut_ticket}

config = types.GenerateContentConfig(
    tools=[obtenir_meteo, statut_ticket],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


# ---------- APPEL À L'IA, PROTÉGÉ CONTRE LES PANNES ----------

def appeler_ia(historique):
    """Appelle l'IA. Si Google est surchargé (5xx) ou si on va trop vite (429), réessaie en attendant de plus en plus."""
    attente = 5
    for essai in range(1, MAX_ESSAIS + 1):
        try:
            return client.models.generate_content(model=MODELE, contents=historique, config=config)
        except errors.APIError as e:
            erreur_passagere = e.code == 429 or e.code >= 500
            if not erreur_passagere or essai == MAX_ESSAIS:
                raise
            print(f"      [RETRY] Erreur passagère ({e.code}), essai {essai}/{MAX_ESSAIS}, attente {attente} s")
            time.sleep(attente)
            attente *= 2


# ---------- LA BOUCLE D'AGENT ----------

def lancer_agent(question: str, outils_appeles: list | None = None) -> str:
    """Fait travailler l'agent sur une question jusqu'à obtenir une réponse finale.
    Si une liste outils_appeles est fournie, on y note le nom de chaque outil utilisé."""
    historique = [types.Content(role="user", parts=[types.Part(text=question)])]

    for tour in range(1, MAX_TOURS + 1):
        print(f"   [IA] tour {tour} : je réfléchis...")
        rep = appeler_ia(historique)

        # Plus d'outil demandé : c'est la réponse finale
        if not rep.function_calls:
            return rep.text

        # Des outils sont demandés : on les exécute tous
        historique.append(rep.candidates[0].content)
        resultats = []
        for appel in rep.function_calls:
            if outils_appeles is not None:
                outils_appeles.append(appel.name)
            resultat = OUTILS[appel.name](**appel.args)
            print(f"      [OUTIL] résultat : {resultat}")
            resultats.append(types.Part.from_function_response(name=appel.name, response=resultat))
        historique.append(types.Content(role="user", parts=resultats))

    return "ARRÊT DE SÉCURITÉ : trop de tours, l'agent n'a pas conclu."


# ---------- LES TESTS ----------

# ---------- DÉMONSTRATION (seulement si on lance ce fichier directement) ----------

if __name__ == "__main__":
    questions = [
        "Compare la température de Paris et de Tokyo. Où fait-il le plus chaud ?",
        "Il fait plus chaud à Lyon ou à Marseille ? Et le ticket QA-102 est-il terminé ?",
        "Quelle est la capitale de l'Italie ?",
    ]

    for question in questions:
        print(f"\nQUESTION : {question}")
        try:
            reponse = lancer_agent(question)
        except errors.APIError as e:
            reponse = f"ÉCHEC : Google n'a pas pu répondre ({e.code}). Réessayer plus tard."
        print(f"RÉPONSE  : {reponse}")