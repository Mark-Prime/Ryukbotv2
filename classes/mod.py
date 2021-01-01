import re

modOptions = {
    "prefix": "prefix",
    "-p": "prefix",
    "suffix": "suffix",
    "-s": "suffix",
    "commands": "commands",
    "run": "commands",
    "-r": "commands",
    "framerate": "framerate",
    "fps": "framerate",
    "crosshair": "crosshair",
    "-ch": "crosshair",
    "hud": "hud",
    "text_chat": "text_chat",
    "textchat": "text_chat",
    "-tc": "text_chat",
    "voice_chat": "voice_chat",
    "voicechat": "voice_chat",
    "-vc": "voice_chat",
    "output": "output",
    "-o": "output",
    "spectate": "spec_first",
    "-sp": "spec_first",
    "spec_first": "spec_first",
    "specfirst": "spec_first",
    "-s1": "spec_first",
    "specthird": "specthird",
    "-s3": "specthird",
    "run_after": "run_after",
    "runafter": "run_after",
    "-ra": "run_after",
    "end_commands": "end_commands", 
    "endcommands": "end_commands",
    "-ec": "end_commands",
    "extend": "extend",
    "-e": "extend",
}

class Mod:
    TOTAL = 0
    def __init__(self, mod_source):
        Mod.TOTAL += 1
        self.id = Mod.TOTAL
        self.title = mod_source["title"]
        self.description = mod_source["description"]
        self.code = mod_source["code"]
        
        self.generate_effects()
        
    def generate_effects(self):
        self.effects = []
        lines = []
        if ' > ' not in self.code:
            lines = [self.code]
        else:
            lines = self.code.split(" > ")
            
        for line in lines:
            print(line)
            self.generate_effect(line)
        
    def generate_effect(self, line):
        rbcParse = re.compile(r"(.*) \'(.*)\' on \'(killstreak|bookmark|ks|bm|\*)\'( value | unless | -v | -u | includes | excludes | -i | -d )?(\'(.*)\')?", re.IGNORECASE)
        effect_code = rbcParse.search(line)
        self.effects.append(Effect(effect_code))
    
    
class Effect:
    
    def __init__(self, line):
        self.command = self.validate_command(line[1])
        self.value = self.validate_value(line[2])
        self.type = self.validate_type(line[3])
        self.comparitor = self.validate_comparitor(line[4])
        self.compared_value = self.validate_compared_value(line[5])
        
    def validate_command(self, command):
        if command in modOptions:
            return modOptions[command]
        else: 
            raise ValueError('A very specific bad thing happened.')
    
    def validate_value(self, value):
        if value.lower() == '[v]':
            return '[value]'
        
        if value.lower() == '[t]':
            return '[type]'
        
        return value
    
    def validate_type(self, effect_type):
        effect_type_lower = effect_type.lower()
        
        if effect_type_lower == 'bm':
            return 'bookmark'
        
        if effect_type_lower == 'ks':
            return 'killstreak'
        
        return effect_type
    
    def validate_comparitor(self, comparitor):
        if not comparitor:
            return '*'
        
        return comparitor.replace(' ', '')
    
    def validate_compared_value(self, compared_value):
        if not compared_value:
            return "*"
        
        return compared_value.replace('\'', '')
        
    
    
    
mod_source = {
            "title": "Exec configBackup.cfg",
            "description": "execs configBackup.cfg when the clip ends",
            "code": "suffix '[v]' on 'bm' > -o '[v]' on 'bm' excludes 'General&spec'"
        }

mod = Mod(mod_source)