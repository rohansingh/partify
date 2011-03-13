'''
Created on Jan 17, 2011

@author: Rohan
'''

import cherrypy
from cherrypy import request

from partify.api import Api

class Root:
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/index.html")

cherrypy.config.update('partify/cherrypy.conf')
    
cherrypy.tree.mount(Root(), '/', config='partify/root.conf')
cherrypy.tree.mount(Api(), '/api', config='partify/api.conf')

cherrypy.engine.start()