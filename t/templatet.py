from eden.template import (
	new_templatelookup, 
	render_template, 
	setup_template )



import unittest
import os.path



class TemplateTest(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), 'views')

    def test_new_templatelookup_reander(self):

        lookup = new_templatelookup([self.path])
        template = lookup.get_template('test.html')
        assert template.render(name='world') == u'Hello world'

    def test_render_template(self):
        setup_template([self.path])
        assert render_template('test.html', name='world') == u'Hello world'



if __name__ == '__main__':

    unittest.main(verbosity=2)