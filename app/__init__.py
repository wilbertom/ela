import logging

from flask import Flask, g

from flask_appbuilder import SQLA, AppBuilder
from flask_appbuilder.baseviews import BaseView, expose

#from sqlalchemy.engine import Engine
#from sqlalchemy import event

#from app import db
from app.index import ELAIndexView


logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)


#class HomePageView(MultipleView):
    #views = [DeviceModelView, ProjectModelView]

"""
class HomePageView(BaseView):
    route_base = ''
    default_view = 'index'

    @expose('/')
    def index(self):
      # This method redirects the user to a different page depending on
      # whether the user is authenticated or not:
      self.update_redirect
      if g.user is not None and g.user.is_authenticated():
        if g.user.role.name != app.config['AUTH_ROLE_PUBLIC']:
          return redirect(url_for('UserDBModelView.show', pk=g.user.id))
      else:
        return redirect(url_for('PublicView.home'))
"""

app = Flask(__name__)
app.config.from_object('config')
db = SQLA(app)

appbuilder = AppBuilder(app, db.session, indexview=ELAIndexView)
#appbuilder = AppBuilder(app, db.session, indexview=HomePageView)


"""
Only include this for SQLLite constraints

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""    

from app import models, views
