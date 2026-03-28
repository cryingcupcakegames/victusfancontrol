import subprocess
import time
import clr 
from pynvml import *

# ==========================================
# CONFIGURATION
# ==========================================
OMENMON_PATH = r"C:\Users\user\Documents\Programs\victusfancontrol\OmenMon-0.58.0-Release\OmenMon.exe"
LHM_DLL_PATH = r"C:\Users\user\Documents\Programs\victusfancontrol\LibreHardwareMonitor\LibreHardwareMonitorLib.dll"

# FAN BEHAVIOR
FAN_START_TEMP = 40
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
POLLING_RATE = 3
COOLDOWN_SECONDS = 10
SPIN_DOWN_DELAY = 15
KEEP_ALIVE_INTERVAL = 90  # keeps fan alive

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
    return 0

last_applied_speed = -1
last_change_time = 0
drop_start_time = 0 

if __name__ == "__main__":
    print("--- OMEN Manual Step Controller (Final Stable) ---")
    print("Waiting 20 seconds for Windows services...")
    time.sleep(20)
    
    try:
        while True:
            current_time = time.time()
            
            # =========================
            # READ CPU TEMP
            # =========================
            cpu_raw = 0
            if cpu_hw:
                cpu_hw.Update()
                temps = [s.Value for s in cpu_hw.Sensors if s.SensorType == Hardware.SensorType.Temperature]
                if temps:
                    cpu_raw = int(max(temps))
            
            # =========================
            # READ GPU TEMP (fallback = CPU)
            # =========================
            gpu_raw = cpu_raw
            if gpu_handle:
                try:
                    gpu_raw = nvmlDeviceGetTemperature(gpu_handle, NVML_TEMPERATURE_GPU)
                except:
                    pass

            current_max = max(cpu_raw, gpu_raw)

            # =========================
            # FAILSAFE
            # =========================
            if current_max == 0 or current_max > 110:
                target_speed = 100
                drop_start_time = 0
                print(f"WARNING: Sensor error ({current_max}°C)", end='\r')

            else:
                target_speed = get_step_speed(current_max)

                # =========================
                # HYSTERESIS
                # =========================
                if last_applied_speed == 0:
                    if current_max < FAN_START_TEMP:
                        target_speed = 0
                else:
                    if current_max <= FAN_STOP_TEMP:
                        target_speed = 0

                # =========================
                # SPIN DOWN DELAY
                # =========================
                if target_speed < last_applied_speed and last_applied_speed != -1:
                    if drop_start_time == 0:
                        drop_start_time = current_time
                    if (current_time - drop_start_time) < SPIN_DOWN_DELAY:
                        target_speed = last_applied_speed
                else:
                    drop_start_time = 0

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

            # =========================
            # OUTPUT
            # =========================
            if 0 < current_max <= 110:
                print(f"CPU: {cpu_raw}°C | GPU: {gpu_raw}°C | Fan: {last_applied_speed}%   ", end='\r')

            time.sleep(POLLING_RATE)

    finally:
        try:
            nvmlShutdown()
        except:
            pass