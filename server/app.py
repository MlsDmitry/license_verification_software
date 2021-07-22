from gino.ext.sanic import Gino
from sanic import Sanic
from . import key_manager



def create_application():
    global db
    
    app = Sanic("Verification_server")

    # app.config.DB_HOST = 'localhost'
    # app.config.DB_DATABASE = 'verification_database'
    
    # setup database
    # db = Gino()
    # db.init_app(app)
    # setup database models
    from . import models
    # generate public and private keys
    key_manager.setup_keys(save_to_file=True)
    
    from . import api
    app.blueprint(api.api_group)

    return app
    
