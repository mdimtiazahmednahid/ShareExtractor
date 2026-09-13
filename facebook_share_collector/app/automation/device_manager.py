import subprocess
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class DeviceManager:
    @staticmethod
    def get_connected_devices() -> List[Dict[str, str]]:
        devices = []
        try:
            # We run adb devices -l
            result = subprocess.run(
                ['adb', 'devices', '-l'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # skip 'List of devices attached'
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    state = parts[1]
                    
                    # Parse extras like model, device, transport
                    extras = " ".join(parts[2:])
                    model = "Unknown"
                    if "model:" in extras:
                        model = extras.split("model:")[1].split()[0]
                    
                    devices.append({
                        "serial": serial,
                        "state": state,
                        "model": model,
                        "raw": line
                    })
        except FileNotFoundError:
            logger.error("ADB is not installed or not in PATH.")
        except subprocess.TimeoutExpired:
            logger.error("ADB command timed out.")
        except Exception as e:
            logger.error(f"Error getting adb devices: {e}")
            
        return devices

    @staticmethod
    def open_url(serial: str, url: str) -> bool:
        try:
            result = subprocess.run(
                ['adb', '-s', serial, 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', url],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Successfully opened URL on device {serial}")
                return True
            else:
                logger.error(f"Failed to open URL. ADB stderr: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error opening URL via ADB: {e}")
            return False

