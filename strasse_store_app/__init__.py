import os

from flask import Flask
from . import (db_config, authentication)


def make_app(default_config=None):
    # This is used to create the application and configure the factory
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=str(os.urandom(16)),
                            DATABASE=os.path.join(app.instance_path, 'strasse_store_app.sqlite'),
                            )
    if default_config is None:
        # Use the user-defined configuration instance from the main config.py file
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Use the default_config that comes with the app
        app.config.from_mapping(default_config)

    # Do a check on the existence of 'an instance' folder for the app
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Use the route and view below to ensure that the Application Factory is working
    @app.route('/application_factory')
    def application_factory():
        return 'The application factory is working'

    # This runs the db
    db_config.initialize_app(app)

    # This registers the authentication blue-prints with the app instance.
    app.register_blueprint(authentication.blue_prints)

    return app

