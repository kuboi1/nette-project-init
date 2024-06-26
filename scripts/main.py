import os

from project_init.ui import UI
from project_init.project_init import ProjectQuickStarter
from project_init.config_manager import ConfigManager
from services.translator import Translator
from settings import Settings

CONF_PATH = os.path.abspath('data\\conf.pkl')


if __name__ == '__main__':
    ORIGINAL_CWD = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(__file__), '..\\'))

    config_manager = ConfigManager(CONF_PATH)
    
    ui = UI(config_manager.load_configs(force_default=False))
    ui.print_intro()
    conf_dict = ui.get_configs()
    
    config_manager.save_configs(conf_dict)

    print()

    translator = Translator()

    settings = Settings(translator=translator)
    settings.load_settings()

    quick_starter = ProjectQuickStarter(conf_dict, settings.get_settings())
    quick_starter.init_project()

    os.chdir(ORIGINAL_CWD)

    ui.print_outro(quick_starter.get_errors())

    print('\nDon\'t forget to restart all services on Wamp!\n')
    input('Press enter to exit...')