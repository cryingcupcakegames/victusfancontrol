I made this program because of the Hall effect sensor problem. I removed the ribbon cable from the Hall effect board, and after that, I noticed my fans were not working properly. I tried using Omen Gaming Hub's custom fan curve, but the app was also very problematic and unstable. It once used over 20GB of RAM with high CPU usage and kept crashing. Omenmon didn't work directly with my laptop too.

This has only been tested on a Victus Gaming Laptop 16-s0051nt (892P9EA)  
My system has an NVIDIA GPU and an AMD CPU. Because the code is made for this specific hardware, it may not work on other systems without modifications.  
  
Requirements:  
Python 3.13.0  
pip install pythonnet nvidia-ml-py  
https://github.com/OmenMon/OmenMon/releases  
https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases  
  
You should change OMENMON_PATH and LHM_DLL_PATH in the Python file. You can change the fan steps and other options there as well.
  
You can add it to startup using a batch file with code similar to this:  
cd "C:\Users\user\Documents\Programs\victusfancontrol"  
start "" pythonw omen_fan_control.py  

SpeedFan can be very useful for checking whether it is working, but it isn’t guaranteed to display accurate temperatures or fan RPM. It’s the best tool I’ve found for this laptop model:
https://www.almico.com/sfdownload.php

Take a look at my other projects, including games and apps:   
https://cryingcupcakegames.github.io/  
  
Support My Work:  
https://buymeacoffee.com/cryingcupcakegames  
  
  
#HpOwnUpToYourHallSensorDefects  
