import re
import json
from classes.event import Event
from classes.mod import Mod
from classes.clip import Clip

event_lines = """>
[2020/07/11/ 18:43] Player bookmark ("20200711_1835_pl_swiftwater_final1_BOPIS_BLU" at 28438)
>
[2020-01-08_14-23-31] Bookmark General ("20190925_2153_koth_clearcut_b13_lem0n_blu" at 47500)
>
[2020/07/11/ 18:43] penis ("20200711_1835_pl_swiftwater_final1_BOPIS_BLU" at 28438)
>
[2020/07/11/ 18:43] spec ("20200711_1835_pl_swiftwater_final1_BOPIS_BLU" at 28638)
>
[2020/07/13/ 17:50] Kill Streak:4 ("20200713_1745_pl_swiftwater_final1_RED_BOPIS" at 18581)"""

line_regex = re.compile('\[(.*)\] (.*) \("(.*)" at (\d*)\)', re.IGNORECASE)

# Combines it into one string and searches it
event_marks = line_regex.findall(event_lines)

mod = Mod({
            "title": "Exec configBackup.cfg",
            "description": "execs configBackup.cfg when the clip ends",
            "code": "suffix '[v]' on 'bm' unless 'General' > -o '[v]' on 'bm' excludes 'General&spec'"
        })

clips = []

ryukbot_settings = json.load(open('ryukbot_settings.json'))

for event in event_marks:
    new_event = Event(event) 
    new_event.apply_mod(mod)
    clip = Clip(ryukbot_settings, new_event)

    if len(clips) == 0 or clips[len(clips)-1].demo_name != new_event.demo_name:
        clips.append(clip) 
    elif clips[len(clips)-1].can_include(ryukbot_settings['minimum_ticks_between_clips'], clip):
        clips[len(clips)-1].include(ryukbot_settings, clip)
    else: 
        clips.append(clip)