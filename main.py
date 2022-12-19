from flask import Flask, redirect, render_template, session, url_for, request, flash
import gsheets
from export import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from forms import *
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = '#$%^&*'

LOGIN = 'admin'
PASSWORD = 'password'
HASH = generate_password_hash(PASSWORD)


class User(UserMixin):

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return int(self.id)

    def __repr__(self):
        return f"User({self.username})"


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    print('login_form')
    if login_form.validate_on_submit():
        login = login_form.username.data.strip().lower()
        password = login_form.password.data
        if len(login) != len(LOGIN) or not check_password_hash(HASH, password):
            flash('Please check your login details and try again.')
        else:
            if all([login[i] == LOGIN[i] for i in range(len(LOGIN))]) and check_password_hash(HASH, password):
                session['is_login'] = True
                # return flask.render_template('index.html', infoForm=InfoForm())
                return redirect(url_for('index'))
        flash('Please check your login details and try again.')
    return render_template('login.html', login_form=login_form)


@login_manager.user_loader
def load_user(user_id):
    if user_id == LOGIN:
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'is_login' in session.keys():

        if session['is_login']:
            infoForm = InfoForm()
            print(infoForm.startdate.data)
            if infoForm.validate_on_submit():
                print('click')
                session['startdate'] = infoForm.startdate.data.strftime('%d/%m/%Y')
                session['enddate'] = infoForm.enddate.data.strftime('%d/%m/%Y')
                session['project'] = infoForm.project.data
                return redirect(url_for('date'))
            return render_template('index.html', infoForm=infoForm)

    return redirect(url_for('login'))


@app.route('/date', methods=['GET','POST'])
def date():
    if 'is_login' in session.keys():
        print("is_login in session.keys()")
        if session['is_login'] == True:
            print("session['is_login'] == True'")
            session['sheet_id']=f"{session['project']}_{session['startdate']}-{session['enddate']}"
            print(session, type(session['startdate']))
            df = getLeadsDF(session['startdate'], session['enddate'])
            print('start paste')
            session['sheet_id'] = gsheets.pastDataFrame_into_Sheets(df, f'{session["project"]}: {session["startdate"]}-{session["enddate"]}')
            print('pasted')
            return render_template('date.html')
    return render_template('login.html', login_form=LoginForm())


if __name__ == '__main__':
    app.run(debug=True)