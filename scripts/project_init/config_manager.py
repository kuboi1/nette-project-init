import os
import pickle

class ConfigManager:
    def __init__(self, conf_path: str) -> None:
        self.conf_path = conf_path

    def save_configs(self, conf_dict: dict) -> None:
        with open(self.conf_path, 'wb') as f:
            configs = dict(conf_dict)
            # Clear passwords for security reasons
            configs['db_password'] = ''
            configs['ftp_password'] = ''
            pickle.dump(configs, f)
    
    def load_configs(self, force_default=False) -> dict:
        conf_dict = {
            'clone_repo'        : True,
            'repo_link'         : 'https://github.com/visualio/accolade-web-2020',
            'git_safedir'       : True,
            'projects_f_path'   : '..\\..\\projects',
            'project_path'      : '..\\..\\projects\\accolade-web-2020',
            'local_configs'     : True,
            'db_import'         : True,
            'db_host'           : 'localhost',
            'db_user'           : 'root',
            'db_password'       : '',
            'db_name'           : 'accoladeeu',
            'db_file'           : '..\\..\\databases\\accoladeeu.sql',
            'create_vhost'      : False,
            'host'              : 'http://accolade-web.local',
            'ftp_connection'    : True,
            'path_local_dir'    : True,
            'ftp_local_dir'     : '..\\..\\projects\\accolade-web-2020',
            'ftp_name'          : 'accolade',
            'ftp_host'          : 'www.accolade.eu.uvirt96.active24.cz',
            'ftp_username'      : 'accoladeeu1',
            'ftp_password'      : '',
            'composer'          : True,
            'npm'               : True,
            'build'             : True
        }

        if force_default:
            return conf_dict

        if os.path.exists(self.conf_path):
            with open(self.conf_path, 'rb') as f:
                return pickle.load(f)
        else:
            self.save_configs(conf_dict)

        return conf_dict