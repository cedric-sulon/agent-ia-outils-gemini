from google.genai import types
from classer_demande import client, MODELE, DemandeClient

# Prix officiels Gemini 3.1 Flash-Lite (Paid Tier, relevés le 11/11/2026)
PRIX_ENTREE = 0.25   # $ par million de tokens envoyés (texte)
PRIX_SORTIE = 1.50   # $ par million de tokens reçus (réflexion comprise)
DEMANDES_PAR_MOIS = 1000

message = "Bonjour, je suis Mme Dupont. Ma commande est arrivée cassée, c'est la deuxième fois ! Je veux un remboursement immédiat."

reponse = client.models.generate_content(
    model=MODELE,
    contents=f"Analyse cette demande client :\n\n{message}",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=DemandeClient,
    ),
)

# Lire la consommation renvoyée par Google
usage = reponse.usage_metadata
tokens_entree = usage.prompt_token_count or 0
tokens_sortie = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)

# Calculer le coût
cout_une_demande = tokens_entree / 1_000_000 * PRIX_ENTREE + tokens_sortie / 1_000_000 * PRIX_SORTIE
cout_par_mois = cout_une_demande * DEMANDES_PAR_MOIS

print(f"Tokens envoyés                     : {tokens_entree}")
print(f"Tokens reçus (réponse + réflexion) : {tokens_sortie}")
print(f"Coût d'une demande                 : {cout_une_demande:.6f} $")
print(f"Coût pour {DEMANDES_PAR_MOIS} demandes par mois    : {cout_par_mois:.2f} $")