#Victus Fan Control 1.0.3
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
    60: 39,
    70: 48,
    80: 59,
    90: 67,
    100: 100
}

# TIMING
POLLING_RATE = 2
FAN_START_DELAY = 5
FAN_STOP_COOLDOWN = 30
SPIN_DOWN_DELAY = 30
KEEP_ALIVE_INTERVAL = 110 #Keeps fan alive #Fans usually stop after 120 seconds
URGENT_TEMP = 90
# ==========================================

clr.AddReference(LHM_DLL_PATH)
from LibreHardwareMonitor import Hardware

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

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

# ==========================================
# FAN CONTROLLER
# ==========================================
class FanController:
    def __init__(self, name):
        self.name = name
        self.last_applied_speed = 0
        self.start_delay_timer = 0
        self.stop_cooldown_timer = 0
        self.step_down_timer = 0
        self.step_up_timer = 0

    def calculate_target_speed(self, current_temp, current_time):
        if current_temp == 0 or current_temp > 110:
            self.start_delay_timer = 0
            self.stop_cooldown_timer = 0
            self.step_down_timer = 0
            self.step_up_timer = 0
            return 100

        raw_target_speed = get_step_speed(current_temp)

        # STATE 1: FAN IS CURRENTLY OFF
        if self.last_applied_speed == 0:
            self.stop_cooldown_timer = 0
            self.step_down_timer = 0
            self.step_up_timer = 0
            
            if current_temp >= URGENT_TEMP:
                self.start_delay_timer = 0 
                return raw_target_speed
                
            elif current_temp >= FAN_START_TEMP:
                if self.start_delay_timer == 0:
                    self.start_delay_timer = current_time
                    
                if (current_time - self.start_delay_timer) >= FAN_START_DELAY:
                    return raw_target_speed
                else:
                    return 0
            else:
                self.start_delay_timer = 0
                return 0

        # STATE 2: FAN IS CURRENTLY ON
        else:
            self.start_delay_timer = 0
            
            if current_temp < FAN_STOP_TEMP:
                self.step_down_timer = 0
                self.step_up_timer = 0
                
                if self.stop_cooldown_timer == 0:
                    self.stop_cooldown_timer = current_time
                    
                if (current_time - self.stop_cooldown_timer) >= FAN_STOP_COOLDOWN:
                    return 0
                else:
                    return self.last_applied_speed
                    
            else:
                self.stop_cooldown_timer = 0
                
                if raw_target_speed < self.last_applied_speed:
                    self.step_up_timer = 0
                    if self.step_down_timer == 0:
                        self.step_down_timer = current_time
                        
                    if (current_time - self.step_down_timer) >= SPIN_DOWN_DELAY:
                        return raw_target_speed
                    else:
                        return self.last_applied_speed
                        
                elif raw_target_speed > self.last_applied_speed:
                    self.step_down_timer = 0
                    
                    if current_temp >= URGENT_TEMP:
                        self.step_up_timer = 0
                        return raw_target_speed
                    else:
                        if self.step_up_timer == 0:
                            self.step_up_timer = current_time
                            
                        if (current_time - self.step_up_timer) >= FAN_START_DELAY:
                            return raw_target_speed
                        else:
                            return self.last_applied_speed
                            
                else:
                    self.step_down_timer = 0
                    self.step_up_timer = 0
                    return raw_target_speed

if __name__ == "__main__":
    print("--- Victus Fan Control ---")

    if not is_admin():
        print("Script is not running as Administrator!")
        print("Exiting in 5 seconds...")
        time.sleep(5)
        sys.exit(1)

    print("Waiting 20 seconds for Windows services...")
    time.sleep(20)
    
    computer = Hardware.Computer()
    computer.IsCpuEnabled = True
    computer.Open()
    cpu_hw = next((hw for hw in computer.Hardware if hw.HardwareType == Hardware.HardwareType.Cpu), None)

    try:
        nvmlInit()
        gpu_handle = nvmlDeviceGetHandleByIndex(0)
    except:
        gpu_handle = None
    
    cpu_fan = FanController("CPU")
    gpu_fan = FanController("GPU")
    last_global_change_time = 0
    
    try:
        while True:
            current_time = time.monotonic()
            
            cpu_raw = 0
            if cpu_hw:
                cpu_hw.Update()
                temps = [s.Value for s in cpu_hw.Sensors if s.SensorType == Hardware.SensorType.Temperature and s.Value is not None]
                if temps:
                    cpu_raw = int(max(temps))
            
            gpu_raw = cpu_raw
            if gpu_handle:
                try:
                    gpu_raw = nvmlDeviceGetTemperature(gpu_handle, NVML_TEMPERATURE_GPU)
                except:
                    pass

            target_cpu_speed = cpu_fan.calculate_target_speed(cpu_raw, current_time)
            target_gpu_speed = gpu_fan.calculate_target_speed(gpu_raw, current_time)

            # =========================
            # EXECUTION + KEEP ALIVE
            # =========================
            time_since_last = current_time - last_global_change_time
            should_refresh = time_since_last >= KEEP_ALIVE_INTERVAL
            
            speed_changed = (target_cpu_speed != cpu_fan.last_applied_speed) or (target_gpu_speed != gpu_fan.last_applied_speed)

            if speed_changed or should_refresh:
                if (time_since_last >= 2):
                    apply_fan_speed(target_cpu_speed, target_gpu_speed)
                    
                    cpu_fan.last_applied_speed = target_cpu_speed
                    gpu_fan.last_applied_speed = target_gpu_speed
                    last_global_change_time = current_time

            if cpu_raw == 0 or cpu_raw > 110 or gpu_raw == 0 or gpu_raw > 110:
                print(f"WARNING: Sensor error detected! Failsafe engaged.        ", end='\r')
            else:
                print(f"CPU: {cpu_raw}°C ({cpu_fan.last_applied_speed}%) | GPU: {gpu_raw}°C ({gpu_fan.last_applied_speed}%)        ", end='\r')

            time.sleep(POLLING_RATE)

    finally:
        try:
            nvmlShutdown()
        except:
            pass