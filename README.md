# Linear_Desktop_Assistant
A simple break reminder widget based off Linear from the Evolution series.

Currently build for Windows. It could be compiled on other systems with some tweaks since it uses PyQt6, but some window options will need changing.

## Modification
After running the program, right click on the system tray icon (the English bulldog icon), then select Edit Config. This will create a local config file you can edit.

### Timings
Timing values let you change how long your work sprints and breaks are. Stand frequency tells you how often to raise your desk if you have a standing desk. If not, set it to 0 to disable it. Stand time is how long you should stand for at the back end of that work sprint.

### Dialogue
You can change the text prompts in this section. If you're feeling fancy, you can swap out the Linear images as well for your own art in the Images/ folder!

### Window Position
These are a little advanced, but essentially the app always starts on your primary monitor. If you'd like to move it, set an X, Y coordinate offset to the correct position.

For example, say you have two monitors that are 1080p, aka 1920x1080. If the tool appears on the left monitor but you want it on the right, set POSITION_ONE_OFFSET_X to 1920 to tell the program to scoot the window over there.
Conversely, if you want it moved to the left monitor, set that value to -1920.

You can change the active position offset or go back to the default in the system tray menu. The tool will remember your last saved one.

# Issues
Feel free to leave a ticket here or reach out to me if you have any issues or feature requests! This was a tool primarily made to help me avoid getting migraines from overwork, so some things may be tailored too much to me and need to be made generic.