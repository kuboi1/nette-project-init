import re

class UI:
    def __init__(self, conf_dict: dict) -> None:
        self.conf_dict = conf_dict

        self.conf_prompts = {
            'clone_repo' : 'Clone project from GitHub repository?',
            'repo_link' : 'GitHub repository link',
            'projects_f_path' : 'Path to your projects directory',
            'project_path' : 'Path to the main project directory',
            'local_configs' : 'Create local config.neon files?',
            'db_name' : 'Name of your local database',
            'create_vhost' : 'Create a virtual host?',
            'host' : 'Host url for vhost',
            'ftp_connection' : 'Setup a FileZilla FTP connection?',
            'path_local_dir' : 'Local directory for FileZilla same as project directory?',
            'ftp_local_dir' : 'Local directory for FileZilla',
            'ftp_name' : 'Name of the FTP connection',
            'ftp_host' : 'FTP host',
            'ftp_username' : 'FTP username',
            'ftp_password' : 'FTP password',
            'composer' : 'Run \'composer install\'?',
            'npm' : 'Run \'npm install\'?',
            'build' : 'Run build scripts?'
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
            if config == 'repo_link':
                while not self.is_github_link(user_input):
                    print('Invalid visu github repository link')
                    user_input = input(f'{self.conf_prompts[config]} [{current_value}]: ')
            self.conf_dict[config] = user_input if not is_bool else (True if user_input == 'y' else False)
        return self.conf_dict
    
    def should_ask_for_config(self, config: str) -> bool:
        conf_dict = self.conf_dict
        match config:
            case 'repo_link' : return conf_dict['clone_repo']
            case 'projects_f_path' : return conf_dict['clone_repo']
            case 'project_path' : return not conf_dict['clone_repo']
            case 'db_name' : return conf_dict['local_configs']
            case 'host' : return conf_dict['create_vhost']
            case 'path_local_dir' : return conf_dict['ftp_connection']
            case 'ftp_local_dir' : return conf_dict['ftp_connection'] and not conf_dict['path_local_dir']
            case 'ftp_name' : return conf_dict['ftp_connection']
            case 'ftp_host' : return conf_dict['ftp_connection']
            case 'ftp_username' : return conf_dict['ftp_connection']
            case 'ftp_password' : return conf_dict['ftp_connection']
        return True
    
    def is_github_link(self, user_input: str) -> bool:
        return bool(re.match(r'https:\/\/github.com\/[^\/]+\/[^\/]+\/?', user_input))