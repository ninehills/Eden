class App(object):



    def __init__(self):
        self.routes = {}
        self.initialize()



    def initialize(self):
        pass



    def __call__(self, task):
        try:
            handler = self.routes.get(task.action)
            if handler:
                handler(*task.data.get('args' , ()), **task.data.get('kw', {}))
        except:
            pass
            

