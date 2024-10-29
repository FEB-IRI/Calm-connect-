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
    """
    Displays the user's dashboard.

    This view renders the dashboard template, passing the user object as a
    template variable.
    """
    user = db.query(User).filter(User.id == session.get('user_id')).one()
    return render_template('dashboard.html', user=user)


@bp.route('/therapists')
@login_required
def therapists():
    """
    Displays a list of all therapists.

    This view queries all therapists from the database and renders the
    'therapists.html' template, passing the list of therapists as a 
    template variable.
    """
    therapists = db.query(Therapist).all()
    return render_template('therapists.html', therapists=therapists)


@bp.route('/community', methods=['GET', 'POST'])
@login_required
def community():
    """
    Displays a page for users to chat with each other.

    If the request method is POST, it takes the message from the submission
    form and adds it to the database as a new GroupChat object, and redirects
    the user back to the same page.

    If the request method is GET, it queries all GroupChat objects from the
    database, ordered by the created_at timestamp in ascending order, and
    renders the 'group-chat.html' template, passing the list of GroupChat
    objects as a template variable.
    """
    group_id = 1
    if request.method == 'POST':
        message = request.form['message']
        sender_id = session.get('user_id')
        group_chat = GroupChat(sender_id=sender_id, message=message, group_name=group_id)
        db.add(group_chat)
        db.commit()
        return redirect(url_for('views.community', group_id=group_id))

    group = db.query(GroupChat).filter_by(id=group_id).one()
    group_chats = db.query(GroupChat).filter_by(group_name=group_id).order_by(GroupChat.created_at.asc()).all()
    return render_template('community.html', group=group, group_chat=group_chats)


@bp.route('/chat')
@login_required
def chat():
    """
    Displays a page for users to chat with a therapist.

    This view queries the specified therapist from the database, as well as
    all Chat objects where the recipient_id matches the therapist_id, and
    renders the 'chat.html' template, passing the therapist object and the
    list of Chat objects as template variables.
    """
    return render_template('therapists.html')


@bp.route('/chat/<int:therapist_id>/send', methods=['POST'])
@login_required
def send_chat(therapist_id):
    """
    Sends a chat message to a specific therapist.

    This view handles POST requests to send a chat message to the therapist
    specified by therapist_id. It creates a new Chat object with the 
    message from the submission form, associating it with the current user
    as the sender and the specified therapist as the recipient. The new
    chat is added to the database, and the user is redirected to the chat
    page for the specified therapist.
    """
    chat = Chat(sender_id=session.get('user_id'), recipient_id=therapist_id, message=request.form['message'])
    db.add(chat)
    db.commit()
    return redirect(url_for('views.chat', therapist_id=therapist_id))


@bp.route('/wellness-test')
@login_required
def wellness_test():
    """
    Displays a page for users to take a Wellness test.

    This view renders the 'wellness-test.html' template.
    """
    return render_template('wellness-test.html')


@bp.route('/wellness-test/submit', methods=['POST'])
@login_required
def submit_wellness_test():
    """
    Handles POST requests from the Wellness test submission form.

    This view creates a new WellnessTest object with the user's ID and the score
    from the submission form, adds it to the database, and redirects the user
    back to the dashboard.
    """
    test = WellnessTest(user_id=session.get('user_id'), score=request.form['score'])
    db.add(test)
    db.commit()
    return redirect(url_for('views.dashboard'))


@bp.route('/settings')
@login_required
def settings():
    """
    Displays a page for users to manage their profile.

    This view renders the 'settings.html' template.
    """
    return render_template('settings.html')


@bp.route('/progress')
@login_required
def progress():
    """
    Displays a page for users to view their progress.

    This view renders the 'progress.html' template.
    """
    return render_template('progress.html')


@bp.route('/meet_a_therapist')
@login_required
def meet_a_therapist():
    """
    Displays a page for users to view their available therapists.

    This view renders the 'meet-a-therapist.html' template.
    """
    return render_template('meet_a_therapist.html')
