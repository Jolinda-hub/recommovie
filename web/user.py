from datetime import datetime
from db.factory import DecisionFactory, UserFactory
from db.model import Decision, User
from flask import Blueprint, jsonify, redirect, render_template, request, session
from validation import LoginForm, SignupForm
from web import app

auth = Blueprint('user', app.name)


@auth.route('/signup')
def get_signup():
    """
    Get sign up page
    """
    params = {
        'title': 'Create account',
    }

    return render_template('login.html', **params)


@auth.route('/signup', methods=['POST'])
def post_signup():
    """
    Post sign up page
    """
    form = SignupForm()
    uf = UserFactory()

    params = {
        'title': 'Sign up',
    }

    # validate form
    if form.validate_on_submit():
        user = uf.get_by_email(form.email.data)

        # if user is already exists
        if user:
            params['error'] = 'User is already registered'
            return render_template('login.html', **params)

        instance = User(
            name=form.name.data,
            email=form.email.data,
            created_at=datetime.now()
        )
        instance.set_password(form.password.data)

        uf.save(instance)
        return render_template('thanks.html')

    if len(form.errors) > 0:
        params['errors'] = [x[0] for x in form.errors.values()]

    return render_template('login.html', **params)


@auth.route('/login')
def get_login():
    """
    Get login page
    """
    params = {
        'title': 'Sign in',
    }

    return render_template('login.html', **params)


@auth.route('/login', methods=['POST'])
def post_login():
    """
    Post login page
    """
    form = LoginForm()
    uf = UserFactory()
    df = DecisionFactory()

    params = {
        'title': 'Sign in',
    }

    if form.validate_on_submit():
        user = uf.get_by_email(form.email.data)

        # check user
        if user is None or not user.check_password(form.password.data):
            params['error'] = 'Invalid username or password'
            return render_template('login.html', **params)

        # get decisions by logged user
        decisions = df.get_by_user(user.id)

        # set session variables
        session['name'] = user.name
        session['id'] = user.id
        session['decisions'] = [d.title_id for d in decisions]

        return redirect('/')

    if len(form.errors) > 0:
        params['errors'] = [x[0] for x in form.errors.values()]

    return render_template('login.html', **params)


@auth.route('/logout')
def logout():
    """
    Logout user
    """
    keys = [
        'id',
        'name',
        'decisions'
    ]

    # remove session variables
    if session['id']:
        for key in keys:
            session.pop(key)

    return redirect('/')


@auth.route('/save')
def save():
    """
    Save user decision
    """
    if not session['id']:
        return jsonify({'status': False})

    user_id = request.args['user_id']
    title_id = request.args['title_id']

    decision = Decision(
        user_id=user_id,
        title_id=title_id
    )

    # save decision
    df = DecisionFactory()
    df.save(decision)

    # add title id to session
    decisions = session['decisions']
    decisions.append(title_id)
    session['decisions'] = decisions

    return jsonify({'status': True})


@auth.route('/remove')
def remove():
    """
    Remove user decision
    """
    if not session['id']:
        return jsonify({'status': False})

    user_id = request.args['user_id']
    title_id = request.args['title_id']

    # remove decision
    df = DecisionFactory()
    df.remove(user_id, title_id)

    # remove title id from session
    decisions = session['decisions']
    decisions.remove(title_id)
    session['decisions'] = decisions

    return jsonify({'status': True})


@auth.route('/favorites')
def get_favorites():
    """
    Get user favorites
    """
    if not session['id']:
        return redirect('/')

    df = DecisionFactory()
    favorites = df.get_by_user(session['id'])

    try:
        args = {
            'header': 'Favorites by',
            'items': favorites,
            'original': session['name'],
            'flag': True
        }
        return render_template('recommendations.html', **args)
    except BaseException:
        return render_template('error.html')
