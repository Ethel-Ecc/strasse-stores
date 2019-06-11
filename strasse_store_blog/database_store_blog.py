import sqlite3
import click

from flask import current_app, g
from flask.cli import with_appcontext


# The function here connects to the DB
def connect_to_store_blog_db():

    if 'database_store_blog' not in g:
        g.database_store_blog = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.database_store_blog.row_factory = sqlite3.Row

        return g.database_store_blog


# The function here closes the connection to the db
def close_connection_to_store_blog_db(e=None):
    database_store_blog = g.pop('database_store_blog', None)

    if database_store_blog is not None:
        database_store_blog.close()


# The function here initializes the db
def initialize_the_store_blog_db():

    database_store_blog = connect_to_store_blog_db()

    with current_app.open_resource('schema_store_blog.sql') as init_store_blog_db:
        database_store_blog.executescript(init_store_blog_db.read().decode('utf8'))


# The function here maps the above initialization function to a command that can be entered in the
# terminal
@click.command('initialize-store-db')
@with_appcontext
def map_store_blog_db_initialization_to_terminal():
    initialize_the_store_blog_db()
    click.echo("Initialization of strasse_store_blog DATABASE == Successful!")


# The command below registers the 'connect_to_store_blog_db' by first closing all previous connection
# and starting a new instance when the 'map_store_blog_db_initialization_to_terminal' command is called
def db_instance_registration(app):
    app.teardown_appcontext(close_connection_to_store_blog_db)
    app.cli.add_command(map_store_blog_db_initialization_to_terminal)


