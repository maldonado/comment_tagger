import sys

class DBRouter(object):

    to_route_models = ('Repositories', 'ProcessedComments')
    db_to_route = 'comment_classification'

    def db_for_read(self, model, **hints):
        #print >>sys.stderr, (model.__name__)
        if model.__name__ in DBRouter.to_route_models:
            return DBRouter.db_to_route
        else:
            return "default"

    def db_for_write(self, model, **hints):
        if model.__name__ in DBRouter.to_route_models:
            return DBRouter.db_to_route
        else:
            return "default"
