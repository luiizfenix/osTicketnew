from .tickets import tickets_bp
from .users import users_bp
from .organizations import organizations_bp
from .departments import departments_bp
from .helptopics import helptopics_bp
from .statuses import statuses_bp
from .queues import queues_bp

def register_blueprints(app):
    app.register_blueprint(tickets_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(organizations_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(helptopics_bp)
    app.register_blueprint(statuses_bp)
    app.register_blueprint(queues_bp)