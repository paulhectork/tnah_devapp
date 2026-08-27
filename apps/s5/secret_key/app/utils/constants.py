from warnings import warn
from pathlib import Path

# chemin absolu vers dossier utils/
DIR_UTILS = Path(__file__).parent.resolve()

# chemin absolu vers dossier app/ (parent de utils/)
DIR_APP = DIR_UTILS.parent.resolve()

# chemin absolu vers la racine de l'application (parent de app/)
DIR_ROOT = DIR_APP.parent.resolve()

# chemin absolu vers notre dossier de templates (app/templates/)
DIR_TEMPLATES = DIR_APP / "templates" 

# chemin absolu vers notre dossier de statics (app/statics/)
DIR_STATICS = DIR_APP / "statics" 

# chemin vers la base de données sqlite (à la racine du dossier `tnah_devapp/`)
PATH_DB = DIR_ROOT.parent.parent.parent.resolve() / "richelieu.db"

# le nom de l'appli
APP_NAME = "Catalogue Richelieu"

# la clé top secrète
secret_key_default = "Une clé secrète"
SECRET_KEY = "Une clé secrète"

if SECRET_KEY == secret_key_default:
    warn(f"Changez votre clé secrète avant de passer en production ! Clé secrète actuelle: {SECRET_KEY}")
