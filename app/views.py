from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models import User, Therapist, Chat, WellnessTest, GroupChat, db
from functools import wraps
from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from datetime import datetime


bp = Blueprint('views', __name__, template_folder='../templates')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('views.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
def index():
    """
    Redirects to the dashboard if the user is logged in or to the login page
    if the user is not logged in.
    """
    return redirect(url_for('views.dashboard'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles the registration of users.

    If the request method is POST, it verifies the submission form to ensure
    all fields are filled and the password matches the verification password.
    If the form is valid, it creates a new user with the given username,
    email, and password, and redirects the user to the login page.

    If the request method is GET, it renders the registration form.
    """
    if request.method == 'POST':
        fullname = request.form['full-name']
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        verify_pass=request.form['verify-password']

        if fullname and username and email and password and verify_pass:
            if password != verify_pass:
                return redirect(url_for('views.register'))
            try:
                existing_user = db.query(User).filter(
                    and_(
                        User.email.like(email),
                        User.password.like(password)
                        )
                ).one()
            except NoResultFound as error:
                user = User(
                    fullname=fullname, username=username, email=email,
                    password=password, created_at=datetime.now())
                db.add(user)
                db.commit()
                return redirect(url_for('views.login'))
        return redirect(url_for('views.register'))
    if request.method == 'GET':
        return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.

    If the request method is POST, it verifies the submission form to ensure
    all fields are filled. If the form is valid, it looks up the user with the
    given email and password, and if the user exists, it logs the user in by
    setting the 'user_id' session variable and redirects the user to the
    dashboard. Otherwise, it renders the login form.

    If the request method is GET, it renders the login form.
    """
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        try:
            user = db.query(User).filter(
                and_(
                    User.email.like(email),
                    User.password.like(password)
                    )
            ).one()
        except NoResultFound as error:
            return render_template('login.html')
        session['user_id'] = user.id
        return redirect(url_for('views.dashboard'))
    return render_template('login.html')    


@bp.route('/logout')
def logout():
    """
    Logs the user out of the application by removing the 'user_id' session
    variable and redirects the user to the login page.
    """
    session.pop('user_id', None)
    return redirect(url_for('views.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    user = db.query(User).filter(User.id == session.get('user_id')).one()
    return render_template('dashboard.html', user=user)


@bp.route('/therapists')
@login_required
def therapists():
    therapists = Therapist.query.all()
    return render_template('therapists.html', therapists=therapists)


@bp.route('/group-chat', methods=['GET', 'POST'])
@login_required
def group_chat():
    if request.method == 'POST':
        message = request.form['message']
        sender_id = session.get('user_id')
        group_chat = GroupChat(sender_id=sender_id, message=message)
        db.add(group_chat)
        db.commit()
        return redirect(url_for('views.group_chat'))
    
    group_chats = GroupChat.query.order_by(GroupChat.created_at.asc()).all()
    return render_template('group-chat.html', group_chats=group_chats)


@bp.route('/chat/<int:therapist_id>')
@login_required
def chat(therapist_id):
    therapist = Therapist.query.get(therapist_id)
    chats = Chat.query.filter_by(recipient_id=therapist_id).all()
    return render_template('chat.html', therapist=therapist, chats=chats)


@bp.route('/chat/<int:therapist_id>/send', methods=['POST'])
@login_required
def send_chat(therapist_id):
    chat = Chat(sender_id=session.get('user_id'), recipient_id=therapist_id, message=request.form['message'])
    db.add(chat)
    db.commit()
    return redirect(url_for('views.chat', therapist_id=therapist_id))


@bp.route('/wellness-test')
@login_required
def wellness_test():
    return render_template('wellness-test.html')


@bp.route('/wellness-test/submit', methods=['POST'])
@login_required
def submit_wellness_test():
    test = WellnessTest(user_id=session.get('user_id'), score=request.form['score'])
    db.add(test)
    db.commit()
    return redirect(url_for('views.dashboard'))
