import re
from sprint import *

# Activates the color in the console without this there would be no colors
colorama.init()

mod_options = {
    "prefix": "modPrefix",
    "-p": "modPrefix",
    "suffix": "modSuffix",
    "-s": "modSuffix",
    "commands": "modCommands",
    "run": "modCommands",
    "-r": "modCommands",
    "framerate": "modFramerate",
    "fps": "modFramerate",
    "crosshair": "modCrosshair",
    "-ch": "modCrosshair",
    "hud": "modHud",
    "text_chat": "modText_chat",
    "textchat": "modText_chat",
    "-tc": "modText_chat",
    "voice_chat": "modVoice_chat",
    "voicechat": "modVoice_chat",
    "-vc": "modVoice_chat",
    "output": "modOutput",
    "-o": "modOutput",
    "spectate": "modSpectate",
    "-sp": "modSpectate",
    "specfirst": "modSpectate",
    "-s1": "modSpectate",
    "specthird": "modSpectateThird",
    "-s3": "modSpectateThird",
    "run_after": "modEndCommands",
    "runafter": "modEndCommands",
    "-ra": "modEndCommands",
    "end_commands": "modEndCommands",
    "endcommands": "modEndCommands",
    "-ec": "modEndCommands",
    "extend": "modExtend",
    "-e": "modExtend",
}

#! MOD COMMANDS DOCUMENTATION
# Command       Shortcut    Description

# commands      run         Runs tf2 console commands when the clip starts
# crosshair     -ch         Enable or disable crosshair
# endcommands   -ec         Runs tf2 console commands when the clip ends (same as runafter)
# extend        -e          Adds extra time to the end of the recording
# framerate     fps         Changes the fps of the clip
# hud                       Enable or disable hud
# prefix        -p          Add text to the beginning of a clip
# output        -o          The folder to output this clip to
# runafter      -ra         Runs tf2 console commands when the clip ends (same as endcommands)
# specfirst     -s1         Spectate a specific player in an stv demo in firstperson (same as spectate)
# spectate      -sp         Spectate a specific player in an stv demo (same as specfirst)
# specthird     -s3         Spectate a specific player in an stv demo in thirdperson
# suffix        -s          Add text to the end of a clip
# textchat      -tc         Enable or disable text chat
# voicechat     -vc         Enable or disable voice chat

#! MOD VALUE DOCUMENTION
# Value         Shortcut    Descrption

# [value]       [v]         Whatever the value of the bookmark or killstreak is
# [lastvalue]   [lv]        Whatever the last value/word of the bookmark or killstreak is 
# [firstvalue]  [fv]        Whatever the first value/word of the bookmark or killstreak is
# [type]        [t]         If its a killstreak or bookmark

#! MOD ACTIVATOR DOCUMENTATION
# Activator     Shortcut    Descrption

# bookmark      bm          
# killstreak    ks
# *             All clips no matter what it is


def get_mod_options():
    return mod_options


def validate_code(condition, value, event):
    if condition == ' value ' or condition == ' -v ':
        if (event[2].lower() == value) or (value == '*'):
            return True
    elif condition == ' unless ' or condition == ' -u ':
        if not event[2].lower() == value:
            return True
    elif condition == ' includes ' or condition == ' -i ':
        if value in event[2].lower():
            return True
    elif condition == ' excludes ' or condition == ' -x ':
        if not value in event[2].lower():
            return True
    else: 
        return False   
        

def run_mod(code, event, mod_properties, type, valid):
    #* These are the results of the regex
    # code.group()  =>  suffix 'LOL' on 'killstreak' value '69'
    # code.group(1) =>  suffix
    # code.group(2) =>  LOL
    # code.group(3) =>  killstreak
    # code.group(4) =>  value   (might not be there)
    # code.group(5) =>  69      (might not be there)
    
    # If any code was found at all
    command = code.group(1).replace(' ','').lower()
    if command in mod_options if code.group() else False:
        
        # Check if the type matches the type of the clip
        code_lower = code.group(3).lower()
        event_lower = event[1].lower()
        if ((code_lower == 'bookmark' or code_lower == 'bm') and event_lower == 'bookmark'):
            type = True
        elif ((code_lower == 'killstreak' or code_lower == 'ks') and (event_lower == 'killstreak' or event_lower == 'kill')):
            type = True
        elif (code_lower == '*'):
            type = True
        
        # Only run if the types match
        if type:
            # if the value section doesnt exist default to any value 
            if code.group(5) is None:
                valid = True
            else:
                code_value = code.group(5).lower().replace("'", "")
                # checks if it should run when it matches or when it doesnt match
                if '&' in code_value: 
                    value_split = code_value.split('&')
                    for value in value_split:
                        valid = validate_code(code.group(4), value, event)
                        if not valid:
                            break
                elif '|' in code_value:
                    value_split = code_value.split('|')
                    for value in value_split:
                        valid = validate_code(code.group(4), value, event)
                        if valid:
                            break
                else:
                    valid = validate_code(code.group(4), code_value, event)
            
            # run if fully valid on all ends
            if valid:
                # rbcParse = re.compile(r"(.*) \'(.*)\' on \'(killstreak|bookmark|ks|bm|\*)\'( value | unless | -v | -u | includes | discludes | -i | -d )?(\'(.*)\')?", re.IGNORECASE)
                if code.group(2).lower() == '[type]' or code.group(2).lower() == '[t]':
                    mod_properties[mod_options[command]] = event[1]
                elif code.group(2).lower() == '[value]' or code.group(2).lower() == '[v]':
                    mod_properties[mod_options[command]] = event[2]
                elif code.group(2).lower() == '[firstvalue]' or code.group(2).lower() == '[fv]':
                    split_event = event[2].split(' ')
                    mod_properties[mod_options[command]] = split_event[0]
                elif code.group(2).lower() == '[lastvalue]' or code.group(2).lower() == '[lv]':
                    print(event[2])
                    split_event = event[2].split(' ')
                    print(split_event)
                    mod_properties[mod_options[command]] = split_event[len(split_event) - 1]
                else:
                    mod_properties[mod_options[command]] = code.group(2)

def check_mods(ryukbot_settings, event, mod_properties):
    rbcParse = re.compile(r"(.*) \'(.*)\' on \'(killstreak|bookmark|ks|bm|\*)\'( value | unless | -v | -u | includes | excludes | -i | -e )?(\'(.*)\')?", re.IGNORECASE)
    if "mods" in ryukbot_settings:
        for mod in ryukbot_settings["mods"]:
            try: 
                if ">" in mod["code"]:
                    code_split = mod['code'].split('>')
                    for code_item in code_split:
                        if not code_item.replace(' ','') == '':
                            code = rbcParse.search(code_item)
                            run_mod(code, event, mod_properties, False, False)
                else: 
                    code = rbcParse.search(mod["code"])
                    run_mod(code, event, mod_properties, False, False)
            except: 
                print_error(ryukbot_settings, 'Mod lacking code or it is incorrectly coded', 431)
            
            
                    
                        
    return mod_properties