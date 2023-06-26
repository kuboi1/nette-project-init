import os
import shutil

# LocalConfiger class creates local config neon files in the projects app\config folder
class LocalConfiger:
    def __init__(self, project_path: str, db_name: str) -> None:
        self.config_dir_path = project_path + '\\app\\config'
        self.multiple_configs = self.has_multiple_configs()
        self.db_name = db_name
        self.created_files = 0
        self.main_config_path = ''
    
    def create_configs(self) -> None:
        main_config = 'config.neon' if not self.multiple_configs else 'main.neon'
        self.main_config_path = os.path.join(self.config_dir_path, main_config)

        print('Creating local config files...')

        if not os.path.exists(self.main_config_path):
            print(f'EXCEPTION: {main_config} file found at {os.path.abspath(self.main_config_path)}')
            return
        
        if not self.multiple_configs:
            trgt = os.path.join(self.config_dir_path, 'config.local.neon')
            self.create_db_config(trgt)
        else:
            self.multiple_configs_process()
        
        print('Successfully created ' +  (f'{self.created_files} local config files.' if self.created_files > 1 else 'config.local.neon file.'))
    
    def has_multiple_configs(self) -> bool:
        return os.path.exists(os.path.join(self.config_dir_path, 'main.neon'))

    def multiple_configs_process(self) -> None:
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
            src = os.path.join(self.config_dir_path, config)
            trgt = os.path.join(self.config_dir_path, local_config)
            if split_local_config[0] == 'database':
                self.create_db_config(trgt)
                continue
            try:
                shutil.copyfile(src, trgt)
            except FileNotFoundError:
                print(f'EXCEPTION: There was an error with copying a config file to {trgt}')
                return
            self.created_files += 1

    def get_configs_from_main(self) -> list:
        try:
            with open(self.main_config_path, 'r') as f:
                all_configs = []
                in_section = False
                while True:
                    line = f.readline()
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
        except FileNotFoundError:
            print(f'EXCEPTION: Main config not found at {self.main_config_path}')
            exit()
    
    def create_db_config(self, trgt)-> None:
        db_lines = [
            'database:\n',
           f'    dsn: \'mysql:host=localhost;dbname={self.db_name}\'\n',
            '    user: root\n',
            '    password: \n'
        ]
        with open(trgt, 'w') as f:
            f.writelines(db_lines)
        self.created_files += 1