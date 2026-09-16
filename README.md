# COURS M2 TNAH: développement applicatif

On va développer graveeeeeeee ça va être superrrrrr 🪩🪩🪩

Ce cours (6 séances de 12h) introduit en développement applicatif en Python
avec Flask. 

---

## TODO

- tout relire
- compléter README: utilisation
- potentiellement rajouter des images ou des tables de résumé ?

---

## Compétences

On va apprendre à:

- créer une appli Web
- utiliser des templates pour générer dynamiquement des pages HTML
- interagir avec une base de données SQL: *read* / *create* / *update* / *delete*
- écrire des formulaires
- tester une application Web
- créer une API basique
- structurer une *codebase* en modules et travailler sur un projet Python
    "taille nature"

On verra les librairies suivantes:
- [Flask](https://flask.palletsprojects.com/en/stable/), notre framework Web
- [Jinja](https://jinja.palletsprojects.com/en/stable/) pour créer des
    templates HTML
- [SQLAlchemy](https://docs.sqlalchemy.org/) pour l'interaction Python/SQL
- [WTForms](https://wtforms.readthedocs.io/) pour créer des formulaires (et son
    plugin, Flask-WTForms)
- [Pytest](https://docs.pytest.org/en/stable/) pour écrire des tests

---

## Installation

Il faut avoir Git et Python installés sur votre machine.

```bash
# cloner le dépôt
git clone https://github.com/paulhectork/tnah_devapp.git
# se déplacer dans le dossier cloné
cd tnah_devapp
# créer un environnement virtuel
python3 -m venv .venv
# sourcer l'environnement virtuel
source .venv/bin/activate
# installer toutes les dépendances
pip install -r requirements.txt
```

---

## Utilisation

```bash
# se déplacer dans le dossier du cours
cd tnah_devapp
# sourcer l'environnement virtuel
source .venv/bin/activate
# ...
```

---

## Pour aller plus loin

- [le tutoriel de Miguel Greenberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world), beaucoup plus complet et très quali

---

## Licence

Le code et les notebooks sont distribués sous GNU GPL 3.0, les images sous
licence ouverte CC-BY 0. 
