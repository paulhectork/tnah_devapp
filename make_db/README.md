# pipeline de migration depuis la db Richelieu de prod vers la db de cours

--- 

## pipeline

une fois la base de données importée dans postgres, le script python:
- supprime la base sqlite préeexistante si besoin
- crée une nouvelle base sqlite dans `../richelieu.db` et définit son schema
    à partir de `../richelieu_schema.db`
- lit certaines tables de la base postgres en dataframes
- supprime ou simplifie des jointures entre tables
- pour chaque manifeste IIIF, séléctionne l'URL IIIF d'une image à afficher
    pour chaque ressource
- supprime certaines colonnes
- retype et renomme certaines colonnes
- s'assure que les contraintes de notre base de sortie sont respectées

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

