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
            'file_versions_directory' : '../file_versions/',
        }
        return configs[desired_path] 

class TagHandlerConfig(object):
    """docstring for TagHandlerConfig"""
    
    def __init__(self, arg):
        super(TagHandlerConfig, self).__init__()
        self.arg = arg

    # '\..*' = regex to remove invisible files/folders
    def get_parameter(desired_regex):
        configs = {
            'unwanted_file_regex' : '\..*',
            'unwanted_directory_regex' : '\..*',
        }
        return configs[desired_regex] 

class FileHandlerConfig(object):
    """docstring for FileHandlerConfig"""
    
    def __init__(self, arg):
        super(FileHandlerConfig, self).__init__()
        self.arg = arg

    # '\..*' = regex to remove invisible files/folders
    def get_parameter(desired_regex):
        configs = {
            'parseable_files_regex' : '.*\.java$',
            'git_log_file_regex' : '^commit\s([a-z0-9]{40})$|Author:\s(.*?)\<(.*?)\>|Date:\s*([A-Za-z]{3}\s[A-Za-z]{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}\s\d{4}\s.\d{3,4})|(.*?)\|',
        }
        return configs[desired_regex] 