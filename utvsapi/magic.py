from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
from ripozo import restmixins, Relationship, RequestContainer
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
resources = []


def default_permission_func(function_name, request, resource):
    '''Default permission handling for almost all resources'''
    return 'cvut:utvs:general:read' in request.client_info['scopes']


def fk_magic(cls, fields):
    '''Create links automagically'''
    fks = tuple(field for field in fields if field.startswith('fk_'))
    rels = []
    for fk in fks:
        unfk = fk[3:]
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
    pks = ('id',)
    rels = fk_magic(cls, fields)

    manager_cls = type(cls.__name__ + 'Manager',
                       (AlchemyManager,),
                       {'fields': fields,
                        'model': cls,
                        'paginate_by': paginate_by})

    pres = getattr(cls, '__preprocessors__', tuple()) + (auth.preprocessor,)
    posts = getattr(cls, '__postprocessors__', tuple()) + (auth.postprocessor,)
    pfunc = getattr(cls, '__permission_func__', default_permission_func)

    resource_cls = type(cls.__name__ + 'Resource',
                        (restmixins.RetrieveRetrieveList,),
                        {'manager': manager_cls(session_handler),
                         'resource_name': cls.__name__.lower() + 's',
                         'pks': pks,
                         '_relationships': rels,
                         'preprocessors': pres,
                         'postprocessors': posts,
                         'permission_func': pfunc})

    resources.append(resource_cls)
    return cls


def get_related(resource, name):
    '''Get related resource of a resource by name'''
    for related_resource in resource.related_resources:
        if related_resource.name == name:
            resource = related_resource.resource
            # Unfortunately this resource only contains it's ID
            # So we need to construct a request for the full resource
            request = RequestContainer(url_params=resource.properties)
            # We don't want to cycle trough auth again
            request.bypass_auth = True
            # Get the "full" resource
            resource = resource.retrieve(request)
            return resource
