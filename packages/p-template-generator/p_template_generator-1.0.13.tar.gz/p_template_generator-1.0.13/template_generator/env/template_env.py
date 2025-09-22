import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
from typing import Tuple, Dict, Optional

class HardwareDetector:
    def __init__(self):
        self.platform = sys.platform
        self.is_linux = self.platform == "linux"
        self.is_windows = self.platform == "win32"
        self.is_macos = self.platform == "darwin"
        
    def get_command_result(self, cmd: str, timeout: int = 30) -> str:
        try:
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                shell=True, 
                timeout=timeout,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return ""
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.warning(f"Command failed: {cmd}, error: {e}")
            return ""
    
    def detect_nvidia_gpu(self) -> bool:
        if not self.is_linux:
            return False
            
        if self.get_command_result("which nvidia-smi"):
            result = self.get_command_result("nvidia-smi")
            return "NVIDIA" in result and "Driver Version" in result
        return False
    
    def detect_display_server(self) -> Dict[str, bool]:
        result = {
            'x11': False,
            'wayland': False,
            'headless': False
        }
        
        if not self.is_linux:
            result['x11'] = True
            return result
            
        session_type = self.get_command_result("echo $XDG_SESSION_TYPE")
        if session_type:
            session_type_lower = session_type.lower()
            result['wayland'] = 'wayland' in session_type_lower
            result['x11'] = 'x11' in session_type_lower or 'xorg' in session_type_lower
        
        display = self.get_command_result("echo $DISPLAY")
        if display and display.strip():
            test_cmd = f"xdpyinfo -display {display.strip()} > /dev/null 2>&1"
            test_result = subprocess.run(test_cmd, shell=True)
            if test_result.returncode == 0:
                result['x11'] = True
            else:
                result['headless'] = True
        
        if not result['x11'] and not result['wayland']:
            display_env = self.get_command_result("echo $DISPLAY")
            if not display_env or not display_env.strip():
                result['headless'] = True
            else:
                result['headless'] = True
            
        return result
    
    def detect_hardware_acceleration(self) -> Dict[str, bool]:
        result = {
            'nvidia_encode': False,
            'nvidia_decode': False,
            'mesa_software': False,
            'egl_support': False
        }
        
        if not self.is_linux:
            return result
            
        # 检测NVIDIA编码/解码支持
        has_nvidia = self.detect_nvidia_gpu()
        if has_nvidia:
            result['nvidia_encode'] = True
            result['nvidia_decode'] = True
        
        # 检测Mesa软件渲染
        mesa_libs = [
            "/usr/lib/x86_64-linux-gnu/libGL.so",
            "/usr/lib/x86_64-linux-gnu/libGLESv2.so"
        ]
        result['mesa_software'] = any(os.path.exists(lib) for lib in mesa_libs)
        
        # 检测EGL支持
        egl_libs = [
            "/usr/lib/x86_64-linux-gnu/libEGL.so",
            "/usr/lib/libEGL.so"
        ]
        result['egl_support'] = any(os.path.exists(lib) for lib in egl_libs)
        
        return result

class EnvironmentSetup:
    def __init__(self, search_path: str = ""):
        self.search_path = search_path
        self.detector = HardwareDetector()
        self.platform = sys.platform
        
    def get_setup_script_path(self, script_name: str) -> str:
        if self.platform == "linux":
            current_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(current_dir, script_name)
            py_script_path = script_path + ".py"
            
            if os.path.exists(py_script_path):
                self._convert_py_to_sh(py_script_path, script_path)
            
            return script_path if os.path.exists(script_path) else ""
        return ""
    
    def _convert_py_to_sh(self, py_path: str, sh_path: str) -> bool:
        try:
            with open(py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(sh_path, 'w', encoding='utf-8') as f:
                f.write(content)
            os.chmod(sh_path, 0o755)
            os.remove(py_path)#remove .sh.py
            return True
            
        except Exception:
            return False
    
    def should_use_mesa(self, use_hardware_encode: bool = True, use_hardware_decode: bool = True) -> bool:
        if not self.detector.is_linux:
            return False
            
        if not use_hardware_encode:
            return True
            
        display_info = self.detector.detect_display_server()
        hardware_info = self.detector.detect_hardware_acceleration()
        
        # 检查EGL支持情况
        if not hardware_info['egl_support']:
            return True
            
        # 如果是headless环境且没有EGL支持，使用Mesa
        if display_info['headless'] and not hardware_info['egl_support']:
            return True
            
        return False
    
    def should_use_software_encoding(self, use_hardware_encode: bool = True, use_hardware_decode: bool = True) -> bool:
        if not self.detector.is_linux:
            return not use_hardware_encode            
        if not use_hardware_encode or not use_hardware_decode:
            return True
        hardware_info = self.detector.detect_hardware_acceleration()
        if not hardware_info['nvidia_encode'] and not hardware_info['nvidia_decode']:
            return True
        return False
    
    def setup_environment(self, use_hardware_encode: bool = True) -> bool:
        if not self.detector.is_linux:
            return True
            
        libskycore_path = "/usr/lib/libskycore.so"
        if os.path.exists(libskycore_path):
            if os.path.islink(libskycore_path):
                target_path = os.readlink(libskycore_path)
                if os.path.exists(target_path):
                    return True
                else:
                    # 符号链接的目标文件不存在，删除无效链接
                    os.unlink(libskycore_path)
            else:
                return True
            
        # 使用统一的设置脚本
        setup_script = self.get_setup_script_path('setup_unified.sh')
            
        if not setup_script or not os.path.exists(setup_script):
            print(f"setup_script: {setup_script}")
            return False
            
        # 执行设置脚本
        try:
            result = subprocess.run(
                f"sh {setup_script}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                return True
            else:
                # 尝试使用sudo版本
                print(f"result: {result}")
                print("setup_script执行失败，尝试使用sudo版本")
                sudo_script = self.get_setup_script_path("sudo_setup.sh")
                if sudo_script and os.path.exists(sudo_script):
                    result = subprocess.run(
                        f"sh {sudo_script}",
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=600
                    )
                    return result.returncode == 0
                        
        except Exception as ex:
            print(f"setup_script执行失败: {ex}")
            pass
            
        return False
    
    def setup_display(self) -> bool:
        if not self.detector.is_linux:
            return True
        
        # 检查Xvfb是否已经在运行
        result = subprocess.run("ps -ef | grep 'Xvfb :616' | grep -v grep", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            # 直接检查DISPLAY :616是否可用
            test_cmd = "xdpyinfo -display :616 > /dev/null 2>&1"
            test_result = subprocess.run(test_cmd, shell=True)
            if test_result.returncode == 0:
                os.environ['DISPLAY'] = ':616'
                self._setup_egl_environment()
                self._ensure_system_wide_display()
                return True
            else:
                print("Xvfb is running but DISPLAY :616 not accessible, cleaning up...")
                # 清理无效的Xvfb进程
                subprocess.run("pkill -f 'Xvfb :616'", shell=True)
                subprocess.run("sleep 1", shell=True)
        
        # 检查Xvfb是否安装
        xvfb_check = subprocess.run("which Xvfb", shell=True, capture_output=True, text=True)
        if xvfb_check.returncode != 0:
            print("Installing Xvfb...")
            install_result = subprocess.run(
                "apt-get update && apt-get install -y xvfb x11-utils", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            if install_result.returncode != 0:
                print("Warning: Failed to install Xvfb")
                return False
        
        # 启动Xvfb
        xvfb_cmd = "nohup Xvfb :616 -screen 0 1920x1080x24 -ac -nolisten tcp -dpi 96 > /dev/null 2>&1 &"
        subprocess.run(xvfb_cmd, shell=True)
        subprocess.run("sleep 3", shell=True)
        
        # 验证Xvfb启动
        result = subprocess.run("ps -ef | grep 'Xvfb :616' | grep -v grep", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("Xvfb started successfully")
            
            # 验证DISPLAY :616是否可用
            test_cmd = "xdpyinfo -display :616 > /dev/null 2>&1"
            test_result = subprocess.run(test_cmd, shell=True)
            if test_result.returncode == 0:
                # 设置当前进程环境变量
                os.environ['DISPLAY'] = ':616'
                self._setup_egl_environment()
                
                # 立即验证环境变量设置
                current_display = os.environ.get('DISPLAY', '')
                # 设置系统级环境变量持久化
                self._ensure_system_wide_display()
                
                print("DISPLAY setup completed successfully")
                return True
            else:
                print("Warning: Xvfb started but DISPLAY :616 not accessible")
                return False
        else:
            print("Warning: Failed to start Xvfb process")
            return False
        
    def _setup_egl_environment(self):
        """设置EGL环境变量"""
        # 设置Mesa软件渲染环境变量
        os.environ['MESA_GL_VERSION_OVERRIDE'] = '3.3'
        os.environ['MESA_GLSL_VERSION_OVERRIDE'] = '330'
        os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'
        os.environ['GALLIUM_DRIVER'] = 'llvmpipe'
        
        # 设置EGL相关环境变量
        os.environ['EGL_PLATFORM'] = 'x11'
        os.environ['MESA_GLSL_CACHE_DISABLE'] = '1'
        
        # 确保EGL库路径正确
        egl_paths = [
            '/usr/lib/x86_64-linux-gnu/libEGL_mesa.so.0',
            '/usr/lib/x86_64-linux-gnu/libEGL.so.1'
        ]
        
        for path in egl_paths:
            if os.path.exists(path):
                os.environ['EGL_DRIVER_PATH'] = os.path.dirname(path)
                break
    
    def _write_to_file_if_not_exists(self, file_path, content):
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    existing_content = f.read()
                    if 'Template Generator Environment Variables' in existing_content:
                        # 已经存在，跳过
                        return
            
            # 写入文件
            with open(file_path, 'a') as f:
                f.write(content)
        except Exception as e:
            print(f"Warning: Failed to write to {file_path}: {e}")
    
    def _ensure_system_wide_display(self):
        try:
            display_value = os.environ.get('DISPLAY', ':616')
            
            # 1. 写入到/etc/environment（系统级环境变量）
            self._write_display_to_etc_environment(display_value)
            
            # 2. 写入到用户级配置文件（确保用户shell能加载）
            self._write_display_to_user_configs(display_value)
            
            # 3. 尝试在当前shell中导出环境变量
            self._export_to_current_shell(display_value)
            
            # 4. 创建包装脚本，确保环境变量传递
            self._create_wrapper_script(display_value)
        except Exception as e:
            print(f"Warning: Failed to set system-wide DISPLAY: {e}")
    
    def _write_display_to_etc_environment(self, display_value):
        try:
            env_file = '/etc/environment'
            display_line = f'DISPLAY="{display_value}"\n'
            
            # 读取现有内容
            existing_content = ""
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    existing_content = f.read()
            
            # 检查是否已存在DISPLAY设置
            if f'DISPLAY=' in existing_content:
                # 替换现有的DISPLAY设置
                lines = existing_content.split('\n')
                new_lines = []
                for line in lines:
                    if line.startswith('DISPLAY='):
                        new_lines.append(f'DISPLAY="{display_value}"')
                    else:
                        new_lines.append(line)
                new_content = '\n'.join(new_lines)
            else:
                # 添加新的DISPLAY设置
                new_content = existing_content.rstrip() + '\n' + display_line
            
            # 写入文件
            with open(env_file, 'w') as f:
                f.write(new_content)
        except PermissionError:
            print("Warning: Cannot write to /etc/environment (need root permission)")
        except Exception as e:
            print(f"Warning: Failed to write DISPLAY to /etc/environment: {e}")
    
    def _write_display_to_user_configs(self, display_value):
        try:
            display_content = f"""
# Template Generator DISPLAY Configuration
export DISPLAY="{display_value}"
"""
            
            # 只写入最重要的用户配置文件
            user_configs = [
                os.path.expanduser('~/.bashrc'),
                os.path.expanduser('~/.profile')
            ]
            
            for config_file in user_configs:
                self._write_to_file_if_not_exists(config_file, display_content)
                
        except Exception as e:
            print(f"Warning: Failed to write DISPLAY to user configs: {e}")
    
    def _export_to_current_shell(self, display_value):
        """尝试在当前shell中导出环境变量"""
        try:
            # 尝试通过subprocess在当前shell中设置环境变量
            # 注意：这只能影响子进程，不能影响父shell
            export_cmd = f'export DISPLAY="{display_value}"'
            
            # 创建一个临时的shell脚本来设置环境变量
            temp_script = '/tmp/set_display.sh'
            with open(temp_script, 'w') as f:
                f.write(f'#!/bin/bash\n{export_cmd}\necho "DISPLAY set to: $DISPLAY"\n')
            
            os.chmod(temp_script, 0o755)
            
            result = subprocess.run(['bash', temp_script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print(f"Warning: Failed to export DISPLAY: {result.stderr}")
                
        except Exception as e:
            print(f"Warning: Failed to export to current shell: {e}")
    
    def _create_wrapper_script(self, display_value):
        try:
            wrapper_script = '/tmp/set_display_wrapper.sh'
            with open(wrapper_script, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'# Template Generator DISPLAY Wrapper Script\n')
                f.write(f'export DISPLAY="{display_value}"\n')
                f.write(f'echo "DISPLAY环境变量已设置为: $DISPLAY"\n')
                f.write(f'echo "当前shell PID: $$"\n')
                f.write(f'echo "父shell PID: $PPID"\n')
                f.write(f'echo "要在此shell中永久设置DISPLAY，请执行:"\n')
                f.write(f'echo "export DISPLAY=\\"{display_value}\\""\n')
                f.write(f'echo "或者重新启动shell会话"\n')
                f.write(f'echo "验证命令: echo \\$DISPLAY"\n')
            
            os.chmod(wrapper_script, 0o755)
            result = subprocess.run(['bash', wrapper_script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print(f"包装脚本执行失败: {result.stderr}")
                
        except Exception as e:
            print(f"Warning: Failed to create wrapper script: {e}")
    
def maybeMesa(useHardwareEncode=True, useHardwareDecode=True):
    setup = EnvironmentSetup()
    return setup.should_use_mesa(useHardwareEncode, useHardwareDecode)

def maybeSoftWare(useHardwareEncode=True, useHardwareDecode=True):
    setup = EnvironmentSetup()
    return setup.should_use_software_encoding(useHardwareEncode, useHardwareDecode)