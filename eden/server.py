from eden.web import WebServer
from eden.template import  render_template
import os.path

class EdenController(object):

    def index(self):
        return render_template('index.html')

    def get(self, name='Test'):
        return "Name: " + name

    def page(self, page=1):
        return 'Page %s' % (page)


class EdenWebServer(WebServer):

    def bootstrap(self):
        self.bootstrap_template()

    def bootstrap_template(self):
        from eden.template import setup_template, template_vars

        template_vars['sitename'] = self.server_name
        template_vars['page_title'] = 'Home'
        path = os.path.dirname(__file__)
        setup_template([
            os.path.join(path, 'views/'),
            os.path.join(path, 'views/layouts/')])
        self.asset('/assets', os.path.join(os.path.dirname(__file__), 'assets'))

    def create_app(self):
        ctl = EdenController()
        m = self.new_route()
        m.mapper.explicit = False
        m.connect('index', '/', controller=ctl, action='index')
        m.connect('get', '/get', controller=ctl, action='get')
        m.connect('page', '/page', controller=ctl, action='page')
        m.connect('page', '/page/:page', controller=ctl, action='page')
        return ctl, m


