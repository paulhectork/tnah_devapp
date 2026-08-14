from flask import Flask

app = Flask("Ma première appli")

@app.route("/")
def index():
    return "Hello world !"

if __name__ == "__main__":
    app.run()