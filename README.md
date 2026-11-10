# Agent IA à outils — Python + Gemini

Agent IA qui comprend une question en langage naturel, **choisit lui-même** les outils à utiliser (API météo réelle, statut de tickets), les exécute, puis rédige une réponse fondée uniquement sur les résultats obtenus.

## Ce que démontre ce projet

- **Tool calling en mode manuel** : le LLM décide, le code Python exécute. Aucune action n'échappe au contrôle du programme.
- **Boucle d'agent multi-tours** avec appels d'outils parallèles et limite de sécurité (5 tours).
- **Intégration d'une API REST réelle** : Open-Meteo (géocodage + météo actuelle).
- **Robustesse** : timeout, retry avec attente croissante sur les erreurs 429 et 5xx, erreurs d'outils renvoyées proprement à l'IA.
- **Anti-hallucination** : l'agent ne donne aucune température quand la ville est introuvable.
- **Tests automatisés (pytest)** : 7 tests d'outils, dont une panne d'API simulée par mock, et 4 tests de comportement de l'agent.
- **Gestion des secrets** : clé API dans `.env`, jamais versionnée.

## Fonctionnement

```
Question → LLM (Gemini) → demande d'outil(s) → le code exécute l'outil
        → résultat renvoyé au LLM → ... → réponse finale
```

## Installation (Windows)

```
git clone <url-du-depot>
cd <nom-du-depot>
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copier `.env.example` en `.env`, puis y mettre une clé API Gemini (Google AI Studio).

## Utilisation

```
python premier_agent.py
```

## Tests

```
python -m pytest test_outils.py -v    # rapides, sans appel à l'IA
python -m pytest test_agent.py -v     # appellent Gemini, consomment du quota
```

## Structure

| Fichier | Rôle |
| --- | --- |
| `premier_agent.py` | L'agent : outils, appel protégé à l'IA, boucle d'agent |
| `test_outils.py` | Tests des outils (cas passants, négatifs, panne simulée) |
| `test_agent.py` | Tests du choix des outils et de l'absence d'hallucination |
| `premier_appel.py` | Premier appel LLM avec retry et modèles de secours |
| `lister_modeles.py` | Liste les modèles Gemini disponibles |

## Limites connues

- L'outil tickets utilise des données simulées (pas de vrai Jira).
- Les tests d'agent ne sont pas déterministes : la prochaine étape est une évaluation répétée avec taux de réussite.
- Le quota gratuit de Gemini limite le nombre d'appels.
- Pas encore d'interface utilisateur.

## Auteur

Cédric Sulon — consultant QA en évolution vers l'ingénierie IA agentique.