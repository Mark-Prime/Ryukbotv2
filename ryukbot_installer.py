#python3
import colorama
from termcolor import cprint
import sys
import os

# Activates the color in the console without this there would be no colors
colorama.init()

def installer_text(current_setting, key):
    """The user experience side of the installer

    Args:
        current_setting (dictionary): The value of the current setting being editted/created
        key (string): The name of the dictionary/the settings name in the json file

    Returns:
        string/int: returns the value input into the installer. Can be string or int based on the actual setting itself
    """
    cprint('Ryukbot Installer\n', 'cyan')
    print(current_setting["description"])
    print(f'\nDefault: {current_setting["default"]}\n')
    if (answer := input(f'{key}: ')) == '':
        return current_setting["default"]
    elif current_setting["type"] == 'integer' :
        try:
            return int(answer)
        except Exception:
            os.system('cls')
            cprint('Should be a number with no letters', 'red')
            return installer_text(current_setting, key)
    elif current_setting["type"] == 'boolean' :
        try:
            if int(answer) == 1 or int(answer) == 0:
                return int(answer)
            else: 
                os.system('cls')
                cprint('Should be a 1 for yes or a 0 for no', 'red')
                return installer_text(current_setting, key)
        except Exception:
            os.system('cls')
            cprint('Should be a number with no letters', 'red')
            return installer_text(current_setting, key)
    else:
        return answer
    
def missing_setting_text(current_setting, key):
    """Helps a user install a missing setting

    Args:
        current_setting (dictionary): The value of the current setting being editted/created
        key (string): The name of the dictionary/the settings name in the json file

    Returns:
        string/int: returns the value input into the installer. Can be string or int based on the actual setting itself
    """
    cprint('Ryukbot Installer\n', 'cyan')
    print(current_setting["description"])
    print(f'\nDefault: {current_setting["default"]}\n')
    if (answer := input(f'{key}: ')) == '':
        return current_setting["default"]
    elif current_setting["type"] == 'integer' :
        try:
            return int(answer)
        except Exception:
            os.system('cls')
            cprint('Should be a number with no letters', 'red')
            return missing_setting_text(current_setting, key)
    elif current_setting["type"] == 'boolean' :
        try:
            if int(answer) == 1 or int(answer) == 0:
                return int(answer)
            else: 
                os.system('cls')
                cprint('Should be a 1 for yes or a 0 for no', 'red')
                return missing_setting_text(current_setting, key)
        except Exception:
            os.system('cls')
            cprint('Should be a number with no letters', 'red')
            return missing_setting_text(current_setting, key)
    else:
        return answer

def ryukbot_installer(setting_descriptions):
    """This runs through the settings and lets the user input what they want for it in a user friendly way

    Returns:
        Object: The settings they input to it
    """
    os.system('cls')
    cprint('Looks like this is your first time using ryukbot!', 'green')
    print('Please take some time to follow this installers instructions\nBy the end of this it\'ll be ready to run right away')
    print('At any point hit enter to pick the default example shown')
    input('\nPress Enter to start the installer...')
    os.system('cls')
    new_settings = {}
    for key in setting_descriptions:
        new_settings[key] = installer_text(setting_descriptions[key], key)
        os.system('cls')
        
    if not 'mods' in new_settings:
        new_settings['mods'] = []
        
    return new_settings