# ultrasound_automation

**Keys->**<br> 1)**s** -> region of intrest selector<br> 2)**n**-> next frame (first pause then use)<br> 3)**p**-> prev frame (first pause then use)<br> 4)**q**-> quit <br> 5)**c**-> cancel selector<br> 6)**enter or space** -> play video after selection<br> 7)**x**-> pause video<br> 8)**i**->increament video play back speed by 1 sec<br> 9)**d**->decreament video play back speed by 1 sec<br>

**Command to Run app ->** <br>

> python object_tracker.py --video [path/to/video] --tracker [tracker type example:csrt] --slow [time in sec to slow down video]<br>

**Example Command ->**<br>

> python object_tracker.py --video us_bp.mp4 --tracker csrt --slow 1
