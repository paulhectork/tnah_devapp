from app.app import db

class Iconography(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    iiif_manifest_url = db.Column(db.Text, nullable=False)
    iiif_image_url = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.Text)
    richelieu_url = db.Column(db.Text, nullable=False)
    date_lower = db.Column(db.Integer)    
    date_upper = db.Column(db.Integer)
    institution = db.Column(db.Integer, nullable=False)
    # NOTE: il reste à définir la relation avec la table `author`, mais on verra comment faire plus tard !
    id_author = ...
