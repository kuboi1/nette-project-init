import os
import subprocess as sp
import base64

from local_configer import LocalConfiger

class ProjectQuickStarter:
    def __init__(self, conf_dict: dict, settings: dict) -> None:
        self.conf_dict = conf_dict
        self.settings = settings

        if conf_dict['clone_repo']:
            conf_dict['project_path'] = conf_dict['projects_f_path'] + '\\' + conf_dict['repo_link'].split('/')[-1]
        conf_dict['project_path'].replace('/', '\\')
    
    def init_project(self) -> None:
        conf = self.conf_dict
        if conf['clone_repo']:
            print('Cloning GitHub repo...')
            try:
                self.run_cmd(self.conf_dict['projects_f_path'], ['git', 'clone', self.conf_dict['repo_link']])
            except:
                print('Error: There was a problem with cloning the GitHub repo.')
                exit()
            print('Finished cloning GitHub repo.')
            print()
        if conf['local_configs']:
            local_configer = LocalConfiger(conf['project_path'], conf['db_name'])
            local_configer.create_configs()
            print()
        if conf['create_vhost']:
            host = self.conf_dict['host'].split('/')[-1]
            self.create_vhosts_entry(host)
            self.create_hosts_entry(host)
        if conf['ftp_connection']:
            self.create_ftp_connection()
        if conf['composer']:
            self.install_dependencies('composer')
        if conf['npm']:
            self.install_dependencies('npm')
        if conf['build']:
            self.run_build_scripts()
        
        print('Project ' + self.conf_dict['project_path'].split('\\')[-1] + ' was initialized.')
    
    def install_dependencies(self, type: str) -> None:
        if type == 'npm' and not self.has_package_json():
            print(f'CAN\'T RUN NPM INSTALL -> no package.json found')
            return
        print(f'Running {type} install...')
        self.run_cmd(self.conf_dict['project_path'], [type, 'i'])
        print(f'Finished running {type} install.')
        print()
    
    def run_build_scripts(self) -> None:
        print('Running build scripts...')
        self.run_cmd(self.conf_dict['project_path'], ['npm', 'run', 'build'])
        self.run_cmd(self.conf_dict['project_path'], ['npm', 'run', 'build:admin'])
        print('Finished running build scripts.')
        print()
    
    def run_cmd(self, trgt: str, comm: list) -> None:
        cwd = os.getcwd()
        os.chdir(trgt)
        sp.run(comm, shell=True)
        os.chdir(cwd)
    
    def has_package_json(self) -> bool:
        return 'package.json' in os.listdir(self.conf_dict['project_path'])
    
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
                template_lines[template_lines.index(line)] = line.replace('[project_path]', os.path.abspath(self.conf_dict['project_path']).replace('\\', '/'))
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
            '[host_url]' : self.conf_dict['ftp_host'], 
            '[username]' : self.conf_dict['ftp_username'], 
            '[password]' : self.conf_dict['ftp_password'], 
            '[connection_name]' : self.conf_dict['ftp_name'], 
            '[local_dir_path]' : os.path.abspath(self.conf_dict['project_path' if self.conf_dict['path_local_dir'] else 'ftp_local_dir'])
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
 