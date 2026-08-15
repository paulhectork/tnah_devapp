from flask import Flask

# le code de notre calculette ---------------------------------------------------------------- 

# seu;es ces opérations sont possibles
operations_autorisees = ["addition", "soustraction", "multiplication", "division"]

# cette fonction transforme le résultat en une chaîne de caractères
def format_reponse(operation: str, resultat: float) -> str:
    return "Le résultat de votre " + operation + " est : " + str(resultat) 

# notre fonction calculatrice
def calculatrice(operation: str, x: float, y: float) -> str:
    # on vérifie que `operation` est bien une opération autorisée
    if operation not in operations_autorisees:
        return "Manant ! Cette opération est interdite : " + operation + ". Les opérations autorisées sont : " + str(operations_autorisees)
    # on calcule le résultat 
    if operation == "addition": 
        resultat = x + y
    elif operation == "soustraction": 
        resultat = x - y
    elif operation == "multiplication": 
        resultat = x * y
    elif operation == "division":
        # la division par 0 est impossible => on gère cette erreur
        if y == 0:
            return "Manant ! La division par 0 est impossible !"
        resultat = x / y
    # on retourne une chaîne de caractère qui décrive ce résultat
    return format_reponse(operation, resultat)

# le code de notre appli flask ---------------------------------------------------------------- 

# on instancie notre appli
app = Flask("routes calculatrice")

# on crée une route pour la page d'accueil
@app.route("/")
def index():
    return "Hello world !"

# on crée la route calculatrice.
# `route_calculatrice` est une route Flask qui appelle la fonction `calculatrice`, définie ci-dessus.
# la fonction `calculatrice` se charge de calculer le résultat
# ici on voit que l'anatomie de notre URL suit exactement les arguments attendus par la fonction
# quelques limitations à noter: 
#   - x et y doivent être des floats, pas des entiers ! 
#       `/addition/1/2` ne marchera pas, `/addition/1.0/1.0` si
#   - x et y doivent être des nombres positifs
@app.route("/<string:operation>/<float:x>/<float:y>")
def route_calculatrice(operation: str, x: float, y: float):
    return calculatrice(operation, x, y)

# on lance l´appli
if __name__ == "__main__":
    app.run(debug=True)