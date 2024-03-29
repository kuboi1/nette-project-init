import re
from project_init.config_manager import ConfigKey

class UI:
    def __init__(self, conf_dict: dict) -> None:
        self.conf_dict = conf_dict

        self.conf_prompts = {
            ConfigKey.CLONE_REPO        : 'Clone project from GitHub repository?',
            ConfigKey.REPO_LINK         : 'GitHub repository link',
            ConfigKey.GIT_SAFEDIR       : 'Add project as Git safe directory?',
            ConfigKey.PROJECTS_F_PATH   : 'Path to your projects directory',
            ConfigKey.PROJECT_PATH      : 'Path to the main project directory',
            ConfigKey.LOCAL_CONFIGS     : 'Create local config.neon files?',
            ConfigKey.DB_IMPORT         : 'Create local database and import sql script?',
            ConfigKey.DB_HOST           : 'Local database host',
            ConfigKey.DB_USER           : 'Local database user',
            ConfigKey.DB_PASSWORD       : 'Local database password',
            ConfigKey.DB_NAME           : 'Local database name',
            ConfigKey.DB_FILE           : 'Path to sql script you want to import',
            ConfigKey.CREATE_VHOST      : 'Create a WAMP virtual host?',
            ConfigKey.HOST              : 'Host url for WAMP vhost',
            ConfigKey.FTP_CONNECTION    : 'Setup a FileZilla FTP connection?',
            ConfigKey.PATH_LOCAL_DIR    : 'Local directory for FileZilla same as project directory?',
            ConfigKey.FTP_LOCAL_DIR     : 'Local directory for FileZilla',
            ConfigKey.FTP_NAME          : 'Name of the FTP connection',
            ConfigKey.FTP_HOST          : 'FTP host',
            ConfigKey.FTP_USERNAME      : 'FTP username',
            ConfigKey.FTP_PASSWORD      : 'FTP password',
            ConfigKey.COMPOSER          : 'Run \'composer install\'?',
            ConfigKey.NPM               : 'Run \'npm install\'?',
            ConfigKey.BUILD             : 'Run build scripts?'
        }

    def print_intro(self) -> None:
        print('Nette Project Quick Start')
        print('- configure everything below to get started')
        print('- input y/n for booleans and strings for paths etc.')
        print('- you can press enter with no input to confirm current settings (in square brackets)')
        print()

    def get_configs(self) -> dict:
        for config in self.conf_dict:
            if not self.should_ask_for_config(config):
                continue
            current_value = self.conf_dict[config]
            is_bool = type(current_value) == bool
            if is_bool:
                current_value = 'YES' if current_value else 'NO'
            user_input = input(f'{self.conf_prompts[config]} [{current_value}]: ')
            while user_input not in ['y', 'n', ''] and is_bool:
                print('(y/n)')
                user_input = input(f'{self.conf_prompts[config]} [{current_value}]: ')
            if user_input == '':
                continue
            if config == ConfigKey.REPO_LINK:
                while not self.is_github_link(user_input):
                    print('Invalid visu github repository link')
                    user_input = input(f'{self.conf_prompts[config]} [{current_value}]: ')
            self.conf_dict[config] = user_input if not is_bool else (True if user_input == 'y' else False)
        return self.conf_dict
    
    def should_ask_for_config(self, config: ConfigKey) -> bool:
        conf_dict = self.conf_dict
        match config:
            case ConfigKey.REPO_LINK        : return conf_dict[ConfigKey.CLONE_REPO]
            case ConfigKey.GIT_SAFEDIR      : return conf_dict[ConfigKey.CLONE_REPO]
            case ConfigKey.PROJECTS_F_PATH  : return conf_dict[ConfigKey.CLONE_REPO]
            case ConfigKey.PROJECT_PATH     : return not conf_dict[ConfigKey.CLONE_REPO]
            case ConfigKey.DB_HOST          : return conf_dict[ConfigKey.DB_IMPORT]
            case ConfigKey.DB_USER          : return conf_dict[ConfigKey.DB_IMPORT]
            case ConfigKey.DB_PASSWORD      : return conf_dict[ConfigKey.DB_IMPORT]
            case ConfigKey.DB_NAME          : return conf_dict[ConfigKey.LOCAL_CONFIGS] or conf_dict[ConfigKey.DB_IMPORT]
            case ConfigKey.DB_FILE          : return conf_dict[ConfigKey.DB_IMPORT]
            case ConfigKey.HOST             : return conf_dict[ConfigKey.CREATE_VHOST]
            case ConfigKey.PATH_LOCAL_DIR   : return conf_dict[ConfigKey.FTP_CONNECTION]
            case ConfigKey.FTP_LOCAL_DIR    : return conf_dict[ConfigKey.FTP_CONNECTION] and not conf_dict[ConfigKey.PATH_LOCAL_DIR]
            case ConfigKey.FTP_NAME         : return conf_dict[ConfigKey.FTP_CONNECTION]
            case ConfigKey.FTP_HOST         : return conf_dict[ConfigKey.FTP_CONNECTION]
            case ConfigKey.FTP_USERNAME     : return conf_dict[ConfigKey.FTP_CONNECTION]
            case ConfigKey.FTP_PASSWORD     : return conf_dict[ConfigKey.FTP_CONNECTION]
        # default
        return True
    
    def is_github_link(self, user_input: str) -> bool:
        return bool(re.match(r'https:\/\/github.com\/[^\/]+\/[^\/]+\/?', user_input))