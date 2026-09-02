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

APP_NAME = "Catalogue Richelieu"
