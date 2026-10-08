from flask import Flask


def create_app():
    """Application Factory pattern for Enterprise Student Record & Academic Management Platform."""
    app = Flask(__name__)

    from app.routes.api import api_bp
    from app.routes.views import views_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(views_bp, url_prefix="")

    return app
