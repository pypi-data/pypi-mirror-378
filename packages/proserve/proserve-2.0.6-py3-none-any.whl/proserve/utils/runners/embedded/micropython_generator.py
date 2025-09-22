"""
ProServe MicroPython Code Generator
Generates MicroPython service code from manifests for embedded devices
"""

from typing import List
from ...core.manifest import ServiceManifest


class MicroPythonCodeGenerator:
    """Generates MicroPython service code from ProServe manifests"""
    
    def __init__(self, manifest: ServiceManifest, platform: str):
        self.manifest = manifest
        self.platform = platform
    
    async def generate_service_code(self) -> str:
        """Generate complete MicroPython service code from manifest"""
        lines = []
        
        # Add header
        lines.extend(self._generate_header())
        
        # Add imports
        lines.extend(self._generate_imports())
        
        # Add configuration
        lines.extend(self._generate_configuration())
        
        # Add main service loop
        lines.extend(self._generate_main_loop())
        
        # Add entry point
        lines.extend(self._generate_entry_point())
        
        return '\n'.join(lines)
    
    def _generate_header(self) -> List[str]:
        """Generate file header with metadata"""
        return [
            "# ProServe MicroPython Service",
            f"# Service: {self.manifest.name}",
            f"# Platform: {self.platform}",
            f"# Version: {getattr(self.manifest, 'version', '1.0.0')}",
            ""
        ]
    
    def _generate_imports(self) -> List[str]:
        """Generate required imports for MicroPython"""
        imports = [
            "import machine",
            "import time",
            "import gc"
        ]
        
        # Add platform-specific imports
        if self.platform in ['esp32', 'esp8266']:
            imports.extend([
                "import network",
                "import socket"
            ])
        
        # Add optional imports based on manifest features
        if hasattr(self.manifest, 'endpoints') and self.manifest.endpoints:
            imports.append("import json")
        
        imports.append("")
        return imports
    
    def _generate_configuration(self) -> List[str]:
        """Generate service configuration constants"""
        config_lines = [
            "# Service configuration",
            f"SERVICE_NAME = '{self.manifest.name}'",
            f"PLATFORM = '{self.platform}'"
        ]
        
        # Add port configuration if specified
        if hasattr(self.manifest, 'port') and self.manifest.port:
            config_lines.append(f"SERVICE_PORT = {self.manifest.port}")
        
        # Add environment variables
        if hasattr(self.manifest, 'env_vars') and self.manifest.env_vars:
            config_lines.append("# Environment variables")
            for env_var in self.manifest.env_vars:
                config_lines.append(f"{env_var.upper()} = None  # Set via deployment")
        
        config_lines.append("")
        return config_lines
    
    def _generate_main_loop(self) -> List[str]:
        """Generate main service loop"""
        loop_lines = [
            "def main():",
            "    print(f'Starting ProServe service: {SERVICE_NAME}')",
            "    print(f'Platform: {PLATFORM}')",
            "    ",
            "    # Service initialization",
            "    led = None",
            "    try:",
            "        led = machine.Pin('LED', machine.Pin.OUT)",
            "    except:",
            "        pass  # No LED available",
            "    "
        ]
        
        # Add network setup for WiFi-capable platforms
        if self.platform in ['esp32', 'esp8266']:
            loop_lines.extend([
                "    # Network initialization",
                "    wlan = network.WLAN(network.STA_IF)",
                "    wlan.active(True)",
                "    # Note: WiFi credentials should be set via deployment",
                "    "
            ])
        
        # Add main service loop
        loop_lines.extend([
            "    # Main service loop", 
            "    iteration = 0",
            "    while True:",
            "        try:",
            "            # Service heartbeat",
            "            if led:",
            "                led.toggle()",
            "            ",
            "            # Service logic",
            "            iteration += 1",
            "            print(f'{SERVICE_NAME}: Running iteration {iteration}...')",
            "            "
        ])
        
        # Add endpoint handling if defined
        if hasattr(self.manifest, 'endpoints') and self.manifest.endpoints:
            loop_lines.extend([
                "            # Handle any incoming requests",
                "            # TODO: Implement endpoint handling",
                "            "
            ])
        
        # Add background task simulation
        if hasattr(self.manifest, 'background_tasks') and self.manifest.background_tasks:
            loop_lines.extend([
                "            # Execute background tasks",
                "            if iteration % 10 == 0:  # Every 10 iterations",
                "                print('Executing background tasks...')",
                "            "
            ])
        
        # Complete the loop
        loop_lines.extend([
            "            # Garbage collection",
            "            gc.collect()",
            "            ",
            "            time.sleep(1)",
            "        except KeyboardInterrupt:",
            "            print('Service stopped by user')",
            "            break",
            "        except Exception as e:",
            "            print(f'Service error: {e}')",
            "            time.sleep(5)  # Wait before retry",
            "    ",
            "    # Cleanup",
            "    if led:",
            "        led.off()",
            "    print('Service shutdown complete')"
        ])
        
        return loop_lines
    
    def _generate_entry_point(self) -> List[str]:
        """Generate script entry point"""
        return [
            "",
            "if __name__ == '__main__':",
            "    main()"
        ]
    
    def generate_endpoint_handler(self, endpoint) -> List[str]:
        """Generate handler code for a specific endpoint"""
        handler_lines = [
            f"def handle_{endpoint.path.replace('/', '_').replace('-', '_')}():",
            "    # Handler implementation",
            f"    # Path: {endpoint.path}",
            f"    # Method: {getattr(endpoint, 'method', 'GET')}",
            "    return {'status': 'ok', 'message': 'Handler not implemented'}",
            ""
        ]
        return handler_lines
    
    def generate_background_task(self, task) -> List[str]:
        """Generate background task code"""
        task_name = getattr(task, 'name', 'background_task')
        task_lines = [
            f"def {task_name}():",
            "    # Background task implementation",
            f"    print('Executing {task_name}...')",
            "    # Task logic goes here",
            "    pass",
            ""
        ]
        return task_lines
