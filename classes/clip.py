class Clip:
    
    def __init__(self, settings, event):
        self._events = [event]
        self._demo_name = event.demo_name
        self._has_killstreak = False
        self._effects = event.effects
        
        if event.is_killstreak():
            self.init_killstreak(settings, event)

        else:
            self.init_bookmark(settings, event)

    
    def init_killstreak(self, settings, event):
        self._has_killstreak = True

        self._start = event.tick - (settings['before_killstreak_per_kill'] * int(event.value))

        if self._start < settings['start_delay']:
            self._start = settings['start_delay']

        self._end = event.tick + settings['after_killstreak']

    def init_bookmark(self, settings, event):
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

        if other_clip.start < self._start:
            self._start = other_clip.start

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