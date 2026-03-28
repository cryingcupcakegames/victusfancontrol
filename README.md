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

Take a look at my other projects, including games and apps:   
https://cryingcupcakegames.github.io/  
  
Support My Work:  
https://buymeacoffee.com/cryingcupcakegames  
  
#HpOwnUpToYourHallSensorDefects  
