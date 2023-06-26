import shutil
import os
import subprocess as sp
import pickle
import base64
import re

from settings import Settings


# LocalConfiger class creates local config neon files in the projects app\config folder
class LocalConfiger:
    def __init__(self, project_path, db_name):
        self.config_path = project_path + '\\app\\config\\'
        self.multiple_configs = self.has_multiple_configs()
        self.db_name = db_name
        self.created_files = 0
    
    def create_configs(self):
        main_config = 'config.neon' if not self.multiple_configs else 'main.neon'

        print('Creating local config files...')

        if not os.path.exists(self.config_path + main_config):
            print(f'EXCEPTION: {main_config} file found at {os.path.abspath(self.config_path)}{main_config}')
            return
        
        if not self.multiple_configs:
            trgt = self.config_path + 'config.local.neon'
            self.create_db_config(trgt)
        else:
            self.multiple_configs_process()
        
        print('Successfully created ' +  (f'{self.created_files} local config files.' if self.created_files > 1 else 'config.local.neon file.'))
    
    def has_multiple_configs(self):
        return os.path.exists(self.config_path + 'main.neon')

    def multiple_configs_process(self):
        all_configs = self.get_configs_from_main()
        local_configs = []
        
        for config in all_configs:
            split_config = config.split('.')
            if len(split_config) < 3:
                continue
            if split_config[1] == 'local':
                local_configs.append(config)

        # Creates all local config files by duplicating the original configs
        for local_config in local_configs:
            split_local_config = local_config.split('.')
            config = split_local_config[0] + '.' + split_local_config[2]
            src = self.config_path + config
            trgt = self.config_path + local_config
            if split_local_config[0] == 'database':
                self.create_db_config(trgt)
                continue
            try:
                shutil.copyfile(src, trgt)
            except FileNotFoundError:
                print(f'EXCEPTION: There was an error with copying a config file to {os.path.abspath(self.config_path)}\\{local_config}')
                return
            self.created_files += 1

    def get_configs_from_main(self):
        try:
            main_config = open(self.config_path + 'main.neon')
        except FileNotFoundError:
            print(f'EXCEPTION: Main config not found at {os.path.abspath(self.config_path)}\\main.neon')
            exit()
        all_configs = []
        in_section = False
        while True:
            line = main_config.readline()
            if line[:8] != 'includes' and not in_section:
                continue
            if line[:8] == 'includes':
                in_section = True
                continue
            line = line.strip()
            if len(line) == 0 or line[0] != '-':
                break
            all_configs.append(line.replace('-', '').strip())
        return all_configs
    
    def create_db_config(self, trgt):
        db_lines = [
            'database:\n',
           f'    dsn: \'mysql:host=localhost;dbname={self.db_name}\'\n',
            '    user: root\n',
            '    password: \n'
        ]
        with open(trgt, 'w') as f:
            f.writelines(db_lines)
        self.created_files += 1


class UI:
    def __init__(self):
        self.conf_dict = {}

        self.conf_prompts = {
            'clone_repo' : 'Clone project from GitHub repository?',
            'repo_link' : 'GitHub repository link',
            'projects_f_path' : 'Path to your projects directory',
            'project_path' : 'Path to the main project directory',
            'local_configs' : 'Create local config.neon files?',
            'db_name' : 'Name of your local database',
            'env_file' : 'Create .env file?',
            'create_vhost' : 'Create a virtual host?',
            'host' : 'Host url for vhost and .env file',
            'ftp_connection' : 'Setup a FileZilla FTP connection?',
            'path_local_dir' : 'Local directory for FileZilla same as project directory?',
            'ftp_local_dir' : 'Local directory for FileZilla',
            'ftp_name' : 'Name of the FTP connection',
            'ftp_host' : 'FTP host',
            'ftp_username' : 'FTP username',
            'ftp_password' : 'FTP password',
            'composer' : 'Run \'composer install\'?',
            'npm' : 'Run \'npm install\'?'
        }

    def print_intro(self):
        print('Visu Project Initiator')
        print('- configure everything below to get started')
        print('- input y/n for booleans and strings for paths etc.')
        print('- you can press enter with no input to confirm current settings (in square brackets)')
        print()

    def load_configs(self, force_default=False):
        conf_dict = {
            'clone_repo' : True,
            'repo_link' : 'https://github.com/visualio/accolade-web-2020',
            'projects_f_path' : '..\\projects',
            'project_path' : '..\\projects\\accolade-web-2020',
            'local_configs' : True,
            'db_name' : 'accoladeeu',
            'env_file' : True,
            'create_vhost' : False,
            'host' : 'http://accolade-web.local',
            'ftp_connection' : True,
            'path_local_dir' : True,
            'ftp_local_dir' : '..\\projects\\accolade-web-2020',
            'ftp_name' : 'accolade',
            'ftp_host' : 'www.accolade.eu.uvirt96.active24.cz',
            'ftp_username' : 'accoladeeu1',
            'ftp_password' : '',
            'composer' : True,
            'npm' : True
        }

        if force_default:
            self.conf_dict = conf_dict
            return
        
        self.conf_dict = conf_dict

        if os.path.exists('conf.pkl'):
            with open('conf.pkl', 'rb') as f:
                self.conf_dict = pickle.load(f)
        else:
            self.save_configs()

    def get_configs(self):
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
    
    def should_ask_for_config(self, config):
        conf_dict = self.conf_dict
        match config:
            case 'repo_link' : return conf_dict['clone_repo']
            case 'projects_f_path' : return conf_dict['clone_repo']
            case 'project_path' : return not conf_dict['clone_repo']
            case 'db_name' : return conf_dict['local_configs']
            case 'host' : return conf_dict['env_file'] or conf_dict['create_vhost']
            case 'path_local_dir' : return conf_dict['ftp_connection']
            case 'ftp_local_dir' : return conf_dict['ftp_connection'] and not conf_dict['path_local_dir']
            case 'ftp_name' : return conf_dict['ftp_connection']
            case 'ftp_host' : return conf_dict['ftp_connection']
            case 'ftp_username' : return conf_dict['ftp_connection']
            case 'ftp_password' : return conf_dict['ftp_connection']
        return True

    def save_configs(self):
        with open('conf.pkl', 'wb') as f:
            configs = dict(self.conf_dict)
            # Clear ftp password for security reasons
            configs['ftp_password'] = ''
            pickle.dump(configs, f)
    
    def is_github_link(self, user_input):
        return bool(re.match(r'https:\/\/github.com\/visualio\/[^\/]+\/?', user_input))


class ProjectInitializer:
    def __init__(self, conf, settings):
        self.conf = conf
        self.settings = settings

        if conf['clone_repo']:
            conf['project_path'] = conf['projects_f_path'] + '\\' + conf['repo_link'].split('/')[-1]
        conf['project_path'].replace('/', '\\')
    
    def initialize_project(self):
        conf = self.conf
        if conf['clone_repo']:
            print('Cloning GitHub repo...')
            try:
                self.run_cmd(self.conf['projects_f_path'], ['git', 'clone', self.conf['repo_link']])
            except:
                print('Error: There was a problem with cloning the GitHub repo.')
                exit()
            print('Finished cloning GitHub repo.')
            print()
        if conf['local_configs']:
            local_configer = LocalConfiger(conf['project_path'], conf['db_name'])
            local_configer.create_configs()
            print()
        if conf['env_file']:
            self.create_env_file()
            print()
        if conf['create_vhost']:
            host = self.conf['host'].split('/')[-1]
            self.create_vhosts_entry(host)
            self.create_hosts_entry(host)
        if conf['ftp_connection']:
            self.create_ftp_connection()
        if conf['composer']:
            self.install_dependencies('composer')
        if conf['npm']:
            self.install_dependencies('npm')
        
        print('Project ' + self.conf['project_path'].split('\\')[-1] + ' was initialized.')
    
    def install_dependencies(self, type):
        if type == 'npm' and not self.has_package_json():
            print(f'CAN\'T RUN NPM INSTALL -> no package.json found')
            return
        print(f'Running {type} install...')
        self.run_cmd(self.conf['project_path'], [type, 'i'])
        print(f'Finished running {type} install.')
        print()
    
    def run_cmd(self, trgt, comm):
        cwd = os.getcwd()
        os.chdir(trgt)
        sp.run(comm, shell=True)
        os.chdir(cwd)
    
    def has_package_json(self):
        return 'package.json' in os.listdir(self.conf['project_path'])
    
    def create_env_file(self):
        print('Creating .env file...')
        with open(self.conf['project_path'] + '\\.env', 'w') as env_file:
            env_file.write(f'HOST="' + self.conf['host'] + '"')
        print('.env file created.')
    
    def create_vhosts_entry(self, host):
        with open('templates\\vhost_template.txt', 'r') as f:
            template_lines = f.readlines()
        try:
            f = open(f'C:\\wamp64\\bin\\apache\\apache{self.settings["apache_version"]}\\conf\\extra\\httpd-vhosts.conf', 'a')
        except FileNotFoundError:
            print(f'Error: No vhost file found at: C:/wamp64/bin/apache/apache{self.settings["apache_version"]}/conf/extra/httpd-vhosts.conf')
            return
        for line in template_lines:
            if '[host_name]' in line:
                template_lines[template_lines.index(line)] = line.replace('[host_name]', host)
            if '[project_path]' in line:
                template_lines[template_lines.index(line)] = line.replace('[project_path]', os.path.abspath(self.conf['project_path']).replace('\\', '/'))
        f.write('\n')
        f.writelines(template_lines)
        f.close()
        print('Created a vhost entry.')
        print()
    
    def create_hosts_entry(self, host):
        lines = [f'\n127.0.0.1	{host}', f'\n::1	{host}']
        try:
            f = open('C:\\WINDOWS\\system32\\drivers\\etc\\hosts', 'a')
        except Exception:
            print('Error: Access to hosts file denied. Please restart the script with admin permissions if you want to create a vhost.')
            return
        f.writelines(lines)
        f.close()
        print('Created host entry.')
        print()

    def create_ftp_connection(self):
        print('Setting up FileZilla FTP connection...')
        
        with open('templates\\ftp_template.xml', 'r') as f:
            template_lines = f.readlines()
        variables = {
            '[host_url]' : self.conf['ftp_host'], 
            '[username]' : self.conf['ftp_username'], 
            '[password]' : self.conf['ftp_password'], 
            '[connection_name]' : self.conf['ftp_name'], 
            '[local_dir_path]' : os.path.abspath(self.conf['project_path' if self.conf['path_local_dir'] else 'ftp_local_dir'])
        }
        for i in range(len(template_lines)):
            line = template_lines[i]
            key = self.get_match(line, variables)
            if key == None:
                continue
            if key == '[password]':
                password = variables[key]
                template_lines[i] = line.replace(key, self.get_base64(password))
                continue
            template_lines[i] = line.replace(key, variables[key])
        self.write_to_sitemanager(template_lines)
        print('FTP connection setup finished.')
        print()
    
    def get_match(self, line, variables):
        for key in variables:
            if key in line:
                return key
        return None
    
    def get_base64(self, input):
        input_b = input.encode('ascii')
        base64_input_b = base64.b64encode(input_b)
        return base64_input_b.decode('ascii')
    
    def write_to_sitemanager(self, write_lines):
        try:
            f = open(os.getenv('APPDATA') + '\\FileZilla\\sitemanager.xml', 'r')
        except FileNotFoundError:
            print(f'Error: Sitemanager file not found at ' + os.getenv('APPDATA') + '\\FileZilla\\sitemanager.xml, make sure you have FileZilla installed.')
            return
        read_lines = f.readlines()
        f.close()
        f = open(os.getenv('APPDATA') + '\\FileZilla\\sitemanager.xml', 'w')
        start_index = 0
        for line in read_lines:
            if '</Servers>' in line:
                start_index = read_lines.index(line)
                break
        for i, line in enumerate(write_lines, start=start_index):
            read_lines.insert(i, line)
        f.writelines(read_lines)
        f.close()



if __name__ == '__main__':
    ORIGINAL_CWD = os.getcwd()
    os.chdir(os.path.dirname(__file__))

    ui = UI()
    ui.print_intro()
    ui.load_configs(force_default=False)
    conf = ui.get_configs()
    ui.save_configs()
    print()

    settings = Settings()
    settings.load_settings()

    initializer = ProjectInitializer(conf, settings.get_settings())
    initializer.initialize_project()

    os.chdir(ORIGINAL_CWD)

    print('\nDon\'t forget to restart all services on Wamp!\n')
    input('Press enter to exit...')


    
    
    