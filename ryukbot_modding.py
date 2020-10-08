import re
from sprint import *

# Activates the color in the console without this there would be no colors
colorama.init()

modOptions = {
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
}

#! MOD COMMANDS DOCUMENTATION
# Command       Shortcut    Description

# commands      run         Runs tf2 console commands when the clip starts
# crosshair     -ch         Enable or disable crosshair
# endcommands   -ec         Runs tf2 console commands when the clip ends (same as runafter)
# framerate     fps         Changes the fps of the clip
# hud                       Enable or disable hud
# prefix        -p          Add text to the beginning of a clip
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
# [type]        [t]         If its a killstreak or bookmark

#! MOD ACTIVATOR DOCUMENTATION
# Activator     Shortcut    Descrption

# bookmark      bm          
# killstreak    ks
# *                         All clips no matter what it is


def getModOptions():
    return modOptions

def runMod(code, event, mod_properties, type, valid):
    #* These are the results of the regex
    # code.group()  =>  suffix 'LOL' on 'killstreak' value '69'
    # code.group(1) =>  suffix
    # code.group(2) =>  LOL
    # code.group(3) =>  killstreak
    # code.group(4) =>  value   (might not be there)
    # code.group(5) =>  69      (might not be there)
    
    # If any code was found at all
    command = code.group(1).replace(' ','').lower()
    if command in modOptions if code.group() else False:
        
        # Check if the type matches the type of the clip
        codeLower = code.group(3).lower()
        eventLower = event[1].lower()
        if ((codeLower == 'bookmark' or codeLower == 'bm') and eventLower == 'bookmark'):
            type = True
        elif ((codeLower == 'killstreak' or codeLower == 'ks') and (eventLower == 'killstreak' or eventLower == 'kill')):
            type = True
        elif (codeLower == '*'):
            type = True
        
        # Only run if the types match
        if type:
            # if the value section doesnt exist default to any value 
            if code.group(5) is None:
                valid = True
            else:
                # checks if it should run when it matches or when it doesnt match
                if code.group(4) == ' value ' or code.group(4) == ' -v ':
                    if (event[2].lower() == code.group(5).lower().replace("'", "")) or (code.group(5).lower().replace("'", "") == '*'):
                        valid = True
                elif code.group(4) == ' unless ' or code.group(4) == ' -u ':
                    if not event[2].lower() == code.group(5).lower().replace("'", ""):
                        valid = True
            
            # run if fully valid on all ends
            if valid:
                if code.group(2).lower() == '[type]' or code.group(2).lower() == '[t]':
                    mod_properties[modOptions[command]] = event[1]
                elif code.group(2).lower() == '[value]' or code.group(2).lower() == '[v]':
                    mod_properties[modOptions[command]] = event[2]
                else:
                    mod_properties[modOptions[command]] = code.group(2)

def checkMods(ryukbot_settings, event, mod_properties):
    rbcParse = re.compile(r"(.*) \'(.*)\' on \'(killstreak|bookmark|ks|bm|\*)\'( value | unless | -v | -u )?(\'(.*)\')?", re.IGNORECASE)
    if "mods" in ryukbot_settings:
        for mod in ryukbot_settings["mods"]:
            try: 
                if ">" in mod["code"]:
                    codeSplit = mod['code'].split('>')
                    for codeItem in codeSplit:
                        if not codeItem.replace(' ','') == '':
                            code = rbcParse.search(codeItem)
                            runMod(code, event, mod_properties, False, False)
                else: 
                    code = rbcParse.search(mod["code"])
                    runMod(code, event, mod_properties, False, False)
            except: 
                eprint(ryukbot_settings, 'Mod lacking code or it is incorrectly coded', 431)
            
            
                    
                        
    return mod_properties