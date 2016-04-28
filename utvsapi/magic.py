from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
from ripozo import restmixins, Relationship
from ripozo_sqlalchemy import AlchemyManager
from ripozo_sqlalchemy import SessionHandler
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship

from utvsapi import auth


app = Flask(__name__)
url = URL('mysql', query={'read_default_file': './mysql.cnf'})
app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
session_handler = SessionHandler(db.session)
resources = {}


def default_permission_func(function_name, request, resource):
    '''Default permission handling for almost all resources'''
    return 'cvut:utvs:general:read' in request.client_info['scopes']


def fk_magic(cls, fields):
    '''Create links automagically'''
    fks = tuple(field for field in fields if field.endswith('_id'))
    rels = []
    for fk in fks:
        unfk = fk[:-3]
        setattr(cls, unfk,
                relationship(unfk.title(),
                             foreign_keys=(getattr(cls, fk),)))
        rels.append(Relationship(unfk,
                                 property_map={fk: 'id'},
                                 relation=unfk.title() + 'Resource'))
    return tuple(rels)  # must be a tuple


def register(cls, paginate_by=20):
    '''Create default Manager and Resource class for model and register it'''
    fields = tuple(f for f in cls.__dict__.keys() if not f.startswith('_'))
    pks = getattr(cls, '__pks__', ('id',))
    rels = fk_magic(cls, fields)

    manager_cls = type(cls.__name__ + 'Manager',
                       (AlchemyManager,),
                       {'fields': fields,
                        'model': cls,
                        'paginate_by': paginate_by})

    pres = (auth.preprocessor,) + getattr(cls, '__preprocessors__', tuple())
    posts = getattr(cls, '__postprocessors__', tuple())

    resource_cls = type(cls.__name__ + 'Resource',
                        (restmixins.RetrieveRetrieveList,),
                        {'manager': manager_cls(session_handler),
                         'resource_name': cls.__name__.lower() + 's',
                         'pks': pks,
                         '_relationships': rels,
                         'preprocessors': pres,
                         'postprocessors': posts})

    resources[cls.__name__] = resource_cls
    return cls


def onemany(func):
    '''
    A decorator for postprocessors in order to run a given function
    an all resources
    '''
    def processor(cls, function_name, request, resource):
        if function_name == 'retrieve':
            return func(cls, function_name, request, resource)
        if function_name == 'retrieve_list':
            for one in resource.related_resources[0].resource:
                func(cls, 'retrieve', request, one)
    return processor
