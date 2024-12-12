from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


#function used to collect user provided threat data and commitit to the database
@bp.route('/threat', methods=('GET', 'POST'))
@login_required # new
def threat():
    if request.method == 'POST':

        title = request.form['title']
        Field1 = request.form['Field1']
        Field2 = request.form['Field2']
        Field3 = request.form['Field3']
        Field4 = request.form['Field4']
        description = request.form['description']
        g.user['username']

        db = get_db()
        # Takes field data inserted into webpage and stores them into threat SQL database to be called on in view_threat_data webpage
        threat = db.execute(
            f'''INSERT INTO threat (title, username, author_user_id, Field1, Field2, Field3, Field4, description) VALUES ('{title}','{g.user['username']}', {g.user['id']}, '{Field1}', '{Field2}', '{Field3}', '{Field4}', '{description}')'''
        ).fetchall()

        db.commit()

        error = None
        flash(error)

    return render_template('blog/threat.html')


# function used to display user collected threat data from database
@bp.route('/view_threat', methods=('GET', 'POST'))
def view_threat():

    db = get_db()

    threats = db.execute(
        'SELECT id, title, username, author_user_id, Field1, Field2, Field3, Field4, description, created_at, updated_at'
        ' FROM threat'
        ' ORDER BY updated_at DESC'
    ).fetchall()


    return render_template('blog/view_threat.html', threats=threats)



# function used to display user collected threat data from database
@bp.route('/edit_threat', methods=('GET', 'POST'))
@login_required
def edit_threat():
    threat = get_threat(id)

    if request.method == 'POST':
        title = request.form['title']
        username = request.form['username']
        Field1 = request.form['Field1']
        Field2 = request.form['Field2']
        Field3 = request.form['Field3']
        Field4 = request.form['Field4']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE threat SET title = ?, description = ?'
                ' WHERE id = ?',
                (title, description, id)
            )
            db.commit()
            return redirect(url_for('blog.threat'))

    return render_template('blog/view_threat.html')


    return render_template('blog/edit_threat.html', threat=threat)



#function that's called when deleting Threats from the threat database.
@bp.route('/<int:id>/delete_threat', methods=('POST',))
@login_required
def delete_threat(id):
    get_threat(id)
    db = get_db()
    db.execute('DELETE FROM threat WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.view_threat'))


#function that's called to get data for editing a threat.
def get_threat(id, check_author=True):
    threat = get_db().execute(
        'SELECT id, title, username, author_user_id, Field1, Field2, Field3, Field4, description, created_at, updated_at'
        ' FROM threat'
        ' ORDER BY updated_at DESC'
    ).fetchone()

    if threat is None:
        abort(404, f"threat id {id} doesn't exist.")

    if check_author and threat['author_user_id'] != g.user['id']:
        abort(403)

    return threat
