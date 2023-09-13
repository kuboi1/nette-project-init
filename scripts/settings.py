import os
import pickle

from services.translator import Translator


SETTINGS_PATH = os.path.abspath('data\\settings.pkl')

LOCALE_LIST = ['en', 'cs']


# Used for setting up versions and such
class Settings:
    def __init__(self, translator: Translator) -> None:
        self.translator = translator
        self.settings_dict = {}
    
    def setup(self) -> dict:
        for setting in self.settings_dict:
            current_value = self.settings_dict[setting]
            user_input = input(
                f'{self.translator.translate(f"prompt.{setting}", self.get_prompt_params(setting))} [{current_value}]: '
            )
            while not self.special_check(setting, user_input):
                self.print_translate('error.invalid_value')
                user_input = input(
                    f'{self.translator.translate(f"prompt.{setting}", self.get_prompt_params(setting))} [{current_value}]: '
                )
            if user_input == '':
                continue
            self.settings_dict[setting] = user_input
        return self.settings_dict

    def load_settings(self, force_default=False) -> None:
            settings_dict = {
                'locale': 'en',
                'apache_version': '2.4.51'
            }

            if force_default:
                self.settings_dict = settings_dict
                return
            
            self.settings_dict = settings_dict

            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, 'rb') as f:
                    self.settings_dict = pickle.load(f)
            else:
                self.save_settings()
    
    def save_settings(self) -> None:
        with open(SETTINGS_PATH, 'wb') as f:
            settings = dict(self.settings_dict)
            pickle.dump(settings, f)
    
    def get_settings(self) -> dict:
        return self.settings_dict

    def special_check(self, setting: str, input: str) -> bool:
        if input == '':
            return True
        
        match setting:
            case 'locale': return input in LOCALE_LIST
        return True
    
    def print_intro(self) -> None:
        print()
        self.print_translate('title')
        self.print_translate('intro.1')
        self.print_translate('intro.2')
        print()

    def get_prompt_params(self, setting: str) -> dict:
        match setting:
            case 'locale': return {'locale_list': '/'.join(LOCALE_LIST)}
        return {}
    
    def print_translate(self, key: str, params={}) -> None:
        print(self.translator.translate(key, params))


if __name__ == '__main__':
    ORIGINAL_CWD = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(__file__), '..\\'))

    print(os.getcwd())

    translator = Translator()

    if not translator.lang_file_exists():
        print('Fatal: lang.json file not found in data directory.')
        exit()

    settings = Settings(translator)

    settings.load_settings()
    settings_dict = settings.get_settings()

    translator.load_lang(main_key='settings', locale=settings_dict['locale'])

    settings.print_intro()
    settings.setup()
    settings.save_settings()

    os.chdir(ORIGINAL_CWD)

    print(translator.translate('finished.message'))
    input(translator.translate('finished.cta'))