from datetime import datetime as dt
from pathlib import Path
import colorama
import os
from termcolor import cprint

# Activates the color in the console without this there would be no colors
colorama.init()


def print_events(event_file, demo):
    """Prints the events to the _events.txt file

    Args:
        event_file (Path): The path to the file itself that will be added too
        demo (List): The list of ticks in the demo
    """
    _event = open(event_file, 'a')
    
    # Seperates the demos in the file
    _event.write('>\n')
    
    # Loops through and prints each one individually
    for event in demo:
        _event.write(f'[{event["Date"]}] Bookmark {event["Type"]} ("{event["Name"]}" at {event["Number"]})\n')
    
    # Closes to finish the printing
    _event.close()
    

def tick_input(event_file_name, demo_name, ticks, advanced_options):
    """Gets the inputs for the specific ticks in each demo with possible advanced options

    Args:
        event_file_name (String): The name of the file for the header
        demo_name (String): The name of the demo
        ticks (List): List of ticks already made
        advanced_options (Int): If the advanced options setting is enabled

    Returns:
        List: The list of ticks listed for recording
    """
    ##TODO: improve user interface
    cprint(f'{event_file_name} Maker\n', 'cyan')
    tick = {
        "Name": demo_name,
        "Date": (f'{str(dt.now().date()).replace("-", "/")} {str(dt.now().time()).split(".")[0]}')
    }
    try:
        print('The tick of the event you want recorded')
        print('1000 ticks is about 15 seconds\n')
        tick_num = input(f'tick #{len(ticks) + 1}: ')
        if tick_num == '':
            return ticks
        else:
            tick['Number'] = int(tick_num)
            if advanced_options == 1:
                os.system('cls')
                cprint(f'{event_file_name} Maker\n', 'cyan')
                print('The name you want to give the clip')
                print('Default: General\n')
                tick['Type'] = input(f'Type: ')
                if tick['Type'] == '':
                    tick['Type'] = 'General'
            else:
                tick['Type'] = 'General'
            
            ticks.append(tick)
            os.system('cls')
            return tick_input(event_file_name, demo_name, ticks, advanced_options)
    except:
        os.system('cls')
        cprint('Please only use numbers')
        return tick_input(event_file_name, demo_name, ticks, advanced_options)

def _event_maker(event_file, event_file_name, advanced_options):
    """Gives the user the ability to make thier own events easily

    Args:
        event_file (Path): The events file itself
        event_file_name (String): The name of the file
        advanced_options (Int): The option to disable or enable the advanced option

    Returns:
        Boolean: Returns true if printing went through with no issues
    """
    ##TODO: improve user interface
    os.system('cls')
    repeat = True
    demos = []
    while repeat:
        cprint(f'{event_file_name} Maker', 'cyan')
        demo_name = input('Demoname: ')
        if demo_name == '':
            repeat = False
        else:
            os.system('cls')
            demos.append(tick_input(event_file_name, demo_name, [], advanced_options))
            
    for demo in demos:
        sorted_demo = sorted(demo, key=lambda k: k['Number']) 
        print_events(event_file, sorted_demo)
        
        
    return True