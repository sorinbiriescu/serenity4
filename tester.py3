#%%
from __future__ import absolute_import
import models
from serenity4 import app, db, login_manager

test = UserJobSearchLocation.get_job_search_location()

print(test)