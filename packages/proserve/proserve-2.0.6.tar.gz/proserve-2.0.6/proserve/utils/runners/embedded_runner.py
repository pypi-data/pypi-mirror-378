"""
ProServe Embedded Runner - Embedded Device Service Runner
Handles running services on embedded platforms like MicroPython and Arduino devices
"""

import asyncio
import time
from typing import Dict, Any, Optional

from .base_runner import ServiceRunner, HealthChecker
from .runner_config import EmbeddedRunnerConfig, RunnerConfig
from ...core.manifest import ServiceManifest

# Import modular embedded components
from .embedded import (
    DeviceConnectionManager,
    MicroPythonCodeGenerator,
    ArduinoCodeGenerator,
    EmbeddedHealthChecker,
    EmbeddedDeviceInfo
)


class EmbeddedRunner(ServiceRunner):
    """Runner for embedded platforms (MicroPython, Arduino)"""
    
    def __init__(self, manifest: ServiceManifest, config: Optional[RunnerConfig] = None):
        if config is None:
            config = EmbeddedRunnerConfig()
        elif not isinstance(config, EmbeddedRunnerConfig):
            # Convert generic config to EmbeddedRunnerConfig
            config = EmbeddedRunnerConfig(**config.to_dict())
        
        super().__init__(manifest, config)
        self.config: EmbeddedRunnerConfig = config
        
        # Initialize modular components
        self.connection_manager = DeviceConnectionManager(self.config, self.logger)
        self.health_checker = None  # Initialized after connection
        self.device_info_manager = None  # Initialized after connection
        self.deployed_code = None
        
    async def start(self) -> bool:
        """Start embedded service"""
        if self.is_running:
            self.logger.warning("Embedded service is already running")
            return True
        
        self.logger.info(f"Starting embedded service: {self.manifest.name}")
        
        try:
            # Connect to embedded device
            if not await self.connection_manager.connect_device():
                self.logger.error("Failed to connect to embedded device")
                return False
            
            # Initialize managers after successful connection
            isolation_manager = self.connection_manager.get_isolation_manager()
            self.health_checker = EmbeddedHealthChecker(isolation_manager, self.logger)
            self.device_info_manager = EmbeddedDeviceInfo(isolation_manager, self.config, self.logger)
            
            # Deploy service to device
            if not await self._deploy_service():
                self.logger.error("Failed to deploy service to device")
                return False
            
            self.is_running = True
            self.start_time = time.time()
            self.logger.info(f"Embedded service started successfully on {self.config.platform}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start embedded service: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop embedded service"""
        if not self.is_running:
            self.logger.info("Embedded service is not running")
            return True
        
        self.logger.info("Stopping embedded service...")
        
        try:
            # Disconnect from device
            await self.connection_manager.disconnect_device()
            
            self.is_running = False
            self.logger.info("Embedded service stopped successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop embedded service: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check embedded device health"""
        if not self.health_checker:
            return {'healthy': False, 'error': 'Health checker not initialized'}
        
        try:
            return await self.health_checker.comprehensive_health_check(
                self.connection_manager.connection,
                self.connection_manager.get_device_info()
            )
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get embedded service status"""
        status = super().get_status()
        
        # Add device connection status
        if self.connection_manager:
            connection_status = self.device_info_manager.get_basic_device_status(
                self.connection_manager.connection,
                self.connection_manager.get_device_info()
            ) if self.device_info_manager else {}
            
            status.update({
                'device_connected': self.connection_manager.is_connected(),
                'device_info': self.connection_manager.get_device_info(),
                'device_port': self.config.device_port,
                'baud_rate': self.config.baud_rate,
                'firmware_version': self.config.firmware_version,
                'deployed': self.deployed_code is not None,
                **connection_status
            })
        
        return status
    
    async def _deploy_service(self) -> bool:
        """Deploy service to embedded device"""
        try:
            # Generate code based on platform
            if self.config.platform in ['rp2040', 'esp32', 'esp8266']:
                generator = MicroPythonCodeGenerator()
                code = await generator.generate_service_code(self.manifest)
            else:
                generator = ArduinoCodeGenerator()
                code = await generator.generate_service_code(self.manifest)
            
            # Deploy code to device
            isolation_manager = self.connection_manager.get_isolation_manager()
            result = await isolation_manager.execute_script(code)
            
            if result.get('success', False):
                self.deployed_code = code
                self.logger.info("Service deployed successfully to device")
                return True
            else:
                self.logger.error(f"Service deployment failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Service deployment error: {e}")
            return False
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information"""
        if not self.device_info_manager:
            return {'error': 'Device info manager not initialized'}
        
        return await self.device_info_manager.get_comprehensive_device_info()
    
    async def get_memory_info(self) -> Dict[str, Any]:
        """Get device memory information"""
        if not self.device_info_manager:
            return {'error': 'Device info manager not initialized'}
        
        return await self.device_info_manager.get_memory_info()
    
    async def deploy_update(self, new_code: str) -> bool:
        """Deploy code update to device"""
        self.logger.info("Deploying code update to device...")
        
        try:
            isolation_manager = self.connection_manager.get_isolation_manager()
            result = await isolation_manager.execute_script(new_code)
            
            if result.get('success', False):
                self.deployed_code = new_code
                self.logger.info("Code update deployed successfully")
                return True
            else:
                self.logger.error(f"Code update failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Code update error: {e}")
            return False
    
    
