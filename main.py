import os

from flask import Flask

app = Flask(__name__)

    @app.route('/hello')
    def hello():
        return 'sup nerd'
    return app