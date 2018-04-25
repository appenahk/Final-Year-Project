from datetime import datetime
from flask import render_template, jsonify, flash, redirect, url_for, request, g, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db, elasticsearch
from app.forms import LoginForm, RegistrationForm, SearchForm
from app.models import User, Files
import sys
from sqlalchemy import func, distinct

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('start.html')
    
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Home')

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

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    files = Files.query.filter_by(private=0).order_by(Files.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=files.next_num) \
        if files.has_next else None
    prev_url = url_for('explore', page=files.prev_num) \
        if files.has_prev else None
    return render_template('explore.html', title='Explore', files=files.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    '''files2 = Files.query(func.max(Files.version)).filter(author == current_user.username)
    for row in files2:
        print(row.version, file=sys.stderr)'''
    files = user.files.order_by(Files.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    
    next_url = url_for('user', username=user.username, page=files.next_num) \
        if files.has_next else None
    prev_url = url_for('user', username=user.username, page=files.prev_num) \
        if files.has_prev else None
    return render_template('user.html', title='Profile', user=user, files=files.items,
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
    _version = 1
    file = Files(title=request.form['filename'], body=request.form['inputCode'], 
        private=_private, version=_version, author=current_user)
    
    db.session.add(file)
    db.session.commit()
    
    flash('File added')    
    return render_template('index.html', title='Home')

@app.route('/getFile',methods=['POST'])
def getFile():
    _id = request.form['id']
    file = Files.query.filter_by(id=_id)
    for row in file:
        return jsonify({'Title':row.title,'Code':row.body,
            'Private':row.private, 'Version':row.version})
    
@app.route('/editFile', methods=['GET', 'POST'])
@login_required
def editFile():
    _id = request.form['id']
    _version = request.form['versNo']
    newVersion = int(_version) + 1
    
    file = Files(title=request.form['title'], body=request.form['code'], 
        private=request.form['isPrivate'],version=newVersion, author=current_user)
    db.session.add(file)
    db.session.commit()
    flash('File edited')    
    return jsonify({'status':'OK'})


@app.route('/deleteFile',methods=['GET', 'POST'])
@login_required
def deleteFile():
    _id = request.form['id']
    
    Files.query.filter_by(id=_id).delete()
    db.session.commit()
    exists = db.session.query(Files.id).filter_by(id=_id).scalar()
    print(current_user.username, file=sys.stderr)   
    if exists is None:        
        return jsonify({'status':'OK'})
    else:
        return jsonify({'status':'An Error occured'})

@app.route('/saveFile',methods=['GET', 'POST'])
@login_required
def saveFile():
    _id = request.form['id']
    file = Files.query.filter_by(id=_id)
    exists = None
    for row in file:
        newFile = Files(title=row.title, body=row.body, 
        private=1,version=1, author=current_user)
        db.session.add(newFile)
        db.session.commit()
        
        exists = db.session.query(Files.title).filter_by(title=newFile.title).filter_by(author=current_user).scalar()
        print(exists, file=sys.stderr) 
    flash('Saved to User')  
    if exists is not None:        
        return jsonify({'status':'OK'})
    else:
        return jsonify({'status':'An Error occured'})
        
@app.route('/versions',methods=['GET', 'POST'])
@login_required
def versions():
    files = Files.query.filter_by(private=1).order_by(Files.timestamp.desc())
    return jsonify(json_list=[i.serialize for i in files])
'''
@app.route('/overwriteFile',methods=['GET', 'POST'])
@login_required
def overwriteFile():
    _id = request.form['id']
    _version = request.form['versNo']
    newVersion = int(_version) + 1
    print(newVersion, file=sys.stderr)
    file = Files(title=request.form['title'], body=request.form['code'], 
        private=request.form['isPrivate'],version=newVersion, author=current_user)
    db.session.add(file)
    db.session.commit()
    flash('File edited')    
    return render_template('index.html', title='Home')'''

@app.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('explore'))
    page = request.args.get('page', 1, type=int)

    files, total = Files.search(g.search_form.q.data, page,
                               app.config['POSTS_PER_PAGE'])
    print("here", file=sys.stderr)
    next_url = url_for('search', q=g.search_form.q.data, page=page + 1) \
        if total > page * app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', files=files,
                           next_url=next_url, prev_url=prev_url)