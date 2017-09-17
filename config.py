import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True

SECRET_KEY = '~t\x86\xc9\x1ew\x8bOcX\x85O\xb6\xa2\x11kL\xd1\xce\x7f\x14<y\x9e'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,
                                                      'db/SERENITY4.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
