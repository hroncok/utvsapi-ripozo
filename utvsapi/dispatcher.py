from flask_ripozo import FlaskDispatcher
from ripozo import adapters

from utvsapi.magic import app
from utvsapi.models import resources


dispatcher = FlaskDispatcher(app, url_prefix='/')
dispatcher.register_resources(*resources)
dispatcher.register_adapters(adapters.HalAdapter,
                             adapters.SirenAdapter,
                             adapters.JSONAPIAdapter,
                             adapters.BasicJSONAdapter)
