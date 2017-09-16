from datetime import datetime

from sqlalchemy import desc, and_, or_
from flask_login import UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from serenity4 import app, db, login_manager, JOBS_PER_PAGE

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    company = db.Column(db.Text)
    location = db.Column(db.Text)
    description = db.Column(db.Text)
    link = db.Column(db.Text)
    search_term = db.Column(db.Text)
    source = db.Column(db.Text)
    date_first_added = db.Column(db.DateTime, default=datetime.utcnow)
    expired = db.Column(db.Boolean, default=False)
    discovery_count = db.Column(db.Integer, default=0)
    last_date_found = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.relationship("UserJobStatus", backref="jobs", lazy='dynamic')

    @staticmethod
    def get_jobs_all():
        return Jobs.query \
                    .order_by(desc(Jobs.date_first_added))

    @staticmethod
    def get_jobs_filtered(search_term_filter,page):
        if search_term_filter == 'All':
            return Jobs.query \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .filter(Jobs.search_term == search_term_filter) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)

    @staticmethod
    def get_jobs_not_interested(search_term_filter,page):
        if search_term_filter == 'All':
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(UserJobStatus.status == "Not Interested") \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(and_(Jobs.search_term == search_term_filter, \
                                     UserJobStatus.status == "Not Interested")) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)

    @staticmethod
    def get_jobs_interested(search_term_filter,page):
        if search_term_filter == 'All':
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(UserJobStatus.status == "Interested") \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(and_(Jobs.search_term == search_term_filter, \
                                     UserJobStatus.status == "Interested")) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)

    @staticmethod
    def get_jobs_applied(search_term_filter,page):
        if search_term_filter == 'All':
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(UserJobStatus.status == "Applied") \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(and_(Jobs.search_term == search_term_filter, \
                                     UserJobStatus.status == "Applied")) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)

    @staticmethod
    def get_jobs_to_check(search_term_filter,page):
        job_status = [x[0] for x in UserJobStatus.query.with_entities(UserJobStatus.job_id).all()]
        if search_term_filter == 'All':
            return Jobs.query \
                        .outerjoin(UserJobStatus) \
                        .filter(UserJobStatus.status.is_(None)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .outerjoin(UserJobStatus) \
                        .filter(and_(Jobs.search_term == search_term_filter, \
                                     UserJobStatus.status.is_(None))) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)


    @staticmethod
    def get_unique_search_terms():
        return Jobs.query \
                    .with_entities(Jobs.search_term) \
                    .distinct() \
                    .order_by('search_term')

    @staticmethod
    def get_search_term_choices():
        search_term_choices = [('All','All')]
        search_term_choices.extend((x.search_term,x.search_term) for x in Jobs.get_unique_search_terms())
        return search_term_choices

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    password_hash = db.Column(db.String)
    status = db.Column(db.Boolean, default=True)
    job_id = db.relationship('Jobs', backref='user', lazy='dynamic')
    job_status = db.relationship('UserJobStatus', backref='user', lazy='dynamic')
    search_terms = db.relationship('UserJobSearchCriteria', backref='user', lazy='dynamic')
    search_location = db.relationship('UserJobSearchLocation', backref='user', lazy='dynamic')
    search_engines = db.relationship('UserJobSearchEngines', backref='user', lazy='dynamic')


    def __init__(self, name,username,email,password):
        self.name = name
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return "{}".format(self.username)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get_by_username(username):
        user = User.query \
                    .filter_by(username=str(username)) \
                    .first()
        return user

    @staticmethod
    def get_id_by_username(username):
        user = User.query \
                    .filter_by(username=str(username)) \
                    .first()
        return user.id

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(userid):
        return User.query \
                    .get(int(userid))

    @staticmethod
    def add_new_user(name,username,email,password):
        new_user = User(name,username,email,password)
        db.session.add(new_user)
        db.session.commit()
        return True

class UserJobStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    status = db.Column(db.String(180))
    status_changed = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, default=0)

    def __init__(self, user_id, job_id ,status = None):
        if status is None:
            self.user_id = user_id
            self.job_id = job_id
        else:
            self.user_id = user_id
            self.job_id = job_id
            self.status = status

    def __repr__(self):
        return "{}".format(self.status)

    @staticmethod
    def change_status(job_id ,status):
        logged_user = User.get_id_by_username(current_user)
        for job in job_id:
            job_status = UserJobStatus(logged_user,job,status)
            db.session.add(job_status)
        db.session.commit()

    @staticmethod
    def clear_status(job_id):
        logged_user = User.get_id_by_username(current_user)
        for job in job_id:
            status = UserJobStatus.query \
                                    .filter(and_(UserJobStatus.job_id == job,UserJobStatus.user_id == logged_user)) \
                                    .first()
            try:
                db.session.delete(status)
            except:
                pass
        db.session.commit()

class UserJobSearchCriteria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_criteria = db.Column(db.String(40))
    exclude = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, search_criteria,exclude = None):
            self.user_id = user_id
            self.search_criteria = search_criteria
            self.exclude = exclude

    def __repr__(self):
        return "{%s,%s}".format(self.search_criteria,self.exclude)

    @staticmethod
    def get_job_search_criteria():
        logged_user = User.get_id_by_username(current_user)
        return UserJobSearchCriteria.query \
                                    .filter(UserJobSearchCriteria.user_id == logged_user) \
                                    .order_by(UserJobSearchCriteria.search_criteria)

    @staticmethod
    def add_job_search_criteria(search_criteria, exclude = None):
        logged_user = User.get_id_by_username(current_user)
        new_criteria = UserJobSearchCriteria(logged_user,search_criteria,exclude)
        db.session.add(new_criteria)
        db.session.commit()

class UserJobSearchLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_location = db.Column(db.String(40))

    def __init__(self, user_id, search_location):
            self.user_id = user_id
            self.search_location = search_criteria

    def __repr__(self):
        return "{}".format(self.search_criteria)

class UserJobSearchEngines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_engine = db.Column(db.String(40))

    def __init__(self, user_id, search_engine):
            self.user_id = user_id
            self.search_engine = search_engine

    def __repr__(self):
        return "{}".format(self.search_engine)
