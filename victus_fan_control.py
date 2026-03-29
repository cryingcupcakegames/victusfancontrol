#Victus Fan Control 1.0.2
#Copyright (C) 2026 Crying Cupcake Games
import subprocess
import time
import clr 
from pynvml import *
import ctypes
import sys

# ==========================================
# CONFIGURATION
# ==========================================
OMENMON_PATH = r"C:\Users\user\Documents\Programs\victusfancontrol\OmenMon-0.61.1-Release\OmenMon.exe"
LHM_DLL_PATH = r"C:\Users\user\Documents\Programs\victusfancontrol\LibreHardwareMonitor-0.9.6\LibreHardwareMonitorLib.dll"

# FAN BEHAVIOR
FAN_START_TEMP = 50
FAN_STOP_TEMP  = 40

#default omen gaming hub values
#50 31
#55 38
#60 40
#65 43
#70 48
#75 55
#80 59
#85 64
#90 67

FAN_STEPS = {
    40: 18,
    60: 40,
    70: 50,
    80: 60,
    90: 70,
    100: 100
}

# TIMING
POLLING_RATE = 2
FAN_START_DELAY = 5
FAN_STOP_COOLDOWN = 30
SPIN_DOWN_DELAY = 15
KEEP_ALIVE_INTERVAL = 90 # Keeps fan alive
URGENT_TEMP = 90
# ==========================================

clr.AddReference(LHM_DLL_PATH)
from LibreHardwareMonitor import Hardware

computer = Hardware.Computer()
computer.IsCpuEnabled = True
computer.Open()

cpu_hw = next((hw for hw in computer.Hardware if hw.HardwareType == Hardware.HardwareType.Cpu), None)

try:
    nvmlInit()
    gpu_handle = nvmlDeviceGetHandleByIndex(0)
except:
    gpu_handle = None

def apply_fan_speed(cpu_val, gpu_val):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= (0x00000001 | 0x00000080)
    si.wShowWindow = 0 

    s_flags = subprocess.CREATE_NO_WINDOW | 0x00000008 | 0x00000400

    try:
        subprocess.run(
            [OMENMON_PATH, "-Bios", "FanCount", f"FanLevel={cpu_val},{gpu_val}"],
            startupinfo=si,
            creationflags=s_flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
    except:
        pass

def get_step_speed(temp):
    for threshold in sorted(FAN_STEPS.keys(), reverse=True):
        if temp >= threshold:
            return FAN_STEPS[threshold]
    if temp >= FAN_STOP_TEMP:
        return FAN_STEPS[min(FAN_STEPS.keys())]
    return 0

last_applied_speed = 0
last_change_time = 0

start_delay_timer = 0
stop_cooldown_timer = 0
step_down_timer = 0
step_up_timer = 0

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

if __name__ == "__main__":
    print("--- Victus Fan Control ---")

    if not is_admin():
        print("CRITICAL WARNING: Script is not running as Administrator!")
        print("Please restart the script with elevated privileges.")
        print("Exiting in 5 seconds...")
        time.sleep(5)
        sys.exit(1)

    print("Waiting 20 seconds for Windows services...")
    time.sleep(20)
    
    try:
        while True:
            current_time = time.time()
            
            # Read CPU
            cpu_raw = 0
            if cpu_hw:
                cpu_hw.Update()
                temps = [s.Value for s in cpu_hw.Sensors if s.SensorType == Hardware.SensorType.Temperature and s.Value is not None]
                if temps:
                    cpu_raw = int(max(temps))
            
            # Read GPU
            gpu_raw = cpu_raw
            if gpu_handle:
                try:
                    gpu_raw = nvmlDeviceGetTemperature(gpu_handle, NVML_TEMPERATURE_GPU)
                except:
                    pass

            current_max = max(cpu_raw, gpu_raw)

            # Failsafe
            if current_max == 0 or current_max > 110:
                target_speed = 100
                start_delay_timer = 0
                stop_cooldown_timer = 0
                step_down_timer = 0
                step_up_timer = 0
                print(f"WARNING: Sensor error ({current_max}°C)        ", end='\r')
            else:
                raw_target_speed = get_step_speed(current_max)

                # ==========================================
                # STATE 1: FANS ARE CURRENTLY OFF
                # ==========================================
                if last_applied_speed == 0:
                    stop_cooldown_timer = 0
                    step_down_timer = 0
                    step_up_timer = 0
                    
                    if current_max >= URGENT_TEMP:
                        target_speed = raw_target_speed
                        start_delay_timer = 0 
                        
                    elif current_max >= FAN_START_TEMP:
                        if start_delay_timer == 0:
                            start_delay_timer = current_time
                            
                        if (current_time - start_delay_timer) >= FAN_START_DELAY:
                            target_speed = raw_target_speed
                        else:
                            target_speed = 0 
                    else:
                        start_delay_timer = 0
                        target_speed = 0

                # ==========================================
                # STATE 2: FANS ARE CURRENTLY ON
                # ==========================================
                else:
                    start_delay_timer = 0
                    
                    if current_max <= FAN_STOP_TEMP:
                        step_down_timer = 0
                        step_up_timer = 0
                        
                        if stop_cooldown_timer == 0:
                            stop_cooldown_timer = current_time
                            
                        if (current_time - stop_cooldown_timer) >= FAN_STOP_COOLDOWN:
                            target_speed = 0
                        else:
                            target_speed = last_applied_speed
                            
                    else:
                        stop_cooldown_timer = 0
                        
                        if raw_target_speed < last_applied_speed:
                            step_up_timer = 0
                            if step_down_timer == 0:
                                step_down_timer = current_time
                                
                            if (current_time - step_down_timer) >= SPIN_DOWN_DELAY:
                                target_speed = raw_target_speed
                            else:
                                target_speed = last_applied_speed
                                
                        elif raw_target_speed > last_applied_speed:
                            step_down_timer = 0
                            
                            if current_max >= URGENT_TEMP:
                                target_speed = raw_target_speed
                                step_up_timer = 0
                            else:
                                if step_up_timer == 0:
                                    step_up_timer = current_time
                                    
                                if (current_time - step_up_timer) >= FAN_START_DELAY:
                                    target_speed = raw_target_speed
                                else:
                                    target_speed = last_applied_speed
                                    
                        else:
                            step_down_timer = 0
                            step_up_timer = 0
                            target_speed = raw_target_speed

            # =========================
            # EXECUTION + KEEP ALIVE
            # =========================
            time_since_last = current_time - last_change_time
            should_refresh = time_since_last >= KEEP_ALIVE_INTERVAL

            if target_speed != last_applied_speed or should_refresh:
                if (time_since_last >= 2):
                    apply_fan_speed(target_speed, target_speed)
                    last_applied_speed = target_speed
                    last_change_time = current_time

            if 0 < current_max <= 110:
                print(f"CPU: {cpu_raw}°C | GPU: {gpu_raw}°C | Fan: {last_applied_speed}%        ", end='\r')

            time.sleep(POLLING_RATE)

    finally:
        try:
            nvmlShutdown()
        except:
            pass