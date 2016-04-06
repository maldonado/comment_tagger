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
            'nlp_directory' : '../nlp_classifier/',
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

class NLPHandlerConfig(object):
    
    """docstring for NLPHandlerConfig"""
    
    def __init__(self, arg):
        super(NLPHandlerConfig, self).__init__()
        self.arg = arg

    def get_parameter(desired_key):
        configs = {
            'training_dataset_name'     : 'classified_seq.train',
            'test_dataset_name'         : 'classified_seq.test',
            'classification_types'      : [('DESIGN'),('REQUIREMENT'),('WITHOUT_CLASSIFICATION')],
            'comment_text_exact_regex'  : '(.+?)\t',
            'output_regex'              : '(WITHOUT_CLASSIFICATION|DESIGN|REQUIREMENT)', 
            'nlp_classifier_memory_use' : '-mx6144m',
            'training_projects'         : [('apache-ant-1.7.0'), ('emf-2.4.1'), ('jruby-1.4.0'), ('apache-jmeter-2.10'), ('jfreechart-1.0.19'), ('argouml'), ('hibernate-distribution-3.3.2.GA'), ('sql12'), ('jEdit-4.2'), ('columba-1.4-src')],
            
        }
        return configs[desired_key] 
        
class TDAuthorsHandlerConfig(object):

    """docstring for TDAuthorsHandlerConfig"""

    def __init__(self, arg):
        super(TDAuthorsHandlerConfig, self).__init__()
        self.arg = arg
        
    def get_parameter(desired_key):
        configs = {
            'git_log_file_regex' : '^commit\s([a-z0-9]{40})$|Author:\s(.*?)\<(.*?)\>|Date:\s*([A-Za-z]{3}\s[A-Za-z]{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}\s\d{4}\s.\d{3,4})|(.*?)\|',
        }
        return configs[desired_key] 