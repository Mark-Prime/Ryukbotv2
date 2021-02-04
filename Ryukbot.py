#! python3
##importing things (self explanitory)
from datetime import datetime as dt
from pathlib import Path
import re
import json
import sys
import os
import colorama
from shutil import copy
from random import randint
from termcolor import cprint
from ryukbot_installer import *
from ryukbot_settings import descriptions
from ryukbot_maker import _event_maker
from yesNo import yesNo
from sprint import *
from classes.clip import Clip
from classes.event import Event
from classes.mod import Mod
from classes.vdm import VDM

# Activates the color in the console without this there would be no colors
colorama.init()

ryukbot_version = 'v2.1.0'

# Color Coding ruleset:
# grey: 
# red:      Errors and the messages associated
# green:    Ran successfully
# yellow:   Warning labels or important notices
# blue:     
# magenta:  Important but not an error or title
# cyan:     Titles/System messages
# white:    Normal paragraph messages/descriptions of things

setting_descriptions = descriptions()
    

def check_setting(setting, setting_descriptions):
    """Checks the settings file and makes sure its all valid

    Args:
        setting (string):               The key name of the specific setting being checked
        setting_descriptions (object):  The settings information

    Returns:
        Boolean: returns the value of the setting
    """
    
    if setting not in ryukbot_settings:
        cprint(f'{setting} is missing from ryukbot_settings.json', 'red')
        # print_error(ryukbot_settings, f'{setting} is missing from ryukbot_settings.json\nDefault value is: {setting_descriptions["default"]}', 201)
        return missing_setting_text(setting_descriptions, setting)
    
    if (type := setting_descriptions['type']) == 'integer' or type == 'boolean':
        
        if not str(ryukbot_settings[setting]).isdigit():
            print_error(ryukbot_settings, f'{setting} is incorrectly set up (should be a number)', 205)
            
        if type == 'integer':
            return ryukbot_settings[setting]
        
        
        if ryukbot_settings[setting] == 1 or ryukbot_settings[setting] == 0:
            ryukbot_settings[setting] = True if ryukbot_settings[setting] == 1 else False
            return ryukbot_settings[setting]
        else:
            print_error(ryukbot_settings, f'{setting} is incorrectly set up (should be a 1 or 0)', 204)
            
    else: 
        if isinstance(ryukbot_settings[setting], str):
            return ryukbot_settings[setting]
        else:
            print_error(ryukbot_settings, f'{setting} is incorrectly set up (should be wrapped in quotes)', 203)
        
        
def setting_rundown():
    """
        Runs all of the settings in one place
    """
    for key in setting_descriptions:
        ryukbot_settings[key] = check_setting(key, setting_descriptions[key])
        
    printSettings = ryukbot_settings
    for key in ryukbot_settings:
        if ryukbot_settings[key] == True or ryukbot_settings[key] == False:
            printSettings[key] = 1 if ryukbot_settings[key] else 0
        
    if not 'mods' in ryukbot_settings:
        ryukbot_settings['mods'] = []
        
    with open(Path('ryukbot_settings.json'), 'w+') as f:
        json.dump(ryukbot_settings, f, indent=4)
        
# Writes the start of a new command and adds one to the vdm_count variable
def new_command(vdm_count, VDM):
    """Starts the initial command writing that is the same with all vdm commands

    Args:
        vdm_count (int):     The amount of vdm commands there are
        VDM (file):         The VDM file being written to

    Returns:
        int: The count with one more to account for the one just added
    """
    VDM.write('\t"%s"\n\t{\n\t\t' % (vdm_count))
    return vdm_count + 1

def validate_event_file(ryukbot_settings):
    tf_folder = ryukbot_settings["tf_folder"]
        
    if Path(tf_folder + '\\demos\\_events.txt').is_file():
        tf_folder = tf_folder + '\\demos'
        event_file_name = '_events.txt'
    elif Path(tf_folder + '\\demos\\KillStreaks.txt').is_file():
        tf_folder = tf_folder + '\\demos'
        event_file_name = 'KillStreaks.txt'
    elif Path(tf_folder + '\\_events.txt').is_file():
        event_file_name = '_events.txt'
    elif Path(tf_folder + '\\KillStreaks.txt').is_file():
        event_file_name = 'KillStreaks.txt'
    else:
        print_error(ryukbot_settings, 'Can not find KillStreaks.txt or _event.txt', 331)
    
    event_file = Path(f'{tf_folder}\\{event_file_name}')
    
    return tf_folder, event_file_name, event_file

def empty_events(ryukbot_settings, event_file_name, event_file):
    cprint((f"{event_file_name} is empty"), 'red')
    print(f'Would you like to run the {event_file_name} maker?')
    if yesNo():
        if _event_maker(event_file, event_file_name, ryukbot_settings['advanced_event_maker']):
            os.system('cls')
            cprint('Run Ryukbot now?\n', 'cyan')
            if yesNo():
                run()
            else:
                input("Press enter to close...")
                os._exit(0)
    else:
        input("Press enter to close...")
        os._exit(0)

def write_backup(backup_path, event_file):
    # try: 
    date_time = str(dt.now().date()) + '_' + str(dt.now().time()) + '.txt'
    backup_location = Path((backup_path) + '\\' + (date_time.replace(':', '-')).split('.')[0] + '.txt')

    copy(event_file, backup_location)

    # except:
    #     print_error(ryukbot_settings, 'Error while writing backup', 343)

def run():
    ryukbot_settings['tf_folder'], event_file_name, event_file = validate_event_file(ryukbot_settings)

    # Get current directory path and add the backups folder to the end as well as
    # Make the folder if it doesnt exist yet
    if not os.path.exists(dir_path := Path(ryukbot_settings['tf_folder'] + '\\ryukbot_backups\\')):
        os.makedirs(dir_path)
        os.makedirs(Path((str(dir_path) + '\\demos\\')))
    elif not os.path.exists(Path((str(dir_path) + '\\demos\\'))):
        os.makedirs(Path((str(dir_path) + '\\demos\\')))
    
    ryukbot_settings['backup_path'] = dir_path

    write_backup(str(dir_path), event_file)
            
    with open(event_file, 'r') as _events:

        # Saving the file as an array/list variable
        event_lines = _events.readlines()
        
        # REGEX for future use
        regex = re.compile('\[(.*)\] (.*) \("(.*)" at (\d*)\)', re.IGNORECASE)
        carrot_regex = re.compile('\n(\>)?\n')
        
        # Combines it into one string and searches it
        event_marks = regex.findall(''.join(event_lines))
        carrot_count = len(carrot_regex.findall("".join(event_lines))) + 1
        
        #* The syntax for getting the variables and its information
        # LINE: event_marks[*]           --- EXAMPLE ('2020/04/27 20:23', 'Killstreak', '3', '2020-04-27_20-16-21', '29017')
        # DATE: event_marks[*][0]        --- EXAMPLE 2020/04/27 20:23
        # TYPE: event_marks[*][1]        --- EXAMPLE Killstreak 
        # CRITERIA: event_marks[*][2]    --- EXAMPLE 3
        # DEMO: event_marks[*][3]        --- EXAMPLE 2020-04-27_20-16-21
        # TICK: event_marks[*][4]        --- EXAMPLE 29017
        
        # This is used later to check if the demo has changed to the next on the list
        try:
            demo_name = event_marks[0][3]
        except IndexError:
            empty_events(ryukbot_settings, event_file_name, event_file)
        
        # Simple message letting the user know the programs progress.
        # More updates to the user are nice but I want to try and limit spam to the user.
        cprint(f'Scanned {len(event_lines)} different events over the span of {carrot_count} demos.', 'green')
        print_detail(ryukbot_settings, f'Wow! You don\'t get many kills do you?', 'magenta', 68)

        vdm = None

        for event in event_marks:
            new_event = Event(event) 
            for mod in ryukbot_settings['mods']:
                new_event.apply_mod(mod)
            clip = Clip(ryukbot_settings, new_event)

            if not vdm:
                vdm = VDM(ryukbot_settings, clip)
                print_detail(ryukbot_settings, f'\nScanning demo: {vdm.demo_name}.dem', 'green', 2)
            elif vdm.demo_name != new_event.demo_name:
                if ryukbot_settings['record_continuous'] == 1:
                    vdm.close(clip.demo_name)
                else: 
                    vdm.close()

                print_detail(ryukbot_settings, f'Clip {len(vdm)}: {vdm.latest.display_name}', 'cyan', 2)
                print_detail(ryukbot_settings, f'Done writing file: {vdm.demo_name}.vdm', 'green', 0)
                print_detail(ryukbot_settings, f'Found {len(vdm)} clip{"s" if len(vdm) > 1 else ""}', 'green', 1)

                vdm = VDM(ryukbot_settings, clip)
                print_detail(ryukbot_settings, f'\nScanning demo: {vdm.demo_name}.dem', 'green', 2)
            elif vdm.latest.can_include(ryukbot_settings['minimum_ticks_between_clips'], clip):
                vdm.latest.include(ryukbot_settings, clip)
            else: 
                vdm.append(clip)
                print_detail(ryukbot_settings, f'Clip {len(vdm) - 1}: {vdm.latest_display_name}', 'cyan', 2)


        vdm.close()
        print_detail(ryukbot_settings, f'Clip {len(vdm)}: {vdm.latest.display_name}', 'cyan', 2)
        print_detail(ryukbot_settings, f'Done writing file: {vdm.demo_name}.vdm', 'green', 0)
        print_detail(ryukbot_settings, f'Found {len(vdm)} clip{"s" if len(vdm) > 1 else ""}', 'green', 1)

        if ryukbot_settings["clear_events"]:
            cprint(f'Clearing {event_file_name}', 'yellow')
            try:
                open(event_file, 'w+').close()
                cprint(f'{event_file_name} cleared')
            except:
                print_error(ryukbot_settings, f'Error while clearing {event_file_name}', 398)

        cprint('\nRyukbot finished successfully', 'green')
        input("Press enter to close...")
        os._exit(0)
                
if Path('ryukbot_settings.json').is_file():
    # Ensure that ryukbot_settings.json is set correctly
    try:
        ryukbot_settings = json.load(open('ryukbot_settings.json'))
    except:
        print_error({"console_detail": 4}, 'Error loading ryukbot_settings.json\nYou might\'ve failed the install process.\nPlease delete ryukbot_settings.json and restart ryukbot', 195)

    ## Ignore this
    print_detail(ryukbot_settings, f'FUNNY HAHA ENABLED', 'magenta', 68)
    
    ## and all of this
    if (today := dt.today().strftime("%m/%d")) == '12/25':
        cprint(""".      *    *           *.       *   .                      *     .
               .   .                   __   *    .     * .     *
    *       *         *   .     .    _|__|_        *    __   .       *
  .  *  /\       /\          *        ('')    *       _|__|_     .
       /  \   * /  \  *          .  <( . )> *  .       ('')   *   *
  *    /  \     /  \   .   *       _(__.__)_  _   ,--<(  . )>  .    .
      /    \   /    \          *   |       |  )),`   (   .  )     *
   *   `||` ..  `||`   . *.   ... ==========='`   ... '--`-` ... * """, 'cyan')
    elif today == '10/31':
        cprint(""".___,_______,_____Happy_Halloween____.
| ./(       )\.        |             |
| )  \/\_/\/  (        |             |
| `)  (^Y^)  (`      \(|)/           |
|  `),-(~)-,(`      --(")--          |
|      '"'      \\\\    /`\            |
|          .-'```^```'-.    ,     ,  |
|         /   (\ __ /)  \   )\___/(  |
|         |    ` \/ `   |  {(@)v(@)} |
|         \    \____/   /   {|~~~|}  |
|          `'-.......-'`    {/^^^\}  |
.____________________________`m-m`___.""", 'cyan')
    elif today == '06/20':
        cprint("""   __       _   _                         _             
  / _| __ _| |_| |__   ___ _ __ ___    __| | __ _ _   _ 
 | |_ / _` | __| '_ \ / _ \ '__/ __|  / _` |/ _` | | | |
 |  _| (_| | |_| | | |  __/ |  \__ \ | (_| | (_| | |_| |
 |_|  \__,_|\__|_| |_|\___|_|  |___/  \__,_|\__,_|\__, |
                                                  |___/ """, 'cyan') 
        
    elif today == '12/10':
        cprint("""ooooooooooooooooooooooooo
o    Happy Hanukkah     o
o          ! !          o
o        ! | | !        o
o      ! | H H | !      o
o    ! | H H!H H | !    o
o    | H H H|H H H |    o
o    (_H_H_H|H_H_H_)    o
o     (___________)     o
o           H           o
o           H           o
o           H           o
o        ___H___        o
ooooooooooooooooooooooooo""", 'cyan')
    elif today == '05/09':
        cprint("""    __     Happy Mother's Day     \_/
   ((6}     Relax and smell     --(_)--
    )(        some roses.         / \\
   \(\)
    \.'-b____q            <@l> <@l><@l>
    ;;---------;;          \)/ \(/ \(/""", 'cyan')
    elif today == '01/01':
        cprint("""  _ __   _____      __  _   _  ___  __ _ _ __ 
 | '_ \ / _ \ \ /\ / / | | | |/ _ \/ _` | '__|
 | | | |  __/\ V  V /  | |_| |  __/ (_| | |   
 |_| |_|\___| \_/\_/    \__, |\___|\__,_|_|   
                        |___/                 """, 'cyan')
    elif (today == '07/01') or (today == '07/04'):
        cprint("""                                   .''.
       .''.      .        *''*    :_\/_:     .
      :_\/_:   _\(/_  .:.*_\/_*   : /\ :  .'.:.'.
  .''.: /\ :    /)\   ':'* /\ *  : '..'.  -=:o:=-
 :_\/_:'.:::.  | ' *''*    * '.\\'/.'_\(/_ '.':'.'
 : /\ : :::::  =  *_\/_*     -= o =- /)\     '  *
  '..'  ':::' === * /\ *     .'/.\\'.  ' ._____
      *        |   *..*         :       |.   |' .---"|
        *      |     _           .--'|  ||   | _|    |
        *      |  .-'|       __  |   |  |    ||      |
     .-----.   |  |' |  ||  |  | |   |  |    ||      |
 ___'       ' /"\ |  '-."".    '-'   '-.'    '`      |____
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                       ~-~-~-~-~-~-~-~-~-~   /|
          )      ~-~-~-~-~-~-~-~  /|~       /_|\\
        _-H-__  -~-~-~-~-~-~     /_|\    -~======-~
~-\XXXXXXXXXX/~     ~-~-~-~     /__|_\ ~-~-~-~
~-~-~-~-~-~    ~-~~-~-~-~-~    ========  ~-~-~-~
      ~-~~-~-~-~-~-~-~-~-~-~-~-~ ~-~~-~-~-~-~
                        ~-~~-~-~-~-~""", 'cyan')
    elif today == '05/17':
        cprint("""                 .##@@&&&@@##.
              ,##@&::%&&%%::&@##.
             #@&:%%000000000%\%:&@#
           #@&:%00'         '00%:&@#
          #@&:%0'             '0%:&@#
         #@&:%0                 0%:&@#
        #@&:%0                   0%:&@#
        #@&:%0                   0%:&@#
        "" ' "                   " ' ""
      _oOoOoOo_                   .-.-.
     (oOoOoOoOo)                 (  :  )
      )`*****`(                .-.`. .'.-.
     /         \              (_  '.Y.'  _)
    | #         |             (   .'|'.   )
    \           /              '-'  |  '-'
     `=========`""", 'cyan')
    elif today == '02/14':
        cprint("""         (\/)
          \/
  (\/)   .-.  .-.
   \/   ((`-)(-`))
         \\\\    //   (\/)
          \\\\  //     \/
   .=***=._))((_.=***=.
  /  .,   .'  '.   ,.  \\
 /__(,_.-'      '-._,)__\\
`    /|             |\   `
    /_|__         __|_\\
      | `))     ((` |
      |             |
     -"==         =="-""", 'cyan')
        
    if ryukbot_settings['welcome_message']:
        cprint("ATTENTION LEGITIMATE GAMERS", attrs=["bold", "underline"])
        cprint(f"""RYUKBOT {ryukbot_version} HAS BEEN LOADED\n
Developed by Ryuk
Steam: https://steamcommunity.com/id/Ryuktf2/
Patreon: https://www.patreon.com/ryuktf2
Discord: Ryuk#1825\n\n""", attrs=["bold"])
else: 
    with open(Path('ryukbot_settings.json'), 'w') as ryukbot_settings:
        json.dump(ryukbot_installer(setting_descriptions), ryukbot_settings, indent=4)
    ryukbot_settings = json.load(open('ryukbot_settings.json'))
    cprint("ATTENTION LEGITIMATE GAMERS", attrs=["bold", "underline"])
    cprint(f"""RYUKBOT {ryukbot_version} HAS BEEN LOADED\n
Developed by Ryuk
Steam: https://steamcommunity.com/id/Ryuktf2/
Patreon: https://www.patreon.com/ryuktf2
Discord: Ryuk#1825\n\n""", attrs=["bold"])
    

setting_rundown()

for index in range(0, len(ryukbot_settings['mods'])):
    ryukbot_settings['mods'][index] = Mod(ryukbot_settings['mods'][index])

run()