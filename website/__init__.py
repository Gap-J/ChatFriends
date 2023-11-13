from flask import Flask
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '5f1a9e7dfe3b7e0c18dc9a6c109c4aebb1e6d316d89b4a2e8d6d0e3f721ce7d'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=14)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    return app