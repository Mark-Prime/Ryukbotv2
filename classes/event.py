import re

#* The syntax for getting the variables and its information
# LINE: event_marks[*]           --- EXAMPLE ('2020/04/27 20:23', 'Killstreak', '3', '2020-04-27_20-16-21', '29017')
# DATE: event_marks[*][0]        --- EXAMPLE 2020/04/27 20:23
# TYPE: event_marks[*][1]        --- EXAMPLE Killstreak 
# CRITERIA: event_marks[*][2]    --- EXAMPLE 3
# DEMO: event_marks[*][3]        --- EXAMPLE 2020-04-27_20-16-21
# TICK: event_marks[*][4]        --- EXAMPLE 29017

class Event:
    TOTAL = 0
    
    def __init__(self, event):
        Event.TOTAL += 1
        self.id = Event.TOTAL
        self.event = event
        self.date = event[0]
        self.demo_name = event[2]
        self.tick = int(event[3])
        self.type = ""
        self.value = ""
        self.effects = {}
        
        try:
            self.validate_event()
        except Exception:
            print(f'Failed to validate event: {self.id}')
            
    def __str__(self):
        return f'[{self.date}] {self.type} {self.value} ("{self.demo_name}" at {self.tick})'
        
    def __repr__(self):
        return f'[{self.event[0]}] {self.event[1]} ("{self.event[2]}" at {self.event[3]})'
            
    def validate_event(self):
        if ' ' not in self.event[1]:
            self.type = 'Bookmark'
            self.value = self.event[1]
        else:
            event_split = self.event[1].split(' ')

            if event_split[0].lower() == 'kill' or event_split[0].lower() == 'killstreak' or event_split[0].lower() == 'bookmark':
                self.type = event_split[0]
                event_split.pop(0)
            else: 
                self.type = 'Bookmark'

            self.value = " ".join(event_split)
        
            self.convert_prec()
                
    def convert_prec(self):
        if self.type.lower() == 'kill':
            self.type = 'Killstreak'
            self.value = self.value.split(':')[1]
            
        if self.type.lower() == 'player':
            self.type = 'Bookmark'
            self.value = 'General'
            
    def is_killstreak(self):
        return self.type == 'Killstreak'
        
    def display_values(self):
        print('=================')
        print(f'Date: {self.date}')
        print(f'Type: {self.type}')
        print(f'Value: {self.value}')
        print(f'Demo Name: {self.demo_name}')
        print(f'Tick: {self.tick}')
        print(f'Is killsteak: {self.is_killstreak()}')
        print('=================')
            
    def apply_mod(self, mod): 
        for effect in mod.effects:
            if effect.does_effect_apply(self):
                split_value = self.value.split(' ')

                if effect.value == '[value]':
                    value = self.value
                elif effect.type == '[type]':
                    value = self.type
                elif effect.value == '[firstvalue]':
                    value = split_value[0]
                elif effect.value == '[lastvalue]':
                    value = split_value[len(split_value) - 1]
                else:
                    value = effect.value

                self.effects[effect.command] = value