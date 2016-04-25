from flask_ripozo import FlaskDispatcher
from ripozo import adapters

from utvsapi.models import app, resources


dispatcher = FlaskDispatcher(app, url_prefix='/')
dispatcher.register_resources(*resources)
dispatcher.register_adapters(adapters.HalAdapter, adapters.SirenAdapter,
                             adapters.JSONAPIAdapter, adapters.BasicJSONAdapter)
