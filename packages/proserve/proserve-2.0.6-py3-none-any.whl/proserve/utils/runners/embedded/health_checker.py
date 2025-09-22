"""
ProServe Embedded Device Health Checker
Handles platform-specific health checks for embedded devices
"""

import logging
from typing import Dict, Any
from .device_connection import MicroPythonIsolationManager, ArduinoIsolationManager


class EmbeddedHealthChecker:
    """Performs health checks on embedded devices"""
    
    def __init__(self, isolation_manager, logger=None):
        self.isolation_manager = isolation_manager
        self.logger = logger or logging.getLogger(__name__)
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform platform-specific health check"""
        if not self.isolation_manager:
            return {'healthy': False, 'error': 'No isolation manager'}
        
        try:
            # Determine platform and perform appropriate health check
            if isinstance(self.isolation_manager, MicroPythonIsolationManager):
                return await self._micropython_health_check()
            elif isinstance(self.isolation_manager, ArduinoIsolationManager):
                return await self._arduino_health_check()
            else:
                return {'healthy': False, 'error': 'Unknown platform'}
                
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    async def _micropython_health_check(self) -> Dict[str, Any]:
        """MicroPython-specific health check"""
        try:
            # Simple ping test
            test_code = "print('ProServe-Health-Check')"
            result = await self.isolation_manager.execute_script(test_code)
            
            if result.get('success', False):
                return {
                    'healthy': True,
                    'platform': 'micropython',
                    'response_time': result.get('execution_time', 0),
                    'test_output': result.get('output', '')
                }
            else:
                return {
                    'healthy': False,
                    'error': result.get('error', 'Health check failed'),
                    'platform': 'micropython'
                }
                
        except Exception as e:
            return {'healthy': False, 'error': str(e), 'platform': 'micropython'}
    
    async def _arduino_health_check(self) -> Dict[str, Any]:
        """Arduino-specific health check"""
        try:
            # For Arduino, we mainly check if we can compile code
            test_code = """
            void setup() { 
                Serial.begin(9600); 
            }
            void loop() { 
                Serial.println("ProServe-Health-Check"); 
                delay(1000); 
            }
            """
            
            result = await self.isolation_manager.execute_script(test_code)
            
            if result.get('success', False):
                compilation = result.get('compilation', {})
                return {
                    'healthy': True,
                    'platform': 'arduino',
                    'compilation_success': compilation.get('success', False),
                    'sketch_size': compilation.get('sketch_size', {}),
                    'compilation_time': compilation.get('time', 0)
                }
            else:
                return {
                    'healthy': False,
                    'error': result.get('error', 'Health check failed'),
                    'platform': 'arduino'
                }
                
        except Exception as e:
            return {'healthy': False, 'error': str(e), 'platform': 'arduino'}
    
    async def check_device_connection(self, connection) -> Dict[str, Any]:
        """Check basic device connection status"""
        if not connection:
            return {'connected': False, 'error': 'Device not connected'}
        
        return {
            'connected': True,
            'status': 'Device connection active'
        }
    
    async def comprehensive_health_check(self, connection, device_info) -> Dict[str, Any]:
        """Perform comprehensive health check including connection and platform tests"""
        health_status = {
            'timestamp': self._get_current_timestamp(),
            'overall_healthy': True,
            'checks': {}
        }
        
        # Check device connection
        connection_check = await self.check_device_connection(connection)
        health_status['checks']['connection'] = connection_check
        
        if not connection_check.get('connected', False):
            health_status['overall_healthy'] = False
            return health_status
        
        # Perform platform-specific health check
        platform_check = await self.perform_health_check()
        health_status['checks']['platform'] = platform_check
        
        if not platform_check.get('healthy', False):
            health_status['overall_healthy'] = False
        
        # Add device info to health status
        if device_info:
            health_status['device_info'] = device_info
        
        return health_status
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for health check"""
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
