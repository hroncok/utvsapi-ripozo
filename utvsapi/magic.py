from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
from ripozo import restmixins, Relationship
from ripozo_sqlalchemy import AlchemyManager
from ripozo_sqlalchemy import SessionHandler
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship


app = Flask(__name__)
url = URL('mysql', query={'read_default_file': './mysql.cnf'})
app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
session_handler = SessionHandler(db.session)
resources = []


def fk_magic(cls, fields):
    '''Create links automagically'''
    fks = tuple(field for field in fields if field.startswith('fk_'))
    rels = []
    for fk in fks:
        unfk = fk[3:]
        setattr(cls, unfk,
                relationship(unfk.title(),
                             foreign_keys=(cls.__dict__[fk],)))
        rels.append(Relationship(unfk,
                                 property_map={fk: 'id_' + unfk},
                                 relation=unfk.title() + 'Resource'))
    return tuple(rels)  # must be a tuple


def register(cls, paginate_by=20):
    '''Create default Manager and Resource class for model and register it'''
    fields = tuple(f for f in cls.__dict__.keys() if not f.startswith('_'))
    pks = tuple(f for f in fields if f.startswith('id_'))
    rels = fk_magic(cls, fields)

    manager_cls = type(cls.__name__ + 'Manager',
                       (AlchemyManager,),
                       {'fields': fields,
                        'model': cls,
                        'paginate_by': paginate_by})

    resource_cls = type(cls.__name__ + 'Resource',
                        (restmixins.RetrieveRetrieveList,),
                        {'manager': manager_cls(session_handler),
                         'resource_name': cls.__name__.lower() + 's',
                         'pks': pks,
                         '_relationships': rels})

    resources.append(resource_cls)
    return cls
