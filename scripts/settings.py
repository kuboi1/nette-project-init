import os
import pickle


SETTINGS_PATH = 'data\\settings.pkl'


# Used for setting up versions and such
class Settings:
    def __init__(self) -> None:
        self.settings_dict = {}

        self.prompts = {
            'apache_version': 'Apache version that your wamp is currently using'
        }
    
    def setup(self) -> dict:
        for setting in self.settings_dict:
            current_value = self.settings_dict[setting]
            user_input = input(f'{self.prompts[setting]} [{current_value}]: ')
            if user_input == '':
                continue
            self.settings_dict[setting] = user_input
        return self.settings_dict

    def load_settings(self, force_default=False) -> None:
            settings_dict = {
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
    
    def print_intro(self):
        print('Visu Project Initiator - Settings')
        print('- additional one time settings that don\'t need to be included in the main program')
        print('- you can press enter with no input to confirm current settings (in square brackets)')
        print()


if __name__ == '__main__':
    ui = Settings()
    ui.load_settings()
    ui.setup()
    ui.save_settings()

    print('\nSettigs saved successfully')
    input('Press enter to exit...')