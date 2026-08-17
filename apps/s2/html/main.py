from flask import Flask

app = Flask("templates HTML")

@app.route("/")
def index():
    app_name = "Catalogue Richelieu"
    html = f"""
        <html>
            <head>
                <title>{app_name}</title>
            </head>
            <body>
                <h1>Bienvenue sur le {app_name} !</h1>
            </body>
        </html>
    """
    return html

if __name__ == "__main__":
    app.run(debug=True)