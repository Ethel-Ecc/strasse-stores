# This is the application factory for strasse_store_blog

import os
from flask import Flask
from . import (database_store_blog, authentication_store_blog)


def make_app(store_blog_configuration_test=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=str(os.urandom(16)),
                            DATABASE=os.path.join(app.instance_path, 'strasse_store_blog.sqlite3'))

    if store_blog_configuration_test is None:
        app.config.from_pyfile('configuration_store_blog.py', silent=True)
    else:
        app.config.from_mapping(store_blog_configuration_test)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # This route and function below is used to ensure the application factory is working
    @app.route('/test_strasse_store_blog')
    def test_strasse_store_blog():
        return 'This is the test page  that shows the application factory is working.'

    # This registers the 'database_store_blog' with the application
    database_store_blog.db_instance_registration(app)

    # Blueprint registrations, after imports will be registered below this line
    app.register_blueprint(authentication_store_blog.blueprint_store_blog)

    return app
