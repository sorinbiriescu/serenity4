from flask import render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user

from serenity4.models import Jobs, User, UserJobStatus, UserJobSearchCriteria, UserJobSearchLocation, UserJobSearchEngine
from serenity4.forms import FilterSearch, SignupForm, LoginForm, UserProfile

from serenity4 import app, db, login_manager


@app.route('/')
@app.route('/index')
@login_required
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
        jobs = Jobs.get_jobs_filtered(form.search_term.data, page)
        if request.form['submit'] == 'Filter':
            return render_template(
                'jobs.html',
                jobs=jobs,
                filter_text=form.search_term.data,
                form=form)
        elif request.form['submit'] == 'Get jobs':
            Jobs.get_new_jobs()
            return render_template(
                'jobs.html',
                jobs=jobs,
                filter_text=form.search_term.data,
                form=form)
        else:
            if form.table_item_action.data == 'Clear status':
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except:
                    pass
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)
            else:
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except:
                    pass
                UserJobStatus.change_status(
                    request.form.getlist("table_row_checkbox"),
                    form.table_item_action.data)
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)

    else:
        jobs = Jobs.get_jobs_filtered("All", page)
        return render_template(
            'jobs.html', jobs=jobs, filter_text="All", form=form)


@app.route('/jobs_not_interested', methods=['GET', 'POST'])
@app.route('/jobs_not_interested/<int:page>', methods=['GET', 'POST'])
@login_required
def jobs_not_interested(page=1):
    form = FilterSearch()
    if request.method == 'POST':
        jobs = Jobs.get_jobs_not_interested(form.search_term.data, page)
        if request.form['submit'] == 'Filter':
            return render_template(
                'jobs.html',
                jobs=jobs,
                filter_text=form.search_term.data,
                form=form)
        else:
            if form.table_item_action.data == 'Clear status':
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except:
                    pass
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)
            else:
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except Exception:
                    pass
                UserJobStatus.change_status(
                    request.form.getlist("table_row_checkbox"),
                    form.table_item_action.data)
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)

    else:
        jobs = Jobs.get_jobs_not_interested("All", page)
        return render_template(
            'jobs.html', jobs=jobs, filter_text="All", form=form)


@app.route('/jobs_interested', methods=['GET', 'POST'])
@app.route('/jobs_interested/<int:page>', methods=['GET', 'POST'])
@login_required
def jobs_interested(page=1):
    form = FilterSearch()
    if request.method == 'POST':
        jobs = Jobs.get_jobs_interested(form.search_term.data, page)
        if request.form['submit'] == 'Filter':
            return render_template(
                'jobs.html',
                jobs=jobs,
                filter_text=form.search_term.data,
                form=form)
        else:
            if form.table_item_action.data == 'Clear status':
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except Exception:
                    pass
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)
            else:
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except:
                    pass
                UserJobStatus.change_status(
                    request.form.getlist("table_row_checkbox"),
                    form.table_item_action.data)
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)

    else:
        jobs = Jobs.get_jobs_interested("All", page)
        return render_template(
            'jobs.html', jobs=jobs, filter_text="All", form=form)


@app.route('/jobs_applied', methods=['GET', 'POST'])
@app.route('/jobs_applied/<int:page>', methods=['GET', 'POST'])
@login_required
def jobs_applied(page=1):
    form = FilterSearch()
    if request.method == 'POST':
        jobs = Jobs.get_jobs_applied(form.search_term.data, page)
        if request.form['submit'] == 'Filter':
            return render_template(
                'jobs.html',
                jobs=jobs,
                filter_text=form.search_term.data,
                form=form)
        else:
            if form.table_item_action.data == 'Clear status':
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except:
                    pass
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)
            else:
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except:
                    pass
                UserJobStatus.change_status(
                    request.form.getlist("table_row_checkbox"),
                    form.table_item_action.data)
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)

    else:
        jobs = Jobs.get_jobs_applied("All", page)
        return render_template(
            'jobs.html', jobs=jobs, filter_text="All", form=form)


@app.route('/jobs_to_check', methods=['GET', 'POST'])
@app.route('/jobs_to_check/<int:page>', methods=['GET', 'POST'])
@login_required
def jobs_to_check(page=1):
    form = FilterSearch()
    if request.method == 'POST':
        jobs = Jobs.get_jobs_to_check(
            search_term_filter=form.search_term.data,
            page=page)
        if request.form['submit'] == 'Filter':
            return render_template(
                'jobs.html',
                jobs=jobs,
                filter_text=form.search_term.data,
                form=form)
        else:
            if form.table_item_action.data == 'Clear status':
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except Exception:
                    pass
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)
            else:
                try:
                    UserJobStatus.clear_status(
                        request.form.getlist("table_row_checkbox"))
                except Exception:
                    pass
                UserJobStatus.change_status(
                    request.form.getlist("table_row_checkbox"),
                    form.table_item_action.data)
                return render_template(
                    'jobs.html',
                    jobs=jobs,
                    filter_text=form.search_term.data,
                    form=form)

    else:
        jobs = Jobs.get_jobs_to_check(search_term_filter="All", page=page)
        return render_template(
            'jobs.html', jobs=jobs, filter_text="All", form=form)


@app.route('/user_dashboard')
@app.route('/user_dashboard/<username>')
@login_required
def user_dashboard(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_dashboard.html', user=user)

@app.route('/user_profile')
@app.route('/user_profile/<username>', methods=['GET', 'POST'])
@login_required
def user_profile(username):
    form = UserProfile()
    user = User.query.filter_by(username=username).first_or_404()
    criteria = UserJobSearchCriteria.get_job_search_criteria(exclude=False)
    criteria_excluded = UserJobSearchCriteria.get_job_search_criteria(exclude=True)
    location = UserJobSearchLocation.get_job_search_location()
    engine = UserJobSearchEngine.get_job_search_engine()
    content = {
        'username':username,
        'criteria':criteria,
        'criteria_excluded':criteria_excluded,
        'location':location,
        'engine':engine,
        'user':user,
        'form':form
        }
    if request.method == 'POST':
        if request.form['submit'] == 'Add criteria':
            UserJobSearchCriteria.add_job_search_criteria(
                form.job_search_criteria.data, exclude=False)
            return redirect(url_for(
                'user_profile',
                ** content))
        elif request.form['submit'] == 'Remove criteria':
            UserJobSearchCriteria.remove_job_search_criteria(
                request.form['user_profile_search_term'], exclude=False)
            return redirect(url_for(
                'user_profile',
                ** content))
        elif request.form['submit'] == 'Add excluded criteria':
            UserJobSearchCriteria.add_job_search_criteria(
                form.job_search_criteria_exclude.data, exclude=True)
            return redirect(url_for(
                'user_profile',
                ** content))
        elif request.form['submit'] == 'Remove excluded criteria':
            UserJobSearchCriteria.remove_job_search_criteria(
                request.form['user_profile_search_term_excluded'], exclude=True)
            return redirect(url_for(
                'user_profile',
                ** content))
        elif request.form['submit'] == 'Add location':
            UserJobSearchLocation.add_job_search_location(
                form.job_search_location.data)
            return redirect(url_for(
                'user_profile',
                ** content))
        elif request.form['submit'] == 'Remove location':
            UserJobSearchLocation.remove_job_search_location(
                request.form['user_profile_search_location'])
            return redirect(url_for(
                'user_profile',
                ** content))
        elif request.form['submit'] == 'Add engine':
            UserJobSearchEngine.add_job_search_engine(
                form.job_search_engine.data)
            return redirect(url_for(
                'user_profile',
                ** content))
        elif request.form['submit'] == 'Remove engine':
            UserJobSearchEngine.remove_job_search_engine(
                request.form['user_profile_search_engine'])
            return redirect(url_for(
                'user_profile',
                ** content))

        else:
            pass
    else:
        return render_template(
            'user_profile.html',
            ** content)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            username=form.username.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        #flash('Welcome, {}! Please login.'.format(user.username))
        return redirect(url_for('login'))
    return render_template("signup.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            #flash("Logged in successfully as {}.".format(user.username))
            return redirect(
                request.args.get('next')
                or url_for('user_dashboard', username=user.username))
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
