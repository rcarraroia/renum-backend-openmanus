"""
Process Manager for OpenManus communication.

This module provides robust, continuous communication with the OpenManus subprocess
via stdio, maintaining the pipe open and implementing asynchronous reading.
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessManager:
    """
    Manages communication with the OpenManus subprocess.
    
    This class provides robust, continuous communication with the OpenManus
    subprocess via stdio, maintaining the pipe open and implementing
    asynchronous reading of responses.
    """
    
    def __init__(
        self,
        executable_path: str,
        script_path: str,
        working_dir: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        startup_timeout: float = 10.0,
        response_timeout: float = 30.0
    ):
        """
        Initialize the ProcessManager.
        
        Args:
            executable_path: Path to the Python executable
            script_path: Path to the OpenManus script
            working_dir: Working directory for the subprocess
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retry attempts in seconds
            startup_timeout: Timeout for subprocess startup in seconds
            response_timeout: Timeout for response reading in seconds
        """
        self.executable_path = executable_path
        self.script_path = script_path
        self.working_dir = working_dir or os.getcwd()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.startup_timeout = startup_timeout
        self.response_timeout = response_timeout
        
        # Process state
        self.process: Optional[asyncio.subprocess.Process] = None
        self.is_initialized = False
        self.is_running = False
        
        # Communication state
        self.response_buffer = ""
        self.last_activity = 0
        
        logger.info(f"ProcessManager initialized with executable: {executable_path}, script: {script_path}")
    
    async def initialize(self) -> bool:
        """
        Initialize the OpenManus subprocess.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if self.is_initialized:
            logger.warning("ProcessManager already initialized")
            return True
        
        try:
            logger.info("Starting OpenManus subprocess...")
            
            # Start the subprocess with pipes for stdin, stdout, stderr
            self.process = await asyncio.create_subprocess_exec(
                self.executable_path,
                self.script_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir
            )
            
            # Start monitoring stderr in the background
            asyncio.create_task(self._monitor_stderr())
            
            # Wait for startup to complete
            startup_success = await self._wait_for_startup()
            
            if startup_success:
                self.is_initialized = True
                self.is_running = True
                self.last_activity = time.time()
                logger.info("OpenManus subprocess initialized successfully")
                return True
            else:
                logger.error("Failed to initialize OpenManus subprocess")
                await self._cleanup()
                return False
            
        except Exception as e:
            logger.error(f"Error initializing OpenManus subprocess: {e}")
            await self._cleanup()
            return False
    
    async def _wait_for_startup(self) -> bool:
        """
        Wait for the subprocess to complete startup.
        
        Returns:
            True if startup completed successfully, False otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < self.startup_timeout:
            if self.process is None or self.process.returncode is not None:
                logger.error("Process terminated during startup")
                return False
            
            # Check if process is still alive
            try:
                # Send a null byte to check if the process is responsive
                if self.process.stdin:
                    self.process.stdin.write(b"\n")
                    await self.process.stdin.drain()
                    
                # Wait a bit before checking again
                await asyncio.sleep(0.5)
                
                # If we get here without exception, the process is running
                return True
                
            except (BrokenPipeError, ConnectionResetError):
                logger.error("Pipe broken during startup")
                return False
            
            except Exception as e:
                logger.warning(f"Error during startup check: {e}")
                await asyncio.sleep(0.5)
        
        logger.error(f"Startup timeout after {self.startup_timeout} seconds")
        return False
    
    async def _monitor_stderr(self) -> None:
        """
        Monitor the stderr of the subprocess and log any output.
        """
        if not self.process or not self.process.stderr:
            return
        
        while True:
            try:
                line = await self.process.stderr.readline()
                if not line:
                    break
                
                stderr_line = line.decode("utf-8", errors="replace").strip()
                if stderr_line:
                    logger.warning(f"OpenManus stderr: {stderr_line}")
                    
            except Exception as e:
                logger.error(f"Error monitoring stderr: {e}")
                break
    
    async def send_prompt_and_get_response(self, prompt: str) -> Dict[str, Any]:
        """
        Send a prompt to the OpenManus subprocess and get the response.
        
        This method maintains the pipe open for continuous communication.
        
        Args:
            prompt: The prompt to send to OpenManus
            
        Returns:
            The parsed JSON response from OpenManus
        """
        if not self.is_initialized or not self.is_running:
            logger.error("ProcessManager not initialized or not running")
            await self.initialize()
            if not self.is_initialized or not self.is_running:
                return {"error": "Failed to initialize ProcessManager"}
        
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                # Prepare the prompt as JSON
                prompt_json = json.dumps({"prompt": prompt}) + "\n"
                prompt_bytes = prompt_json.encode("utf-8")
                
                # Send the prompt to the subprocess
                if self.process and self.process.stdin:
                    logger.info(f"Sending prompt to OpenManus: {prompt[:50]}...")
                    self.process.stdin.write(prompt_bytes)
                    await self.process.stdin.drain()
                    self.last_activity = time.time()
                else:
                    logger.error("Process stdin not available")
                    await self._restart_process()
                    retry_count += 1
                    continue
                
                # Read the response asynchronously
                response_json = await self._read_response()
                
                # Parse the response
                if response_json:
                    try:
                        response = json.loads(response_json)
                        logger.info(f"Received response from OpenManus: {str(response)[:100]}...")
                        return response
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse response as JSON: {e}")
                        logger.debug(f"Raw response: {response_json}")
                        return {"error": "Failed to parse response", "raw_response": response_json}
                else:
                    logger.error("Empty response from OpenManus")
                    return {"error": "Empty response from OpenManus"}
                
            except (BrokenPipeError, ConnectionResetError) as e:
                logger.error(f"Pipe error during communication: {e}")
                await self._restart_process()
                retry_count += 1
                
            except asyncio.TimeoutError:
                logger.error(f"Timeout waiting for response after {self.response_timeout} seconds")
                await self._restart_process()
                retry_count += 1
                
            except Exception as e:
                logger.error(f"Error during communication: {e}")
                await self._restart_process()
                retry_count += 1
        
        logger.error(f"Failed to get response after {self.max_retries} retries")
        return {"error": f"Failed to get response after {self.max_retries} retries"}
    
    async def _read_response(self) -> str:
        """
        Read the response from the subprocess asynchronously.
        
        Returns:
            The complete response as a string
        """
        if not self.process or not self.process.stdout:
            return ""
        
        response_parts = []
        start_time = time.time()
        
        while time.time() - start_time < self.response_timeout:
            try:
                # Read a chunk of data
                chunk = await asyncio.wait_for(
                    self.process.stdout.readline(),
                    timeout=1.0
                )
                
                if not chunk:  # EOF
                    if response_parts:
                        break
                    else:
                        await asyncio.sleep(0.1)
                        continue
                
                # Decode the chunk
                chunk_str = chunk.decode("utf-8", errors="replace")
                self.last_activity = time.time()
                
                # Check if it's a complete JSON object
                try:
                    # Try to parse as JSON to check completeness
                    json.loads(chunk_str)
                    return chunk_str.strip()
                except json.JSONDecodeError:
                    # Incomplete JSON, continue reading
                    response_parts.append(chunk_str)
                    
                    # Check if we have a complete JSON by combining parts
                    combined = "".join(response_parts)
                    try:
                        json.loads(combined)
                        return combined.strip()
                    except json.JSONDecodeError:
                        # Still incomplete, continue reading
                        pass
                
            except asyncio.TimeoutError:
                # No data received in the timeout period
                if response_parts:
                    # We have partial data, try to combine and return
                    combined = "".join(response_parts)
                    try:
                        json.loads(combined)
                        return combined.strip()
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue waiting
                        pass
                
                # Check if process is still alive
                if self.process.returncode is not None:
                    logger.error("Process terminated while reading response")
                    break
            
            except Exception as e:
                logger.error(f"Error reading response: {e}")
                break
        
        # If we get here, we either timed out or encountered an error
        if response_parts:
            return "".join(response_parts).strip()
        else:
            return ""
    
    async def _restart_process(self) -> bool:
        """
        Restart the OpenManus subprocess after a failure.
        
        Returns:
            True if restart was successful, False otherwise
        """
        logger.info("Restarting OpenManus subprocess...")
        
        await self._cleanup()
        
        # Wait before restarting
        await asyncio.sleep(self.retry_delay)
        
        # Initialize again
        return await self.initialize()
    
    async def _cleanup(self) -> None:
        """
        Clean up resources associated with the subprocess.
        """
        self.is_running = False
        self.is_initialized = False
        
        if self.process:
            try:
                # Try to terminate gracefully first
                if self.process.returncode is None:
                    logger.info("Terminating OpenManus subprocess...")
                    self.process.terminate()
                    
                    # Wait for process to terminate
                    try:
                        await asyncio.wait_for(self.process.wait(), timeout=3.0)
                    except asyncio.TimeoutError:
                        # Force kill if termination takes too long
                        logger.warning("Termination timeout, killing process...")
                        self.process.kill()
            
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            
            finally:
                self.process = None
    
    async def shutdown(self) -> None:
        """
        Shutdown the ProcessManager and clean up resources.
        """
        logger.info("Shutting down ProcessManager...")
        await self._cleanup()
        logger.info("ProcessManager shutdown complete")
    
    def __del__(self):
        """
        Ensure resources are cleaned up when the object is garbage collected.
        """
        if self.is_running:
            # Create a new event loop for cleanup if necessary
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._cleanup())
                else:
                    loop.run_until_complete(self._cleanup())
            except Exception:
                # If we can't get or use the event loop, just log the error
                logger.error("Failed to clean up ProcessManager during garbage collection")
