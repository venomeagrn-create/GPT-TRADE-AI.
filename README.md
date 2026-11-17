# GPT-TRADE-AI.
## Avertissement

Ce projet est un **prototype pédagogique**. Il ne se connecte à aucun courtier et ne passe **aucun ordre réel** : l'exécution est simulée (`PaperExecutionAgent`). Les stratégies (par exemple la croisée de moyennes mobiles) ne garantissent aucun gain et peuvent perdre de l'argent. Ce n'est pas un conseil financier. Ne reliez jamais ce code à un compte réel sans avoir testé longuement et compris chaque règle.

## Lancer

```
python3 -m bot        # démo sur prix synthétiques
python3 -m unittest discover -s tests -t .   # tests
```

## Architecture

- `MarketDataAgent` : récupère les prix (source injectable).
- `SignalAgent` : produit des signaux achat / vente / attente.
- `RiskAgent` : dimensionne les ordres selon le capital et la taille maximale.
- `PaperExecutionAgent` : applique les ordres au portefeuille simulé.
- `orchestrator.run_pipeline` : enchaîne les agents.
