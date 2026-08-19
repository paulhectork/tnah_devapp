# pipeline de migration depuis la db Richelieu de prod vers la db de cours

--- 

## pipeline

une fois la base de données importée dans postgres, le script python:
- lit certaines tables en dataframes
- supprime ou simplifie des jointures entre tables
- supprime certaines colonnes
- retype et renomme certaines colonnes
- pour chaque manifeste IIIF, séléctionne l'URL IIIF d'une image à afficher
    pour chaque ressource

---

## usage

copier `.env.template` dans `.env` et l'éditer. avoir `postgresql` qui tourne
(testé avec postgres 16).

```bash
# importer le dump de base de données
bash restore.sh ./.env

# créer un venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# lancer la pipeline
python main.py
```

