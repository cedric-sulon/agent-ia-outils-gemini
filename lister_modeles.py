import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Demander à Google la liste de ses modèles, et garder les "flash" (rapides et gratuits)
for modele in client.models.list():
    if "flash" in modele.name:
        print(modele.name)