from flask import *
from flask_wtf import FlaskForm
from sql import add_user, is_username_taken, check_user, get_by_id
from wtforms import StringField, PasswordField, SubmitField,TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_caching import Cache
import logging
import asyncio
import httpx
from insert_jobs import get_jobs, get_job


app = Flask(__name__)
app.secret_key = 'upasana12345'



#configuring the Cache data
cache=Cache(app,config={'CACHE_TYPE': 'simple'}) #setting up the cache for the website

# logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')

# @app.before_request
# def log_request_info():
#     logging.info('Request Method : %s', request.method)
#     logging.info('Request url : %s', request.url)
#     logging.info('Request Headers : %s', dict(request.headers))
#     logging.info('Request Data : %s', request.data)

# @app.after_request
# def log_response_info(response):
#     logging.info('Response Status: %s', response.status)
#     logging.info('Request Headers : %s', dict(request.headers))
#     return response

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators= [DataRequired(), Length(min=4, max=20)])
    firstname = StringField('Firstname', validators=[DataRequired(), Length(min=1, max=20)])
    lastname = StringField('lastname', validators=[DataRequired(), Length(min=1, max=20)])
    country = StringField('country', validators=[DataRequired(), Length(min=1, max=20)])
    title = StringField('title', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators= [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),
                                                                     EqualTo('password')])
    submit = SubmitField('Sign Up')
    def validate_username(form, field):
        if is_username_taken(field.data):
            print("error")
            raise ValidationError('Username already taken')

class loginForm(FlaskForm):
    email = StringField('Email', validators= [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class User(UserMixin):
    def __init__(self, id, username,firstname, lastname, country, title, email, password):
         self.id = id
         self.username = username
         self.firstname = firstname
         self.lastname = lastname
         self.country = country
         self.title = title
         self.email = email
         self.password = password
         self.authenticated = False
    def is_active(self):
         return self.is_active()
    def is_anonymous(self):
         return False
    def is_authenticated(self):
         return self.authenticated
    def is_active(self):
         return True
    def get_id(self):
         return self.id   



login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
    
async def fetch_consurrent_data(api_endpoint):
    tasks = [fetch_data(url) for url in api_endpoint ]
    responses = await asyncio.gather(*tasks)
    return responses
 


@login_manager.user_loader
def load_user(user_id):
    data = get_by_id(user_id)
    if data is not None and len(data) >= 4:
        return User(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
    else:
        return None  # Return None to indicate that the user couldn't be loaded



@app.route('/register', methods= ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        country = form.country.data
        title = form.title.data
        email = form.email.data
        password = form.password.data
        add_user(username,firstname, lastname, country, title, email, password)
        return redirect('/login')
    return render_template('register.html', form= form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = check_user(email)
        Us = load_user(user[0]) 

        if email == Us.email and password == Us.password:
            session_key = f'user{email}'
            session_data = {'email': email, 'password': password}
            cache.set(session_key, session_data, timeout=3600)
            login_user(Us)
            Us.authenticated = True
            flash("Successfully logged in")
            return redirect(url_for('homepage'))
        else:
            flash('Login Failed. Invalid Credentials')
    return render_template('login.html', form=form)


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
@login_required
async def homepage():
    return render_template('index.html')

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    return render_template('login_admin.html')

@app.route('/joblisting', methods=['GET', 'POST'])
@login_required
async def job_listing():
    jobs_db = get_jobs()
    print(jobs_db)
    api_endpoint = [
        'https://api.adzuna.com/v1/api/jobs/us/search/1?app_id=ccf89480&app_key=3e60dc4d7e57b3d23b276036be975e66',
        'https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id=ccf89480&app_key=3e60dc4d7e57b3d23b276036be975e66',
        'https://api.adzuna.com/v1/api/jobs/fr/search/1?app_id=ccf89480&app_key=3e60dc4d7e57b3d23b276036be975e66'
        
    ]
    responses = await fetch_consurrent_data(api_endpoint)
    processed_data = []
    for url,response in zip(api_endpoint, responses):
        processed_data.append({
            'url': url,
            'response' : response['results']
        })
    data = jsonify(processed_data).json
    jobs= data
    processed_data_len = len(processed_data)
    return render_template('job_listing.html', jobs=jobs, length= processed_data_len, jobs_db = jobs_db)
    return jobs

# @app.route('/info/<job_id>', methods=['GET', 'POST'])
# @login_required
# async def job(job_id):

#     return render_template('job.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    fname = current_user.firstname
    
    lname = current_user.lastname
    title = current_user.title
    country = current_user.country
    email = current_user.email
    return render_template('profile.html', fname=fname, lname = lname, title=title, country= country, email=email)



# @app.route('/get_media/<media_id>')
# def get_media_flask(media_id):
#     media_data, media_mime = get_media(media_id)
#     return send_file(media_data, mimetype=media_mime)

@app.route('/jobfilter', methods=['POST'])
@login_required
def jobfilter():
    title = request.form.get('title')
    country = request.form.get('country')
    print(title, country)
    return render_template('index.html')

@app.route('/jobdetails', methods=['POST'])
@login_required
def jobdetails():
    job_id = request.form.get('id')
    print(job_id)
    # get job details from mongodb 
    jobdetails = get_job(job_id)
    print(jobdetails)
    return {'data':jobdetails}


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.teardown_appcontext
def close_connection(exception): 
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)