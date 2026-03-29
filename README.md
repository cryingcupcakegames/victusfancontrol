<h2 align="center">
  <a href="https://cryingcupcakegames.github.io/"><img src="icon/victus_fan_control.png" width="36"/></a><span>&nbsp;</span><span>Victus Fan Control</span>
</h2>
I developed this because of the well-known hall effect sensor problem. After removing the ribbon cable from the hall effect board, I noticed my fans were not working properly. I tried using Omen Gaming Hub's custom fan curve, but the app was unstable and problematic. It sometimes used all of the RAM, likely due to a memory leak, and had high CPU usage with frequent crashes. Omenmon also didn't work directly with my laptop.
<br><br>
This has only been tested on a Victus Gaming Laptop 16-s0051nt (892P9EA)  
My system has an NVIDIA GPU and an AMD CPU. Because the code is made for this specific hardware, it may not work on other systems without modifications.  
Optimized for silent browsing and smooth gaming performance with minimal OmenMon calls. My laptop’s fans don’t work below 18% speed. If you experience issues, adjust the fan curve.  
<br><br>
Requirements:  
Python 3.13.0: https://www.python.org/downloads/release/python-3130/  
pip install pythonnet nvidia-ml-py  
https://github.com/OmenMon/OmenMon/releases  
(Replace OmenMon.xml file with my version)  
https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases  
<br><br>
You should change OMENMON_PATH and LHM_DLL_PATH in the Python file. You can change the fan steps and other options there as well.
You should start it with pythonw. Otherwise, it will give errors when creating silent subprocesses.
<br>
You can add it to startup using a batch file with code similar to this:  
cd "C:\Users\user\Documents\Programs\victusfancontrol"  
start "" pythonw omen_fan_control.py  
<br><br>
SpeedFan can be very useful for checking whether it is working, but it isn’t guaranteed to display accurate temperatures or fan RPM. It’s the best tool I’ve found for this laptop model:
https://www.almico.com/sfdownload.php
<br><br>
Take a look at my other projects, including games and apps:   
https://cryingcupcakegames.github.io/  
<br>
Support My Work:  
https://buymeacoffee.com/cryingcupcakegames  
<br><br>
This repository is provided on an "as-is" basis without any warranties, either expressed or implied. By using the content within, you acknowledge and agree that you are doing so entirely at your own risk.  
<br><br>
#HpOwnUpToYourHallSensorDefects  
