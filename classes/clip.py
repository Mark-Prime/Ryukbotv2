class Clip:
    
    def __init__(self, settings, event):
        self._events = [event]
        self._demo_name = event.demo_name
        self._has_killstreak = False
        self._has_bookmark = False
        self._ks_value = 0
        self._effects = event.effects
        
        if event.is_killstreak():
            self.init_killstreak(settings, event)

        else:
            self.init_bookmark(settings, event)

        if 'extend' in self._effects:
            self._end += self._effects['extend']

    
    def init_killstreak(self, settings, event):
        self._has_killstreak = True

        if self._ks_value == 0 or self._ks_value == event.value - 1:
            self._ks_value = int(event.value)
        else:
            self._ks_value += int(event.value)

        self._start = event.tick - (settings['before_killstreak_per_kill'] * int(event.value))

        self.validate_start(settings)

        self._end = event.tick + settings['after_killstreak']

    def init_bookmark(self, settings, event):
        self._has_bookmark = True

        self._start = event.tick - settings['before_bookmark']

        self.validate_start(settings)

        self._end = event.tick + settings['after_bookmark']

    def validate_start(self, settings):
        if self._start < settings['start_delay']:
            self._start = settings['start_delay']

    def can_include(self, min_ticks_between, other_clip):
        return other_clip.start < (self.end + min_ticks_between)

    def include(self, settings, other_clip):
        self._end = other_clip.end
        self._effects.update(other_clip.effects)
        
        if other_clip.has_killstreak:
            self._has_killstreak = True

            if self._ks_value == 0 or self._ks_value == other_clip._ks_value - 1:
                self._ks_value = int(other_clip._ks_value)
            else:
                self._ks_value += int(other_clip._ks_value)
        
        if other_clip.has_bookmark:
            self._has_bookmark = True

        if other_clip.start < self._start:
            self._start = other_clip.start

        self.validate_start(settings)

        if (self._events[len(self._events) - 1].tick - other_clip._events[len(self._events) - 1].tick) <= settings['interval_for_rewind_double_taps']:
            self._start = self._start - settings['rewind_amount']
            self.validate_start(settings)

    @property
    def demo_name(self):
        return self._demo_name

    @property
    def has_killstreak(self):
        return self._has_killstreak

    @property
    def has_bookmark(self):
        return self._has_bookmark

    @property
    def events(self):
        return self._events

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def effects(self):
        return self._effects

    @property
    def type(self):
        clip_type = ''
        if self.has_bookmark:
            clip_type = 'BM'
            if self._ks_value > 0:
                clip_type += str(self._ks_value) + '+'
        else: 
            clip_type = 'KS' + str(self._ks_value)

        return clip_type