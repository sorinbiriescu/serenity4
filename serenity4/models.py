from datetime import datetime

from sqlalchemy import desc, and_, or_
from flask_login import UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from serenity4 import app, db, login_manager, JOBS_PER_PAGE
from serenity4.jobs_parser import JobElement, IndeedParser

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


class Jobs(db.Model):
    '''
    Jobs Table
    '''
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
        '''
        Queries table Jobs for all entries.
        '''
        return Jobs.query \
                    .order_by(desc(Jobs.date_first_added))

    @staticmethod
    def get_jobs_filtered(search_term_filter, page):
        '''
        Queries table Jobs for all entries with filters.
        '''
        logged_user = User.get_id_by_username(current_user)
        if search_term_filter == 'All':
            return Jobs.query \
                        .filter(Jobs.user_id == logged_user) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .filter(and_(Jobs.search_term == search_term_filter, \
                                    Jobs.user_id == logged_user)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)

    @staticmethod
    def get_jobs_not_interested(search_term_filter, page):
        logged_user = User.get_id_by_username(current_user)
        if search_term_filter == 'All':
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(and_(UserJobStatus.status == "Not Interested", \
                                    Jobs.user_id == logged_user)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(and_(Jobs.search_term == search_term_filter, \
                                     UserJobStatus.status == "Not Interested", \
                                     Jobs.user_id == logged_user)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)

    @staticmethod
    def get_jobs_interested(search_term_filter, page):
        logged_user = User.get_id_by_username(current_user)
        if search_term_filter == 'All':
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(and_(UserJobStatus.status == "Interested", \
                                    Jobs.user_id == logged_user)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(and_(Jobs.search_term == search_term_filter, \
                                     UserJobStatus.status == "Interested", \
                                     Jobs.user_id == logged_user)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)

    @staticmethod
    def get_jobs_applied(search_term_filter, page):
        logged_user = User.get_id_by_username(current_user)
        if search_term_filter == 'All':
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(and_(UserJobStatus.status == "Applied", \
                                    Jobs.user_id == logged_user)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .join(UserJobStatus) \
                        .filter(and_(Jobs.search_term == search_term_filter, \
                                     UserJobStatus.status == "Applied", \
                                     Jobs.user_id == logged_user)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)

    @staticmethod
    def get_jobs_to_check(search_term_filter, page):
        logged_user = User.get_id_by_username(current_user)
        if search_term_filter == 'All':
            return Jobs.query \
                        .outerjoin(UserJobStatus) \
                        .filter(and_(UserJobStatus.status.is_(None),
                                    Jobs.user_id == logged_user)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
        else:
            return Jobs.query \
                        .outerjoin(UserJobStatus) \
                        .filter(and_(Jobs.search_term == search_term_filter, \
                                     UserJobStatus.status.is_(None), \
                                     Jobs.user_id == logged_user)) \
                        .order_by(desc(Jobs.date_first_added)) \
                        .paginate(page, JOBS_PER_PAGE, False)
    
    @staticmethod
    def get_total_jobs_to_check():

        logged_user = User.get_id_by_username(current_user)
        total_jobs_to_check = Jobs.query \
                                    .outerjoin(UserJobStatus) \
                                    .filter(and_(UserJobStatus.status.is_(None),
                                                Jobs.user_id == logged_user)) \
                                    .count()
        
        return total_jobs_to_check

    @staticmethod
    def get_unique_search_terms():
        return Jobs.query \
                    .with_entities(Jobs.search_term) \
                    .distinct() \
                    .order_by('search_term')

    @staticmethod
    def get_search_term_choices():
        search_term_choices = [('All', 'All')]
        search_term_choices.extend((x.search_term, x.search_term)
                                   for x in Jobs.get_unique_search_terms())
        return search_term_choices

    @staticmethod
    def get_new_jobs():
        logged_user = User.get_id_by_username(current_user)
        search_terms = [item.__dict__['search_criteria'] for item in UserJobSearchCriteria.get_job_search_criteria(exclude=False).all()]
        search_terms_excluded = [item.__dict__['search_criteria'] for item in UserJobSearchCriteria.get_job_search_criteria(exclude=True).all()]
        search_locations = [item.__dict__['search_location'] for item in UserJobSearchLocation.get_job_search_location().all()]
        arguments = {
            'search_terms':search_terms,
            'search_terms_excluded': search_terms_excluded,
            'search_locations': search_locations,
            'result_limit': 40
            }
        job_results = IndeedParser(**arguments).parse_queries()

        for entry in job_results:
            if not Jobs.query \
                        .filter(and_(Jobs.title == entry.title,\
                                Jobs.description == entry.description,\
                                Jobs.user_id == logged_user)) \
                        .first():

                db.session \
                    .add(Jobs( \
                        title=entry.title, \
                        company=entry.company, \
                        location=entry.location, \
                        description=entry.description, \
                        link=entry.link, \
                        search_term=(entry.search_term).replace("+", " ").title(), \
                        source=entry.source, \
                        user_id=logged_user))

            else:
                duplicate = Jobs.query \
                                .filter(and_(Jobs.title == entry.title, \
                                            Jobs.description == entry.description, \
                                            Jobs.user_id == logged_user)) \
                                .first()
                duplicate.discovery_count += 1
                duplicate.last_date_found = datetime.utcnow()
            db.session.commit()


class User(db.Model, UserMixin):
    '''
    User Table
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    password_hash = db.Column(db.String)
    status = db.Column(db.Boolean, default=True)
    last_job_fetch = db.Column(db.DateTime, default=datetime.utcnow)
    job_id = db.relationship('Jobs', backref='user', lazy='dynamic')
    job_status = db.relationship('UserJobStatus', backref='user', lazy='dynamic')
    search_terms = db.relationship('UserJobSearchCriteria', backref='user', lazy='dynamic')
    search_location = db.relationship('UserJobSearchLocation', backref='user', lazy='dynamic')
    search_engines = db.relationship('UserJobSearchEngine', backref='user', lazy='dynamic')

    def __init__(self, name, username, email, password):
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
        '''
        Returns User.id if supplied with User.username
        '''
        user = User.query \
                    .filter_by(username=str(username)) \
                    .first()
        return int(user.id)

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
    def add_new_user(name, username, email, password):
        new_user = User(name, username, email, password)
        db.session.add(new_user)
        db.session.commit()
        return True

    @staticmethod
    def get_last_job_fetch():
        logged_user = User.get_id_by_username(current_user)
        date_last_fetch = User.query \
                                .filter(User.id == logged_user) \
                                .first()
        return date_last_fetch.last_job_fetch.strftime('%d %b %Y %H:%M')

    @staticmethod
    def update_last_job_fetch():
        logged_user = User.get_id_by_username(current_user)
        date_last_fetch = User.query \
                                .filter(User.id == logged_user) \
                                .first()
        date_last_fetch.last_job_fetch = datetime.utcnow()
        db.session.commit()
        return date_last_fetch.last_job_fetch.strftime('%d %b %Y %H:%M')


class UserJobStatus(db.Model):
    '''
    Table with user job statuses
    '''
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    status = db.Column(db.String(180))
    status_changed = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, default=0)

    def __init__(self, user_id, job_id, status=None):
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
    def change_status(job_id, status):
        logged_user = User.get_id_by_username(current_user)
        for job in job_id:
            job_status = UserJobStatus(logged_user, job, status)
            db.session.add(job_status)
        db.session.commit()

    @staticmethod
    def clear_status(job_id):
        logged_user = User.get_id_by_username(current_user)
        for job in job_id:
            status = UserJobStatus.query \
                                    .filter(and_(UserJobStatus.job_id == job,
                                                 UserJobStatus.user_id == logged_user)) \
                                    .first()
            try:
                db.session.delete(status)
            except Exception:
                pass
        db.session.commit()

    @staticmethod
    def get_total_jobs_applied():
        logged_user = User.get_id_by_username(current_user)
        total_jobs_applied = UserJobStatus.query \
                                            .filter(and_(UserJobStatus.status == 'Applied',
                                                        UserJobStatus.user_id == logged_user)) \
                                            .count()
        return total_jobs_applied

    @staticmethod
    def get_total_jobs_interested():
        logged_user = User.get_id_by_username(current_user)
        total_jobs_interested = UserJobStatus.query \
                                            .filter(and_(UserJobStatus.status == 'Interested',
                                                        UserJobStatus.user_id == logged_user)) \
                                            .count()
        return total_jobs_interested

    @staticmethod
    def last_job_update():
        logged_user = User.get_id_by_username(current_user)
        last_job_update = UserJobStatus.query \
                                            .with_entities(UserJobStatus.status_changed) \
                                            .filter(and_(UserJobStatus.status == 'Applied',
                                                         UserJobStatus.user_id == logged_user)) \
                                            .order_by(desc(UserJobStatus.status_changed)) \
                                            .first()
        if not last_job_update:
            return None
        else:
            return last_job_update.status_changed.strftime('%d %b %Y')

class UserJobSearchCriteria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_criteria = db.Column(db.String(40))
    exclude = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, search_criteria, exclude):
        self.user_id = user_id
        self.search_criteria = search_criteria
        self.exclude = exclude

    def __repr__(self):
        return "'%s'" % (self.search_criteria)

    @staticmethod
    def get_job_search_criteria(exclude):
        logged_user = User.get_id_by_username(current_user)
        return UserJobSearchCriteria.query \
                                    .filter(and_(UserJobSearchCriteria.user_id == logged_user,
                                                 UserJobSearchCriteria.exclude == exclude)) \
                                    .order_by(UserJobSearchCriteria.search_criteria) \

    @staticmethod
    def add_job_search_criteria(search_criteria, exclude):
        logged_user = User.get_id_by_username(current_user)
        new_criteria = UserJobSearchCriteria(logged_user, search_criteria, exclude)
        db.session.add(new_criteria)
        db.session.commit()

    @staticmethod
    def remove_job_search_criteria(search_criteria, exclude):
        '''
        remove_job _search_criteria(search_criteria,exclude=False)
        ------ 
        Removes a job search criteria from a user's UserJobSearchCriteria table.
        Takes a criteria ID as an argument, get the current logged in user and remove the criteria.
        '''
        logged_user = User.get_id_by_username(current_user)
        entry = UserJobSearchCriteria.query \
                    .filter(and_(UserJobSearchCriteria.id == search_criteria,
                                UserJobSearchCriteria.user_id == logged_user,
                                UserJobSearchCriteria.exclude == exclude)) \
                    .first()
        try:
            db.session.delete(entry)
        except:
            pass
        db.session.commit()


class UserJobSearchLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_location = db.Column(db.String(40))

    def __init__(self, user_id, search_location):
        self.user_id = user_id
        self.search_location = search_location

    def __repr__(self):
        return "{}".format(self.search_location)

    @staticmethod
    def get_job_search_location():
        logged_user = User.get_id_by_username(current_user)
        return UserJobSearchLocation.query \
                                    .filter(UserJobSearchLocation.user_id == logged_user) \
                                    .order_by(UserJobSearchLocation.search_location)

    @staticmethod
    def add_job_search_location(search_location, exclude=None):
        logged_user = User.get_id_by_username(current_user)
        new_location = UserJobSearchLocation(logged_user, search_location)
        db.session.add(new_location)
        db.session.commit()

    @staticmethod
    def remove_job_search_location(search_location):
        '''
        remove_job _search_location(search_location)
        ------
        Removes a job search criteria from a user's UserJobSearchCriteria table.
        Takes a location ID as an argument, gets the current logged in user and remove the criteria.
        '''
        logged_user = User.get_id_by_username(current_user)
        entry = UserJobSearchLocation.query \
                    .filter(and_(UserJobSearchLocation.id == search_location,
                                 UserJobSearchLocation.user_id == logged_user)) \
                    .first()
        try:
            db.session.delete(entry)
        except:
            pass
        db.session.commit()


class UserJobSearchEngine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_engine = db.Column(db.String(40))

    def __init__(self, user_id, search_engine):
        self.user_id = user_id
        self.search_engine = search_engine

    def __repr__(self):
        return "{}".format(self.search_engine)

    @staticmethod
    def get_job_search_engine():
        logged_user = User.get_id_by_username(current_user)
        return UserJobSearchEngine.query \
                                    .filter(UserJobSearchEngine.user_id == logged_user) \
                                    .order_by(UserJobSearchEngine.search_engine)

    @staticmethod
    def add_job_search_engine(search_engine, exclude=None):
        logged_user = User.get_id_by_username(current_user)
        new_engine = UserJobSearchEngine(logged_user, search_engine)
        db.session.add(new_engine)
        db.session.commit()

    @staticmethod
    def remove_job_search_engine(search_engine):
        '''
        remove_job _search_location(search_location)
        ------
        Removes a job search criteria from a user's UserJobSearchCriteria table.
        Takes a location ID as an argument, gets the current logged in user and remove the criteria.
        '''
        logged_user = User.get_id_by_username(current_user)
        entry = UserJobSearchEngine.query \
                    .filter(and_(UserJobSearchEngine.id == search_engine,
                                 UserJobSearchEngine.user_id == logged_user)) \
                    .first()
        try:
            db.session.delete(entry)
        except:
            pass
        db.session.commit()
