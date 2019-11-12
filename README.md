# ultrasound_automation

keys-><br>
1)s -> region of intrest selector<br>
2)n-> next frame (first pause then use)<br>
3)p-> prev frame (first pause then use)<br>
4)q-> quit <br>
5)c-> cancel selector<br>
6)enter or space -> play video after selection<br>

command python object_tracker.py --video [path/to/video] --tracker [tracker type example:csrt] --slow [time in sec to slow down video]<br>

example command: python object_tracker.py --video us_bp.mp4 --tracker csrt --slow 1
