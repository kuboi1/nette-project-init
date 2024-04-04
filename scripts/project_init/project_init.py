import os
import subprocess as sp
import base64
import json

from project_init.config_manager import ConfigKey
from project_init.sql_manager import SqlManager
from project_init.local_configer import LocalConfiger

class ProjectQuickStarter:
    def __init__(self, conf_dict: dict, settings: dict) -> None:
        self._conf_dict = conf_dict
        self._settings = settings
        
        self._errors = {}

        if self._conf_dict[ConfigKey.CLONE_REPO]:
            self._conf_dict[ConfigKey.PROJECT_PATH] = conf_dict[ConfigKey.PROJECTS_DIR_PATH] + '\\' + conf_dict[ConfigKey.REPO_LINK].split('/')[-1]
        self._conf_dict[ConfigKey.PROJECT_PATH].replace('/', '\\')
    
    def init_project(self) -> None:
        if self._conf_dict[ConfigKey.CLONE_REPO]:
            print('Cloning GitHub repo...')
            try:
                self._run_cmd(self._conf_dict[ConfigKey.PROJECTS_DIR_PATH], ['git', 'clone', self._conf_dict[ConfigKey.REPO_LINK]])
            except:
                print('Fatal: Github repo could not be cloned!')
                print()
                input('Press enter to exit...')
                exit()
            print('Finished cloning GitHub repo.')
            print()
        if self._conf_dict[ConfigKey.GIT_SAFEDIR]:
            abs_project_path = os.path.abspath(self._conf_dict[ConfigKey.PROJECT_PATH])
            self._run_cmd('.', ['git', 'config', '--global', '--add', 'safe.directory', abs_project_path])
            print('Added project as a Git safe directory.')
            print()
        if self._conf_dict[ConfigKey.LOCAL_CONFIGS]:
            local_configer = LocalConfiger(self._conf_dict[ConfigKey.PROJECT_PATH], self._conf_dict[ConfigKey.DB_NAME])
            try:
                local_configer.create_configs()
            except FileNotFoundError as e:
                self._error(ConfigKey.LOCAL_CONFIGS, str(e))
            print()
        if self._conf_dict[ConfigKey.DB_IMPORT]:
            self._import_database()
        if self._conf_dict[ConfigKey.CREATE_VHOST]:
            host = self._conf_dict[ConfigKey.HOST].split('/')[-1]
            self._create_vhosts_entry(host)
            self._create_hosts_entry(host)
        if self._conf_dict[ConfigKey.FTP_CONNECTION]:
            self._create_ftp_connection()
        if self._conf_dict[ConfigKey.COMPOSER]:
            self._install_dependencies('composer')
        if self._conf_dict[ConfigKey.NPM]:
            self._install_dependencies('npm')
        if self._conf_dict[ConfigKey.BUILD]:
            self._run_build_scripts()

    def get_errors(self) -> dict:
        return self._errors
    
    def _install_dependencies(self, type: str) -> None:
        if type == 'npm' and not self._has_package_json():
            self._error(ConfigKey.NPM, f'CAN\'T RUN NPM INSTALL -> no package.json found')
            return
        print(f'Running {type} install...')
        self._run_cmd(self._conf_dict[ConfigKey.PROJECT_PATH], [type, 'i'])
        print(f'Finished running {type} install.')
        print()
    
    def _run_build_scripts(self) -> None:
        if not self._has_package_json():
            self._error(ConfigKey.BUILD, f'CAN\'T RUN BUILD SCRIPTS -> no package.json found')
            return
        
        with open(os.path.join(self._conf_dict[ConfigKey.PROJECT_PATH], 'package.json'), 'r') as pf:
            package_json: dict = json.load(pf)

        if not 'scripts' in package_json:
            self._error(ConfigKey.BUILD, f'CAN\'T RUN BUILD SCRIPTS -> no scripts found in package.json')
            return
        
        build_scripts = [script for script in package_json['scripts'].keys() if script.startswith("build")]

        if len(build_scripts) == 0:
            self._error(ConfigKey.BUILD, f'CAN\'T RUN BUILD SCRIPTS -> no build scripts found in package.json')
            return

        print('Running build scripts...')
        for script in build_scripts:
            print(f'Running "npm run {script}"...')
            self._run_cmd(self._conf_dict[ConfigKey.PROJECT_PATH], ['npm', 'run', script])
        print('Finished running build scripts.')
        print()
    
    def _run_cmd(self, trgt: str, comm: list) -> None:
        if not os.path.exists(trgt):
            self._error(
                ConfigKey.PROJECT_PATH,
                f'Couldn\'t run a cmd command at {trgt}: path does not exist'
            )
            return

        cwd = os.getcwd()
        os.chdir(trgt)
        sp.run(comm, shell=True)
        os.chdir(cwd)
    
    def _has_package_json(self) -> bool:
        if not os.path.exists(self._conf_dict[ConfigKey.PROJECT_PATH]):
            self._error(ConfigKey.NPM, f'CAN\'T RUN NPM SCRIPTS -> project path invalid')
            return False
        return 'package.json' in os.listdir(self._conf_dict[ConfigKey.PROJECT_PATH])
    
    def _import_database(self) -> None:
        with SqlManager() as db:
            connected = db.connect(
                host=self._conf_dict[ConfigKey.DB_HOST],
                user=self._conf_dict[ConfigKey.DB_USER],
                password=self._conf_dict[ConfigKey.DB_PASSWORD],
            )

            if not connected:
                self._error(ConfigKey.DB_IMPORT, 'Error: CAN\'T IMPORT DATABASE -> connection failed')
                return
            
            db_created = db.create_database(self._conf_dict[ConfigKey.DB_NAME])

            if not db_created:
                self._error(ConfigKey.DB_IMPORT, 'Error: CAN\'T IMPORT DATABASE -> sql database creation failed')
                return
            
            db.use_database(self._conf_dict[ConfigKey.DB_NAME])
            sql_imported = db.import_sql_file(os.path.abspath(self._conf_dict[ConfigKey.DB_FILE]))
        
            if not sql_imported:
                self._error(ConfigKey.DB_IMPORT, 'Error: CAN\'T IMPORT DATABASE -> sql script import failed')
                return
        
        print()
        print(f'Imported {self._conf_dict[ConfigKey.DB_NAME]} database.')
        print()

    def _create_vhosts_entry(self, host: str) -> None:
        with open('templates\\vhost_template.txt', 'r') as f:
            template_lines = f.readlines()
        try:
            f = open(f'C:\\wamp64\\bin\\apache\\apache{self._settings["apache_version"]}\\conf\\extra\\httpd-vhosts.conf', 'a')
        except FileNotFoundError:
            self._error(
                ConfigKey.CREATE_VHOST, 
                f'Error: No vhost file found at: C:/wamp64/bin/apache/apache{self._settings["apache_version"]}/conf/extra/httpd-vhosts.conf'
            )
            return
        for line in template_lines:
            if '[host_name]' in line:
                template_lines[template_lines.index(line)] = line.replace('[host_name]', host)
            if '[project_path]' in line:
                path = os.path.join(os.path.abspath(self._conf_dict[ConfigKey.PROJECT_PATH]).replace('\\', '/'), 'www')
                template_lines[template_lines.index(line)] = line.replace('[project_path]', path)
        f.write('\n')
        f.writelines(template_lines)
        f.close()
        print('Created a vhost entry.')
        print()
    
    def _create_hosts_entry(self, host: str) -> None:
        lines = [f'\n127.0.0.1	{host}', f'\n::1	{host}']
        try:
            f = open('C:\\WINDOWS\\system32\\drivers\\etc\\hosts', 'a')
        except Exception:
            self._error(
                ConfigKey.CREATE_VHOST, 
                'Error: Access to hosts file denied. Please restart the script with admin permissions if you want to create a vhost.'
            )
            return
        f.writelines(lines)
        f.close()
        print('Created host entry.')
        print()

    def _create_ftp_connection(self) -> None:
        print('Setting up FileZilla FTP connection...')
        
        with open('templates\\ftp_template.xml', 'r') as f:
            template_lines = f.readlines()
        variables = {
            '[host_url]'        : self._conf_dict[ConfigKey.FTP_HOST], 
            '[username]'        : self._conf_dict[ConfigKey.FTP_USERNAME], 
            '[password]'        : self._conf_dict[ConfigKey.FTP_PASSWORD], 
            '[connection_name]' : self._conf_dict[ConfigKey.FTP_NAME], 
            '[local_dir_path]'  : os.path.abspath(self._conf_dict[ConfigKey.PROJECT_PATH if self._conf_dict[ConfigKey.PATH_LOCAL_DIR] else 'ftp_local_dir'])
        }
        for i in range(len(template_lines)):
            line = template_lines[i]
            key = self._get_match(line, variables)
            if key == None:
                continue
            if key == '[password]':
                password = variables[key]
                template_lines[i] = line.replace(key, self._get_base64(password))
                continue
            template_lines[i] = line.replace(key, variables[key])
        self._write_to_sitemanager(template_lines)
        print('FTP connection setup finished.')
        print()
    
    def _get_match(self, line: str, variables: dict) -> str|None:
        for key in variables:
            if key in line:
                return key
        return None
    
    def _get_base64(self, input: str) -> str:
        input_b = input.encode('ascii')
        base64_input_b = base64.b64encode(input_b)
        return base64_input_b.decode('ascii')
    
    def _write_to_sitemanager(self, write_lines: list) -> None:
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
            self._error(
                ConfigKey.FTP_CONNECTION, 
                f'Error: Sitemanager file not found at ' + os.getenv('APPDATA') + '\\FileZilla\\sitemanager.xml, make sure you have FileZilla installed.'
            )
    
    def _error(self, key: ConfigKey, message: str) -> None:
        print(f'ERROR: {message}')

        if key in self._errors:
            self._errors[key].append(message)
        
        self._errors[key] = [message]