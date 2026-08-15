from flask import Flask

app = Flask("routes parametres")

@app.route("/")
def index():
    return "Hello world !"

@app.route("/page/<id_page>")
def chemin_page(id_page):
    return "Vous êtes sur la page " + id_page

if __name__ == "__main__":
    app.run(debug=True)