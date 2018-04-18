from flask import Flask, render_template, jsonify, request, session, redirect
from flask_mysql import MySQL
from time import gmtime, strftime
from werkzeug import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'kieta'
app.config['MYSQL_DATABASE_PASSWORD'] = 'kieta'
app.config['MYSQL_DATABASE_DB'] = 'fyproj'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/showAddFile')
def showAddFile():
    return render_template('addFile.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')
@app.route('/showDashboard')
def showDashboard():
    return render_template('dashboard.html')

@app.route('/getFile',methods=['POST'])
def getFile():
    try:
        if session.get('user'):
            _user = session.get('user')
           
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetUserFiles',(_user))
            
            files = cursor.fetchall()        

            response = []
            files_dict = []
            for file in files:
                files_dict = {
                        'Id': file[0],
                        'Title': file[1],
                        'Code': file[2],
                        'Date': file[4]}
                files_dict.append(files_dict)
            response.append(files_dict)
            
            return jsonify(response)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/getAllFiles')
def getAllFiles():
    try:
        if session.get('user'):
            
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetAllFiles')
            result = cursor.fetchall()
              
            file_dict = []
            for file in result:
                file_dict = {
                        'Id': file[0],
                        'Title': file[1],
                        'Code': file[2]}
                file_dict.append(file_dict)       

           

            return jsonify(file_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))


@app.route('/getFileById',methods=['POST'])
def getFileById():
    try:
        if session.get('user'):
            
            _id = request.form['id']
            _user = session.get('user')
    
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetFileById',(_id,_user))
            result = cursor.fetchall()

            files = []
            files.append({'Id':result[0][0],'Title':result[0][1],'Code':result[0][2],'Private':result[0][3]})

            return jsonify(files)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/addFile',methods=['POST'])
def addFile():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _code = request.form['inputCode']
            _user = session.get('user')
            _date = strftime("%a, %d %b %Y %H:%M:%S")
            
            if request.form.get('private') is None:
                _private = 0
            else:
                _private = 1
          
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addFile',(_title,_code,_user,_private, _date))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
  

@app.route('/editFile', methods=['POST'])
def editFile():
    try:
        if session.get('user'):
            _user = session.get('user')
            _title = request.form['title']
            _code = request.form['code']
            _file_id = request.form['id']
            _isPrivate = request.form['isPrivate']           

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_editFile',(_title,_code,_file_id,_user,_isPrivate))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return jsonify({'status':'OK'})
            else:
                return jsonify({'status':'ERROR'})
    except Exception as e:
        return jsonify({'status':'Unauthorized access'})


@app.route('/deleteFile',methods=['POST'])
def deleteFile():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_deleteFile',(_id,_user))
            result = cursor.fetchall()

            if len(result) is 0:
                conn.commit()
                return jsonify({'status':'OK'})
            else:
                return jsonify({'status':'An Error occured'})
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return jsonify({'status':str(e)})

@app.route('/saveFile',methods=['POST'])
def saveFile():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')
    
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetFileById',(_id))
            result = cursor.fetchall()

            newFile.copy(result)
            cursor.callproc('sp_addFile',(newFile[0][1],newFile[0][2],_user,newFile[0][3],newFile[0][4]))

            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/versionFile',methods=['GET'])
def versionFile(): 
    try:
		if session.get('user'):
            _user = session.get('user')
           

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetFileVersion',(_user, ))
            
            files = cursor.fetchall()        

            response = []
            files_dict = []
            for file in files:
                files_dict = {
                        'Id': file[0],
                        'Title': file[1],
                        'Code': file[2],
                        'Timestamp': file[4]}
                files_dict.append(files_dict)
            response.append(files_dict)
            
            return jsonify(response)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

@app.route('/overwriteFile',methods=['POST'])
def overwriteFile():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
           	_user = session.get('user')
          
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addFile',(_title,_code,_user,_private, _date))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        
        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/showDashboard')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return jsonify({'message':'User created successfully'})
            else:
                return jsonify({'error':str(data[0])})
        else:
            return jsonify({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return jsonify({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

if __name__ == "__main__":
    app.run(port=5014, debug=TRUE)