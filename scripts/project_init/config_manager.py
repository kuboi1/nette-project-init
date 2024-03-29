import os
import pickle
from enum import Enum

class ConfigKey(Enum):
    CLONE_REPO = 'clone_repo'
    REPO_LINK = 'repo_link'
    GIT_SAFEDIR = 'git_safedir'
    PROJECTS_F_PATH = 'projects_f_path'
    PROJECT_PATH = 'project_path'
    LOCAL_CONFIGS = 'local_configs'
    DB_IMPORT = 'db_import'
    DB_HOST = 'db_host'
    DB_USER = 'db_user'
    DB_PASSWORD = 'db_password'
    DB_NAME = 'db_name'
    DB_FILE = 'db_file'
    CREATE_VHOST = 'create_vhost'
    HOST = 'host'
    FTP_CONNECTION = 'ftp_connection'
    PATH_LOCAL_DIR = 'path_local_dir'
    FTP_LOCAL_DIR = 'ftp_local_dir'
    FTP_NAME = 'ftp_name'
    FTP_HOST = 'ftp_host'
    FTP_USERNAME = 'ftp_username'
    FTP_PASSWORD = 'ftp_password'
    COMPOSER = 'composer'
    NPM = 'npm'
    BUILD = 'build'


class ConfigManager:
    def __init__(self, conf_path: str) -> None:
        self.conf_path = conf_path

    def save_configs(self, conf_dict: dict) -> None:
        with open(self.conf_path, 'wb') as f:
            configs = dict(conf_dict)
            # Clear passwords for security reasons
            configs[ConfigKey.DB_PASSWORD] = ''
            configs[ConfigKey.FTP_PASSWORD] = ''
            pickle.dump(configs, f)
    
    def load_configs(self, force_default=False) -> dict:
        conf_dict = {
            ConfigKey.CLONE_REPO        : True,
            ConfigKey.REPO_LINK         : 'https://github.com/visualio/accolade-web-2020',
            ConfigKey.GIT_SAFEDIR       : True,
            ConfigKey.PROJECTS_F_PATH   : '..\\..\\projects',
            ConfigKey.PROJECT_PATH      : '..\\..\\projects\\accolade-web-2020',
            ConfigKey.LOCAL_CONFIGS     : True,
            ConfigKey.DB_IMPORT         : True,
            ConfigKey.DB_HOST           : 'localhost',
            ConfigKey.DB_USER           : 'root',
            ConfigKey.DB_PASSWORD       : '',
            ConfigKey.DB_NAME           : 'accoladeeu',
            ConfigKey.DB_FILE           : '..\\..\\databases\\accoladeeu.sql',
            ConfigKey.CREATE_VHOST      : False,
            ConfigKey.HOST              : 'http://accolade-web.local',
            ConfigKey.FTP_CONNECTION    : True,
            ConfigKey.PATH_LOCAL_DIR    : True,
            ConfigKey.FTP_LOCAL_DIR     : '..\\..\\projects\\accolade-web-2020',
            ConfigKey.FTP_NAME          : 'accolade',
            ConfigKey.FTP_HOST          : 'www.accolade.eu.uvirt96.active24.cz',
            ConfigKey.FTP_USERNAME      : 'accoladeeu1',
            ConfigKey.FTP_PASSWORD      : '',
            ConfigKey.COMPOSER          : True,
            ConfigKey.NPM               : True,
            ConfigKey.BUILD             : True
        }

        if force_default:
            return conf_dict

        if os.path.exists(self.conf_path):
            with open(self.conf_path, 'rb') as f:
                return pickle.load(f)
        else:
            self.save_configs(conf_dict)

        return conf_dict