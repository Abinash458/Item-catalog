from flask import (
    Flask,
    render_template,
    url_for, request,
    redirect,
    flash,
    jsonify
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Brand, BrandModel, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']

app = Flask(__name__)

# connect to database
engine = create_engine('sqlite:///carsmodel.db')
Base.metadata.bind = engine

# Create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a state token to prevent request forgery.(Anti-forgery)
# store it in the session for later validation.


@app.route('/login/')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase +
            string.digits)for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
        access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is used for the identifier user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's User ID does not match with given usre ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client id does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # add provider to login session
    login_session['provider'] = 'google'

    # check if user is exists on not, if not exists then make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome,'
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;'\
        ' height: 300px;'\
        ' border-radius: 150px;'\
        ' -moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User function


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


# show all brands
@app.route('/')
@app.route('/brand/')
def showBrand():
    session = DBSession()
    brands = session.query(Brand).all()
    return render_template('brand.html', brands=brands)

# create new brands


@app.route('/brand/new/', methods=['GET', 'POST'])
def newBrand():
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBrand = Brand(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newBrand)
        session.commit()
        flash('Brand Successfully created %s' % newBrand.name)
        return redirect(url_for('showBrand'))
    else:
        return render_template('newBrand.html')

# edit brands


@app.route('/brand/<int:brand_id>/edit/', methods=['GET', 'POST'])
def editBrand(brand_id):
    session = DBSession()
    editedBrand = session.query(Brand).filter_by(id=brand_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedBrand.user_id != login_session['user_id']:
        return "<script>{alert('You are Unauthorized!');}</script>"
    if request.method == 'POST':
        if request.form['name']:
            editedBrand.name = request.form['name']
            flash('Brand Successfully Edited %s' % editedBrand.name)
            return redirect(url_for('showBrand'))
    else:
        return render_template('editBrand.html', brand=editedBrand)

# delete brands


@app.route('/brand/<int:brand_id>/delete/', methods=['GET', 'POST'])
def deleteBrand(brand_id):
    session = DBSession()
    brandToDelete = session.query(Brand).filter_by(id=brand_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if brandToDelete.user_id != login_session['user_id']:
        return "<script>{alert('You are Unauthorized!');}</script>"
    if request.method == 'POST':
        session.delete(brandToDelete)
        flash('%s Successfully deleted' % brandToDelete.name)
        session.commit()
        return redirect(url_for('showBrand'))
    else:
        return render_template('deleteBrand.html', brand=brandToDelete)

# show all brandmodels


@app.route('/brand/<int:brand_id>/')
@app.route('/brand/<int:brand_id>/model/')
def showModel(brand_id):
    session = DBSession()
    brand = session.query(Brand).filter_by(id=brand_id).one()
    models = session.query(BrandModel).filter_by(brand_id=brand_id).all()
    return render_template('model.html', brand=brand, models=models)

# create new brandmodels


@app.route('/brand/<int:brand_id>/model/new/', methods=['GET', 'POST'])
def newModel(brand_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBrandModel = BrandModel(
            name=request.form['name'],
            description=request.form['description'],
            brand_id=brand_id,
            # user_id=brand.user_id
            user_id=login_session['user_id'])
        session.add(newBrandModel)
        session.commit()
        flash("Model has been added.")
        return redirect(url_for('showModel', brand_id=brand_id))
    else:
        return render_template('newModel.html', brand_id=brand_id)

# edit brandmodels


@app.route(
    '/brand/<int:brand_id>/model/<int:model_id>/edit/',
    methods=[
        'GET',
        'POST'])
def editModel(brand_id, model_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    editedModel = session.query(BrandModel).filter_by(id=model_id).one()
    if editedModel.user_id != login_session['user_id']:
        return "<script>{alert('You are Unauthorized!');}</script>"
    if request.method == 'POST':
        if request.form['name']:
            editedModel.name = request.form['name']
        if request.form['description']:
            editedModel.description = request.form['description']
        session.add(editedModel)
        session.commit()
        flash("Model has been edited Successfully.")
        return redirect(url_for('showModel', brand_id=brand_id))
    else:
        return render_template(
            'editModel.html',
            brand_id=brand_id,
            model_id=model_id,
            models=editedModel)

# delete brandmodels


@app.route(
    '/brand/<int:brand_id>/model/<int:model_id>/delete',
    methods=[
        'GET',
        'POST'])
def deleteModel(brand_id, model_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    modelToDelete = session.query(BrandModel).filter_by(id=model_id).one()
    if modelToDelete.user_id != login_session['user_id']:
        return "<script>{alert('You are Unauthorized!');}</script>"
    if request.method == 'POST':
        session.delete(modelToDelete)
        session.commit()
        flash("Model has been deleted Successfully.")
        return redirect(url_for('showModel', brand_id=brand_id))
    else:
        return render_template('deleteModel.html', models=modelToDelete)

# JSON to view Info.


@app.route('/brand/JSON/')
def JSONBrand():
    session = DBSession()
    brand = session.query(Brand).all()
    return jsonify(brand=[i.serialize for i in brand])


@app.route('/brand/<int:brand_id>/model/JSON/')
def JSONModel(brand_id):
    session = DBSession()
    brand = session.query(Brand).filter_by(id=brand_id).one()
    models = session.query(BrandModel).filter_by(brand_id=brand_id).all()
    return jsonify(BrandModel=[r.serialize for r in models])


@app.route('/brand/<int:brand_id>/model/<int:model_id>/JSON/')
def JSONModelDetail(brand_id, model_id):
    modelDetail = session.query(BrandModel).filter_by(id=model_id).one()
    return jsonify(BrandModel=modelDetail.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
