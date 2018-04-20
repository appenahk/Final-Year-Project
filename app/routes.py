from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Files
import sys

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    files = Files.query.order_by(Files.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=files.next_num) \
        if files.has_next else None
    prev_url = url_for('explore', page=files.prev_num) \
        if files.has_prev else None
    return render_template('explore.html', title='Explore', files=files.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    files = user.files.order_by(Files.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    
    next_url = url_for('user', username=user.username, page=files.next_num) \
        if files.has_next else None
    prev_url = url_for('user', username=user.username, page=files.prev_num) \
        if files.has_prev else None
    return render_template('user.html', user=user, files=files.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/addFile',methods=['GET', 'POST'])
@login_required
def addFile():
    _title = request.form['filename']
    _code = request.form['inputCode']
    if request.form.get('private') is None:
        _private = 0
    else:
        _private = 1
    file = Files(title=request.form['filename'], body=request.form['inputCode'], 
        private=_private, author=current_user)
    
    db.session.add(file)
    db.session.commit()
    
    flash('File added')    
    return render_template('index.html', title='Home')

@app.route('/getFile',methods=['POST'])
def getFile():
    print("check", file=sys.stderr)

@app.route('/editFile', methods=['POST'])
def editFile():
    print("check", file=sys.stderr)


@app.route('/deleteFile',methods=['POST'])
def deleteFile():
    print("check", file=sys.stderr)