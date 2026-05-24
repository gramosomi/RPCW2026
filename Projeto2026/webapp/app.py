from flask import Flask
from routes.main import main_bp
from routes.ontology import ontology_bp
from routes.competency import competency_bp
from routes.admin import admin_bp
from config import ONTOLOGY_NS

def local_name(value):
    if not value:
        return ""

    value = str(value)

    if "#" in value:
        return value.split("#")[-1]

    if "/" in value:
        return value.rstrip("/").split("/")[-1]

    return value

def is_internal_resource(value):
    if not value:
        return False

    return str(value).startswith(ONTOLOGY_NS)

def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    app.jinja_env.filters["local_name"] = local_name
    app.jinja_env.tests["internal_resource"] = is_internal_resource

    app.register_blueprint(main_bp)
    app.register_blueprint(ontology_bp, url_prefix="/ontology")
    app.register_blueprint(competency_bp, url_prefix="/competency")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)