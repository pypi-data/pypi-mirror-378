"""
ProServe Embedded Device Connection Manager
Handles device discovery, connection, and isolation manager setup
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Import isolation functionality from Servos package
try:
    from servos.core.isolation import ProcessIsolationManager as IsolationManager
    from servos.isolation.platforms.device_detection import DeviceDetector, DetectedDevice
    # Create aliases for backward compatibility
    MicroPythonIsolationManager = IsolationManager
    ArduinoIsolationManager = IsolationManager
    
    def detect_connected_devices():
        """Wrapper for device detection"""
        detector = DeviceDetector()
        return detector.scan_devices()
    
    def auto_select_isolation_manager(platform=None):
        """Auto-select appropriate isolation manager"""
        return IsolationManager
        
except ImportError:
    # Fallback if Servos not available
    class MockIsolationManager:
        def __init__(self, *args, **kwargs):
            self.platform = kwargs.get('platform', 'unknown')
            
        async def execute_script(self, code):
            return {'error': 'Servos package required for isolation'}
    
    MicroPythonIsolationManager = MockIsolationManager
    ArduinoIsolationManager = MockIsolationManager
    
    def detect_connected_devices():
        return []
    
    def auto_select_isolation_manager(platform=None):
        return MockIsolationManager


class DeviceConnectionManager:
    """Manages embedded device connections and isolation managers"""
    
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.device_info = None
        self.connection = None
        self.isolation_manager = None
    
    async def connect_device(self) -> bool:
        """Connect to embedded device"""
        self.logger.info(f"Connecting to {self.config.platform} device...")
        
        try:
            # Auto-detect device if not specified
            if self.config.auto_detect_device and not self.config.device_port:
                devices = detect_connected_devices()
                matching_devices = [d for d in devices if d.platform == self.config.platform]
                
                if matching_devices:
                    device = matching_devices[0]
                    self.config.device_port = device.port
                    self.device_info = device.to_dict()
                    self.logger.info(f"Auto-detected device: {device.description} on {device.port}")
                else:
                    self.logger.warning("No matching devices found, using emulation mode")
                    return await self.setup_emulation_mode()
            
            # Create appropriate isolation manager
            if self.config.platform in ['rp2040', 'esp32', 'esp8266', 'pyboard']:
                self.isolation_manager = MicroPythonIsolationManager(
                    platform=self.config.platform,
                    device_port=self.config.device_port,
                    baud_rate=self.config.baud_rate,
                    timeout=self.config.timeout,
                    auto_detect_device=False  # Already detected
                )
            elif self.config.platform in ['uno_r4_wifi', 'esp32dev', 'nano33iot', 'leonardo']:
                self.isolation_manager = ArduinoIsolationManager(
                    platform=self.config.platform,
                    upload_port=self.config.device_port,
                    compile_only=False
                )
            else:
                raise ValueError(f"Unsupported platform: {self.config.platform}")
            
            # Setup isolation environment
            await self.isolation_manager.setup_environment()
            
            self.connection = True  # Simplified connection tracking
            return True
            
        except Exception as e:
            self.logger.error(f"Device connection failed: {e}")
            return False
    
    async def setup_emulation_mode(self) -> bool:
        """Setup emulation mode when no physical device is available"""
        self.logger.info("Setting up emulation mode...")
        
        try:
            # Use MicroPython emulation by default
            self.isolation_manager = MicroPythonIsolationManager(
                platform=self.config.platform or 'rp2040',
                use_emulator=True
            )
            
            await self.isolation_manager.setup_environment()
            
            self.connection = True
            self.device_info = {
                'mode': 'emulation',
                'platform': self.config.platform,
                'emulated': True
            }
            
            self.logger.info("Emulation mode setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Emulation setup failed: {e}")
            return False
    
    async def disconnect_device(self) -> bool:
        """Disconnect from embedded device"""
        self.logger.info("Disconnecting from device...")
        
        try:
            if self.isolation_manager:
                await self.isolation_manager.cleanup_environment()
                
            self.connection = None
            self.isolation_manager = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Device disconnection error: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self.connection is not None
    
    def get_isolation_manager(self):
        """Get the current isolation manager"""
        return self.isolation_manager
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        return self.device_info or {}
