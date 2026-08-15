from flask import Flask

app = Flask("routes multiples")

@app.route("/")
def index():
    return "Hello world !"

@app.route("/page/1")
def page1():
    return "Vous êtes sur la page 1"

@app.route("/page/2")
def page2():
    return "Vous êtes sur la page 2"

if __name__ == "__main__":
    app.run(debug=True)