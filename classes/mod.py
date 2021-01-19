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
            # print(line)
            self.generate_effect(line)
        
    def generate_effect(self, line):
        rbcParse = re.compile(r"(.*) \'(.*)\' on \'(killstreak|bookmark|ks|bm|\*)\'( value | unless | -v | -u | includes | excludes | -i | -d )?(\'(.*)\')?", re.IGNORECASE)
        effect_code = rbcParse.search(line)
        self.effects.append(Effect(effect_code))
        
    def run(self):
        pass
    
    
class Effect:
    
    def __init__(self, line):
        self.command = self.validate_command(line[1])
        self.value = self.validate_value(line[2])
        self.type = self.validate_type(line[3])
        self.comparitor = self.validate_comparitor(line[4])
        self.compared_value = self.validate_compared_value(line[5])

    def __str__(self):
        return f"""Command: {self.command}
Value: {self.value}
Type: {self.type}
Comparitor: {self.comparitor}
Compared Value: {self.split_type.join(self.compared_value)}"""
        
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
        self.split_type = '|'
        if not compared_value:
            return ["*"]

        compared_value.replace('\'', '')

        if "&" in compared_value:
            self.split_type = '&'
            compared_value = compared_value.split('&')
        elif "|" in compared_value:
            compared_value = compared_value.split('|')
        else:
            compared_value = [compared_value]
        
        return compared_value

    def is_type_match(self, event):
        return self.type.lower() == event.type.lower() or self.type == '*'

    def does_effect_apply(self, event):
        if not self.is_type_match(event):
            return False

        if self.comparitor == '*':
            return True

        elif self.comparitor == 'value':
            return self.is_value(event)

        elif self.comparitor == 'unless':
            return not self.is_value(event)

        elif self.comparitor == 'includes':
            return self.is_included(event)

        elif self.comparitor == 'excludes':
            return self.is_excluded(event)
        
        return False

    def is_value(self, event):
        if self.split_type == "|":
            for value in self.compared_value:
                value = value.replace('\'', '')
                if event.value == value or value == '*':
                    return True
            return False

        elif self.split_type == "&":
            for value in self.compared_value:
                value = value.replace('\'', '')
                if event.value != value or value == '*':
                    return False
            return True
        
    def is_included(self, event):
        if self.split_type == "|":
            for value in self.compared_value:
                value = value.replace('\'', '')
                if value in event.value or value == '*':
                    return True
            return False

        elif self.split_type == "&":
            for value in self.compared_value:
                value = value.replace('\'', '')
                if value not in event.value or value == '*':
                    return False
            return True 

    def is_excluded(self, event):
        if self.split_type == "|":
            for value in self.compared_value:
                value = value.replace('\'', '')
                if value not in event.value or value == '*':
                    return True
            return False

        elif self.split_type == "&":
            for value in self.compared_value:
                value = value.replace('\'', '')
                if value in event.value or value == '*':
                    return False
            return True