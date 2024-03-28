import os
import json


LANG_PATH = '.\\data\\lang.json'


class Translator:
    def __init__(self) -> None:
        self.lang = {}
    
    def load_lang(self, main_key: str, locale: str) -> dict:
        with open(LANG_PATH, 'r', encoding='utf-8') as f:
            lang = json.load(f)
        self.lang = lang[main_key][locale]
    
    def lang_file_exists(self) -> bool:
        return os.path.exists(os.path.join(os.getcwd(), LANG_PATH))

    def translate(self, path_key: str, params={}) -> str:
        path = path_key.split('.')
        current_level = self.lang

        for key in path:
            if key not in current_level:
                return path_key
            
            current_level = current_level[key]
        
        if type(current_level) is not str:
            return path_key
        
        result = current_level

        for param_key in params:
            if f'%{param_key}%' in result:
                result = result.replace(f'%{param_key}%', params[param_key])
        
        return result
