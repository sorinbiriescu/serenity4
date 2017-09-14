from serenity4 import app, db, login_manager

from flask import render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user

from models import Jobs,User,UserJobStatus
from forms import FilterSearch, SignupForm, LoginForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.route('/jobs', methods=['GET', 'POST'])
@app.route('/jobs/<int:page>', methods=['GET', 'POST'])
@login_required
def jobs(page=1):
    form = FilterSearch()
    if request.method == 'POST':
        jobs = Jobs.get_jobs_filtered(form.search_term.data,page)
        if request.form['submit'] == 'Filter':
            return render_template('jobs.html', jobs = jobs, filter_text = form.search_term.data, form=form)
        else:
            if form.table_item_action.data == 'Clear status':
                UserJobStatus.clear_status(request.form.getlist("table_row_checkbox"))
                return render_template('jobs.html', jobs = jobs, filter_text = form.search_term.data, form=form)
            else:
                try:
                    UserJobStatus.clear_status(request.form.getlist("table_row_checkbox"))
                except:
                    pass
                UserJobStatus.change_status(request.form.getlist("table_row_checkbox"), form.table_item_action.data)
                return render_template('jobs.html', jobs = jobs, filter_text = form.search_term.data, form=form)

    else:
        jobs = Jobs.get_jobs_filtered("All",page)
        return render_template('jobs.html', jobs = jobs, filter_text = "All", form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html', user=user)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(name=form.name.data,
                    username=form.username.data,
                    email=form.email.data,
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        #flash('Welcome, {}! Please login.'.format(user.username))
        return redirect(url_for('login'))
    return render_template("signup.html", form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            #flash("Logged in successfully as {}.".format(user.username))
            return redirect(request.args.get('next') or url_for('user',
                                                username=user.username))
        #flash('Incorrect username or password.')
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_issue(e):
    return render_template('500.html'), 500
