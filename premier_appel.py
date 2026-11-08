import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

# 1. Récupérer la clé dans le coffre-fort .env
load_dotenv()
cle = os.getenv("GEMINI_API_KEY")
if not cle:
    print("ERREUR : clé introuvable. Vérifie le fichier .env")
    raise SystemExit(1)
print(f"Clé chargée ({len(cle)} caractères)")

client = genai.Client(api_key=cle)

# 2. Réglages
QUESTION = "Explique en 2 phrases simples ce qu'est un agent IA."
MODELES = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"]
ESSAIS_MAX = 3
ATTENTE_SECONDES = 5

# 3. Essayer chaque modèle, plusieurs fois si le serveur est surchargé
reponse = None
for modele in MODELES:
    for essai in range(1, ESSAIS_MAX + 1):
        try:
            print(f"Essai {essai}/{ESSAIS_MAX} avec {modele}...")
            reponse = client.models.generate_content(model=modele, contents=QUESTION)
            break
        except errors.ServerError as e:
            print(f"  Serveur indisponible ({e.code}), nouvel essai dans {ATTENTE_SECONDES} s")
            time.sleep(ATTENTE_SECONDES)
        except errors.ClientError as e:
            print(f"  Modèle refusé ({e.code}), on passe au suivant")
            break
    if reponse is not None:
        print(f"Réponse obtenue avec {modele}")
        break

if reponse is None:
    print("ÉCHEC : aucun modèle n'a répondu. Réessaie plus tard.")
    raise SystemExit(1)

# 4. Afficher la réponse et la consommation
print("\nRéponse :")
print(reponse.text)
usage = reponse.usage_metadata
print("\nTokens envoyés :", usage.prompt_token_count)
print("Tokens total   :", usage.total_token_count)