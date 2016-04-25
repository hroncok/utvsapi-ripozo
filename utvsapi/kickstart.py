from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from ripozo_sqlalchemy import SessionHandler
from sqlalchemy.engine.url import URL


app = Flask(__name__)
url = URL('mysql', query={'read_default_file': './mysql.cnf'})
app.config['SQLALCHEMY_DATABASE_URI'] = url
db = SQLAlchemy(app)
session_handler = SessionHandler(db.session)
resources = []
