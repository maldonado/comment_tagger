class DBConfig(object):
    """docstring for DBConfig"""
    
    def __init__(self, arg):
        super(DBConfig, self).__init__()
        self.arg = arg

        
    def get_parameter(desired_key):
        configs = {
            'db_host' : 'localhost',
            'db_port' : 5432,
            'db_name' : 'comment_classification',
            'db_user' : 'evermal',
            'db_pass' : '',
        }
        return configs[desired_key]

class DiretoryConfig(object):
    """docstring for DiretoryConfig"""
    
    def __init__(self, arg):
        super(DiretoryConfig, self).__init__()
        self.arg = arg
    
    def get_parameter(desired_path):
        configs = {
            'repository_directory' : '../cloned_repositories/',
        }
        return configs[desired_path] 