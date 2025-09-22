"""
ProServe Embedded Device Information Retriever
Handles device information collection from embedded platforms
"""

import logging
from typing import Dict, Any
from .device_connection import MicroPythonIsolationManager, ArduinoIsolationManager


class EmbeddedDeviceInfo:
    """Collects and manages device information for embedded platforms"""
    
    def __init__(self, isolation_manager, config, logger=None):
        self.isolation_manager = isolation_manager
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
    
    async def get_comprehensive_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information"""
        if not self.isolation_manager:
            return {'error': 'No device connected'}
        
        try:
            # Get platform-specific device info
            if isinstance(self.isolation_manager, MicroPythonIsolationManager):
                return await self._get_micropython_device_info()
            elif isinstance(self.isolation_manager, ArduinoIsolationManager):
                return await self._get_arduino_device_info()
            else:
                return {'error': 'Unknown isolation manager type'}
                
        except Exception as e:
            self.logger.error(f"Failed to get device info: {e}")
            return {'error': str(e)}
    
    async def _get_micropython_device_info(self) -> Dict[str, Any]:
        """Get MicroPython device information"""
        info_code = """
import sys
import gc
try:
    import machine
    machine_available = True
except ImportError:
    machine_available = False

try:
    result = {
        'platform': sys.platform,
        'version': sys.version,
        'implementation': sys.implementation[0] if hasattr(sys, 'implementation') else 'unknown',
        'memory_free': gc.mem_free(),
        'memory_alloc': gc.mem_alloc(),
        'machine_available': machine_available
    }
    
    if machine_available:
        try:
            result['unique_id'] = str(machine.unique_id())
        except:
            result['unique_id'] = 'unavailable'
        
        try:
            result['freq'] = machine.freq()
        except:
            result['freq'] = 'unavailable'
    
    print('DEVICE_INFO_START')
    for key, value in result.items():
        print(f'{key}: {value}')
    print('DEVICE_INFO_END')
    
except Exception as e:
    print(f'DEVICE_INFO_ERROR: {str(e)}')
"""
        
        try:
            result = await self.isolation_manager.execute_script(info_code)
            
            if result.get('success', False):
                # Parse device info from output
                device_info = self._parse_micropython_output(result.get('output', ''))
                
                # Add configuration info
                device_info.update({
                    'platform_config': self.config.platform,
                    'device_port': self.config.device_port,
                    'baud_rate': self.config.baud_rate,
                    'connection_type': 'micropython'
                })
                
                return device_info
            else:
                return {
                    'error': result.get('error', 'Failed to retrieve device info'),
                    'platform_config': self.config.platform,
                    'connection_type': 'micropython'
                }
                
        except Exception as e:
            return {'error': str(e), 'connection_type': 'micropython'}
    
    async def _get_arduino_device_info(self) -> Dict[str, Any]:
        """Get Arduino device information"""
        # Arduino device info is mainly from compilation and configuration
        device_info = {
            'platform': self.config.platform,
            'board_fqbn': getattr(self.isolation_manager, 'board_fqbn', 'unknown'),
            'compilation_tools': 'arduino-cli',
            'connection_type': 'arduino',
            'upload_port': self.config.device_port
        }
        
        # Try to get compilation info if available
        try:
            # Simple compilation test to get board info
            test_sketch = """
void setup() {
    Serial.begin(9600);
    Serial.println("Arduino Device Info");
    #ifdef ARDUINO_AVR_UNO
    Serial.println("Board: Arduino Uno");
    #endif
    #ifdef ARDUINO_ESP32_DEV
    Serial.println("Board: ESP32 Dev Module");
    #endif
    #ifdef ARDUINO_SAMD_NANO_33_IOT
    Serial.println("Board: Arduino Nano 33 IoT");
    #endif
}

void loop() {
    delay(1000);
}
"""
            
            result = await self.isolation_manager.execute_script(test_sketch)
            
            if result.get('success', False):
                compilation = result.get('compilation', {})
                device_info.update({
                    'compilation_success': True,
                    'sketch_size': compilation.get('sketch_size', {}),
                    'compiler_version': compilation.get('compiler_version', 'unknown')
                })
            else:
                device_info.update({
                    'compilation_success': False,
                    'compilation_error': result.get('error', 'Unknown error')
                })
                
        except Exception as e:
            device_info['compilation_error'] = str(e)
        
        return device_info
    
    def _parse_micropython_output(self, output: str) -> Dict[str, Any]:
        """Parse MicroPython device info from script output"""
        device_info = {}
        
        lines = output.split('\n')
        in_device_info = False
        
        for line in lines:
            line = line.strip()
            
            if line == 'DEVICE_INFO_START':
                in_device_info = True
                continue
            elif line == 'DEVICE_INFO_END':
                in_device_info = False
                continue
            elif line.startswith('DEVICE_INFO_ERROR:'):
                device_info['error'] = line.replace('DEVICE_INFO_ERROR:', '').strip()
                break
            
            if in_device_info and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to convert numeric values
                if value.isdigit():
                    value = int(value)
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                
                device_info[key] = value
        
        return device_info
    
    def get_basic_device_status(self, connection, device_info) -> Dict[str, Any]:
        """Get basic device status information"""
        status = {
            'connected': connection is not None,
            'platform': self.config.platform,
            'device_port': self.config.device_port,
            'baud_rate': self.config.baud_rate
        }
        
        if device_info:
            status.update({
                'device_mode': device_info.get('mode', 'physical'),
                'emulated': device_info.get('emulated', False)
            })
        
        return status
    
    async def get_memory_info(self) -> Dict[str, Any]:
        """Get device memory information (MicroPython specific)"""
        if not isinstance(self.isolation_manager, MicroPythonIsolationManager):
            return {'error': 'Memory info only available for MicroPython devices'}
        
        memory_code = """
import gc
try:
    gc.collect()  # Force garbage collection
    result = {
        'free': gc.mem_free(),
        'allocated': gc.mem_alloc(),
    }
    try:
        total = result['free'] + result['allocated']
        result['total'] = total
        result['usage_percent'] = round((result['allocated'] / total) * 100, 2)
    except:
        pass
    
    print('MEMORY_INFO_START')
    for key, value in result.items():
        print(f'{key}: {value}')
    print('MEMORY_INFO_END')
    
except Exception as e:
    print(f'MEMORY_INFO_ERROR: {str(e)}')
"""
        
        try:
            result = await self.isolation_manager.execute_script(memory_code)
            
            if result.get('success', False):
                return self._parse_micropython_output(result.get('output', ''))
            else:
                return {'error': result.get('error', 'Failed to get memory info')}
                
        except Exception as e:
            return {'error': str(e)}
