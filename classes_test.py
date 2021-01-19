import re
import json
from classes.event import Event
from classes.mod import Mod
from classes.clip import Clip
from classes.vdm import VDM

event_lines = """>
[2020/07/11/ 18:43] Player bookmark ("20190920_2153_koth_clearcut_b13_lem0n_blu" at 28438)
[2020/07/13/ 17:50] Kill Streak:4 ("20190920_2153_koth_clearcut_b13_lem0n_blu" at 28581)
>
[2020-01-08_14-23-31] Bookmark General ("20190925_2153_koth_clearcut_b13_lem0n_blu" at 47500)
>
[2020/07/13/ 17:50] Kill Streak:4 ("20200713_1745_pl_swiftwater_final1_RED_BOPIS" at 18581)
>
[2020/07/11/ 18:43] penis moncher ("20200711_1835_pl_swiftwater_final1_BOPIS_BLU" at 28438)
[2020/07/11/ 18:43] spec ("20200711_1835_pl_swiftwater_final1_BOPIS_BLU" at 35638)"""

line_regex = re.compile('\[(.*)\] (.*) \("(.*)" at (\d*)\)', re.IGNORECASE)

# Combines it into one string and searches it
event_marks = line_regex.findall(event_lines)

mod = Mod({
            "title": "Exec configBackup.cfg",
            "description": "execs configBackup.cfg when the clip ends",
            "code": "suffix '[v]' on 'bm' unless 'General' > -o '[v]' on 'bm' excludes 'General&spec'"
        })

vdm = None

ryukbot_settings = json.load(open('ryukbot_settings.json'))

for event in event_marks:
    new_event = Event(event) 
    new_event.apply_mod(mod)
    clip = Clip(ryukbot_settings, new_event)

    if not vdm:
        vdm = VDM(ryukbot_settings, clip)
    elif vdm.demo_name != new_event.demo_name:
        vdm.close(clip.demo_name)

        vdm = VDM(ryukbot_settings, clip)
    elif vdm.latest.can_include(ryukbot_settings['minimum_ticks_between_clips'], clip):
        vdm.latest.include(ryukbot_settings, clip)
    else: 
        vdm.append(clip)

vdm.close()