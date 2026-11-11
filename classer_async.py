import asyncio
import time
from google.genai import types, errors
from classer_demande import client, MODELE, DemandeClient, MAX_ESSAIS

MAX_EN_PARALLELE = 3   # nombre de "guichets" ouverts en même temps

MESSAGES = [
    "Mon colis est arrivé avec deux semaines de retard et le carton était déchiré.",
    "Vous m'avez facturé deux fois le même abonnement ce mois-ci.",
    "Livrez-vous en Belgique ?",
    "Acceptez-vous le paiement en trois fois ?",
    "Je voudrais commander 10 cartouches d'encre référence X200.",
    "Pouvez-vous m'envoyer un devis pour 200 chaises de bureau ?",
    "Je souhaiterais postuler à votre offre d'emploi de comptable.",
    "Félicitations pour votre nouveau site, il est très réussi !",
    "Le produit ne fonctionne plus après trois jours d'utilisation.",
    "Quels sont les délais de livraison pour Marseille ?",
]


async def classer_demande_async(message: str, guichets: asyncio.Semaphore) -> DemandeClient:
    """Classe une demande, en attendant qu'un guichet soit libre. Réessaie en cas d'erreur passagère."""
    async with guichets:
        attente = 5
        for essai in range(1, MAX_ESSAIS + 1):
            try:
                reponse = await client.aio.models.generate_content(
                    model=MODELE,
                    contents=f"Analyse cette demande client :\n\n{message}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DemandeClient,
                    ),
                )
                return reponse.parsed
            except errors.APIError as e:
                erreur_passagere = e.code == 429 or e.code >= 500
                if not erreur_passagere or essai == MAX_ESSAIS:
                    raise
                print(f"      [RETRY] Erreur passagère ({e.code}), attente {attente} s")
                await asyncio.sleep(attente)
                attente *= 2


async def main():
    guichets = asyncio.Semaphore(MAX_EN_PARALLELE)
    debut = time.perf_counter()

    # Lancer toutes les demandes, et attendre qu'elles soient toutes finies
    fiches = await asyncio.gather(*(classer_demande_async(m, guichets) for m in MESSAGES))

    duree = time.perf_counter() - debut
    for message, fiche in zip(MESSAGES, fiches):
        print(f"{fiche.categorie:12} | {message}")
    print(f"\n{len(MESSAGES)} demandes traitées en {duree:.1f} s avec {MAX_EN_PARALLELE} guichet(s)")


if __name__ == "__main__":
    asyncio.run(main())