import re

class Event:
    TOTAL = 0
    
    def __init__(self, event):
        Event.TOTAL += 1
        self.id = Event.TOTAL
        self.event = event
        self.date = event[0]
        self.demo_name = event[2]
        self.original_tick = int(event[3])
        
        try:
            self.validate_event()
        except:
            print('Failed to validate event: ' + self.id)
            
    def validate_event(self):
        if not (' ' in self.event[1]):
            self.type = 'Bookmark'
            self.value = self.event[1]
        else:
            event_split = self.event[1].split(' ')
            self.type = event_split[0]
            event_split.pop(0)
            self.value = " ".join(event_split)
        
            self.convert_prec()
                
    def convert_prec(self):
        if self.type == 'Kill':
            self.type = 'Killstreak'
            self.value = self.value.split(':')[1]
            
        if self.type == 'Player':
            self.type = 'Bookmark'
            self.value = 'General'
            
    def is_killstreak(self):
        return self.type == 'Killstreak'
            
    def print(self):
        print(f'[{self.date}] {self.type} {self.value} ("{self.demo_name}" at {self.original_tick})')
        
    def print_event(self):
        print(f'[{self.event[0]}] {self.event[1]} ("{self.event[2]}" at {self.event[3]})')
        
    def display_values(self):
        print(f'Date: {self.date}')
        print(f'Type: {self.type}')
        print(f'Value: {self.value}')
        print(f'Demo Name: {self.demo_name}')
        print(f'Tick: {self.original_tick}')
        print(f'ID: {self.id}')
        print(f'Is killsteak: {self.is_killstreak()}')
