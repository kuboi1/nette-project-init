import os
import subprocess as sp
import base64
import json

from project_init.config_manager import ConfigKey
from project_init.sql_manager import SqlManager
from project_init.local_configer import LocalConfiger

class ProjectQuickStarter:
    def __init__(self, conf_dict: dict, settings: dict) -> None:
        self.conf_dict = conf_dict
        self.settings = settings

        if conf_dict[ConfigKey.CLONE_REPO]:
            conf_dict[ConfigKey.PROJECT_PATH] = conf_dict[ConfigKey.PROJECTS_F_PATH] + '\\' + conf_dict[ConfigKey.REPO_LINK].split('/')[-1]
        conf_dict[ConfigKey.PROJECT_PATH].replace('/', '\\')
    
    def init_project(self) -> None:
        if self.conf_dict[ConfigKey.CLONE_REPO]:
            print('Cloning GitHub repo...')
            try:
                self.run_cmd(self.conf_dict[ConfigKey.PROJECTS_F_PATH], ['git', 'clone', self.conf_dict[ConfigKey.REPO_LINK]])
            except:
                print('Error: There was a problem with cloning the GitHub repo.')
                exit()
            print('Finished cloning GitHub repo.')
            print()
        if self.conf_dict[ConfigKey.GIT_SAFEDIR]:
            abs_project_path = os.path.abspath(self.conf_dict[ConfigKey.PROJECT_PATH])
            print(' '.join(['git', 'config', '--global', '--add', 'safe.directory', abs_project_path]))
            self.run_cmd('.', ['git', 'config', '--global', '--add', 'safe.directory', abs_project_path])
            print('Added project as a Git safe directory.')
            print()
        if self.conf_dict[ConfigKey.LOCAL_CONFIGS]:
            local_configer = LocalConfiger(self.conf_dict[ConfigKey.PROJECT_PATH], self.conf_dict[ConfigKey.DB_NAME])
            local_configer.create_configs()
            print()
        if self.conf_dict[ConfigKey.DB_IMPORT]:
            self.import_database()
        if self.conf_dict[ConfigKey.CREATE_VHOST]:
            host = self.conf_dict[ConfigKey.HOST].split('/')[-1]
            self.create_vhosts_entry(host)
            self.create_hosts_entry(host)
        if self.conf_dict[ConfigKey.FTP_CONNECTION]:
            self.create_ftp_connection()
        if self.conf_dict[ConfigKey.COMPOSER]:
            self.install_dependencies('composer')
        if self.conf_dict[ConfigKey.NPM]:
            self.install_dependencies('npm')
        if self.conf_dict[ConfigKey.BUILD]:
            self.run_build_scripts()
        
        print('Project ' + self.conf_dict[ConfigKey.PROJECT_PATH].split('\\')[-1] + ' was initialized.')
    
    def install_dependencies(self, type: str) -> None:
        if type == 'npm' and not self.has_package_json():
            print(f'CAN\'T RUN NPM INSTALL -> no package.json found')
            return
        print(f'Running {type} install...')
        self.run_cmd(self.conf_dict[ConfigKey.PROJECT_PATH], [type, 'i'])
        print(f'Finished running {type} install.')
        print()
    
    def run_build_scripts(self) -> None:
        if not self.has_package_json():
            print(f'CAN\'T RUN BUILD SCRIPTS -> no package.json found')
            return
        
        with open(os.path.join(self.conf_dict[ConfigKey.PROJECT_PATH], 'package.json'), 'r') as pf:
            package_json: dict = json.load(pf)

        if not 'scripts' in package_json:
            print(f'CAN\'T RUN BUILD SCRIPTS -> no scripts found in package.json')
            return
        
        build_scripts = [script for script in package_json['scripts'].keys() if script.startswith("build")]

        if len(build_scripts) == 0:
            print(f'CAN\'T RUN BUILD SCRIPTS -> no build scripts found in package.json')
            return

        print('Running build scripts...')
        for script in build_scripts:
            print(f'Running "npm run {script}"...')
            self.run_cmd(self.conf_dict[ConfigKey.PROJECT_PATH], ['npm', 'run', script])
        print('Finished running build scripts.')
        print()
    
    def run_cmd(self, trgt: str, comm: list) -> None:
        cwd = os.getcwd()
        os.chdir(trgt)
        sp.run(comm, shell=True)
        os.chdir(cwd)
    
    def has_package_json(self) -> bool:
        return 'package.json' in os.listdir(self.conf_dict[ConfigKey.PROJECT_PATH])
    
    def import_database(self) -> None:
        with SqlManager() as db:
            connected = db.connect(
                host=self.conf_dict[ConfigKey.DB_HOST],
                user=self.conf_dict[ConfigKey.DB_USER],
                password=self.conf_dict[ConfigKey.DB_PASSWORD],
            )

            if not connected:
                print('Error: CAN\'T IMPORT DATABASE -> connection failed')
                return
            
            db_created = db.create_database(self.conf_dict[ConfigKey.DB_NAME])

            if not db_created:
                print('Error: CAN\'T IMPORT DATABASE -> sql database creation failed')
                return
            
            db.use_database(self.conf_dict[ConfigKey.DB_NAME])
            sql_imported = db.import_sql_file(os.path.abspath(self.conf_dict[ConfigKey.DB_FILE]))
        
            if not sql_imported:
                print('Error: CAN\'T IMPORT DATABASE -> sql script import failed')
                return
        
        print()
        print(f'Imported {self.conf_dict["db_name"]} database.')
        print()

    def create_vhosts_entry(self, host: str) -> None:
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
                path = os.path.join(os.path.abspath(self.conf_dict[ConfigKey.PROJECT_PATH]).replace('\\', '/'), 'www')
                template_lines[template_lines.index(line)] = line.replace('[project_path]', path)
        f.write('\n')
        f.writelines(template_lines)
        f.close()
        print('Created a vhost entry.')
        print()
    
    def create_hosts_entry(self, host: str) -> None:
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

    def create_ftp_connection(self) -> None:
        print('Setting up FileZilla FTP connection...')
        
        with open('templates\\ftp_template.xml', 'r') as f:
            template_lines = f.readlines()
        variables = {
            '[host_url]'        : self.conf_dict[ConfigKey.FTP_HOST], 
            '[username]'        : self.conf_dict[ConfigKey.FTP_USERNAME], 
            '[password]'        : self.conf_dict[ConfigKey.FTP_PASSWORD], 
            '[connection_name]' : self.conf_dict[ConfigKey.FTP_NAME], 
            '[local_dir_path]'  : os.path.abspath(self.conf_dict[ConfigKey.PROJECT_PATH if self.conf_dict[ConfigKey.PATH_LOCAL_DIR] else 'ftp_local_dir'])
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
    
    def get_match(self, line: str, variables: dict) -> str|None:
        for key in variables:
            if key in line:
                return key
        return None
    
    def get_base64(self, input: str) -> str:
        input_b = input.encode('ascii')
        base64_input_b = base64.b64encode(input_b)
        return base64_input_b.decode('ascii')
    
    def write_to_sitemanager(self, write_lines: list) -> None:
        sitemanager_path = os.path.join(os.getenv('APPDATA'), 'FileZilla\\sitemanager.xml')
        try:
            with open(sitemanager_path, 'r') as rf:
                read_lines = rf.readlines()
                with open(sitemanager_path, 'w') as wf:
                    start_index = 0
                    for line in read_lines:
                        if '</Servers>' in line:
                            start_index = read_lines.index(line)
                            break
                    for i, line in enumerate(write_lines, start=start_index):
                        read_lines.insert(i, line)
                    wf.writelines(read_lines)
        except FileNotFoundError:
            print(f'Error: Sitemanager file not found at ' + os.getenv('APPDATA') + '\\FileZilla\\sitemanager.xml, make sure you have FileZilla installed.')
 