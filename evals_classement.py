import time
from classer_demande import classer_demande

# Jeu de recette : (message fictif, catégorie attendue)
CAS = [
    # Réclamations
    ("Mon colis est arrivé avec deux semaines de retard et le carton était déchiré.", "reclamation"),
    ("Vous m'avez facturé deux fois le même abonnement ce mois-ci, je veux être remboursé.", "reclamation"),
    ("Le produit ne fonctionne plus après trois jours d'utilisation. C'est inadmissible.", "reclamation"),
    ("Votre livreur a laissé mon colis devant la porte sous la pluie, tout est mouillé.", "reclamation"),
    ("Je n'ai toujours pas reçu le remboursement promis il y a un mois.", "reclamation"),
    # Demandes d'information
    ("Livrez-vous en Belgique ?", "information"),
    ("Quels sont les délais de livraison pour Marseille ?", "information"),
    ("Est-ce que ce modèle existe en noir ?", "information"),
    ("Comment puis-je modifier mon mot de passe sur votre site ?", "information"),
    ("Acceptez-vous le paiement en trois fois ?", "information"),
    # Commandes
    ("Je voudrais commander 10 cartouches d'encre référence X200.", "commande"),
    ("Pouvez-vous m'envoyer un devis pour 200 chaises de bureau ?", "commande"),
    ("Je souhaite ajouter un deuxième article à ma commande de ce matin.", "commande"),
    ("Merci de me réserver 3 places pour la formation du 15 décembre.", "commande"),
    ("Je souhaite renouveler mon abonnement annuel.", "commande"),
    # Autres (hors périmètre)
    ("Bonjour, je suis commercial dans une agence de publicité et je voudrais vous présenter nos services.", "autre"),
    ("Félicitations pour votre nouveau site, il est très réussi !", "autre"),
    ("Je souhaiterais postuler à votre offre d'emploi de comptable.", "autre"),
    ("Ceci est un message de test, merci de l'ignorer.", "autre"),
    ("Pouvez-vous transmettre mes amitiés à Julie du service client ?", "autre"),
]

reussites = 0
echecs = []

for numero, (message, attendu) in enumerate(CAS, start=1):
    try:
        obtenu = classer_demande(message).categorie
    except Exception as erreur:
        obtenu = f"ERREUR ({type(erreur).__name__})"

    if obtenu == attendu:
        reussites += 1
        statut = "PASS"
    else:
        statut = "FAIL"
        echecs.append((numero, message, attendu, obtenu))

    print(f"{numero:2d}. {statut} | attendu = {attendu:12} | obtenu = {obtenu}")
    time.sleep(4)  # pause pour respecter le quota gratuit

taux = reussites / len(CAS) * 100
print(f"\nTAUX DE RÉUSSITE : {reussites}/{len(CAS)} = {taux:.0f} %")

if echecs:
    print("\nDÉTAIL DES ÉCHECS :")
    for numero, message, attendu, obtenu in echecs:
        print(f"  {numero}. « {message} »")
        print(f"     attendu : {attendu} | obtenu : {obtenu}")