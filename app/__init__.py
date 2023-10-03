from flask import Flask
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

from app import routes

if __name__ == '__main__':
    app.run(debug=True)
