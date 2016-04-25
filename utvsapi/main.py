from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_ripozo import FlaskDispatcher
from ripozo import restmixins, ListRelationship, Relationship, adapters, apimethod
from ripozo_sqlalchemy import AlchemyManager, SessionHandler
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship

app = Flask(__name__)
url = URL('mysql', query={'read_default_file': './mysql.cnf'})
app.config['SQLALCHEMY_DATABASE_URI'] = url
db = SQLAlchemy(app)


PAGINATE_BY = 20

resources = []
session_handler = SessionHandler(db.session)


def register(cls):
    '''Let's not code N*2 useless classes'''
    fields = tuple(field for field in cls.__dict__.keys() if not field.startswith('_'))
    pks = tuple(field for field in fields if field.startswith('id_'))
    
    # This magic creates links
    fks = tuple(field for field in fields if field.startswith('fk_'))
    rels = []
    for fk in fks:
        unfk = fk[3:]
        setattr(cls, unfk, relationship(unfk.title(), foreign_keys=(cls.__dict__[fk],)))
        rels.append(Relationship(unfk, property_map={fk: 'id_' + unfk}, relation=unfk.title() + 'Resource'))
    rels = tuple(rels)  # must be a tuple


    manager_cls = type(cls.__name__ + 'Manager',
                       (AlchemyManager,),
                       {'fields': fields,
                        'model': cls,
                        'paginate_by': PAGINATE_BY})

    resource_cls = type(cls.__name__ + 'Resource',
                       (restmixins.RetrieveRetrieveList,),
                       {'manager': manager_cls(session_handler),
                        'resource_name': cls.__name__.lower() + 's',
                        'pks': pks,
                        '_relationships': rels})

    resources.append(resource_cls)
    return cls


@register
class Destination(db.Model):
    __tablename__ = 'v_destination'

    id_destination = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)


@register
class Hall(db.Model):
    __tablename__ = 'v_hall'

    id_hall = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)


@register
class Teacher(db.Model):
    __tablename__ = 'v_lectors'

    id_teacher = db.Column('id_lector', db.Integer, primary_key=True)
    title_before = db.Column(db.String)
    name = db.Column(db.String)
    surname = db.Column(db.String)
    title_behind = db.Column(db.String)
    personal_number = db.Column('pers_number', db.String)
    url = db.Column(db.String)


@register
class Sport(db.Model):
    __tablename__ = 'v_sports'

    id_sport = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String)
    sport = db.Column(db.String)
    description = db.Column(db.String)


@register
class Enrollment(db.Model):
    __tablename__ = 'v_students'

    id_enrollment = db.Column('id_student', db.Integer, primary_key=True)
    personal_number = db.Column(db.Integer)
    kos_kod = db.Column(db.String)
    semester = db.Column(db.String)
    registration_date = db.Column(db.DateTime)
    tour = db.Column(db.Boolean)
    kos_code = db.Column(db.Boolean)

    fk_course = db.Column('utvs', db.Integer,
                       db.ForeignKey('v_subjects.id_subjects'))


@register
class Course(db.Model):
    __tablename__ = 'v_subjects'

    id_course = db.Column('id_subjects', db.Integer,
                          primary_key=True)
    shortcut = db.Column(db.String)
    day = db.Column(db.Integer)
    begin = db.Column(db.String)
    end = db.Column(db.String)
    notice = db.Column(db.String)
    semester = db.Column(db.Integer)

    fk_sport = db.Column('sport', db.Integer, db.ForeignKey('v_sports.id_sport'))
    fk_hall = db.Column('hall', db.Integer, db.ForeignKey('v_hall.id_hall'))
    fk_teacher = db.Column('lector', db.Integer,
                        db.ForeignKey('v_lectors.id_lector'))


dispatcher = FlaskDispatcher(app, url_prefix='/')
dispatcher.register_resources(*resources)
dispatcher.register_adapters(adapters.HalAdapter, adapters.SirenAdapter,
                             adapters.JSONAPIAdapter, adapters.BasicJSONAdapter)

if __name__ == '__main__':
    app.run(debug=True)

