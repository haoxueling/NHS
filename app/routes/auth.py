"""User Registration and Login Interface"""
#print("auth.py Module loading commences", flush=True)
from flask import Blueprint, request, jsonify, render_template, redirect, make_response, session, url_for
from flask_jwt_extended import create_access_token
from datetime import timedelta
from app import db
from app.models import User
from flask_cors import cross_origin  # Resolving cross-domain issues
from sqlalchemy.exc import IntegrityError

# Initialise blueprint (no additional prefix; route maps directly to root path)
bp = Blueprint('auth', __name__)

# Login Page Routing (Frontend access to /login)
@bp.route('/login')
def login_page():
    return render_template('login.html')

# Registration Page Routing (Frontend Access /register)
@bp.route('/register')
def register_page():
    return render_template('register.html')

# Registration Interface (Frontend Request /api/register)
@bp.route('/api/register', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def register():
    """User Registration"""
    if request.method == 'OPTIONS':
        return jsonify(), 200

    data = request.json
    if not data:
        return jsonify(msg='Request data is empty'), 400

    # Verify required fields
    required_fields = ['name', 'gender', 'date_of_birth', 'email', 'phone', 'password', "role"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify(msg=f'Missing necessary fields or empty field values: {field}'), 400

    # Verify email uniqueness
    #if User.query.filter_by(email=data['email']).first():
        #return jsonify(msg='This email address has already been registered.'), 400

    role = data['role']

    if role == 'user':  # Patient registration
        chi_number = data.get('chi_number')
        tumor_type = data.get('tumor_type')  # Obtain tumour type

        # Validate patient-specific fields
        if not chi_number:
            return jsonify(msg='Please provide CHI Number'), 400
        if not tumor_type:
            return jsonify(msg='Please select tumor type'), 400

        # Ensure CHI numbers are unique (including compatibility with the medical_id field)
        if User.query.filter(
                (User.chi_number == chi_number) | (User.medical_id == chi_number)
        ).first():
            return jsonify(msg='This CHI Number has already been registered'), 400

        medical_id = chi_number  

    elif role == 'doctor':  # Clinician registration
        medical_id = data.get('medical_id')
        tumor_type = None  # no tumor_type
        if not medical_id:
            return jsonify(msg='Please provide Medical ID'), 400

        if User.query.filter_by(medical_id=medical_id).first():
            return jsonify(msg='This medical ID has already been registered'), 400

        chi_number = None  # no chi_number

    else:
        return jsonify(msg='Invalid role'), 400


    # Insert user data into the database
    try:
        user = User(
            name=data['name'],
            gender=data['gender'],
            date_of_birth=data['date_of_birth'],
            medical_id=medical_id,
            chi_number=chi_number,
            email=data['email'],
            phone=data['phone'],
            role=role,
            tumor_type=tumor_type  # Store tumor type for patients
        )
        user.set_password(data['password'])  # Hash and store password
        db.session.commit()
        return jsonify(msg='registered successfully'), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify(msg=f'Registration failed: Database insertion error {str(e)}'), 500
    except Exception as e:
        db.session.rollback()
        return jsonify(msg=f'register has failed：{str(e)}'), 500

# Login Interface (Frontend Request /api/login)
@bp.route('/api/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login():
    """User Login"""
    print("Login request received", flush=True)
    if request.method == 'OPTIONS':
        return jsonify(), 200

    try:  # Use try-except to catch unexpected errors
        data = request.json
        print(f"Request data:{data}", flush=True)  # Debug: print request data
        if not data:
            return jsonify(msg='The requested data is empty.'), 400

        role = data.get('role')
        password = data.get('password')

        if not role or not password:
            return jsonify(msg='Missing role or password'), 400

        user = None

        if role == 'patient':
            chi_number = data.get('chi_number')
            if not chi_number:
                return jsonify(msg='lack of CHI Number'), 400
            user = User.query.filter_by(role='user', chi_number=chi_number).first()
        # The role field in the database corresponds to clinician, while the user field corresponds to patient.
        elif role == 'clinician':
            medical_id = data.get('medical_id')
            if not medical_id:
                return jsonify(msg='lack of Medical ID'), 400
            user = User.query.filter_by(role='doctor', medical_id=medical_id).first()

        else:
            return jsonify(msg='Invalid role'), 400

        if not user or not user.check_password(password):
            return jsonify(msg='Account or password error'), 401
        
        # Store user information in the session
        session['user_id'] = user.id
        session['role'] = user.role

        # Generate JWT Token (valid for 24 hours)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role},
            expires_delta=timedelta(hours=24)
        )
        resp = make_response(jsonify(
            access_token=access_token,
            user={
                 'id': user.id,
                  'name': user.name,
                  'role': user.role,
                  'medical_id': user.medical_id,
                 'chi_number': user.chi_number,
                 'tumor_type': user.tumor_type  # Return tumor type to frontend
                  }
        ))
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    except Exception as e:  # Catch all unexpected exceptions
        print(f"登录接口异常：{str(e)}", flush=True)  # Log the error for debugging
        return jsonify(msg=f"服务器内部错误：{str(e)}"), 500

# Root path redirection to login page
@bp.route('/')
def index():
    return redirect('/login')  # Redirect to login page

# Logout Interface (Frontend Request /logout)
@bp.route('/logout')
def logout():
    """User logout: Clear the token cookie and redirect to the login page."""
    # Clear the Flask session before redirection
    session.clear()
    # Create a response object for deleting cookies
    resp = make_response(redirect(url_for('auth.login_page')))  # Redirect to the login page
    resp.delete_cookie('access_token', path='/')  # Delete the JWT token cookie

    return resp
