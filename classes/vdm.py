from pathlib import Path
from datetime import datetime as dt

class VDM:
    def __init__(self, settings, clip):
        self._clips = [clip]
        self._demo_name = clip.demo_name
        self._settings = settings
        self._command_count = 1
        self._last_clip_end = settings['start_delay'] - 100

        self.open()

    def __len__(self):
        return len(self._clips)

    def append(self, clip):
        self.print_latest_clip()
        self._clips.append(clip)

    def open(self):
        self._path = Path(f'{self._settings["tf_folder"]}/{self._demo_name}.vdm')
        self._is_printable = True

        if self._path.is_file() and self._settings['safe_mode'] == 1:
            self._is_printable = False

        if self._is_printable:
            self._output = open(self._path, 'w+')

            self.write('demoactions\n{\n')

    def write(self, message):
        if self._is_printable:
            self._output.write(message)

    def print_latest_clip(self):
        self.skip_to_clip()
        self.start_clip()
        self.end_clip()

    def start_clip(self):
        self.start_command()
        commands = self.validate_commands()
        self.write("""factory "PlayCommands"
		name "record_start"
		starttick "%s"
		commands "%s"
	}\n""" % (self.latest.start, commands))

    def validate_commands(self):
        commands = ''
        effects = self.latest.effects

        self.check_effect('HUD')
        self.check_effect('voice_chat')
        self.check_effect('text_chat')
        self.check_effect('crosshair')
        self.check_effect('framerate')

        commands += f'cl_drawhud {1 if effects["HUD"] else 0}; '
        commands += f'voice_enable {1 if effects["voice_chat"] else 0}; '
        commands += f'hud_saytext_time {12 if effects["text_chat"] else 0}; '
        commands += f'crosshair {1 if effects["crosshair"] else 0}; '
        commands += f'host_framerate {effects["framerate"]}; '


        if 'commands' not in effects:
            effects['commands'] = self._settings['commands']
        elif self._settings["commands"] != "": 
            effects['commands'] = f'{effects["commands"]}; {self._settings["commands"]};'
        else:
            effects['commands'] = ''

        if 'spec_first' in effects:
            effects['commands'] = f'{effects["commands"]} spec_player {effects["spec_first"]}; spec_mode;'
        elif 'spec_third' in effects:
            effects['commands'] = f'{effects["commands"]} spec_player {effects["spec_third"]}; spec_mode; spec_mode;'

        
        if 'output_folder' not in effects:
            if self._settings["output_folder"] != "":
                effects['output_folder'] = f'{self._settings["output_folder"]}\\'
            else: 
                effects['output_folder'] = ''
        elif self._settings["output_folder"] != "": 
            effects['output_folder'] = f'{effects["output_folder"]}\\'
        elif effects['output_folder'] != "":
            effects['output_folder'] = effects['output_folder'].replace(' ', '_') + '\\'

        self.check_effect('prefix', "")
        self.check_effect('suffix', "")

        clip_type = self.latest.type

        self.latest_display_name = f"{effects['output_folder']}{effects['prefix'].replace(' ', '_')}{self._demo_name}_{self.latest.start}-{self.latest.end}_{clip_type}{effects['suffix'].replace(' ', '_')}"
        self.latest.display_name = self.latest_display_name
        return f"{commands}{effects['commands']} startmovie {self.latest.display_name} h264; clear"

    def check_effect(self, effect, default=None):
        if effect not in self.latest.effects:
            if default != None:
                self.latest.effects[effect] = default
            else:
                self.latest.effects[effect] = self._settings[effect]
        elif effect == "prefix":
            self.latest.effects[effect] += '_'
        elif effect == "suffix":
            self.latest.effects[effect] = '_' + self.latest.effects[effect]

    def end_clip(self):
        self.start_command()
        self._last_clip_end = self.latest.end

        end_commands = "endmovie; host_framerate 0"

        if 'end_commands' in self.latest.effects:
            end_commands = f'{self.latest.effects["end_commands"]}; {end_commands}'

        if 'spec_first' in self.latest.effects:
            end_commands = f'spec_mode; spec_mode; {end_commands}'
        elif 'spec_third' in self.latest.effects:
            end_commands = f'spec_mode; {end_commands}'

        self.write("""factory "PlayCommands"
		name "record_stop"
		starttick "%s"
		commands "%s"
	}\n""" % (self._last_clip_end, end_commands))

    def skip_to_clip(self):
        if ((self.latest.start - 100) - (self._last_clip_end + 100)) > self._settings['minimum_ticks_between_clips']:
            self.start_command()

            self.write(f"""factory "SkipAhead"
		name "skip"
		starttick "{self._last_clip_end + 100}"
		skiptotick "{self.latest.start - 100}"
    """ + '}\n')

    def start_command(self):
        self.write('\t"%s"\n\t{\n\t\t' % (self._command_count))
        self._command_count += 1

    def close(self, next_demo=None):
        self.backup()
        self.print_latest_clip()
        self.start_command()
        self.write("""factory "PlayCommands"
		name "VDM end"
		starttick "%s"
		commands "%s"
	}\n""" % (self._last_clip_end + 100, f'playdemo {next_demo}' if next_demo != None else 'quit'))
        self.write('}')
        if self._is_printable:
            self._output.close()

    def backup(self):
        # The location of the file we want to make
        backup_demo_location = Path((str(self._settings['backup_path']) + '\\demos\\' + self.demo_name + '.txt'))

        self.print_backup(backup_demo_location, always_overwrite=True)

    def print_backup(self, backup_location, always_overwrite=False):
        if not always_overwrite and backup_location.is_file():
            write_method = 'a'
        else: 
            write_method = 'w'
            
        backup_file = open(backup_location, write_method)
        
        backup_file.write('>\n')
        for clip in self._clips:
            for event in clip._events:
                # Write the line to the backup
                backup_file.write(str(event) + '\n')

    @property
    def demo_name(self):
        return self._demo_name

    @property
    def latest(self):
        return self._clips[len(self._clips) - 1]