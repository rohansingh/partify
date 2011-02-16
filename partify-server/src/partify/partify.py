'''
Created on Jan 17, 2011

@author: Rohan
'''

import cherrypy
from cherrypy import request

from api import Api

import os.path
current_dir = os.path.dirname(os.path.abspath(__file__))

class Root:
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/index.html")

cherrypy.config.update('cherrypy.conf')
    
cherrypy.tree.mount(Root(), '/', config='root.conf')
cherrypy.tree.mount(Api(), '/api', config='api.conf')

cherrypy.engine.start()