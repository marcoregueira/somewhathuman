from __future__ import absolute_import  # Fix 'from .  import x' statements on python 2.6
from flask import Flask, g, jsonify
import sys
import os
import re
import subprocess
import uuid
from makehuman import make_user_dir, get_platform_paths, redirect_standard_streams, init_logging, getCwd, close_standard_streams
# from flask.ext.compress import Compress
app = Flask(__name__, static_folder='static', static_url_path='')
# Compress(app)
#app.config['DEBUG'] = True
#app.debug = True
# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


def set_sys_path():
    """
    Append local module folders to python search path.
    """
    #[BAL 07/11/2013] make sure we're in the right directory
    if sys.platform != 'darwin': # Causes issues with py2app builds on MAC
        os.chdir(getCwd())
    syspath = ["./", "./lib", "./apps", "./shared", "./apps/gui", "./core", "./web", "./plugins"]
    syspath.extend(sys.path)
    sys.path = syspath

#@app.before_request
#def set_global_objects():
#    set_sys_path()
@app.route('/mh')
def mh():
    pass

@app.route('/getmodel', methods=['POST'])
def result():
    #weight = float(request.forms.get('weight').upper())
    #muscle = float(request.forms.get('muscle').upper())
    #chest = float(request.forms.get('chest').upper())
    #hip = float(request.forms.get('hip').upper())
    #waist = float(request.forms.get('waist').upper())
    #age = float(request.forms.get('age').upper())

    set_sys_path()

    from core import Globals, G
    g.G = Globals()
    
    make_user_dir()
    get_platform_paths()
    redirect_standard_streams()
    init_logging()

    from core import G
    G.args = dict()

    from mhmain import MHApplication
    application = MHApplication()
    application.startupSequence()
    
    from webfunctions import support, webfunctions

    id = str(uuid.uuid4())
    directory = os.path.dirname(os.path.realpath(__file__)) + '/static/models/' + id
    os.makedirs(directory)
    filename = directory + '/model.obj'
    support.exportObj(filename)


    #clean up
    close_standard_streams()
    return jsonify(model = '/models/' + id + '/model.obj',
                   texture= '/models/' + id + '/model.mtl')

if __name__ == '__main__':
    import os
    host = os.environ.get('SERVER_HOST', '0.0.0.0')
    try:
        port = int(os.environ.get('SERVER_PORT', '5556'))
    except ValueError:
        port = 5555
    app.run(host, port)

