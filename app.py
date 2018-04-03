from flask import Flask, render_template, json, request, session
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


@app.route('/editFile', methods=['POST'])
def editFile():
    try:
        if session.get('user'):
            _user = session.get('user')
            _title = request.form['title']
            _description = request.form['description']
            _file_id = request.form['id']
            _isPrivate = request.form['isPrivate']           

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_editFile',(_title,_description,_file_id,_user,_isPrivate))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'ERROR'})
    except Exception as e:
        return json.dumps({'status':'Unauthorized access'})
    finally:
        cursor.close()
        conn.close()

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
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'An Error occured'})
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return json.dumps({'status':str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/getFile',methods=['POST'])
def getWish():
    try:
        if session.get('user'):
            _user = session.get('user')
           

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetFileByUser',(_user))
            
            files = cursor.fetchall()        

            response = []
            files_dict = []
            for file in files:
                files_dict = {
                        'Id': file[0],
                        'Title': file[1],
                        'Description': file[2],
                        'Date': file[4]}
                files_dict.append(files_dict)
            response.append(files_dict)
            
            return json.dumps(response)
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
                        'Description': file[2]}
                file_dict.append(file_dict)       

           

            return json.dumps(file_dict)
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
            files.append({'Id':result[0][0],'Title':result[0][1],'Description':result[0][2],'Private':result[0][3]})

            return json.dumps(files)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))

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
    finally:
        cursor.close()
        conn.close()
            

@app.route('/addFile',methods=['POST'])
def addFile():
    try:
        if session.get('user'):
            _temp = request.form['inputTitle']
            '''_description = request.form['inputDescription']'''
            _user = session.get('user')
            timestr = strftime("%Y%m%d-%H%M%S")
            _time = strftime("%a, %d %b %Y %H:%M:%S")
            _title = _temp.append(timestr)
            if request.form.get('private') is None:
                _private = 0
            else:
                _private = 1
          

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addFile',(_title,_user,_private, _time))
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
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

if __name__ == "__main__":
    app.run(port=5002)