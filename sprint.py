import os
import colorama
from termcolor import cprint

# Activates the color in the console without this there would be no colors
colorama.init()

def print_error(ryukbot_settings, message, errorCode):
    """Prints out and error message and code then closes the program when the user hits enter

    Args:
        message (string):   The error message the user sees
        errorCode (int):    The error code used by the support team to pin down the issue
    """ 
    print_detail(ryukbot_settings, f'I don\'t even know how you managed it but', 'magenta', 68)
    cprint(message, 'red')
    cprint(f'Error Code: {errorCode}', 'red')
    input('Press enter to close...')
    os._exit(0)
    
def print_detail(ryukbot_settings, message, color, value):
    """Prints a message to the console based on the console detail setting in ryukbot_settings.json

    Args:
        message (string):   The message to show
        color (string):     The color of the message on the page
        value (int):        The console detail level the setting must be above to show
    """
    if ryukbot_settings['console_detail'] > 69:
        ryukbot_settings['console_detail'] = 68
        
        
    if ryukbot_settings['console_detail'] > value:
        cprint(message, color)