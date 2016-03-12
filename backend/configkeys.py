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
            'parsed_files_directory' : '../parsed_files/',
        }
        return configs[desired_path] 

class TagHandlerConfig(object):
    """docstring for TagHandlerConfig"""
    
    def __init__(self, arg):
        super(TagHandlerConfig, self).__init__()
        self.arg = arg

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

    def get_parameter(desired_regex):
        configs = {
            'parseable_files_regex' : '.*\.java$',
            'git_log_file_regex' : '^commit\s([a-z0-9]{40})$|Author:\s(.*?)\<(.*?)\>|Date:\s*([A-Za-z]{3}\s[A-Za-z]{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}\s\d{4}\s.\d{3,4})|(.*?)\|',
            'git_deleted_log_file_regex' : '^commit\s([a-z0-9]{40})$|Author:\s(.*?)\<(.*?)\>|Date:\s*([A-Za-z]{3}\s[A-Za-z]{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}\s\d{4}\s.\d{3,4})|\sdelete\smode\s100644\s(.*)'
        }
        return configs[desired_regex] 

class HeuristicHandlerConfig(object):
    """docstring for HeuristicHandlerConfig"""
    
    def __init__(self, arg):
        super(HeuristicHandlerConfig, self).__init__()
        self.arg = arg

    def get_parameter(desired_regex):
        configs = {
            'exception_words_to_remove_javadoc_comments_regex' : 'TODO:|FIXME|XXX',
            'exception_words_to_remove_license_comments_regex' : 'TODO:|FIXME|XXX',
            'commented_source_code_regex' : 'else\s*\{|try\s*\{|do\s*\{|finally\s*\{|if\s*\(|for\s*\(|while\s*\(|switch\s*\(|Long\s*\(|Byte\s*\(|Double\s*\(|Float\s*\(|Integer\s*\(|Short\s*\(|BigDecimal\s*\(|BigInteger\s*\(|Character\s*\(|Boolean\s*\(|String\s*\(|assert\s*\(|System.out.|public\s*void|private\s*static\*final|catch\s*\('
        }
        return configs[desired_regex] 




        