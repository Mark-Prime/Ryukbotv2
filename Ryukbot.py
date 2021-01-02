#! python3
##importing things (self explanitory)
from datetime import datetime as dt
from pathlib import Path
import re
import json
import sys
import os
import colorama
from random import randint
from termcolor import cprint
from ryukbot_installer import *
import ryukbot_settings
from ryukbot_maker import _event_maker
from yesNo import yesNo
from sprint import *
from ryukbot_modding import check_mods, get_mod_options
from classes.clip import Clip
from classes.event import Event
from classes.mod import Mod

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

setting_descriptions = ryukbot_settings.descriptions()
mod_options = get_mod_options()
    

def check_setting(setting, setting_descriptions):
    """Checks the settings file and makes sure its all valid

    Args:
        setting (string):               The key name of the specific setting being checked
        setting_descriptions (object):  The settings information

    Returns:
        Boolean: returns the value of the setting
    """
    
    if setting in ryukbot_settings:
        if (type := setting_descriptions['type']) == 'integer' or type == 'boolean':
            if str(ryukbot_settings[setting]).isdigit():
                if type == 'boolean':
                    if ryukbot_settings[setting] == 1 or ryukbot_settings[setting] == 0:
                        ryukbot_settings[setting] = True if ryukbot_settings[setting] == 1 else False
                        return ryukbot_settings[setting]
                    else:
                        print_error(ryukbot_settings, f'{setting} is incorrectly set up (should be a 1 or 0)', 204)
                else: 
                    return ryukbot_settings[setting]
                    
            else:
                print_error(ryukbot_settings, f'{setting} is incorrectly set up (should be a number)', 205)
        else: 
            if isinstance(ryukbot_settings[setting], str):
                return ryukbot_settings[setting]
            else:
                print_error(ryukbot_settings, f'{setting} is incorrectly set up (should be wrapped in quotes)', 203)
    else:
        cprint(f'{setting} is missing from ryukbot_settings.json', 'red')
        # print_error(ryukbot_settings, f'{setting} is missing from ryukbot_settings.json\nDefault value is: {setting_descriptions["default"]}', 201)
        return missing_setting_text(setting_descriptions, setting)
        
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

# Prints the body of the vdm for each clip to be recorded
def print_VDM(VDM, demo_name, start_tick, end_tick, suffix, last_tick, vdm_count, mod_effects):
    """Prints the body of the vdm for each clip to be recorded

    Args:
        VDM (file):         The file being written to
        demo_name (string):  The name of the demo file minus the extension
        start_tick (int):    The tick the recording itself starts at
        end_tick (int):      The tick the recording ends at
        suffix (string):    A string to add to the end of the clips filename
        last_tick (int):     The previous end_tick
        vdm_count (int):     A count of how many vdm commands have been written

    Returns:
        int:    It returns the vdm_count at the end of the function so everything
                remains  consistent in that area throughout the entire 
                vdm printing process.
    """
    
    
    framerate = mod_effects["mod_framerate"] if "mod_framerate" in mod_effects else ryukbot_settings["framerate"]
    crosshair = mod_effects["mod_crosshair"] if "mod_crosshair" in mod_effects else ryukbot_settings["crosshair"]
    hud = mod_effects["mod_hud"] if "mod_hud" in mod_effects else ryukbot_settings["HUD"]
    outputFolder = mod_effects["mod_output"] if "mod_output" in mod_effects else ryukbot_settings["output_folder"]
    snd_fix = mod_effects["mod_snd_fix"] if "mod_snd_fix" in mod_effects else ryukbot_settings["snd_fix"]
    text_chat = mod_effects["mod_text_chat"] if "mod_text_chat" in mod_effects else ryukbot_settings["text_chat"]
    voice_chat = mod_effects["mod_voice_chat"] if "mod_voice_chat" in mod_effects else ryukbot_settings["voice_chat"]
    end_commands = mod_effects["mod_end_commands"] if "mod_end_commands" in mod_effects else ryukbot_settings["end_commands"]
    
    output_path = Path(f'{ryukbot_settings["tf_folder"]}\{outputFolder}')
    
    if not output_path.exists():
        os.mkdir(output_path)
    
    
    # Starts the new command line
    try:
        vdm_count = new_command(vdm_count, VDM)
        VDM.write('factory "SkipAhead"\n\t\tname "skip"\n\t\tstarttick "%s"\n\t\tskiptotick "%s"\n\t}\n'
                % (last_tick, start_tick - 100))
        
        vdm_count = new_command(vdm_count, VDM)
    except:
        print_error(ryukbot_settings, f'Error printing to {demo_name}.vdm', 372)
    
    # sets the chat_time based on the settings
    if text_chat:
        chat_time = 12
    else:
        chat_time = 0
        
    # Creates the commands to later be written in the VDM file.
    try:
        pre_commands = f' {mod_effects["mod_commands"]}; {ryukbot_settings["commands"]}; ' if 'mod_commands' in mod_effects else f' {ryukbot_settings["commands"]}; '
        commands = f'{"snd_soundmixer Default_mix; " if snd_fix else ""}hud_saytext_time {chat_time}; voice_enable {1 if voice_chat else 0}; crosshair {1 if crosshair else 0}; cl_drawhud {1 if hud else 0}; host_framerate {framerate};{pre_commands}'
        
        
        if 'mod_prefix' in mod_effects:
            demo_name = f'{mod_effects["mod_prefix"].replace(" ", "-")}_{demo_name}'
            
        if 'mod_suffix' in mod_effects:
            suffix = f'{suffix}_{mod_effects["mod_suffix"].replace(" ", "-")}'
            
        if 'mod_spectate' in mod_effects:
            commands = f'{commands} spec_player {mod_effects["mod_spectate"]}; spec_mode;'
            end_commands = f'{end_commands}; spec_mode; spec_mode'
        elif 'mod_spectateThird' in mod_effects:
            commands = f'{commands} spec_player {mod_effects["mod_spectate"]}; spec_mode; spec_mode;'
            end_commands = f'{end_commands}; spec_mode'
            
        if not outputFolder == '':
            demo_name = f'{outputFolder}\{demo_name}'
            
        # Writes the bulk of the startmovie command
        VDM.write('factory "PlayCommands"\n\t\tname "record_start"\n\t\tstarttick "%s"\n\t\tcommands "%s startmovie %s_%s-%s_%s %s; clear"\n\t}\n'
                % (start_tick, commands, demo_name, start_tick, end_tick, suffix, ryukbot_settings["method"]))
    except: 
        print_error(ryukbot_settings, f'Error printing to {demo_name}.vdm', 373)
    
    try:
        vdm_count = new_command(vdm_count, VDM)
        VDM.write('factory "PlayCommands"\n\t\tname "record_stop"\n\t\tstarttick "%s"\n\t\tcommands "%s; endmovie; host_framerate 0"\n\t}\n'
                % (end_tick, end_commands))
    except: 
        print_error(ryukbot_settings, f'Error printing to {demo_name}.vdm', 374)
    
    return vdm_count + 1


def complete_VDM(VDM, next_demo, last_tick, vdm_count, demo_name):
    """Ends the VDM file and optionally leads to the next demo if possible or toggled.

    Args:
        VDM (file):             The VDM to be written to
        next_demo (string):      The name of the demo that happens after the current one.
        last_tick (int):         The last tick used by the VDM in the printing process
        vdm_count (int):         The count of vdm commands so far in the vdm
        demo_name (string):      The name of the current demo
    """
    try:
        if next_demo == 'end' or not ryukbot_settings["record_continuous"]:
            commands = 'quit'
        else: 
            commands = f'playdemo {next_demo}'
        vdm_count = new_command(vdm_count, VDM)
        VDM.write('factory "PlayCommands"\n\t\tname "VDM end"\n\t\tstarttick "%s"\n\t\tcommands "%s"\n\t}\n}'
                % (last_tick, commands))
    except:
        print_error(ryukbot_settings, f'Error printing to {demo_name}.vdm', 379)


# Prints the backups to the folders told to
def write_backup(backup_location, events_per_demo):
    """Prints the backups to the folders its told to

    Args:
        backup_location (Path):         The path to the backup .txt file
        events_per_demo (Array/List):     The list of events in each demo
    """
    try: 
        if backup_location.is_file():
            write_method = 'a'
        else: 
            write_method = 'w'
            
        with open(backup_location, write_method) as backup_file:
            backup_file.write('>\n')
            for demoEvent in events_per_demo:
                # Write the line to the backup
                backup_file.write('[%s] %s %s ("%s" at %s)\n' % (demoEvent))
    except:
        print_error(ryukbot_settings, 'Error while writing backup', 343)
            
# Returns the amount of ticks to put before the clip
def ticks_prior(event):
    """Finds the amount of ticks to put before the clip being analysed

    Args:
        event (Array/List):     A list returned from REGEX showing all the pieces of the event being parsed

    Returns:
        int: The amount of ticks to put before the current clip
    """
    if event[1].lower() == 'killstreak':
        return ryukbot_settings['before_killstreak_per_kill'] * int(event[2])
    else:
        return ryukbot_settings['before_bookmark']
      
# Returns the amount of ticks to put after the clip      
def ticks_after(event):
    """Finds the amount of ticks to put after the clip being analysed

    Args:
        event (Array/List):     A list returned from REGEX showing all the pieces of the event being parsed

    Returns:
        int: The amount of ticks to put after the current clip
    """
    if event[1].lower() == 'killstreak':
        return ryukbot_settings['after_killstreak']
    else:
        return ryukbot_settings['after_bookmark']
    
def killstreak_counter(event, current_count):
    """Counts the amount of kills in each killstreak

    Args:
        event (Array/List): A list returned from REGEX showing all the pieces of the event being parsed
        current_count (int): The amount of kills in the killstreak already

    Returns:
        int: The amount of kills in the killstreak
    """
    try:
        if event[1].lower() == 'killstreak':
            if int(event[2]) >= int(current_count + 1):
                return int(event[2])
            else:
                return current_count + int(event[2])
        elif event[1].lower() == 'kill':
            if int(event[2].split(':')[1]) >= int(current_count + 1):
                return int(event[2].split(':')[1])
            else:
                return current_count + int(event[2].split(':')[1])
        else:
            return current_count
    except:
        print_error(ryukbot_settings, 'Error counting killstreak amount', 405)
    
# Counts the amount of time bookmark is tapped
def tap_counter(event, next_event, tap_count):
    """Counts the amount of time bookmark is "tapped"

    Args:
        event (Array/List): A list returned from REGEX showing all the pieces of the event being parsed
        next_event (Array/List): The event after the current one
        tap_count (int): The amount of taps already

    Returns:
        int: The amount of times the bookmark button has been hit
    """
    if event[1].lower() == 'bookmark':
        if next_event[1].lower() == 'bookmark':
            if int(event[4]) + ryukbot_settings['interval_for_rewind_double_taps'] >= int(next_event[4]):
                tap_count += 1
    return tap_count

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
        
# Read _events.txt or killstreaks.txt file 
def ryukbot():
    """
        The base of the entire program
    """
    try:
        tf_folder, event_file_name, event_file = validate_event_file(ryukbot_settings)
            
        with open(event_file, 'r') as _events:

            # Saving the file as an array/list variable
            eventLines = _events.readlines()
            
            # REGEX for future use
            lineRegex = re.compile('\[(.*)\] (kill|killstreak|bookmark|player) (.*) \("(.*)" at (\d*)\)', re.IGNORECASE)
            carrotRegex = re.compile('\n(\>)?\n')
            
            # Combines it into one string and searches it
            event_marks = lineRegex.findall(''.join(eventLines))
            carrot_count = len(carrotRegex.findall("".join(eventLines))) + 1
            
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
                cprint((f"{event_file_name} is empty"), 'red')
                print(f'Would you like to run the {event_file_name} maker?')
                if yesNo():
                    if _event_maker(event_file, event_file_name, ryukbot_settings['advanced_event_maker']):
                        os.system('cls')
                        cprint('Run Ryukbot now?\n', 'cyan')
                        if yesNo():
                            ryukbot()
                        else:
                            input("Press enter to close...")
                            os._exit(0)
                else:
                    input("Press enter to close...")
                    os._exit(0)
            
            # Simple message letting the user know the programs progress.
            # More updates to the user are nice but I want to try and limit spam to the user.
            cprint(f'Scanned {len(eventLines)} different events over the span of {carrot_count} demos.', 'green')
            print_detail(ryukbot_settings, f'Wow! You don\'t get many kills do you?', 'magenta', 68)
        
            all_events = []
            events_per_demo = []
            # Loops through the list of events in the event_marks list
            for event in event_marks:
                # Checks if part of the same demo
                if demo_name != event[3]:
                    # Appends to the all_events list for later use
                    all_events.append(events_per_demo)
                    
                    # resets the demo_name
                    demo_name = event[3]
                    
                    # resets the events
                    events_per_demo = []
                
                # Appends the current event to the end of the events_per_demo list
                events_per_demo.append(event)
                
            # Pushes the last demo to the all_events list as the for loop above doesn't do it
            all_events.append(events_per_demo)
            
            
            # Get current directory path and add the backups folder to the end as well as
            # Make the folder if it doesnt exist yet
            if not os.path.exists(dir_path := Path(tf_folder + '\\ryukbot_backups\\')):
                os.makedirs(dir_path)
                os.makedirs(Path((str(dir_path) + '\\demos\\')))
            elif not os.path.exists(Path((str(dir_path) + '\\demos\\'))):
                os.makedirs(Path((str(dir_path) + '\\demos\\')))
                
            # Saves the date time locally for naming purposes
            date_time = str(dt.now().date()) + '_' + str(dt.now().time()) + '.txt'
            
            
            demo_index = 0
            while demo_index < len(all_events):
                demo_events = all_events[demo_index]
                demo_name = demo_events[0][3]
                
                if (demo_index + 1 < len(all_events)):
                    next_demo = all_events[demo_index + 1][0][3]
                else:
                    next_demo = 'end'
                
                print_detail(ryukbot_settings, f'\nScanning demo: {demo_name}', 'green', 2)
                
                # The location of the file we want to make
                backup_demo_location = Path((str(dir_path) + '\\demos\\' + demo_name + '.txt'))
                backup_location = Path((str(dir_path) + '\\' + (date_time.replace(':', '-')).split('.')[0] + '.txt'))
                
                # Writes the backups to the files
                write_backup(backup_demo_location, demo_events)
                write_backup(backup_location, demo_events)

                i = 0
                clip_count = 0
                bookmark = False
                vdm_path = Path(tf_folder + '\\' + demo_name + '.vdm')
                
                demo_ticks = []
                
                if not (vdm_path.exists() and (ryukbot_settings["safe_mode"])):
                    with open(vdm_path, 'w+') as VDM:
                        last_tick = ryukbot_settings['start_delay']
                        
                        VDM.write('demoactions\n{\n')
                        
                        while i < len(demo_events):
                            event = demo_events[i]
                            killstreak_count = killstreak_counter(event, 0)

                            mod_effects = check_mods(ryukbot_settings, event, {})
                            
                            if event[1].lower() == 'bookmark':
                                bookmark = True
                            
                            start_tick = int(event[4]) - ticks_prior(event)
                            end_tick = int(event[4]) + ticks_after(event)
                            end_tick += int(mod_effects['modExtend']) if "modExtend" in mod_effects else 0
                            
                            check_next = True
                            tap_count = 0
                            while check_next:
                                
                                # Checks that its less than the length of the list
                                if i+1 < len(demo_events):
                                    # Confirms rewind double taps
                                    tap_count = tap_counter(event, demo_events[i+1], tap_count)
                                    
                                    # Checks if end_tick is before the start of the next clip
                                    if end_tick >= ((int(demo_events[i+1][4]) - ticks_prior(demo_events[i+1])) - ryukbot_settings['minimum_ticks_between_clips']):
                                        killstreak_count =  killstreak_counter(demo_events[i+1], killstreak_count)
                                        # Sets a new end tick
                                        end_tick = int(demo_events[i+1][4]) + ticks_after(demo_events[i+1])
                                        end_tick += int(mod_effects['modExtend']) if "modExtend" in mod_effects else 0
                                        mod_effects = check_mods(ryukbot_settings, demo_events[i+1], mod_effects)
                                        # Incriments i to show that line has been parsed already
                                        i += 1
                                    else:
                                        check_next = False
                                else:
                                    check_next = False
                            
                            clip_count += 1
                            suffix = ''
                            if killstreak_count == 0:
                                suffix = 'BM'
                            else: 
                                if bookmark:
                                    suffix = ('BM%s+' % (killstreak_count))
                                else:
                                    suffix = ('KS%s' % (killstreak_count))
                                    
                            start_tick -= tap_count * ryukbot_settings['rewind_amount']
                            
                            if start_tick < ryukbot_settings["start_delay"]:
                                start_tick = ryukbot_settings["start_delay"]
                                
                            if end_tick < ryukbot_settings["start_delay"]:
                                end_tick = ryukbot_settings["start_delay"] + 500
                            
                            demo_ticks.append({
                                "start_tick": start_tick,
                                "end_tick": end_tick,
                                "suffix": suffix,
                                "mod_effects": mod_effects
                            })
                            
                            display_demo_name = f'{mod_effects["mod_prefix"].replace(" ", "-")}_{demo_name}' if 'mod_prefix' in mod_effects else demo_name
                            
                            display_suffix = f'{suffix}_{mod_effects["mod_suffix"].replace(" ", "-")}' if 'mod_suffix' in mod_effects else suffix
                                
                            print_detail(ryukbot_settings, f'Clip {clip_count}: {display_demo_name}_{start_tick}-{end_tick}_{display_suffix}', 'cyan', 2)
                            
                            # IGNORE THIS
                            if ((rand := randint(1, 100)) <= 5):
                                print_detail(ryukbot_settings, f'Oh god this one is BAD', 'magenta', 68)
                            elif (5 < rand <= 10):
                                print_detail(ryukbot_settings, f'Don\'t even record this one', 'magenta', 68)
                            elif (10 < rand <= 15):
                                print_detail(ryukbot_settings, f'I don\'t know why this was even marked', 'magenta', 68)
                            elif (15 < rand <= 20):
                                print_detail(ryukbot_settings, f'I have learned what pain feels like from that clip', 'magenta', 68)
                            elif (20 < rand <= 25):
                                print_detail(ryukbot_settings, f'This is why robots will eventually take over', 'magenta', 68)
                            elif (25 < rand <= 30):
                                print_detail(ryukbot_settings, f'Imagine spending all this time playing to only get a clip like that', 'magenta', 68)
                                
                                
                            # Increment i
                            i += 1
                        
                        vdm_count = 1
                        clip = 0
                        
                        print_detail(ryukbot_settings, f'Writing file: {demo_name}.vdm', 'green', 3)
                        
                        while clip < len(demo_ticks):
                            
                            # Sets original tick counts 
                            clip_start = demo_ticks[clip]["start_tick"]
                            clip_end = demo_ticks[clip]["end_tick"]
                            suffix = demo_ticks[clip]["suffix"]
                            demo_mods = demo_ticks[clip]["mod_effects"]
                            
                            double_check = True
                            while double_check:
                                
                                # Checks that its less than the length of the list
                                if i+1 < len(demo_ticks):
                                    # Checks if end_tick is before the start of the next clip
                                    if clip_end >= ((demo_ticks[clip+1]["start_tick"]) - ryukbot_settings['minimum_ticks_between_clips']):
                                        # Sets a new end tick
                                        clip_end = int(demo_ticks[clip+1]["end_tick"])
                                        
                                        # Combines the suffixes to show it was multiple seperated clips combined
                                        suffix = suffix + '_' + demo_ticks[clip+1]["suffix"]
                                        # Incriments i to show that line has been parsed already
                                        clip += 1
                                    else:
                                        double_check = False
                                else:
                                    double_check = False
                                    
                            vdm_count = print_VDM(VDM, demo_name, clip_start, clip_end, suffix, last_tick, vdm_count, demo_mods)
                            last_tick = clip_end + 100
                            clip += 1
                            
                        complete_VDM(VDM, next_demo, last_tick, vdm_count, demo_name)
                        
                        print_detail(ryukbot_settings, f'Done writing file: {demo_name}.vdm', 'green', 0)
                        print_detail(ryukbot_settings, f'Found {clip_count} clip(s)', 'green', 1)
                                
                        demo_index += 1
                else: 
                    demo_index += 1
                    print_detail(ryukbot_settings, f'{demo_name}.vdm already exists', 'yellow', 0)  
                    print_detail(ryukbot_settings, f'Disable "safe_mode" in the settings to overwrite anyway', 'yellow', 0)  
                    print_detail(ryukbot_settings, f'I didn\'t think anyone would ever actually use that awful setting', 'magenta', 68)
                

        cprint(f'\nScanning {event_file_name} is complete', 'green')
        if ryukbot_settings["clear_events"]:
            cprint(f'Clearing {event_file_name}', 'yellow')
            try:
                open(event_file, 'w+').close()
                cprint(f'{event_file_name} cleared')
            except:
                print_error(ryukbot_settings, f'Error while clearing {event_file_name}', 398)
        input("Press enter to close...")
        os._exit(0)
    except IndexError:
        print_error(ryukbot_settings, 'An Unexpected error occurred while running Ryukbot', 101)
                
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
        
ryukbot()