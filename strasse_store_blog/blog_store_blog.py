from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from strasse_store_blog.database_store_blog import connect_to_store_blog_db
from strasse_store_blog.authentication_store_blog import user_login_required

blueprint_store_blog = Blueprint('blog_store_blog', __name__)

# The Homepage view
@blueprint_store_blog.route('/')
def homepage():
    connect_db = connect_to_store_blog_db()

    get_post = connect_db.execute(
        'SELECT p.id, title, body, created_at, author_id, username '
        'FROM posts_store_blog p JOIN users_store_blog u ON p.author_id = u.id '
        'ORDER BY created_at DESC').fetchall()

    return render_template('blog/homepage.html', get_post=get_post)

# The create blog view
@blueprint_store_blog.route('/create', methods=('GET', 'POST'))
@user_login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Please add a title to your blog.'

        if error is not None:
            flash(error)
        else:
            connect_db = connect_to_store_blog_db()
            connect_db.execute('INSERT INTO posts_store_blog (title, body, author_id) VALUES (?, ?, ?)',
                               (title, body, g.logged_in_user['id'])
                               )
            connect_db.commit()

            return redirect(url_for('blog_store_blog.homepage'))

    return render_template('blog/create.html')


# The Update and delete post view will be required to fetch a blog post by ID
# So, before updating, I have to get the ID of the POST
@blueprint_store_blog.route('/update', methods=('GET', 'POST'))
def get_blog_posts(id, check_author=True):
    get_post = connect_to_store_blog_db().execute(
                                    'SELECT p.id, title, body, created_at, author_id, username'
                                    ' FROM posts_store_blog p JOIN users_store_blog u'
                                    ' ON p.author_id = u.id WHERE p.id = ?', (id,)).fetchone()

    if get_post is None:
        abort(404, 'The Post id {0} does not exist.'.format(id))

    if check_author and get_post['author_id'] != g.logged_in_user['id']:
        abort(403)

    return get_post

# After, getting the ID of the POST, I have to update it.
@blueprint_store_blog.route('/<int:id>/update', methods=('GET', 'POST'))
@user_login_required
def update_blog(id):
    get_post = get_blog_posts(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            connect_db = connect_to_store_blog_db()
            connect_db.execute('UPDATE posts_store_blog SET title = ?, body = ? WHERE id = ?', (title, body, id))
            connect_db.commit()

            return redirect(url_for('blog_store_blog.homepage'))

    return render_template('blog/update.html', get_post=get_post)


@blueprint_store_blog.route('/<int:id>/delete', methods=('POST',))
@user_login_required
def delete(id):
    get_blog_posts(id)
    connect_db = connect_to_store_blog_db()
    connect_db.execute('DELETE FROM posts_store_blog WHERE id = ?', (id,))
    connect_db.commit()
    return redirect(url_for('blog_store_blog.homepage'))
