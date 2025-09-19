try:
    from .common_utils import safe_print
except ImportError:
    from omnipkg.common_utils import safe_print
"""
omnipkg
An intelligent installer that lets pip run, then surgically cleans up downgrades
and isolates conflicting versions in deduplicated bubbles to guarantee a stable environment.
"""
import hashlib
import importlib.metadata
import io
import json
import locale as sys_locale
import os
import threading
import platform
import time
import re
import shutil
import site
import subprocess
import sys
import collections
import tarfile
import tempfile
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False
import requests as http_requests
from filelock import FileLock
from importlib.metadata import version, metadata, PackageNotFoundError
from packaging.utils import canonicalize_name
from packaging.version import parse as parse_version, InvalidVersion
from .i18n import _
from .package_meta_builder import omnipkgMetadataGatherer
from .cache import SQLiteCacheClient
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    magic = None
    HAS_MAGIC = False

def _get_core_dependencies() -> set:
    """
    Correctly reads omnipkg's own production dependencies and returns them as a set.
    """
    try:
        pkg_meta = metadata('omnipkg')
        reqs = pkg_meta.get_all('Requires-Dist') or []
        return {canonicalize_name(re.match('^[a-zA-Z0-9\\-_.]+', req).group(0)) for req in reqs if re.match('^[a-zA-Z0-9\\-_.]+', req)}
    except PackageNotFoundError:
        try:
            pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
            if pyproject_path.exists():
                with pyproject_path.open('rb') as f:
                    pyproject_data = tomllib.load(f)
                return pyproject_data['project'].get('dependencies', [])
        except Exception as e:
            safe_print(_('⚠️ Could not parse pyproject.toml, falling back to empty list: {}').format(e))
            return []
    except Exception as e:
        safe_print(_('⚠️ Could not determine core dependencies, falling back to empty list: {}').format(e))
        return []

class ConfigManager:
    """
    Manages loading and first-time creation of the omnipkg config file.
    Now includes Python interpreter hotswapping capabilities and is environment-aware.
    """

    def __init__(self, suppress_init_messages=False):
        """
        Initializes the ConfigManager with a robust, fail-safe sequence.
        This new logic correctly establishes environment identity first, then loads
        or creates the configuration, and finally handles the one-time environment
        setup for interpreters.
        """
        env_id_override = os.environ.get('OMNIPKG_ENV_ID_OVERRIDE')
        self.venv_path = self._get_venv_root()
        if env_id_override:
            self.env_id = env_id_override
        else:
            self.env_id = hashlib.md5(str(self.venv_path.resolve()).encode()).hexdigest()[:8]
        self._python_cache = {}
        self._preferred_version = (3, 11)
        self.config_dir = Path.home() / '.config' / 'omnipkg'
        self.config_path = self.config_dir / 'config.json'
        self.config = self._load_or_create_env_config(interactive=not suppress_init_messages)
        if self.config:
            self.multiversion_base = Path(self.config.get('multiversion_base', ''))
        else:
            if not suppress_init_messages:
                safe_print(_('⚠️ CRITICAL Warning: Config failed to load, omnipkg may not function.'))
            self.multiversion_base = Path('')
            return
        is_nested_interpreter = '.omnipkg/interpreters' in str(Path(sys.executable).resolve())
        setup_complete_flag = self.venv_path / '.omnipkg' / '.setup_complete'
        if not setup_complete_flag.exists() and (not is_nested_interpreter):
            if not suppress_init_messages:
                safe_print('\n' + '=' * 60)
                safe_print(_('  🚀 OMNIPKG ONE-TIME ENVIRONMENT SETUP'))
                safe_print('=' * 60)
            try:
                if not suppress_init_messages:
                    safe_print(_('   - Step 1: Registering the native Python interpreter...'))
                native_version_str = f'{sys.version_info.major}.{sys.version_info.minor}'
                self._register_and_link_existing_interpreter(Path(sys.executable), native_version_str)
                if sys.version_info[:2] != self._preferred_version:
                    if not suppress_init_messages:
                        safe_print(_('\n   - Step 2: Setting up the required Python 3.11 control plane...'))
                    temp_omnipkg = omnipkg(config_manager=self)
                    result_code = temp_omnipkg._fallback_to_download('3.11')
                    if result_code != 0:
                        raise RuntimeError('Failed to set up the Python 3.11 control plane.')
                setup_complete_flag.parent.mkdir(parents=True, exist_ok=True)
                setup_complete_flag.touch()
                if not suppress_init_messages:
                    safe_print('\n' + '=' * 60)
                    safe_print(_('  ✅ SETUP COMPLETE'))
                    safe_print('=' * 60)
                    safe_print(_('Your environment is now fully managed by omnipkg.'))
                    safe_print('=' * 60)
            except Exception as e:
                if not suppress_init_messages:
                    safe_print(_('❌ A critical error occurred during one-time setup: {}').format(e))
                    import traceback
                    traceback.print_exc()
                if setup_complete_flag.exists():
                    setup_complete_flag.unlink(missing_ok=True)
                sys.exit(1)

    def _set_rebuild_flag_for_version(self, version_str: str):
        """
        Sets a flag indicating that a new interpreter needs its knowledge base built.
        This is a stateful, safe way to trigger a one-time setup.
        """
        flag_file = self.venv_path / '.omnipkg' / '.needs_kb_rebuild'
        lock_file = self.venv_path / '.omnipkg' / '.needs_kb_rebuild.lock'
        flag_file.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(lock_file):
            versions_to_rebuild = []
            if flag_file.exists():
                try:
                    with open(flag_file, 'r') as f:
                        versions_to_rebuild = json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass
            if version_str not in versions_to_rebuild:
                versions_to_rebuild.append(version_str)
            with open(flag_file, 'w') as f:
                json.dump(versions_to_rebuild, f)
        safe_print(_('   🚩 Flag set: Python {} will build its knowledge base on first use.').format(version_str))

    def _peek_config_for_flag(self, flag_name: str) -> bool:
        """
        Safely checks the config file for a boolean flag for the current environment
        without fully loading the ConfigManager. Returns False if file doesn't exist.
        """
        if not self.config_path.exists():
            return False
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            return data.get('environments', {}).get(self.env_id, {}).get(flag_name, False)
        except (json.JSONDecodeError, IOError):
            return False

    def _get_venv_root(self) -> Path:
        """
        Finds the virtual environment root with enhanced validation to prevent
        environment cross-contamination from stale shell variables.
        """
        override = os.environ.get('OMNIPKG_VENV_ROOT')
        if override:
            return Path(override)
        current_executable = Path(sys.executable).resolve()
        venv_path_str = os.environ.get('VIRTUAL_ENV')
        if venv_path_str:
            venv_path = Path(venv_path_str).resolve()
            if str(current_executable).startswith(str(venv_path)):
                return venv_path
        conda_prefix_str = os.environ.get('CONDA_PREFIX')
        if conda_prefix_str:
            conda_path = Path(conda_prefix_str).resolve()
            if str(current_executable).startswith(str(conda_path)):
                return conda_path
        search_dir = current_executable.parent
        while search_dir != search_dir.parent:
            if (search_dir / 'pyvenv.cfg').exists():
                return search_dir
            search_dir = search_dir.parent
        return Path(sys.prefix)

    def _reset_setup_flag_on_disk(self):
        """Directly modifies the config file on disk to reset the setup flag."""
        try:
            full_config = {'environments': {}}
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    full_config = json.load(f)
            if self.env_id in full_config.get('environments', {}):
                full_config['environments'][self.env_id].pop('managed_python_setup_complete', None)
            with open(self.config_path, 'w') as f:
                json.dump(full_config, f, indent=4)
        except (IOError, json.JSONDecodeError) as e:
            safe_print(_('   ⚠️  Could not reset setup flag in config file: {}').format(e))

    def _trigger_hotswap_relaunch(self):
        """
        Handles the user interaction and download process for an environment that needs to be upgraded.
        This function is self-contained and does not depend on self.config. It ends with an execv call.
        """
        safe_print('\n' + '=' * 60)
        safe_print(_('  🚀 Environment Hotswap to a Managed Python 3.11'))
        safe_print('=' * 60)
        safe_print(f'omnipkg works best with Python 3.11. Your version is {sys.version_info.major}.{sys.version_info.minor}.')
        safe_print(_("\nTo ensure everything 'just works', omnipkg will now perform a one-time setup:"))
        safe_print(_('  1. Download a self-contained Python 3.11 into your virtual environment.'))
        safe_print('  2. Relaunch seamlessly to continue your command.')
        try:
            choice = input('\nDo you want to proceed with the automatic setup? (y/n): ')
            if choice.lower() == 'y':
                self._install_python311_in_venv()
            else:
                safe_print('🛑 Setup cancelled. Aborting, as a managed Python 3.11 is required.')
                sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            safe_print(_('\n🛑 Operation cancelled. Aborting.'))
            sys.exit(1)

    def _has_suitable_python311(self) -> bool:
        """
        Comprehensive check for existing suitable Python 3.11 installations.
        Returns True if we already have a usable Python 3.11 setup.
        """
        if sys.version_info[:2] == (3, 11) and sys.executable.startswith(str(self.venv_path)):
            return True
        registry_path = self.venv_path / '.omnipkg' / 'interpreters' / 'registry.json'
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
                python_311_path = registry.get('interpreters', {}).get('3.11')
                if python_311_path and Path(python_311_path).exists():
                    try:
                        result = subprocess.run([python_311_path, '-c', "import sys; safe_print(f'{sys.version_info.major}.{sys.version_info.minor}')"], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0 and result.stdout.strip() == '3.11':
                            return True
                    except:
                        pass
            except:
                pass
        expected_exe_path = self._get_interpreter_dest_path(self.venv_path) / ('python.exe' if platform.system() == 'Windows' else 'bin/python3.11')
        if expected_exe_path.exists():
            try:
                result = subprocess.run([str(expected_exe_path), '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'Python 3.11' in result.stdout:
                    return True
            except:
                pass
        bin_dir = self.venv_path / ('Scripts' if platform.system() == 'Windows' else 'bin')
        if bin_dir.exists():
            for possible_name in ['python3.11', 'python']:
                exe_path = bin_dir / (f'{possible_name}.exe' if platform.system() == 'Windows' else possible_name)
                if exe_path.exists():
                    try:
                        result = subprocess.run([str(exe_path), '-c', "import sys; safe_print(f'{sys.version_info.major}.{sys.version_info.minor}')"], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0 and result.stdout.strip() == '3.11':
                            return True
                    except:
                        pass
        return False

    def _align_config_to_interpreter(self, python_exe_path_str: str):
        """
        Updates and saves config paths to match the specified Python executable
        by running it as a subprocess to get its true paths.
        """
        safe_print(_('🔧 Aligning configuration to use Python interpreter: {}').format(python_exe_path_str))
        correct_paths = self._get_paths_for_interpreter(python_exe_path_str)
        if not correct_paths:
            safe_print(f'❌ CRITICAL: Failed to determine paths for {python_exe_path_str}. Configuration not updated.')
            return
        safe_print(_('   - New site-packages path: {}').format(correct_paths['site_packages_path']))
        safe_print(_('   - New Python executable: {}').format(correct_paths['python_executable']))
        self.set('python_executable', correct_paths['python_executable'])
        self.set('site_packages_path', correct_paths['site_packages_path'])
        self.set('multiversion_base', correct_paths['multiversion_base'])
        self.config.update(correct_paths)
        self.multiversion_base = Path(self.config['multiversion_base'])
        safe_print(_('   ✅ Configuration updated and saved successfully.'))

    def _setup_native_311_environment(self):
        """
        Performs the one-time setup for an environment that already has Python 3.11.
        This primarily involves symlinking and registering the interpreter.
        This function runs AFTER self.config is loaded.
        """
        safe_print('\n' + '=' * 60)
        safe_print('  🚀 Finalizing Environment Setup for Python 3.11')
        safe_print('=' * 60)
        safe_print(_('✅ Detected a suitable Python 3.11 within your virtual environment.'))
        safe_print('   - Registering it with omnipkg for future operations...')
        self._register_and_link_existing_interpreter(Path(sys.executable), f'{sys.version_info.major}.{sys.version_info.minor}')
        registered_311_path = self.get_interpreter_for_version('3.11')
        if registered_311_path:
            self._align_config_to_interpreter(str(registered_311_path))
        else:
            safe_print(_('⚠️ Warning: Could not find registered Python 3.11 path after setup. Config may be incorrect.'))
        self.set('managed_python_setup_complete', True)
        safe_print(_('\n✅ Environment setup is complete!'))

    def _load_path_registry(self):
        """Load path registry (placeholder for your path management)."""
        pass

    def _ensure_proper_registration(self):
        """
        Ensures the current Python 3.11 is properly registered even if already detected.
        """
        if sys.version_info[:2] == (3, 11):
            current_path = Path(sys.executable).resolve()
            registry_path = self.venv_path / '.omnipkg' / 'interpreters' / 'registry.json'
            needs_registration = True
            if registry_path.exists():
                try:
                    with open(registry_path, 'r') as f:
                        registry = json.load(f)
                    registered_311 = registry.get('interpreters', {}).get('3.11')
                    if registered_311 and Path(registered_311).resolve() == current_path:
                        needs_registration = False
                except:
                    pass
            if needs_registration:
                safe_print(_('   - Registering current Python 3.11...'))
                self._register_all_interpreters(self.venv_path)

    def _register_and_link_existing_interpreter(self, interpreter_path: Path, version: str):
        """
        "Adopts" the native venv interpreter by creating a symlink to it inside
        the managed .omnipkg/interpreters directory. It then ensures the registry
        points to this new, centralized symlink.
        On Windows, falls back to creating a directory junction if creating a symlink fails.
        """
        safe_print(_('   - Centralizing native Python {}...').format(version))
        managed_interpreters_dir = self.venv_path / '.omnipkg' / 'interpreters'
        managed_interpreters_dir.mkdir(parents=True, exist_ok=True)
        symlink_dir_name = f'cpython-{version}-venv-native'
        symlink_path = managed_interpreters_dir / symlink_dir_name
        target_for_link = interpreter_path.parent.parent

        if symlink_path.exists():
            safe_print(_('   - ✅ Link already exists.'))
            # Optional: Add validation to check if the existing link is correct
        else:
            try:
                safe_print(_('   - Attempting to create a symbolic link...'))
                symlink_path.symlink_to(target_for_link, target_is_directory=True)
                safe_print(_('   - ✅ Created symlink: {} -> {}').format(symlink_path, target_for_link))
            except (PermissionError, OSError) as e:
                if platform.system() == 'Windows':
                    safe_print(_('   - ⚠️ Symlink creation failed ({}). Falling back to creating a directory junction...').format(e))
                    try:
                        import subprocess
                        subprocess.run(['cmd', '/c', 'mklink', '/J', str(symlink_path), str(target_for_link)], check=True, capture_output=True)
                        safe_print(_('   - ✅ Created junction: {} -> {}').format(symlink_path, target_for_link))
                    except (subprocess.CalledProcessError, FileNotFoundError) as junction_error:
                        safe_print(_('   - ❌ Failed to create directory junction: {}').format(junction_error))
                        safe_print(_('   - ❌ Could not adopt the interpreter. Please try running with administrative privileges.'))
                else:
                    safe_print(_('   - ❌ Failed to create symlink: {}').format(e))
                    safe_print(_('   - ❌ Could not adopt the interpreter.'))

        self._register_all_interpreters(self.venv_path)

    def _register_all_interpreters(self, venv_path: Path):
        """
        FIXED: Discovers and registers ONLY the Python interpreters that are explicitly
        managed within the .omnipkg/interpreters directory. This is the single
        source of truth for what is "swappable".
        """
        safe_print(_('🔧 Registering all managed Python interpreters...'))
        managed_interpreters_dir = venv_path / '.omnipkg' / 'interpreters'
        managed_interpreters_dir.mkdir(parents=True, exist_ok=True)
        registry_path = managed_interpreters_dir / 'registry.json'
        interpreters = {}
        if not managed_interpreters_dir.is_dir():
            safe_print(_('   ⚠️  Managed interpreters directory not found.'))
            return
        for interp_dir in managed_interpreters_dir.iterdir():
            if not (interp_dir.is_dir() or interp_dir.is_symlink()):
                continue
            safe_print(_('   -> Scanning directory: {}').format(interp_dir.name))
            found_exe_path = None
            search_locations = [interp_dir / 'bin', interp_dir / 'Scripts', interp_dir]
            possible_exe_names = ['python3.12', 'python3.11', 'python3.10', 'python3.9', 'python3', 'python', 'python.exe']
            for location in search_locations:
                if location.is_dir():
                    for exe_name in possible_exe_names:
                        exe_path = location / exe_name
                        if exe_path.is_file() and os.access(exe_path, os.X_OK):
                            version_tuple = self._verify_python_version(str(exe_path))
                            if version_tuple:
                                found_exe_path = exe_path
                                safe_print(_('      ✅ Found valid executable: {}').format(found_exe_path))
                                break
                if found_exe_path:
                    break
            if found_exe_path:
                version_tuple = self._verify_python_version(str(found_exe_path))
                if version_tuple:
                    version_str = f'{version_tuple[0]}.{version_tuple[1]}'
                    interpreters[version_str] = str(found_exe_path.resolve())
        primary_version = '3.11' if '3.11' in interpreters else sorted(interpreters.keys(), reverse=True)[0] if interpreters else None
        registry_data = {'primary_version': primary_version, 'interpreters': {k: v for k, v in interpreters.items()}, 'last_updated': datetime.now().isoformat()}
        with open(registry_path, 'w') as f:
            json.dump(registry_data, f, indent=4)
        if interpreters:
            safe_print(_('   ✅ Registered {} managed Python interpreters.').format(len(interpreters)))
            for version, path in sorted(interpreters.items()):
                safe_print(_('      - Python {}: {}').format(version, path))
        else:
            safe_print(_('   ⚠️  No managed Python interpreters were found or could be registered.'))

    def _find_existing_python311(self) -> Optional[Path]:
        """Checks if a managed Python 3.11 interpreter already exists."""
        venv_path = Path(sys.prefix)
        expected_exe_path = self._get_interpreter_dest_path(venv_path) / ('python.exe' if platform.system() == 'windows' else 'bin/python3.11')
        if expected_exe_path.exists() and expected_exe_path.is_file():
            safe_print(_('✅ Found existing Python 3.11 interpreter.'))
            return expected_exe_path
        return None

    def get_interpreter_for_version(self, version: str) -> Optional[Path]:
        """
        Get the path to a specific Python interpreter version from the registry.
        """
        registry_path = self.venv_path / '.omnipkg' / 'interpreters' / 'registry.json'
        if not registry_path.exists():
            safe_print(_('   [DEBUG] Interpreter registry not found at: {}').format(registry_path))
            return None
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            interpreter_path = registry.get('interpreters', {}).get(version)
            if interpreter_path and Path(interpreter_path).exists():
                return Path(interpreter_path)
        except (IOError, json.JSONDecodeError):
            pass
        return None

    def _find_project_root(self):
        """
        Find the project root directory by looking for setup.py, pyproject.toml, or .git
        """
        from pathlib import Path
        current_dir = Path.cwd()
        module_dir = Path(__file__).parent.parent
        search_paths = [current_dir, module_dir]
        for start_path in search_paths:
            for path in [start_path] + list(start_path.parents):
                project_files = ['setup.py', 'pyproject.toml', 'setup.cfg', '.git', 'omnipkg.egg-info']
                for project_file in project_files:
                    if (path / project_file).exists():
                        safe_print(_('     (Found project root: {})').format(path))
                        return path
        safe_print(_('     (No project root found)'))
        return None

    def _install_essential_packages(self, python_exe: Path):
        """
        Installs essential packages for a new interpreter using a robust hybrid strategy.
        It installs dependencies first using the new interpreter's pip, then installs
        omnipkg itself without its dependencies to avoid resolver conflicts.
        """
        safe_print('📦 Bootstrapping essential packages for new interpreter...')

        def run_verbose(cmd: List[str], error_msg: str):
            """Helper to run a command and show its output."""
            safe_print(_('   🔩 Running: {}').format(' '.join(cmd)))
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
            except subprocess.CalledProcessError as e:
                safe_print(_('   ❌ {}').format(error_msg))
                safe_print('   --- Stderr ---')
                safe_print(e.stderr)
                safe_print('   ----------------')
                raise
        try:
            safe_print(_('   - Bootstrapping pip, setuptools, wheel...'))
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as tmp_file:
                script_path = tmp_file.name
                with urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py') as response:
                    tmp_file.write(response.read().decode('utf-8'))
            pip_cmd = [str(python_exe), script_path, '--no-cache-dir', 'pip', 'setuptools', 'wheel']
            run_verbose(pip_cmd, 'Failed to bootstrap pip.')
            os.unlink(script_path)
            safe_print(_('   ✅ Pip bootstrap complete.'))
            core_deps = _get_core_dependencies()
            if core_deps:
                safe_print(_('   - Installing omnipkg core dependencies...'))
                deps_install_cmd = [str(python_exe), '-m', 'pip', 'install', '--no-cache-dir'] + sorted(list(core_deps))
                run_verbose(deps_install_cmd, 'Failed to install omnipkg dependencies.')
                safe_print(_('   ✅ Core dependencies installed.'))
            safe_print(_('   - Installing omnipkg application layer...'))
            project_root = self._find_project_root()
            if project_root:
                safe_print(_('     (Developer mode detected: performing editable install)'))
                install_cmd = [str(python_exe), '-m', 'pip', 'install', '--no-cache-dir', '--no-deps', '-e', str(project_root)]
            else:
                safe_print('     (Standard mode detected: installing from PyPI)')
                install_cmd = [str(python_exe), '-m', 'pip', 'install', '--no-cache-dir', '--no-deps', 'omnipkg']
            run_verbose(install_cmd, 'Failed to install omnipkg application.')
            safe_print(_('   ✅ Omnipkg bootstrapped successfully!'))
        except Exception as e:
            safe_print(_('❌ A critical error occurred during the bootstrap process: {}').format(e))
            raise

    def _create_omnipkg_executable(self, new_python_exe: Path, venv_path: Path):
        """
        Creates a proper shell script executable that forces the use of the new Python interpreter.
        """
        safe_print(_('🔧 Creating new omnipkg executable...'))
        bin_dir = venv_path / ('Scripts' if platform.system() == 'Windows' else 'bin')
        omnipkg_exec_path = bin_dir / 'omnipkg'
        system = platform.system().lower()
        if system == 'windows':
            script_content = f'@echo off\nREM This script was auto-generated by omnipkg to ensure the correct Python is used.\n"{new_python_exe.resolve()}" -m omnipkg.cli %*\n'
            omnipkg_exec_path = bin_dir / 'omnipkg.bat'
        else:
            script_content = f'#!/bin/bash\n# This script was auto-generated by omnipkg to ensure the correct Python is used.\n\nexec "{new_python_exe.resolve()}" -m omnipkg.cli "$@"\n'
        with open(omnipkg_exec_path, 'w') as f:
            f.write(script_content)
        if system != 'windows':
            omnipkg_exec_path.chmod(493)
        safe_print(_('   ✅ New omnipkg executable created.'))

    def _update_default_python_links(self, venv_path: Path, new_python_exe: Path):
        """Updates the default python/python3 symlinks to point to Python 3.11."""
        safe_print(_('🔧 Updating default Python links...'))
        bin_dir = venv_path / ('Scripts' if platform.system() == 'Windows' else 'bin')
        if platform.system() == 'Windows':
            for name in ['python.exe', 'python3.exe']:
                target = bin_dir / name
                if target.exists():
                    target.unlink()
                shutil.copy2(new_python_exe, target)
        else:
            for name in ['python', 'python3']:
                target = bin_dir / name
                if target.exists() or target.is_symlink():
                    target.unlink()
                target.symlink_to(new_python_exe)
        version_tuple = self._verify_python_version(str(new_python_exe))
        version_str = f'{version_tuple[0]}.{version_tuple[1]}' if version_tuple else 'the new version'
        safe_print(_('   ✅ Default Python links updated to use Python {}.').format(version_str))

    def _auto_register_original_python(self, venv_path: Path) -> None:
        """
        Automatically detects and registers the original Python interpreter that was
        used to create this environment, without moving or copying it.
        """
        safe_print(_('🔍 Auto-detecting original Python interpreter...'))
        current_exe = Path(sys.executable).resolve()
        current_version = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
        major_minor = f'{sys.version_info.major}.{sys.version_info.minor}'
        safe_print(_('   - Detected: Python {} at {}').format(current_version, current_exe))
        interpreters_dir = venv_path / '.omnipkg' / 'interpreters'
        registry_path = venv_path / '.omnipkg' / 'python_registry.json'
        registry = {}
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
            except Exception as e:
                safe_print(f'   ⚠️  Warning: Could not load registry: {e}')
                registry = {}
        if major_minor in registry:
            safe_print(_('   ✅ Python {} already registered at: {}').format(major_minor, registry[major_minor]['path']))
            return
        managed_name = f'original-{current_version}'
        managed_dir = interpreters_dir / managed_name
        managed_dir.mkdir(parents=True, exist_ok=True)
        bin_dir = managed_dir / 'bin'
        bin_dir.mkdir(exist_ok=True)
        original_links = [('python', current_exe), (f'python{sys.version_info.major}', current_exe), (f'python{major_minor}', current_exe)]
        safe_print(_('   📝 Registering Python {} (original) without copying...').format(major_minor))
        for link_name, target in original_links:
            link_path = bin_dir / link_name
            if link_path.exists():
                link_path.unlink()
            try:
                link_path.symlink_to(target)
                safe_print(_('      ✅ Created symlink: {} -> {}').format(link_name, target))
            except Exception as e:
                safe_print(_('      ⚠️  Could not create symlink {}: {}').format(link_name, e))
        pip_candidates = [current_exe.parent / 'pip', current_exe.parent / f'pip{sys.version_info.major}', current_exe.parent / f'pip{major_minor}']
        for pip_path in pip_candidates:
            if pip_path.exists():
                pip_link = bin_dir / pip_path.name
                if not pip_link.exists():
                    try:
                        pip_link.symlink_to(pip_path)
                        safe_print(_('      ✅ Created pip symlink: {}').format(pip_path.name))
                        break
                    except Exception as e:
                        safe_print(_('      ⚠️  Could not create pip symlink: {}').format(e))
        registry[major_minor] = {'path': str(bin_dir / f'python{major_minor}'), 'version': current_version, 'type': 'original', 'source': str(current_exe), 'managed_dir': str(managed_dir), 'registered_at': datetime.now().isoformat()}
        try:
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            safe_print(_('   ✅ Registered Python {} in registry').format(major_minor))
        except Exception as e:
            safe_print(f'   ❌ Failed to save registry: {e}')
            return
        if hasattr(self, 'config') and self.config:
            managed_interpreters = self.config.get('managed_interpreters', {})
            managed_interpreters[major_minor] = str(bin_dir / f'python{major_minor}')
            self.set('managed_interpreters', managed_interpreters)
            safe_print(f'   ✅ Updated main config with Python {major_minor}')

    def _should_auto_register_python(self, version: str) -> bool:
        """
        Determines if we should auto-register the original Python instead of downloading.
        """
        major_minor = '.'.join(version.split('.')[:2])
        current_major_minor = f'{sys.version_info.major}.{sys.version_info.minor}'
        return major_minor == current_major_minor

    def _enhanced_python_adopt(self, version: str) -> int:
        """
        Enhanced adoption logic that prioritizes registering the original interpreter
        when appropriate, falling back to download only when necessary.
        """
        safe_print(_('🐍 Attempting to adopt Python {} into the environment...').format(version))
        if self._should_auto_register_python(version):
            safe_print(_('   🎯 Requested version matches current Python {}.{}').format(sys.version_info.major, sys.version_info.minor))
            safe_print(_('   📋 Auto-registering current interpreter instead of downloading...'))
            try:
                self._auto_register_original_python(self.venv_path)
                safe_print(_('🎉 Successfully registered Python {} (original interpreter)!').format(version))
                safe_print(_("   You can now use 'omnipkg swap python {}'").format(version))
                return 0
            except Exception as e:
                safe_print(_('   ❌ Auto-registration failed: {}').format(e))
                safe_print(_('   🔄 Falling back to download strategy...'))
        return self._existing_adopt_logic(version)

    def _register_all_managed_interpreters(self) -> None:
        """
        Enhanced version that includes original interpreters in the scan.
        """
        safe_print(_('🔧 Registering all managed Python interpreters...'))
        interpreters_dir = self.venv_path / '.omnipkg' / 'interpreters'
        if not interpreters_dir.exists():
            safe_print(_('   ℹ️  No interpreters directory found.'))
            return
        registry_path = self.venv_path / '.omnipkg' / 'python_registry.json'
        registry = {}
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
            except Exception:
                registry = {}
        managed_interpreters = {}
        for interpreter_dir in interpreters_dir.iterdir():
            if not interpreter_dir.is_dir():
                continue
            safe_print(_('   -> Scanning directory: {}').format(interpreter_dir.name))
            bin_dir = interpreter_dir / 'bin'
            if not bin_dir.exists():
                safe_print(_('      ⚠️  No bin/ directory found in {}').format(interpreter_dir.name))
                continue
            python_exe = None
            for candidate in bin_dir.glob('python[0-9].[0-9]*'):
                if candidate.is_file() and os.access(candidate, os.X_OK):
                    python_exe = candidate
                    break
            if not python_exe:
                safe_print(_('      ⚠️  No valid Python executable found in {}').format(interpreter_dir.name))
                continue
            try:
                result = subprocess.run([str(python_exe), '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version_match = re.search('Python (\\d+\\.\\d+)', result.stdout)
                    if version_match:
                        major_minor = version_match.group(1)
                        managed_interpreters[major_minor] = str(python_exe)
                        if major_minor not in registry:
                            registry[major_minor] = {'path': str(python_exe), 'type': 'downloaded' if 'cpython-' in interpreter_dir.name else 'original', 'managed_dir': str(interpreter_dir), 'registered_at': datetime.now().isoformat()}
                        interpreter_type = registry[major_minor].get('type', 'unknown')
                        safe_print(_('      ✅ Found valid executable: {} ({})').format(python_exe, interpreter_type))
                    else:
                        safe_print(_('      ⚠️  Could not parse version from: {}').format(result.stdout.strip()))
                else:
                    safe_print(_('      ⚠️  Failed to get version: {}').format(result.stderr.strip()))
            except Exception as e:
                safe_print(_('      ⚠️  Error testing executable: {}').format(e))
        try:
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            safe_print(f'   ⚠️  Could not save registry: {e}')
        if managed_interpreters:
            self.set('managed_interpreters', managed_interpreters)
            safe_print(_('   ✅ Registered {} managed Python interpreters.').format(len(managed_interpreters)))
            for version, path in managed_interpreters.items():
                interpreter_type = registry.get(version, {}).get('type', 'unknown')
                safe_print(_('      - Python {}: {} ({})').format(version, path, interpreter_type))
        else:
            safe_print(_('   ℹ️  No managed interpreters found.'))

    def _install_managed_python(self, venv_path: Path, full_version: str) -> Path:
        """
        Downloads and installs a specific, self-contained version of Python
        from the python-build-standalone project. Returns the path to the new executable.
        """
        safe_print(_('\n🚀 Installing managed Python {}...').format(full_version))
        system = platform.system().lower()
        arch = platform.machine().lower()
        py_arch_map = {'x86_64': 'x86_64', 'amd64': 'x86_64', 'aarch64': 'aarch64', 'arm64': 'aarch64'}
        py_arch = py_arch_map.get(arch)
        if not py_arch:
            raise OSError(_('Unsupported architecture: {}').format(arch))
        VERSION_TO_RELEASE_TAG_MAP = {'3.13.7': '20250818', '3.13.6': '20250807', '3.13.1': '20241211', '3.13.0': '20241016', '3.12.11': '20250818', '3.12.8': '20241211', '3.12.7': '20241008', '3.12.6': '20240814', '3.12.5': '20240726', '3.12.4': '20240726', '3.12.3': '20240415', '3.11.13': '20250603', '3.11.12': '20241211', '3.11.10': '20241008', '3.11.9': '20240726', '3.11.6': '20231002', '3.10.18': '20250818', '3.10.15': '20241008', '3.10.14': '20240726', '3.10.13': '20231002', '3.9.23': '20250818', '3.9.21': '20241211', '3.9.20': '20241008', '3.9.19': '20240726', '3.9.18': '20231002'}
        release_tag = VERSION_TO_RELEASE_TAG_MAP.get(full_version)
        if not release_tag:
            available_versions = list(VERSION_TO_RELEASE_TAG_MAP.keys())
            safe_print(_('❌ No known standalone build for Python version {}.').format(full_version))
            safe_print(_('   Available versions: {}').format(', '.join(sorted(available_versions))))
            raise ValueError(f'No known standalone build for Python version {full_version}. Cannot download.')
        py_ver_plus_tag = f'{full_version}+{release_tag}'
        base_url = f'https://github.com/astral-sh/python-build-standalone/releases/download/{release_tag}'
        archive_name_templates = {'linux': f'cpython-{py_ver_plus_tag}-{py_arch}-unknown-linux-gnu-install_only.tar.gz', 'darwin': f'cpython-{py_ver_plus_tag}-{py_arch}-apple-darwin-install_only.tar.gz', 'windows': f'cpython-{py_ver_plus_tag}-{py_arch}-pc-windows-msvc-shared-install_only.tar.gz'}
        if system == 'macos':
            system = 'darwin'
        archive_name = archive_name_templates.get(system)
        if not archive_name:
            raise OSError(_('Unsupported operating system: {}').format(system))
        url = f'{base_url}/{archive_name}'
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / archive_name
            safe_print(f'📥 Downloading Python {full_version} for {system.title()}...')
            safe_print(_('   - URL: {}').format(url))
            try:
                safe_print(_('   - Attempting download...'))
                urllib.request.urlretrieve(url, archive_path)
                if not archive_path.exists():
                    raise OSError(_('Download failed: file does not exist'))
                file_size = archive_path.stat().st_size
                if file_size < 1000000:
                    raise OSError(_('Downloaded file is too small ({} bytes), likely incomplete or invalid').format(file_size))
                safe_print(_('✅ Downloaded {} bytes').format(file_size))
                safe_print(_('   - Extracting archive...'))
                with tarfile.open(archive_path, 'r:gz') as tar:
                    extract_path = Path(temp_dir) / 'extracted'
                    tar.extractall(extract_path)
                source_python_dir = extract_path / 'python'
                if not source_python_dir.exists():
                    possible_dirs = list(extract_path.glob('**/python'))
                    if possible_dirs:
                        source_python_dir = possible_dirs[0]
                    else:
                        raise OSError(_('Could not find python directory in extracted archive'))
                python_dest = venv_path / '.omnipkg' / 'interpreters' / f'cpython-{full_version}'
                safe_print(_('   - Installing to: {}').format(python_dest))
                python_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source_python_dir, python_dest, dirs_exist_ok=True)
                python_exe_candidates = []
                if system == 'windows':
                    python_exe_candidates = [python_dest / 'python.exe', python_dest / 'Scripts/python.exe']
                else:
                    python_exe_candidates = [python_dest / 'bin/python3', python_dest / 'bin/python', python_dest / f"bin/python{full_version.split('.')[0]}.{full_version.split('.')[1]}"]
                python_exe = None
                for candidate in python_exe_candidates:
                    if candidate.exists():
                        python_exe = candidate
                        break
                if not python_exe:
                    raise OSError(_('Python executable not found in expected locations: {}').format([str(c) for c in python_exe_candidates]))
                if system != 'windows':
                    python_exe.chmod(493)
                    major_minor = '.'.join(full_version.split('.')[:2])
                    versioned_symlink = python_exe.parent / f'python{major_minor}'
                    if not versioned_symlink.exists():
                        try:
                            versioned_symlink.symlink_to(python_exe.name)
                        except OSError as e:
                            safe_print(_('   - Warning: Could not create versioned symlink: {}').format(e))
                safe_print(_('   - Testing installation...'))
                result = subprocess.run([str(python_exe), '--version'], capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    raise OSError(_('Python executable test failed: {}').format(result.stderr))
                safe_print(_('   - ✅ Python version: {}').format(result.stdout.strip()))
                self._install_essential_packages(python_exe)
                safe_print(_('\n✨ New interpreter bootstrapped.'))
                try:
                    safe_print(_('🔧 Forcing rescan to register the new interpreter...'))
                    self._register_all_interpreters(self.venv_path)
                    safe_print(_('   ✅ New interpreter registered successfully.'))
                except Exception as e:
                    safe_print(_('   ⚠️  Interpreter registration failed: {}').format(e))
                    import traceback
                    traceback.print_exc()
                major_minor_version = '.'.join(full_version.split('.')[:2])
                self._set_rebuild_flag_for_version(major_minor_version)
                return python_exe
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    safe_print(_('❌ Python {} not found in python-build-standalone releases.').format(full_version))
                    safe_print(_('   This might be a very new version. Check https://github.com/indygreg/python-build-standalone/releases'))
                    safe_print(_('   for available versions.'))
                raise OSError(_('HTTP error downloading Python: {} - {}').format(e.code, e.reason))
            except Exception as e:
                raise OSError(_('Failed to download or extract Python: {}').format(e))

    def _find_python_interpreters(self) -> Dict[Tuple[int, int], str]:
        """
        Discovers all available Python interpreters on the system.
        Returns a dict mapping (major, minor) version tuples to executable paths.
        """
        if self._python_cache:
            return self._python_cache
        interpreters = {}
        search_patterns = ['python{}.{}', 'python{}{}']
        search_paths = []
        if 'PATH' in os.environ:
            search_paths.extend(os.environ['PATH'].split(os.pathsep))
        common_paths = ['/usr/bin', '/usr/local/bin', '/opt/python*/bin', str(Path.home() / '.pyenv' / 'versions' / '*' / 'bin'), '/usr/local/opt/python@*/bin', 'C:\\Python*', 'C:\\Users\\*\\AppData\\Local\\Programs\\Python\\Python*']
        search_paths.extend(common_paths)
        current_python_dir = Path(sys.executable).parent
        search_paths.append(str(current_python_dir))
        for path_str in search_paths:
            try:
                if '*' in path_str:
                    from glob import glob
                    expanded_paths = glob(path_str)
                    for expanded_path in expanded_paths:
                        if Path(expanded_path).is_dir():
                            search_paths.append(expanded_path)
                    continue
                path = Path(path_str)
                if not path.exists() or not path.is_dir():
                    continue
                for major in range(3, 4):
                    for minor in range(6, 15):
                        for pattern in search_patterns:
                            exe_name = pattern.format(major, minor)
                            exe_path = path / exe_name
                            if platform.system() == 'Windows':
                                exe_path_win = path / f'{exe_name}.exe'
                                if exe_path_win.exists():
                                    exe_path = exe_path_win
                            if exe_path.exists() and exe_path.is_file():
                                version = self._verify_python_version(str(exe_path))
                                if version and version not in interpreters:
                                    interpreters[version] = str(exe_path)
                        for generic_name in ['python', 'python3']:
                            exe_path = path / generic_name
                            if platform.system() == 'Windows':
                                exe_path = path / f'{generic_name}.exe'
                            if exe_path.exists() and exe_path.is_file():
                                version = self._verify_python_version(str(exe_path))
                                if version and version not in interpreters:
                                    interpreters[version] = str(exe_path)
            except (OSError, PermissionError):
                continue
        current_version = sys.version_info[:2]
        interpreters[current_version] = sys.executable
        self._python_cache = interpreters
        return interpreters

    def find_true_venv_root(self) -> Path:
        """
        Helper to find the true venv root by looking for pyvenv.cfg,
        which is reliable across different Python interpreters within the same venv.
        """
        current_path = Path(sys.executable).resolve()
        while current_path != current_path.parent:
            if (current_path / 'pyvenv.cfg').exists():
                return current_path
        return Path(sys.prefix)

        
    def _verify_python_version(self, python_path: str) -> Optional[Tuple[int, int]]:
        """
        Verify that a Python executable works and get its version.
        Returns (major, minor) tuple or None if invalid.
        """
        from .common_utils import safe_print
        try:
            # --- THIS IS THE FIX ---
            # The subprocess is an isolated environment and only knows built-in functions.
            # We must use 'print', not 'safe_print', inside the command string.
            command_string = 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
            
            result = subprocess.run(
                [python_path, '-c', command_string],
                capture_output=True, text=True, timeout=10
            )
            # --- END FIX ---

            if result.returncode == 0:
                version_str = result.stdout.strip()
                major, minor = map(int, version_str.split('.'))
                return (major, minor)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError, OSError):
            pass
        return None

    def get_best_python_for_version_range(self, min_version: Tuple[int, int]=None, max_version: Tuple[int, int]=None, preferred_version: Tuple[int, int]=None) -> Optional[str]:
        """Find the best Python interpreter for a given version range."""
        interpreters = self._find_python_interpreters()
        if not interpreters:
            return None
        candidates = {}
        for version, path in interpreters.items():
            if min_version and version < min_version:
                continue
            if max_version and version > max_version:
                continue
            candidates[version] = path
        if not candidates:
            return None
        if preferred_version and preferred_version in candidates:
            return candidates[preferred_version]
        if self._preferred_version in candidates:
            return candidates[self._preferred_version]
        best_version = max(candidates.keys())
        return candidates[best_version]

    def _get_bin_paths(self) -> List[str]:
        """Gets a list of standard binary paths to search for executables."""
        paths = set()
        paths.add(str(Path(sys.executable).parent))
        for path in ['/usr/local/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin']:
            if Path(path).exists():
                paths.add(path)
        return sorted(list(paths))

    def _get_system_lang_code(self):
        """Helper to get a valid system language code."""
        try:
            lang_code = sys_locale.getlocale()[0]
            if lang_code and '_' in lang_code:
                lang_code = lang_code.split('_')[0]
            return lang_code or 'en'
        except Exception:
            return 'en'

    def _get_sensible_defaults(self) -> Dict:
        """
        Generates sensible default configuration paths based STRICTLY on the
        currently active virtual environment to ensure safety and prevent permission errors.
        """
        safe_print(_('💡 Grounding configuration in the current active environment...'))
        active_python_exe = sys.executable
        safe_print(_(' ✅ Using: {} (Your active interpreter)').format(active_python_exe))
        calculated_paths = self._get_paths_for_interpreter(active_python_exe)
        
        if not calculated_paths:
            safe_print(_(' ⚠️ Falling back to basic path detection within the current environment.'))
            site_packages = str(self._get_actual_current_site_packages())
            calculated_paths = {
                'site_packages_path': site_packages,
                'multiversion_base': str(Path(site_packages) / '.omnipkg_versions'),
                'python_executable': sys.executable
            }
        
        return {
            **calculated_paths,
            'python_interpreters': self.list_available_pythons() or {},
            'preferred_python_version': f'{self._preferred_version[0]}.{self._preferred_version[1]}',
            'builder_script_path': str(Path(__file__).parent / 'package_meta_builder.py'),
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_key_prefix': 'omnipkg:pkg:',
            'install_strategy': 'stable-main',
            'uv_executable': 'uv',
            'paths_to_index': self._get_bin_paths(),
            'language': self._get_system_lang_code(),
            'enable_python_hotswap': True
        }

    def _get_actual_current_site_packages(self) -> Path:
        """
        Gets the ACTUAL site-packages directory for the currently running Python interpreter.
        This is more reliable than calculating it from sys.prefix when hotswapping is involved.
        Cross-platform compatible with special handling for Windows.
        """
        import platform
        is_windows = platform.system() == 'Windows'
        
        try:
            # First, try to use site.getsitepackages() - most reliable method
            site_packages_list = site.getsitepackages()
            if site_packages_list:
                current_python_dir = Path(sys.executable).parent
                
                # Find the site-packages that belongs to our current Python
                for sp in site_packages_list:
                    sp_path = Path(sp)
                    try:
                        # Check if this site-packages is under our Python installation
                        sp_path.relative_to(current_python_dir)
                        # Additional validation: check if it actually contains packages
                        if sp_path.exists():
                            return sp_path
                    except ValueError:
                        continue
                
                # If relative path matching fails, prefer the longest path (most specific)
                # and ensure it exists
                for sp in sorted(site_packages_list, key=len, reverse=True):
                    sp_path = Path(sp)
                    if sp_path.exists():
                        return sp_path
                
                # Fallback to first path (even if it doesn't exist yet)
                return Path(site_packages_list[0])
        except Exception:
            # Continue with fallback logic
            pass
        
        # Fallback: Manual construction based on OS
        python_version = f'python{sys.version_info.major}.{sys.version_info.minor}'
        current_python_path = Path(sys.executable)
        
        # Handle omnipkg's own interpreter management
        if '.omnipkg/interpreters' in str(current_python_path):
            interpreter_root = current_python_path.parent.parent
            if is_windows:
                site_packages_path = interpreter_root / 'Lib' / 'site-packages'
            else:
                site_packages_path = interpreter_root / 'lib' / python_version / 'site-packages'
        else:
            # Standard environment detection
            venv_path = Path(sys.prefix)
            
            if is_windows:
                # Windows has multiple possible locations, try in order of preference
                candidates = [
                    venv_path / 'Lib' / 'site-packages',  # Standard Windows location
                    venv_path / 'lib' / 'site-packages',  # Sometimes used
                    venv_path / 'lib' / python_version / 'site-packages'  # Version-specific
                ]
                
                for candidate in candidates:
                    if candidate.exists():
                        site_packages_path = candidate
                        break
                else:
                    # Default to the most common Windows location
                    site_packages_path = venv_path / 'Lib' / 'site-packages'
            else:
                # Unix-like systems (Linux, macOS)
                site_packages_path = venv_path / 'lib' / python_version / 'site-packages'
        
        return site_packages_path

        
    def _get_paths_for_interpreter(self, python_exe_path: str) -> Optional[Dict[str, str]]:
            """
            Runs an interpreter in a subprocess to ask for its version and calculates
            its site-packages path. This is the only reliable way to get paths for an
            interpreter that isn't the currently running one.
            """
            from .common_utils import safe_print
            try:
                # Step 1: Get version and prefix (this part works fine)
                cmd = [python_exe_path, '-I', '-c', "import sys, json; print(json.dumps({'version': f'{sys.version_info.major}.{sys.version_info.minor}', 'prefix': sys.prefix}))"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
                interp_info = json.loads(result.stdout)

                # Step 2: Ask the interpreter for its site-packages path authoritatively.
                # This improved command is more robust on all platforms, including Windows CI.
                site_packages_cmd = [
                    python_exe_path, '-I', '-c',
                    "import site, json; print(json.dumps(site.getsitepackages() or [sp for sp in sys.path if 'site-packages' in sp]))"
                ]
                sp_result = subprocess.run(site_packages_cmd, capture_output=True, text=True, check=True, timeout=10)
                sp_list = json.loads(sp_result.stdout)

                if not sp_list:
                    raise RuntimeError("Subprocess could not determine site-packages location.")

                # On Windows CI, site.getsitepackages() can return the parent dir.
                # We must find the path that actually contains 'site-packages'.
                site_packages_path = None
                for path in sp_list:
                    if 'site-packages' in path and Path(path).exists():
                        site_packages_path = Path(path)
                        break
                
                if not site_packages_path:
                    raise RuntimeError(f"No valid site-packages directory found in {sp_list}")

                return {
                    'site_packages_path': str(site_packages_path),
                    'multiversion_base': str(site_packages_path / '.omnipkg_versions'),
                    'python_executable': python_exe_path
                }
            except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, KeyError, RuntimeError) as e:
                error_details = f'Error: {e}'
                if isinstance(e, subprocess.CalledProcessError):
                    error_details += f'\nSTDERR:\n{e.stderr}'
                safe_print(f'⚠️  Could not determine paths for interpreter {python_exe_path}: {error_details}')
                return None

    

    def list_available_pythons(self) -> Dict[str, str]:
        """
        List all available Python interpreters with their versions.
        FIXED: Prioritize actual interpreters over symlinks, show hotswapped paths correctly.
        """
        interpreters = self._find_python_interpreters()
        result = {}
        for (major, minor), path in sorted(interpreters.items()):
            version_key = f'{major}.{minor}'
            path_obj = Path(path)
            if version_key in result:
                existing_path = Path(result[version_key])
                current_is_hotswapped = '.omnipkg/interpreters' in str(path_obj)
                existing_is_hotswapped = '.omnipkg/interpreters' in str(existing_path)
                current_is_versioned = f'python{major}.{minor}' in path_obj.name
                existing_is_versioned = f'python{major}.{minor}' in existing_path.name
                if current_is_hotswapped and (not existing_is_hotswapped):
                    result[version_key] = str(path)
                elif existing_is_hotswapped and (not current_is_hotswapped):
                    continue
                elif current_is_versioned and (not existing_is_versioned):
                    result[version_key] = str(path)
                elif existing_is_versioned and (not current_is_versioned):
                    continue
                elif len(str(path)) > len(str(existing_path)):
                    result[version_key] = str(path)
            else:
                result[version_key] = str(path)
        return result

    def _first_time_setup(self, interactive=True) -> Dict:
        """Interactive setup for the first time the tool is run."""
        import os
        self.config_dir.mkdir(parents=True, exist_ok=True)
        defaults = self._get_sensible_defaults()
        final_config = defaults.copy()
        if interactive and (not os.environ.get('CI')):
            safe_print(_("🌍 Welcome to omnipkg! Let's get you configured."))
            safe_print('-' * 60)
            available_pythons = defaults['python_interpreters']
            if len(available_pythons) > 1:
                safe_print(_('🐍 Discovered Python interpreters:'))
                for version, path in available_pythons.items():
                    marker = ' ⭐' if version == defaults['preferred_python_version'] else ''
                    safe_print(_('   Python {}: {}{}').format(version, path, marker))
                safe_print()
            safe_print('Auto-detecting paths for your environment. Press Enter to accept defaults.\n')
            safe_print(_('📦 Choose your default installation strategy:'))
            safe_print(_('   1) stable-main:  Prioritize a stable main environment. (Recommended)'))
            safe_print(_('   2) latest-active: Prioritize having the latest versions active.'))
            strategy = input(_('   Enter choice (1 or 2) [1]: ')).strip() or '1'
            final_config['install_strategy'] = 'stable-main' if strategy == '1' else 'latest-active'
            bubble_path = input(f"Path for version bubbles [{defaults['multiversion_base']}]: ").strip() or defaults['multiversion_base']
            final_config['multiversion_base'] = bubble_path
            python_path = input(_('Python executable path [{}]: ').format(defaults['python_executable'])).strip() or defaults['python_executable']
            final_config['python_executable'] = python_path
            while True:
                host_input = input(_('Redis host [{}]: ').format(defaults['redis_host'])) or defaults['redis_host']
                try:
                    import socket
                    socket.gethostbyname(host_input)
                    final_config['redis_host'] = host_input
                    break
                except socket.gaierror:
                    safe_print(_("   ❌ Error: Invalid hostname '{}'. Please try again.").format(host_input))
            final_config['redis_port'] = int(input(_('Redis port [{}]: ').format(defaults['redis_port'])) or defaults['redis_port'])
            hotswap_choice = input(_('Enable Python interpreter hotswapping? (y/n) [y]: ')).strip().lower()
            final_config['enable_python_hotswap'] = hotswap_choice != 'n'
        try:
            with open(self.config_path, 'r') as f:
                full_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            full_config = {'environments': {}}
        if 'environments' not in full_config:
            full_config['environments'] = {}
        full_config['environments'][self.env_id] = final_config
        with open(self.config_path, 'w') as f:
            json.dump(full_config, f, indent=4)
        if interactive and (not os.environ.get('CI')):
            safe_print(_('\n✅ Configuration saved to {}.').format(self.config_path))
            safe_print(_('   You can edit this file manually later.'))
            safe_print(_('🧠 Initializing omnipkg knowledge base...'))
            safe_print(_('   This may take a moment with large environments (like yours with {} packages).').format(len(defaults.get('installed_packages', []))))
            safe_print(_('   💡 Future startups will be instant!'))
        rebuild_cmd = [str(final_config['python_executable']), '-m', 'omnipkg.cli', 'reset', '-y']
        try:
            if interactive and (not os.environ.get('CI')):
                process = subprocess.Popen(rebuild_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output and ('Processing' in output or 'Building' in output or 'Scanning' in output):
                        safe_print(_('   {}').format(output.strip()))
                process.wait()
                if process.returncode != 0:
                    safe_print(_('   ⚠️  Knowledge base initialization encountered issues but continuing...'))
            else:
                subprocess.run(rebuild_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            if interactive and (not os.environ.get('CI')):
                safe_print(_('   ⚠️  Knowledge base will be built on first command usage instead.'))
            pass
        return final_config

    def _load_or_create_env_config(self, interactive: bool=True) -> Dict:
        """
        Loads the config for the current environment from the global config file.
        If the environment is not registered, triggers the first-time setup for it.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        full_config = {'environments': {}}
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    full_config = json.load(f)
                if 'environments' not in full_config:
                    full_config['environments'] = {}
            except json.JSONDecodeError:
                safe_print(_('⚠️ Warning: Global config file is corrupted. Starting fresh.'))
        if self.env_id in full_config.get('environments', {}):
            return full_config['environments'][self.env_id]
        else:
            if interactive:
                safe_print(_('👋 New environment detected (ID: {}). Starting first-time setup.').format(self.env_id))
            return self._first_time_setup(interactive=interactive)

    def get(self, key, default=None):
        """Get a configuration value, with an optional default."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set a configuration value for the current environment and save."""
        self.config[key] = value
        try:
            with open(self.config_path, 'r') as f:
                full_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            full_config = {'environments': {}}
        if 'environments' not in full_config:
            full_config['environments'] = {}
        full_config['environments'][self.env_id] = self.config
        with open(self.config_path, 'w') as f:
            json.dump(full_config, f, indent=4)

class InterpreterManager:
    """
    Manages multiple Python interpreters within the same environment.
    Provides methods to switch between interpreters and run commands with specific versions.
    """

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.venv_path = Path(sys.prefix)

    def list_available_interpreters(self) -> Dict[str, Path]:
        """Returns a dict of version -> path for all available interpreters."""
        registry_path = self.venv_path / '.omnipkg' / 'interpreters' / 'registry.json'
        if not registry_path.exists():
            return {}
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            interpreters = {}
            for version, path_str in registry.get('interpreters', {}).items():
                path = Path(path_str)
                if path.exists():
                    interpreters[version] = path
            return interpreters
        except:
            return {}

    def run_with_interpreter(self, version: str, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run a command with a specific Python interpreter version."""
        interpreter_path = self.config_manager.get_interpreter_for_version(version)
        if not interpreter_path:
            raise ValueError(_('Python {} interpreter not found').format(version))
        full_cmd = [str(interpreter_path)] + cmd
        return subprocess.run(full_cmd, capture_output=True, text=True)

    def install_package_with_version(self, package: str, python_version: str):
        """Install a package using a specific Python version."""
        interpreter_path = self.config_manager.get_interpreter_for_version(python_version)
        if not interpreter_path:
            raise ValueError(_('Python {} interpreter not found').format(python_version))
        cmd = [str(interpreter_path), '-m', 'pip', 'install', package]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f'Failed to install {package} with Python {python_version}: {result.stderr}')
        return result

class BubbleIsolationManager:

    def __init__(self, config: Dict, parent_omnipkg):
        self.config = config
        self.parent_omnipkg = parent_omnipkg
        self.site_packages = Path(config['site_packages_path'])
        self.multiversion_base = Path(config['multiversion_base'])
        self.file_hash_cache = {}
        self.package_path_registry = {}
        self.registry_lock = FileLock(self.multiversion_base / 'registry.lock')
        self._load_path_registry()
        self.http_session = http_requests.Session()

    def _load_path_registry(self):
        """Load the file path registry from JSON."""
        if not hasattr(self, 'multiversion_base'):
            return
        registry_file = self.multiversion_base / 'package_paths.json'
        if registry_file.exists():
            with self.registry_lock:
                try:
                    with open(registry_file, 'r') as f:
                        self.package_path_registry = json.load(f)
                except Exception:
                    safe_print(_('    ⚠️ Warning: Failed to load path registry, starting fresh.'))
                    self.package_path_registry = {}

    def _save_path_registry(self):
        """Save the file path registry to JSON with atomic write."""
        registry_file = self.multiversion_base / 'package_paths.json'
        with self.registry_lock:
            temp_file = registry_file.with_suffix(f'{registry_file.suffix}.tmp')
            try:
                registry_file.parent.mkdir(parents=True, exist_ok=True)
                with open(temp_file, 'w') as f:
                    json.dump(self.package_path_registry, f, indent=2)
                os.rename(temp_file, registry_file)
            finally:
                if temp_file.exists():
                    temp_file.unlink()

    def _register_file(self, file_path: Path, pkg_name: str, version: str, file_type: str, bubble_path: Path):
        """Register a file in the registry."""
        file_hash = self._get_file_hash(file_path)
        path_str = str(file_path)
        c_name = pkg_name.lower().replace('_', '-')
        if c_name not in self.package_path_registry:
            self.package_path_registry[c_name] = {}
        if version not in self.package_path_registry[c_name]:
            self.package_path_registry[c_name][version] = []
        self.package_path_registry[c_name][version].append({'path': path_str, 'hash': file_hash, 'type': file_type, 'bubble_path': str(bubble_path)})
        self._save_path_registry()

    def create_isolated_bubble(self, package_name: str, target_version: str) -> bool:
        safe_print(_('🫧 Creating isolated bubble for {} v{}').format(package_name, target_version))
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            if not self._install_exact_version_tree(package_name, target_version, temp_path):
                return False
            installed_tree = self._analyze_installed_tree(temp_path)
            bubble_path = self.multiversion_base / f'{package_name}-{target_version}'
            if bubble_path.exists():
                shutil.rmtree(bubble_path)
            return self._create_deduplicated_bubble(installed_tree, bubble_path, temp_path)

    def _install_exact_version_tree(self, package_name: str, version: str, target_path: Path) -> bool:
        try:
            historical_deps = self._get_historical_dependencies(package_name, version)
            install_specs = ['{}=={}'.format(package_name, version)] + historical_deps
            cmd = [self.config['python_executable'], '-m', 'pip', 'install', '--target', str(target_path)] + install_specs
            safe_print(_('    📦 Installing full dependency tree to temporary location...'))
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                safe_print(_('    ❌ Failed to install exact version tree: {}').format(result.stderr))
                return False
            return True
        except Exception as e:
            safe_print(_('    ❌ Unexpected error during installation: {}').format(e))
            return False

    def _get_historical_dependencies(self, package_name: str, version: str) -> List[str]:
        safe_print(_('    -> Trying strategy 1: pip dry-run...'))
        deps = self._try_pip_dry_run(package_name, version)
        if deps is not None:
            safe_print(_('    ✅ Success: Dependencies resolved via pip dry-run.'))
            return deps
        safe_print(_('    -> Trying strategy 2: PyPI API...'))
        deps = self._try_pypi_api(package_name, version)
        if deps is not None:
            safe_print(_('    ✅ Success: Dependencies resolved via PyPI API.'))
            return deps
        safe_print(_('    -> Trying strategy 3: pip show fallback...'))
        deps = self._try_pip_show_fallback(package_name, version)
        if deps is not None:
            safe_print(_('    ✅ Success: Dependencies resolved from existing installation.'))
            return deps
        safe_print(_('    ⚠️ All dependency resolution strategies failed for {}=={}.').format(package_name, version))
        safe_print(_('    ℹ️  Proceeding with full temporary installation to build bubble.'))
        return []

    def _try_pip_dry_run(self, package_name: str, version: str) -> Optional[List[str]]:
        req_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(_('{}=={}\n').format(package_name, version))
                req_file = f.name
            cmd = [self.config['python_executable'], '-m', 'pip', 'install', '--dry-run', '--report', '-', '-r', req_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                return None
            if not result.stdout or not result.stdout.strip():
                return None
            stdout_stripped = result.stdout.strip()
            if not (stdout_stripped.startswith('{') or stdout_stripped.startswith('[')):
                return None
            try:
                report = json.loads(result.stdout)
            except json.JSONDecodeError:
                return None
            if not isinstance(report, dict) or 'install' not in report:
                return None
            deps = []
            for item in report.get('install', []):
                try:
                    if not isinstance(item, dict) or 'metadata' not in item:
                        continue
                    metadata = item['metadata']
                    item_name = metadata.get('name')
                    item_version = metadata.get('version')
                    if item_name and item_version and (item_name.lower() != package_name.lower()):
                        deps.append('{}=={}'.format(item_name, item_version))
                except Exception:
                    continue
            return deps
        except Exception:
            return None
        finally:
            if req_file and Path(req_file).exists():
                try:
                    Path(req_file).unlink()
                except Exception:
                    pass

    def _try_pypi_api(self, package_name: str, version: str) -> Optional[List[str]]:
        try:
            import requests
        except ImportError:
            safe_print(_("    ⚠️  'requests' package not found. Skipping PyPI API strategy."))
            return None
        try:
            clean_version = version.split('+')[0]
            url = f'https://pypi.org/pypi/{package_name}/{clean_version}/json'
            headers = {'User-Agent': 'omnipkg-package-manager/1.0', 'Accept': 'application/json'}
            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code == 404:
                if clean_version != version:
                    url = f'https://pypi.org/pypi/{package_name}/{version}/json'
                    response = requests.get(url, timeout=10, headers=headers)
            if response.status_code != 200:
                return None
            if not response.text.strip():
                return None
            try:
                pkg_data = response.json()
            except json.JSONDecodeError:
                return None
            if not isinstance(pkg_data, dict):
                return None
            requires_dist = pkg_data.get('info', {}).get('requires_dist')
            if not requires_dist:
                return []
            dependencies = []
            for req in requires_dist:
                if not req or not isinstance(req, str):
                    continue
                if ';' in req:
                    continue
                req = req.strip()
                match = re.match('^([a-zA-Z0-9\\-_.]+)([<>=!]+.*)?', req)
                if match:
                    dep_name = match.group(1)
                    version_spec = match.group(2) or ''
                    dependencies.append(_('{}{}').format(dep_name, version_spec))
            return dependencies
        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None

    def _try_pip_show_fallback(self, package_name: str, version: str) -> Optional[List[str]]:
        try:
            cmd = [self.config['python_executable'], '-m', 'pip', 'show', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return None
            for line in result.stdout.split('\n'):
                if line.startswith('Requires:'):
                    requires = line.replace('Requires:', '').strip()
                    if requires and requires != '':
                        deps = [dep.strip() for dep in requires.split(',')]
                        return [dep for dep in deps if dep]
                    else:
                        return []
            return []
        except Exception:
            return None

    def _classify_package_type(self, files: List[Path]) -> str:
        has_python = any((f.suffix in ['.py', '.pyc'] for f in files))
        has_native = any((f.suffix in ['.so', '.pyd', '.dll'] for f in files))
        if has_native and has_python:
            return 'mixed'
        elif has_native:
            return 'native'
        else:
            return 'pure_python'

    def _find_existing_c_extension(self, file_hash: str) -> Optional[str]:
        """Disabled: C extensions are copied, not symlinked."""
        return None

    def _analyze_installed_tree(self, temp_path: Path) -> Dict[str, Dict]:
        """
        Analyzes the temporary installation, now EXPLICITLY finding executables
        and summarizing file registry warnings instead of printing each one.
        """
        installed = {}
        unregistered_file_count = 0
        for dist_info in temp_path.glob('*.dist-info'):
            try:
                dist = importlib.metadata.Distribution.at(dist_info)
                if not dist:
                    continue
                pkg_files = []
                if dist.files:
                    for file_entry in dist.files:
                        if file_entry.parts and file_entry.parts[0] == 'bin':
                            continue
                        abs_path = Path(dist_info.parent) / file_entry
                        if abs_path.exists():
                            pkg_files.append(abs_path)
                executables = []
                entry_points = dist.entry_points
                console_scripts = [ep for ep in entry_points if ep.group == 'console_scripts']
                if console_scripts:
                    temp_bin_path = temp_path / 'bin'
                    if temp_bin_path.is_dir():
                        for script in console_scripts:
                            exe_path = temp_bin_path / script.name
                            if exe_path.is_file():
                                executables.append(exe_path)
                pkg_name = dist.metadata['Name'].lower().replace('_', '-')
                version = dist.metadata['Version']
                installed[dist.metadata['Name']] = {'version': version, 'files': [p for p in pkg_files if p.exists()], 'executables': executables, 'type': self._classify_package_type(pkg_files)}
                redis_key = _('{}bubble:{}:{}:file_paths').format(self.parent_omnipkg.redis_key_prefix, pkg_name, version)
                existing_paths = set(self.parent_omnipkg.cache_client.smembers(redis_key)) if self.parent_omnipkg.cache_client.exists(redis_key) else set()
                all_package_files_for_check = pkg_files + executables
                for file_path in all_package_files_for_check:
                    if str(file_path) not in existing_paths:
                        unregistered_file_count += 1
            except Exception as e:
                safe_print(_('    ⚠️  Could not analyze {}: {}').format(dist_info.name, e))
        if unregistered_file_count > 0:
            safe_print(_('    ⚠️  Found {} files not in registry. They will be registered during bubble creation.').format(unregistered_file_count))
        return installed

    def _is_binary(self, file_path: Path) -> bool:
        """
        Robustly checks if a file is a binary executable, excluding C extensions.
        Uses multiple detection strategies with intelligent fallbacks.
        """
        if file_path.suffix in {'.so', '.pyd', '.dylib'}:
            return False
        if HAS_MAGIC:
            try:
                mime = magic.Magic(mime=True)
                file_type = mime.from_file(str(file_path))
                executable_types = {'application/x-executable', 'application/x-sharedlib', 'application/x-pie-executable', 'application/x-mach-binary', 'application/x-ms-dos-executable'}
                return any((t in file_type for t in executable_types)) or file_path.suffix in {'.dll', '.exe'}
            except Exception:
                pass
        if not getattr(self, '_magic_warning_shown', False):
            safe_print(_("⚠️  Warning: 'python-magic' not installed. Using enhanced binary detection."))
            self._magic_warning_shown = True
        try:
            if file_path.stat().st_mode & 73:
                if file_path.is_file() and file_path.stat().st_size > 0:
                    result = self._detect_binary_by_header(file_path)
                    if result:
                        return True
        except (OSError, PermissionError):
            pass
        if file_path.suffix.lower() in {'.exe', '.dll', '.bat', '.cmd', '.ps1'}:
            return True
        return self._is_likely_executable_name(file_path)

    def _detect_binary_by_header(self, file_path: Path) -> bool:
        """
        Detect binary executables by reading file headers/magic numbers.
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
            if len(header) < 4:
                return False
            if header.startswith(b'\x7fELF'):
                return True
            if header.startswith(b'MZ'):
                return True
            magic_numbers = [b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe']
            for magic in magic_numbers:
                if header.startswith(magic):
                    return True
            return False
        except (OSError, IOError, PermissionError):
            return False

    def _is_likely_executable_name(self, file_path: Path) -> bool:
        """
        Additional heuristic: check if filename suggests it's an executable.
        Used as a final fallback for edge cases.
        """
        name = file_path.name.lower()
        common_executables = {'python', 'python3', 'pip', 'pip3', 'node', 'npm', 'yarn', 'git', 'docker', 'kubectl', 'terraform', 'ansible', 'uv', 'poetry', 'pipenv', 'black', 'flake8', 'mypy', 'gcc', 'clang', 'make', 'cmake', 'ninja', 'curl', 'wget', 'ssh', 'scp', 'rsync'}
        if name in common_executables:
            return True
        import re
        if re.match('^[a-z][a-z0-9]*[0-9]+(?:\\.[0-9]+)*$', name):
            base_name = re.sub('[0-9]+(?:\\.[0-9]+)*$', '', name)
            return base_name in common_executables
        return False

    def _create_deduplicated_bubble(self, installed_tree: Dict, bubble_path: Path, temp_install_path: Path) -> bool:
        """
        Enhanced Version: Fixes flask-login and similar packages with missing submodules.
        
        Key improvements:
        1. Better detection of package internal structure
        2. Conservative approach for packages with submodules
        3. Enhanced failsafe scanning
        4. Special handling for namespace packages
        """
        safe_print(_('    🧹 Creating deduplicated bubble at {}').format(bubble_path))
        bubble_path.mkdir(parents=True, exist_ok=True)
        main_env_hashes = self._get_or_build_main_env_hash_index()
        stats = {'total_files': 0, 'copied_files': 0, 'deduplicated_files': 0, 'c_extensions': [], 'binaries': [], 'python_files': 0, 'package_modules': {}, 'submodules_found': 0}
        c_ext_packages = {pkg_name for pkg_name, info in installed_tree.items() if info.get('type') in ['native', 'mixed']}
        binary_packages = {pkg_name for pkg_name, info in installed_tree.items() if info.get('type') == 'binary'}
        complex_packages = set()
        for pkg_name, pkg_info in installed_tree.items():
            pkg_files = pkg_info.get('files', [])
            py_files_in_subdirs = [f for f in pkg_files if f.suffix == '.py' and len(f.parts) > 2 and (f.parts[-2] != '__pycache__')]
            if len(py_files_in_subdirs) > 1:
                complex_packages.add(pkg_name)
                stats['package_modules'][pkg_name] = len(py_files_in_subdirs)
        if c_ext_packages:
            safe_print(_('    🔬 Found C-extension packages: {}').format(', '.join(c_ext_packages)))
        if binary_packages:
            safe_print(_('    ⚙️  Found binary packages: {}').format(', '.join(binary_packages)))
        if complex_packages:
            safe_print(_('    📦 Found complex packages with submodules: {}').format(', '.join(complex_packages)))
        processed_files = set()
        for pkg_name, pkg_info in installed_tree.items():
            if pkg_name in c_ext_packages:
                should_deduplicate_this_package = False
                safe_print(_('    🔬 {}: C-extension - copying all files').format(pkg_name))
            elif pkg_name in binary_packages:
                should_deduplicate_this_package = False
                safe_print(_('    ⚙️  {}: Binary package - copying all files').format(pkg_name))
            elif pkg_name in complex_packages:
                should_deduplicate_this_package = False
                safe_print(_('    📦 {}: Complex package ({} submodules) - copying all files').format(pkg_name, stats['package_modules'][pkg_name]))
            else:
                should_deduplicate_this_package = True
            pkg_copied = 0
            pkg_deduplicated = 0
            for source_path in pkg_info.get('files', []):
                if not source_path.is_file():
                    continue
                processed_files.add(source_path)
                stats['total_files'] += 1
                is_c_ext = source_path.suffix in {'.so', '.pyd'}
                is_binary = self._is_binary(source_path)
                is_python_module = source_path.suffix == '.py'
                if is_c_ext:
                    stats['c_extensions'].append(source_path.name)
                elif is_binary:
                    stats['binaries'].append(source_path.name)
                elif is_python_module:
                    stats['python_files'] += 1
                should_copy = True
                if should_deduplicate_this_package:
                    if is_python_module and '/__pycache__/' not in str(source_path):
                        should_copy = True
                    else:
                        try:
                            file_hash = self._get_file_hash(source_path)
                            if file_hash in main_env_hashes:
                                should_copy = False
                        except (IOError, OSError):
                            pass
                if should_copy:
                    stats['copied_files'] += 1
                    pkg_copied += 1
                    self._copy_file_to_bubble(source_path, bubble_path, temp_install_path, is_binary or is_c_ext)
                else:
                    stats['deduplicated_files'] += 1
                    pkg_deduplicated += 1
            if pkg_copied > 0 or pkg_deduplicated > 0:
                safe_print(_('    📄 {}: copied {}, deduplicated {}').format(pkg_name, pkg_copied, pkg_deduplicated))
        all_temp_files = {p for p in temp_install_path.rglob('*') if p.is_file()}
        missed_files = all_temp_files - processed_files
        if missed_files:
            safe_print(_('    ⚠️  Found {} file(s) not listed in package metadata.').format(len(missed_files)))
            missed_by_package = {}
            for source_path in missed_files:
                owner_pkg = self._find_owner_package(source_path, temp_install_path, installed_tree)
                if owner_pkg not in missed_by_package:
                    missed_by_package[owner_pkg] = []
                missed_by_package[owner_pkg].append(source_path)
            for owner_pkg, files in missed_by_package.items():
                safe_print(_('    📦 {}: found {} additional files').format(owner_pkg, len(files)))
                for source_path in files:
                    stats['total_files'] += 1
                    is_python_module = source_path.suffix == '.py'
                    is_init_file = source_path.name == '__init__.py'
                    should_deduplicate = owner_pkg not in c_ext_packages and owner_pkg not in binary_packages and (owner_pkg not in complex_packages) and (not self._is_binary(source_path)) and (source_path.suffix not in {'.so', '.pyd'}) and (not is_init_file) and (not is_python_module)
                    should_copy = True
                    if should_deduplicate:
                        try:
                            file_hash = self._get_file_hash(source_path)
                            if file_hash in main_env_hashes:
                                should_copy = False
                        except (IOError, OSError):
                            pass
                    is_c_ext = source_path.suffix in {'.so', '.pyd'}
                    is_binary = self._is_binary(source_path)
                    if is_c_ext:
                        stats['c_extensions'].append(source_path.name)
                    elif is_binary:
                        stats['binaries'].append(source_path.name)
                    else:
                        stats['python_files'] += 1
                    if should_copy:
                        stats['copied_files'] += 1
                        self._copy_file_to_bubble(source_path, bubble_path, temp_install_path, is_binary or is_c_ext)
                    else:
                        stats['deduplicated_files'] += 1
        self._verify_package_integrity(bubble_path, installed_tree, temp_install_path)
        efficiency = stats['deduplicated_files'] / stats['total_files'] * 100 if stats['total_files'] > 0 else 0
        safe_print(_('    ✅ Bubble created: {} files copied, {} deduplicated.').format(stats['copied_files'], stats['deduplicated_files']))
        safe_print(_('    📊 Space efficiency: {}% saved.').format(efficiency))
        if stats['package_modules']:
            safe_print(_('    📦 Complex packages preserved: {} packages with submodules').format(len(stats['package_modules'])))
        self._create_bubble_manifest(bubble_path, installed_tree, stats)
        return True

    def _verify_package_integrity(self, bubble_path: Path, installed_tree: Dict, temp_install_path: Path) -> None:
        """
        Verify that critical package files are present in the bubble.
        This catches issues like missing flask_login.config modules.
        """
        safe_print(_('    🔍 Verifying package integrity...'))
        for pkg_name, pkg_info in installed_tree.items():
            pkg_files = pkg_info.get('files', [])
            package_dirs = set()
            for file_path in pkg_files:
                if file_path.name == '__init__.py':
                    package_dirs.add(file_path.parent)
            for pkg_dir in package_dirs:
                relative_pkg_path = pkg_dir.relative_to(temp_install_path)
                bubble_pkg_path = bubble_path / relative_pkg_path
                if not bubble_pkg_path.exists():
                    safe_print(_('    ⚠️  Missing package directory: {}').format(relative_pkg_path))
                    continue
                expected_py_files = [f for f in pkg_files if f.suffix == '.py' and f.parent == pkg_dir]
                for py_file in expected_py_files:
                    relative_py_path = py_file.relative_to(temp_install_path)
                    bubble_py_path = bubble_path / relative_py_path
                    if not bubble_py_path.exists():
                        safe_print(_('    🚨 CRITICAL: Missing Python module: {}').format(relative_py_path))
                        self._copy_file_to_bubble(py_file, bubble_path, temp_install_path, False)
                        safe_print(_('    🔧 Fixed: Copied missing module {}').format(relative_py_path))

    def _find_owner_package(self, file_path: Path, temp_install_path: Path, installed_tree: Dict) -> Optional[str]:
        """
        Helper to find which package a file belongs to, now supporting .egg-info.
        """
        try:
            for parent in file_path.parents:
                if parent.name.endswith(('.dist-info', '.egg-info')):
                    pkg_name = parent.name.split('-')[0]
                    return pkg_name.lower().replace('_', '-')
        except Exception:
            pass
        return None

    def _copy_file_to_bubble(self, source_path: Path, bubble_path: Path, temp_install_path: Path, make_executable: bool=False):
        """Helper method to copy a file to the bubble with proper error handling."""
        try:
            rel_path = source_path.relative_to(temp_install_path)
            dest_path = bubble_path / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            if make_executable:
                os.chmod(dest_path, 493)
        except Exception as e:
            safe_print(_('    ⚠️ Warning: Failed to copy {}: {}').format(source_path.name, e))

    def _get_or_build_main_env_hash_index(self) -> Set[str]:
        """
        Builds or loads a FAST hash index using multiple strategies:
        1. Isolated subprocess for authoritative file lists (preferred)
        2. Package metadata approach (fallback)
        3. Full filesystem scan (last resort)
        
        This method prevents cross-version contamination and provides the most
        accurate representation of the main environment state.
        """
        if not self.parent_omnipkg.cache_client:
            self.parent_omnipkg._connect_cache()
            if not self.parent_omnipkg.cache_client:
                return set()
        redis_key = f'{self.parent_omnipkg.redis_key_prefix}main_env:file_hashes'
        if self.parent_omnipkg.cache_client.exists(redis_key):
            safe_print(_('    ⚡️ Loading main environment hash index from cache...'))
            cached_hashes = set(self.parent_omnipkg.cache_client.sscan_iter(redis_key))
            safe_print(_('    📈 Loaded {} file hashes from Redis.').format(len(cached_hashes)))
            return cached_hashes
        safe_print(_('    🔍 Building main environment hash index...'))
        hash_set = set()
        try:
            safe_print(_('    📦 Attempting fast indexing via isolated subprocess...'))
            installed_packages = self.parent_omnipkg.get_installed_packages(live=True)
            package_names = list(installed_packages.keys())
            if not package_names:
                safe_print(_('    ✅ No packages found in the main environment to index.'))
                return hash_set
            safe_print(f"    -> Querying {self.parent_omnipkg.config.get('python_executable')} for file lists of {len(package_names)} packages...")
            package_files_map = self.parent_omnipkg._get_file_list_for_packages_live(package_names)
            files_to_hash = [Path(p) for file_list in package_files_map.values() for p in file_list]
            files_iterator = tqdm(files_to_hash, desc='    📦 Hashing files', unit='file') if HAS_TQDM else files_to_hash
            for abs_path in files_iterator:
                try:
                    if abs_path.is_file() and abs_path.suffix not in {'.pyc', '.pyo'} and ('__pycache__' not in abs_path.parts):
                        hash_set.add(self._get_file_hash(abs_path))
                except (IOError, OSError):
                    continue
            safe_print(_('    ✅ Successfully indexed {} files from {} packages via subprocess.').format(len(files_to_hash), len(package_names)))
        except Exception as e:
            safe_print(_('    ⚠️ Isolated subprocess indexing failed ({}), trying metadata approach...').format(e))
            try:
                safe_print(_('    📦 Attempting indexing via package metadata...'))
                successful_packages = 0
                failed_packages = []
                package_iterator = tqdm(installed_packages.keys(), desc='    📦 Indexing via metadata', unit='pkg') if HAS_TQDM else installed_packages.keys()
                for pkg_name in package_iterator:
                    try:
                        dist = importlib.metadata.distribution(pkg_name)
                        if dist.files:
                            pkg_hashes = 0
                            for file_path in dist.files:
                                try:
                                    abs_path = dist.locate_file(file_path)
                                    if abs_path and abs_path.is_file() and (abs_path.suffix not in {'.pyc', '.pyo'}) and ('__pycache__' not in abs_path.parts):
                                        hash_set.add(self._get_file_hash(abs_path))
                                        pkg_hashes += 1
                                except (IOError, OSError, AttributeError):
                                    continue
                            if pkg_hashes > 0:
                                successful_packages += 1
                            else:
                                failed_packages.append(pkg_name)
                        else:
                            failed_packages.append(pkg_name)
                    except Exception:
                        failed_packages.append(pkg_name)
                safe_print(_('    ✅ Successfully indexed {} packages via metadata').format(successful_packages))
                if failed_packages:
                    safe_print(_('    🔄 Fallback scan for {} packages: {}{}').format(len(failed_packages), ', '.join(failed_packages[:3]), '...' if len(failed_packages) > 3 else ''))
                    potential_files = []
                    for file_path in self.site_packages.rglob('*'):
                        if file_path.is_file() and file_path.suffix not in {'.pyc', '.pyo'} and ('__pycache__' not in file_path.parts):
                            file_str = str(file_path).lower()
                            if any((pkg.lower().replace('-', '_') in file_str or pkg.lower().replace('_', '-') in file_str for pkg in failed_packages)):
                                potential_files.append(file_path)
                    files_iterator = tqdm(potential_files, desc='    📦 Fallback scan', unit='file') if HAS_TQDM else potential_files
                    for file_path in files_iterator:
                        try:
                            hash_set.add(self._get_file_hash(file_path))
                        except (IOError, OSError):
                            continue
            except Exception as e2:
                safe_print(_('    ⚠️ Metadata approach also failed ({}), falling back to full filesystem scan...').format(e2))
                files_to_process = [p for p in self.site_packages.rglob('*') if p.is_file() and p.suffix not in {'.pyc', '.pyo'} and ('__pycache__' not in p.parts)]
                files_to_process_iterator = tqdm(files_to_process, desc='    📦 Full scan', unit='file') if HAS_TQDM else files_to_process
                for file_path in files_to_process_iterator:
                    try:
                        hash_set.add(self._get_file_hash(file_path))
                    except (IOError, OSError):
                        continue
        safe_print(_('    💾 Saving {} file hashes to Redis cache...').format(len(hash_set)))
        if hash_set:
            with self.parent_omnipkg.cache_client.pipeline() as pipe:
                chunk_size = 5000
                hash_list = list(hash_set)
                for i in range(0, len(hash_list), chunk_size):
                    chunk = hash_list[i:i + chunk_size]
                    pipe.sadd(redis_key, *chunk)
                pipe.execute()
        safe_print(_('    📈 Indexed {} files from main environment.').format(len(hash_set)))
        return hash_set

    def _register_bubble_location(self, bubble_path: Path, installed_tree: Dict, stats: dict):
        """
        Register bubble location and summary statistics in a single batch operation.
        """
        registry_key = '{}bubble_locations'.format(self.parent_omnipkg.redis_key_prefix)
        bubble_data = {'path': str(bubble_path), 'python_version': '{}.{}'.format(sys.version_info.major, sys.version_info.minor), 'created_at': datetime.now().isoformat(), 'packages': {pkg: info['version'] for pkg, info in installed_tree.items()}, 'stats': {'total_files': stats['total_files'], 'copied_files': stats['copied_files'], 'deduplicated_files': stats['deduplicated_files'], 'c_extensions_count': len(stats['c_extensions']), 'binaries_count': len(stats['binaries']), 'python_files': stats['python_files']}}
        bubble_id = bubble_path.name
        self.parent_omnipkg.cache_client.hset(registry_key, bubble_id, json.dumps(bubble_data))
        safe_print(_('    📝 Registered bubble location and stats for {} packages.').format(len(installed_tree)))

    def _get_file_hash(self, file_path: Path) -> str:
        path_str = str(file_path)
        if path_str in self.file_hash_cache:
            return self.file_hash_cache[path_str]
        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while (chunk := f.read(8192)):
                h.update(chunk)
        file_hash = h.hexdigest()
        self.file_hash_cache[path_str] = file_hash
        return file_hash

    def _create_bubble_manifest(self, bubble_path: Path, installed_tree: Dict, stats: dict):
        """
        Creates both a local manifest file and registers the bubble in Redis.
        This replaces the old _create_bubble_manifest with integrated registry functionality.
        """
        total_size = sum((f.stat().st_size for f in bubble_path.rglob('*') if f.is_file()))
        size_mb = round(total_size / (1024 * 1024), 2)
        symlink_origins = set()
        for item in bubble_path.rglob('*.so'):
            if item.is_symlink():
                try:
                    real_path = item.resolve()
                    symlink_origins.add(str(real_path.parent))
                except Exception:
                    continue
        stats['symlink_origins'] = sorted(list(symlink_origins), key=len, reverse=True)
        manifest_data = {'created_at': datetime.now().isoformat(), 'python_version': _('{}.{}').format(sys.version_info.major, sys.version_info.minor), 'omnipkg_version': '1.0.0', 'packages': {name: {'version': info['version'], 'type': info['type'], 'install_reason': info.get('install_reason', 'dependency')} for name, info in installed_tree.items()}, 'stats': {'bubble_size_mb': size_mb, 'package_count': len(installed_tree), 'total_files': stats['total_files'], 'copied_files': stats['copied_files'], 'deduplicated_files': stats['deduplicated_files'], 'deduplication_efficiency_percent': round(stats['deduplicated_files'] / stats['total_files'] * 100 if stats['total_files'] > 0 else 0, 1), 'c_extensions_count': len(stats['c_extensions']), 'binaries_count': len(stats['binaries']), 'python_files': stats['python_files'], 'symlink_origins': stats['symlink_origins']}, 'file_types': {'c_extensions': stats['c_extensions'][:10], 'binaries': stats['binaries'][:10], 'has_more_c_extensions': len(stats['c_extensions']) > 10, 'has_more_binaries': len(stats['binaries']) > 10}}
        manifest_path = bubble_path / '.omnipkg_manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        registry_key = _('{}bubble_locations').format(self.parent_omnipkg.redis_key_prefix)
        bubble_id = bubble_path.name
        redis_bubble_data = {**manifest_data, 'path': str(bubble_path), 'manifest_path': str(manifest_path), 'bubble_id': bubble_id}
        try:
            with self.parent_omnipkg.cache_client.pipeline() as pipe:
                pipe.hset(registry_key, bubble_id, json.dumps(redis_bubble_data))
                for pkg_name, pkg_info in installed_tree.items():
                    canonical_pkg_name = canonicalize_name(pkg_name)
                    main_pkg_key = f'{self.parent_omnipkg.redis_key_prefix}{canonical_pkg_name}'
                    version_str = pkg_info['version']
                    version_specific_key = f'{main_pkg_key}:{version_str}'
                    pipe.hset(main_pkg_key, f'bubble_version:{version_str}', 'true')
                    pipe.hset(version_specific_key, 'path', str(bubble_path))
                    pipe.sadd(_('{}:installed_versions').format(main_pkg_key), version_str)
                    index_key = f'{self.parent_omnipkg.redis_env_prefix}index'
                    pipe.sadd(index_key, canonical_pkg_name)
                for pkg_name, pkg_info in installed_tree.items():
                    pkg_version_key = '{}=={}'.format(canonicalize_name(pkg_name), pkg_info['version'])
                    pipe.hset(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix), pkg_version_key, bubble_id)
                size_category = 'small' if size_mb < 10 else 'medium' if size_mb < 100 else 'large'
                pipe.sadd(_('{}bubbles_by_size:{}').format(self.parent_omnipkg.redis_key_prefix, size_category), bubble_id)
                pipe.execute()
            safe_print(_('    📝 Created manifest and registered bubble for {} packages ({} MB).').format(len(installed_tree), size_mb))
        except Exception as e:
            safe_print(_('    ⚠️ Warning: Failed to register bubble in Redis: {}').format(e))
            import traceback
            traceback.print_exc()
            safe_print(_('    📝 Local manifest created at {}').format(manifest_path))

    def get_bubble_info(self, bubble_id: str) -> dict:
        """
        Retrieves comprehensive bubble information from Redis registry.
        """
        registry_key = _('{}bubble_locations').format(self.parent_omnipkg.redis_key_prefix)
        bubble_data = self.parent_omnipkg.cache_client.hget(registry_key, bubble_id)
        if bubble_data:
            return json.loads(bubble_data)
        return {}

    def find_bubbles_for_package(self, pkg_name: str, version: str=None) -> list:
        """
        Finds all bubbles containing a specific package.
        """
        if version:
            pkg_key = '{}=={}'.format(pkg_name, version)
            bubble_id = self.parent_omnipkg.cache_client.hget(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix), pkg_key)
            return [bubble_id] if bubble_id else []
        else:
            pattern = f'{pkg_name}==*'
            matching_keys = []
            for key in self.parent_omnipkg.cache_client.hkeys(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix)):
                if key.startswith(f'{pkg_name}=='):
                    bubble_id = self.parent_omnipkg.cache_client.hget(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix), key)
                    matching_keys.append(bubble_id)
            return matching_keys

    def cleanup_old_bubbles(self, keep_latest: int=3, size_threshold_mb: float=500):
        """
        Cleanup old bubbles based on size and age, keeping most recent ones.
        """
        registry_key = _('{}bubble_locations').format(self.parent_omnipkg.redis_key_prefix)
        all_bubbles = {}
        for bubble_id, bubble_data_str in self.parent_omnipkg.cache_client.hgetall(registry_key).items():
            bubble_data = json.loads(bubble_data_str)
            all_bubbles[bubble_id] = bubble_data
        by_package = {}
        for bubble_id, data in all_bubbles.items():
            pkg_name = bubble_id.split('-')[0]
            if pkg_name not in by_package:
                by_package[pkg_name] = []
            by_package[pkg_name].append((bubble_id, data))
        bubbles_to_remove = []
        total_size_freed = 0
        for pkg_name, bubbles in by_package.items():
            bubbles.sort(key=lambda x: x[1]['created_at'], reverse=True)
            for bubble_id, data in bubbles[keep_latest:]:
                bubbles_to_remove.append((bubble_id, data))
                total_size_freed += data['stats']['bubble_size_mb']
        for bubble_id, data in all_bubbles.items():
            if (bubble_id, data) not in bubbles_to_remove:
                if data['stats']['bubble_size_mb'] > size_threshold_mb:
                    bubbles_to_remove.append((bubble_id, data))
                    total_size_freed += data['stats']['bubble_size_mb']
        if bubbles_to_remove:
            safe_print(_('    🧹 Cleaning up {} old bubbles ({} MB)...').format(len(bubbles_to_remove), total_size_freed))
            with self.parent_omnipkg.cache_client.pipeline() as pipe:
                for bubble_id, data in bubbles_to_remove:
                    pipe.hdel(registry_key, bubble_id)
                    for pkg_name, pkg_info in data.get('packages', {}).items():
                        pkg_key = '{}=={}'.format(pkg_name, pkg_info['version'])
                        pipe.hdel(_('{}pkg_to_bubble').format(self.parent_omnipkg.redis_key_prefix), pkg_key)
                    size_mb = data['stats']['bubble_size_mb']
                    size_category = 'small' if size_mb < 10 else 'medium' if size_mb < 100 else 'large'
                    pipe.srem(_('{}bubbles_by_size:{}').format(self.parent_omnipkg.redis_key_prefix, size_category), bubble_id)
                    bubble_path = Path(data['path'])
                    if bubble_path.exists():
                        shutil.rmtree(bubble_path, ignore_errors=True)
                pipe.execute()
            safe_print(_('    ✅ Freed {} MB of storage.').format(total_size_freed))
        else:
            safe_print(_('    ✅ No bubbles need cleanup.'))

class ImportHookManager:

    def __init__(self, multiversion_base: str, config: Dict, cache_client=None):
        self.multiversion_base = Path(multiversion_base)
        self.version_map = {}
        self.active_versions = {}
        self.hook_installed = False
        self.cache_client = cache_client
        self.config = config
        self.http_session = http_requests.Session()

    def load_version_map(self):
        if not self.multiversion_base.exists():
            return
        for version_dir in self.multiversion_base.iterdir():
            if version_dir.is_dir() and '-' in version_dir.name:
                pkg_name, version = version_dir.name.rsplit('-', 1)
                if pkg_name not in self.version_map:
                    self.version_map[pkg_name] = {}
                self.version_map[pkg_name][version] = str(version_dir)

    def refresh_bubble_map(self, pkg_name: str, version: str, bubble_path: str):
        """
        Immediately adds a newly created bubble to the internal version map
        to prevent race conditions during validation.
        """
        pkg_name = pkg_name.lower().replace('_', '-')
        if pkg_name not in self.version_map:
            self.version_map[pkg_name] = {}
        self.version_map[pkg_name][version] = bubble_path
        safe_print(_('    🧠 HookManager now aware of new bubble: {}=={}').format(pkg_name, version))

    def remove_bubble_from_tracking(self, package_name: str, version: str):
        """
        Removes a bubble from the internal version map tracking.
        Used when cleaning up redundant bubbles.
        """
        pkg_name = package_name.lower().replace('_', '-')
        if pkg_name in self.version_map and version in self.version_map[pkg_name]:
            del self.version_map[pkg_name][version]
            safe_print(f'    ✅ Removed bubble tracking for {pkg_name}=={version}')
            if not self.version_map[pkg_name]:
                del self.version_map[pkg_name]
                safe_print(f'    ✅ Removed package {pkg_name} from version map (no more bubbles)')
        if pkg_name in self.active_versions and self.active_versions[pkg_name] == version:
            del self.active_versions[pkg_name]
            safe_print(f'    ✅ Removed active version tracking for {pkg_name}=={version}')

    def validate_bubble(self, package_name: str, version: str) -> bool:
        """
        Validates a bubble's integrity by checking for its physical existence
        and the presence of a manifest file.
        """
        bubble_path_str = self.get_package_path(package_name, version)
        if not bubble_path_str:
            safe_print(_("    ❌ Bubble not found in HookManager's map for {}=={}").format(package_name, version))
            return False
        bubble_path = Path(bubble_path_str)
        if not bubble_path.is_dir():
            safe_print(_('    ❌ Bubble directory does not exist at: {}').format(bubble_path))
            return False
        manifest_path = bubble_path / '.omnipkg_manifest.json'
        if not manifest_path.exists():
            safe_print(_('    ❌ Bubble is incomplete: Missing manifest file at {}').format(manifest_path))
            return False
        bin_path = bubble_path / 'bin'
        if not bin_path.is_dir():
            safe_print(_("    ⚠️  Warning: Bubble for {}=={} does not contain a 'bin' directory.").format(package_name, version))
        safe_print(_('    ✅ Bubble validated successfully: {}=={}').format(package_name, version))
        return True

    def install_import_hook(self):
        if self.hook_installed:
            return
        sys.meta_path.insert(0, MultiversionFinder(self))
        self.hook_installed = True

    def set_active_version(self, package_name: str, version: str):
        self.active_versions[package_name.lower()] = version

    def get_package_path(self, package_name: str, version: str=None) -> Optional[str]:
        pkg_name = package_name.lower().replace('_', '-')
        version = version or self.active_versions.get(pkg_name)
        if pkg_name in self.version_map and version in self.version_map[pkg_name]:
            return self.version_map[pkg_name][version]
        if hasattr(self, 'bubble_manager') and pkg_name in self.bubble_manager.package_path_registry:
            if version in self.bubble_manager.package_path_registry[pkg_name]:
                return str(self.multiversion_base / '{}-{}'.format(pkg_name, version))
        return None

class MultiversionFinder:

    def __init__(self, hook_manager: ImportHookManager):
        self.hook_manager = hook_manager
        self.http_session = http_requests.Session()

    def find_spec(self, fullname, path, target=None):
        top_level = fullname.split('.')[0]
        pkg_path = self.hook_manager.get_package_path(top_level)
        if pkg_path and os.path.exists(pkg_path):
            if pkg_path not in sys.path:
                sys.path.insert(0, pkg_path)
        return None

class omnipkg:

    def __init__(self, config_manager: ConfigManager):
        """
        Initializes the Omnipkg core engine with a robust, fail-safe sequence.
        """
        self.config_manager = config_manager
        self.config = config_manager.config
        if not self.config:
            raise RuntimeError('OmnipkgCore cannot initialize: Configuration is missing or invalid.')
        self.env_id = self._get_env_id()
        self.multiversion_base = Path(self.config['multiversion_base'])
        self.cache_client = None
        self._info_cache = {}
        self._installed_packages_cache = None
        self.http_session = http_requests.Session()
        self.multiversion_base.mkdir(parents=True, exist_ok=True)
        if not self._connect_cache():
            sys.exit(1)
        self.interpreter_manager = InterpreterManager(self.config_manager)
        self.hook_manager = ImportHookManager(str(self.multiversion_base), config=self.config, cache_client=self.cache_client)
        self.bubble_manager = BubbleIsolationManager(self.config, self)
        migration_flag_key = f'omnipkg:env_{self.env_id}:migration_v2_env_aware_keys_complete'
        if not self.cache_client.get(migration_flag_key):
            old_keys_iterator = self.cache_client.scan_iter('omnipkg:pkg:*', count=1)
            if next(old_keys_iterator, None):
                self._perform_redis_key_migration(migration_flag_key)
            else:
                self.cache_client.set(migration_flag_key, 'true')
        self.hook_manager.load_version_map()
        self.hook_manager.install_import_hook()
        safe_print(_('✅ Omnipkg core initialized successfully.'))

    def _perform_redis_key_migration(self, migration_flag_key: str):
        """
        Performs a one-time, automatic migration of Redis keys from the old
        global format to the new environment-and-python-specific format.
        """
        safe_print('🔧 Performing one-time Knowledge Base upgrade for multi-environment support...')
        old_prefix = 'omnipkg:pkg:'
        all_old_keys = self.cache_client.keys(f'{old_prefix}*')
        if not all_old_keys:
            safe_print('   ✅ No old-format data found to migrate. Marking as complete.')
            self.cache_client.set(migration_flag_key, 'true')
            return
        new_prefix_for_current_env = self.redis_key_prefix
        migrated_count = 0
        with self.cache_client.pipeline() as pipe:
            for old_key in all_old_keys:
                new_key = old_key.replace(old_prefix, new_prefix_for_current_env, 1)
                pipe.rename(old_key, new_key)
                migrated_count += 1
            pipe.set(migration_flag_key, 'true')
            pipe.execute()
        safe_print(f'   ✅ Successfully upgraded {migrated_count} KB entries for this environment.')

    def _get_env_id(self) -> str:
        """Creates a short, stable hash from the venv path to uniquely identify it."""
        venv_path = str(Path(sys.prefix).resolve())
        return hashlib.md5(venv_path.encode()).hexdigest()[:8]

    @property
    def redis_env_prefix(self) -> str:
        """
        Gets the environment-and-python-specific part of the Redis key,
        e.g., 'omnipkg:env_12345678:py3.11:'.
        This is the correct base for keys like 'index' that are not package-specific.
        """
        return self.redis_key_prefix.rsplit('pkg:', 1)[0]

    @property
    def redis_key_prefix(self) -> str:
        python_exe_path = self.config.get('python_executable', sys.executable)
        py_ver_str = 'unknown'
        match = re.search('python(3\\.\\d+)', python_exe_path)
        if match:
            py_ver_str = f'py{match.group(1)}'
        else:
            try:
                result = subprocess.run([python_exe_path, '-c', "import sys; safe_print(f'py{sys.version_info.major}.{sys.version_info.minor}')"], capture_output=True, text=True, check=True, timeout=2)
                py_ver_str = result.stdout.strip()
            except Exception:
                py_ver_str = f'py{sys.version_info.major}.{sys.version_info.minor}'
        return f'omnipkg:env_{self.config_manager.env_id}:{py_ver_str}:pkg:'

    def _connect_cache(self) -> bool:
        """
        Attempts to connect to Redis if the library is installed. If it fails or
        is not installed, falls back to a local SQLite database.
        """
        if REDIS_AVAILABLE:
            try:
                redis_host = self.config.get('redis_host', 'localhost')
                redis_port = self.config.get('redis_port', 6379)
                if not redis_host:
                    raise redis.ConnectionError('Redis is not configured.')
                cache_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True, socket_connect_timeout=1)
                cache_client.ping()
                self.cache_client = cache_client
                safe_print(_('⚡️ Connected to Redis successfully (High-performance mode).'))
                return True
            except redis.ConnectionError:
                safe_print(_('⚠️ Could not connect to Redis. Falling back to local SQLite cache.'))
            except Exception as e:
                safe_print(_('⚠️ Redis connection attempt failed: {}. Falling back to SQLite.').format(e))
        else:
            safe_print(_('⚠️ Redis library not installed. Falling back to local SQLite cache.'))
        try:
            sqlite_db_path = self.config_manager.config_dir / f'cache_{self.env_id}.sqlite'
            self.cache_client = SQLiteCacheClient(sqlite_db_path)
            if not self.cache_client.ping():
                raise RuntimeError('SQLite connection failed ping test.')
            safe_print(_('✅ Using local SQLite cache at: {}').format(sqlite_db_path))
            return True
        except Exception as e:
            safe_print(_('❌ FATAL: Could not initialize SQLite fallback cache: {}').format(e))
            import traceback
            traceback.print_exc()
            return False

    def reset_configuration(self, force: bool=False) -> int:
        """
        Deletes the config.json file to allow for a fresh setup.
        """
        config_path = Path.home() / '.config' / 'omnipkg' / 'config.json'
        if not config_path.exists():
            safe_print(_('✅ Configuration file does not exist. Nothing to do.'))
            return 0
        safe_print(_('🗑️  This will permanently delete your configuration file at:'))
        safe_print(_('   {}').format(config_path))
        if not force:
            confirm = input(_('\n🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
            if confirm != 'y':
                safe_print(_('🚫 Reset cancelled.'))
                return 1
        try:
            config_path.unlink()
            safe_print(_('✅ Configuration file deleted successfully.'))
            safe_print('\n' + '─' * 60)
            safe_print(_('🚀 The next time you run `omnipkg`, you will be guided through the first-time setup.'))
            safe_print('─' * 60)
            return 0
        except OSError as e:
            safe_print(_('❌ Error: Could not delete configuration file: {}').format(e))
            safe_print(_('   Please check your file permissions for {}').format(config_path))
            return 1

    def reset_knowledge_base(self, force: bool=False) -> int:
        """
        Deletes ALL omnipkg data for the CURRENT environment from Redis,
        as well as any legacy global data. It then triggers a full rebuild.
        """
        if not self._connect_cache():
            return 1
        env_context_prefix = self.redis_key_prefix.rsplit('pkg:', 1)[0]
        new_env_pattern = f'{env_context_prefix}*'
        old_global_pattern = 'omnipkg:pkg:*'
        migration_flag_pattern = 'omnipkg:migration:*'
        snapshot_pattern = 'omnipkg:snapshot:*'
        safe_print(_('\n🧠 omnipkg Knowledge Base Reset'))
        safe_print('-' * 50)
        safe_print(_("   This will DELETE all data for the current environment (matching '{}')").format(new_env_pattern))
        safe_print(_('   It will ALSO delete any legacy global data from older omnipkg versions.'))
        safe_print(_('   ⚠️  This command does NOT uninstall any Python packages.'))
        if not force:
            confirm = input(_('\n🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
            if confirm != 'y':
                safe_print(_('🚫 Reset cancelled.'))
                return 1
        safe_print(_('\n🗑️  Clearing knowledge base...'))
        try:
            keys_new_env = self.cache_client.keys(new_env_pattern)
            keys_old_global = self.cache_client.keys(old_global_pattern)
            keys_migration = self.cache_client.keys(migration_flag_pattern)
            keys_snapshot = self.cache_client.keys(snapshot_pattern)
            all_keys_to_delete = set(keys_new_env + keys_old_global + keys_migration + keys_snapshot)
            if all_keys_to_delete:
                delete_command = self.cache_client.unlink if hasattr(self.cache_client, 'unlink') else self.cache_client.delete
                delete_command(*all_keys_to_delete)
                safe_print(_('   ✅ Cleared {} cached entries from Redis.').format(len(all_keys_to_delete)))
            else:
                safe_print(_('   ✅ Knowledge base was already clean.'))
        except Exception as e:
            safe_print(_('   ❌ Failed to clear knowledge base: {}').format(e))
            return 1
        self._info_cache.clear()
        self._installed_packages_cache = None
        return self.rebuild_knowledge_base(force=True)

    def rebuild_knowledge_base(self, force: bool=False):
        """
        FIXED: Rebuilds the knowledge base by directly invoking the metadata gatherer
        in-process, now passing the correct target Python context to ensure
        metadata is stamped with the correct version.
        """
        safe_print(_('🧠 Forcing a full rebuild of the knowledge base...'))
        if not self._connect_cache():
            return 1
        try:
            configured_exe = self.config.get('python_executable')
            version_tuple = self.config_manager._verify_python_version(configured_exe)
            current_python_version = f'{version_tuple[0]}.{version_tuple[1]}' if version_tuple else None
            if not current_python_version:
                safe_print(_('   ❌ CRITICAL: Could not determine configured Python version. Aborting rebuild.'))
                return 1
            safe_print(f'   🐍 Rebuilding knowledge base for Python {current_python_version} context...')
            gatherer = omnipkgMetadataGatherer(config=self.config, env_id=self.env_id, force_refresh=force, omnipkg_instance=self, target_context_version=current_python_version)
            gatherer.cache_client = self.cache_client
            gatherer.run()
            self._info_cache.clear()
            self._installed_packages_cache = None
            safe_print(_('✅ Knowledge base rebuilt successfully.'))
            return 0
        except Exception as e:
            safe_print(_('    ❌ An unexpected error occurred during knowledge base rebuild: {}').format(e))
            import traceback
            traceback.print_exc()
            return 1

    def _analyze_rebuild_needs(self) -> dict:
        project_files = []
        for ext in ['.py', 'requirements.txt', 'pyproject.toml', 'Pipfile']:
            pass
        return {'auto_rebuild': len(project_files) > 0, 'components': ['dependency_cache', 'metadata', 'compatibility_matrix'], 'confidence': 0.95, 'suggestions': []}

    def _rebuild_component(self, component: str) -> None:
        if component == 'metadata':
            safe_print(_('   🔄 Rebuilding core package metadata...'))
            try:
                cmd = [self.config['python_executable'], self.config['builder_script_path'], '--force']
                subprocess.run(cmd, check=True)
                safe_print(_('   ✅ Core metadata rebuilt.'))
            except Exception as e:
                safe_print(_('   ❌ Metadata rebuild failed: {}').format(e))
        else:
            safe_print(_('   (Skipping {} - feature coming soon!)').format(component))

    def prune_bubbled_versions(self, package_name: str, keep_latest: Optional[int]=None, force: bool=False):
        """
        Intelligently removes old bubbled versions of a package.
        """
        self._synchronize_knowledge_base_with_reality()
        c_name = canonicalize_name(package_name)
        all_installations = self._find_package_installations(c_name)
        active_version_info = next((p for p in all_installations if p['type'] == 'active'), None)
        bubbled_versions = [p for p in all_installations if p['type'] == 'bubble']
        if not bubbled_versions:
            safe_print(_("✅ No bubbles found for '{}'. Nothing to prune.").format(c_name))
            return 0
        bubbled_versions.sort(key=lambda x: parse_version(x['version']), reverse=True)
        to_prune = []
        if keep_latest is not None:
            if keep_latest < 0:
                safe_print(_("❌ 'keep-latest' must be a non-negative number."))
                return 1
            to_prune = bubbled_versions[keep_latest:]
            kept_count = len(bubbled_versions) - len(to_prune)
            safe_print(_('🔎 Found {} bubbles. Keeping the latest {}, pruning {} older versions.').format(len(bubbled_versions), kept_count, len(to_prune)))
        else:
            to_prune = bubbled_versions
            safe_print(_("🔎 Found {} bubbles to prune for '{}'.").format(len(to_prune), c_name))
        if not to_prune:
            safe_print(_('✅ No bubbles match the pruning criteria.'))
            return 0
        safe_print(_('\nThe following bubbled versions will be permanently deleted:'))
        for item in to_prune:
            safe_print(_('  - v{} (bubble)').format(item['version']))
        if active_version_info:
            safe_print(_('🛡️  The active version (v{}) will NOT be affected.').format(active_version_info['version']))
        if not force:
            confirm = input(_('\n🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
            if confirm != 'y':
                safe_print(_('🚫 Prune cancelled.'))
                return 1
        specs_to_uninstall = [f"{item['name']}=={item['version']}" for item in to_prune]
        for spec in specs_to_uninstall:
            safe_print('-' * 20)
            self.smart_uninstall([spec], force=True)
        safe_print(_("\n🎉 Pruning complete for '{}'.").format(c_name))
        return 0

    def _check_and_run_pending_rebuild(self) -> bool:
        """
        Checks for a flag file indicating a new interpreter needs its KB built.
        If the current context matches a version in the flag, it runs the build.
        Returns True if a rebuild was run, False otherwise.
        """
        flag_file = self.config_manager.venv_path / '.omnipkg' / '.needs_kb_rebuild'
        if not flag_file.exists():
            return False
        configured_exe = self.config.get('python_executable')
        version_tuple = self.config_manager._verify_python_version(configured_exe)
        if not version_tuple:
            return False
        current_version_str = f'{version_tuple[0]}.{version_tuple[1]}'
        lock_file = self.config_manager.venv_path / '.omnipkg' / '.needs_kb_rebuild.lock'
        with FileLock(lock_file):
            versions_to_rebuild = []
            try:
                with open(flag_file, 'r') as f:
                    versions_to_rebuild = json.load(f)
            except (json.JSONDecodeError, IOError):
                flag_file.unlink(missing_ok=True)
                return False
            if current_version_str in versions_to_rebuild:
                safe_print(_('💡 First use of Python {} detected.').format(current_version_str))
                safe_print(_('   Building its knowledge base now...'))
                rebuild_status = self.rebuild_knowledge_base(force=True)
                if rebuild_status == 0:
                    versions_to_rebuild.remove(current_version_str)
                    if not versions_to_rebuild:
                        flag_file.unlink(missing_ok=True)
                    else:
                        with open(flag_file, 'w') as f:
                            json.dump(versions_to_rebuild, f)
                    safe_print(f'   ✅ Knowledge base for Python {current_version_str} is ready.')
                    return True
                else:
                    safe_print(_('   ❌ Failed to build knowledge base. It will be re-attempted on the next run.'))
                    return False
        return False

    def _synchronize_knowledge_base_with_reality(self, verbose: bool=False):
        """
        Self-healing function that is now fully robust AND context-aware. 
        It only scans packages that belong to the currently active Python interpreter,
        preventing cross-interpreter contamination and scan failures.
        (Enhanced Version 5 - Context-Aware Python Interpreter Scoping)
        """
        if self._check_and_run_pending_rebuild():
            return
        safe_print(_('🧠 Performing context-aware sync of knowledge base...'))
        configured_python_exe = self.config.get('python_executable', sys.executable)
        configured_site_packages = self.config.get('site_packages_path')
        if not configured_site_packages or not Path(configured_site_packages).exists():
            safe_print(_('   ⚠️  Configured site-packages path is invalid or missing: {}').format(configured_site_packages))
            safe_print(_('   🛑 Aborting sync. Please check your omnipkg configuration.'))
            return
        version_tuple = self.config_manager._verify_python_version(configured_python_exe)
        if not version_tuple:
            safe_print(f'   ⚠️  Could not determine version for configured interpreter: {configured_python_exe}')
            safe_print(_('   🛑 Aborting sync.'))
            return
        current_python_version = f'{version_tuple[0]}.{version_tuple[1]}'
        current_site_packages = Path(configured_site_packages)
        safe_print(_('   🐍 Configured Python context: {} ({})').format(current_python_version, configured_python_exe))
        safe_print(_('   📦 Scanning configured site-packages: {}').format(current_site_packages))
        if not self.cache_client:
            self._connect_cache()
            if not self.cache_client:
                safe_print(_('   ❌ Cannot perform sync: Cache connection failed.'))
                return
        live_active_versions = self._get_all_active_versions_live_for_context(Path(self.config['site_packages_path']), verbose=verbose)
        packages_in_bubbles = self._get_packages_in_bubbles_for_context(current_python_version, verbose=verbose)
        index_key = f'{self.redis_env_prefix}index'
        packages_in_kb_index = self.cache_client.smembers(index_key)
        context_filtered_kb_packages = set()
        for pkg_name in packages_in_kb_index:
            main_key = f'{self.redis_key_prefix}{pkg_name}'
            cached_versions = self.cache_client.smembers(f'{main_key}:installed_versions')
            for version in cached_versions:
                version_key = f'{main_key}:{version}'
                indexed_by_python = self.cache_client.hget(version_key, 'indexed_by_python')
                if indexed_by_python == current_python_version:
                    context_filtered_kb_packages.add(pkg_name)
                    break
        safe_print(f'   🎯 Found {len(context_filtered_kb_packages)} packages in KB for Python {current_python_version}')
        ESSENTIAL_FIELDS = {'Name', 'Version', 'path'}
        IMPORTANT_FIELDS = {'checksum', 'last_indexed', 'Metadata-Version'}
        OPTIONAL_AUDIT_FIELDS = {'security.audit_status', 'security.issues_found', 'security.report', 'health.import_check.importable', 'health.import_check.version', 'dependencies', 'cli_analysis.common_flags', 'cli_analysis.subcommands', 'help_text', 'indexed_by_python'}
        discrepancies = 0
        packages_to_rebuild = set()
        for pkg_name in context_filtered_kb_packages:
            main_key = f'{self.redis_key_prefix}{pkg_name}'
            real_active_version = live_active_versions.get(pkg_name)
            real_bubbled_versions = packages_in_bubbles.get(pkg_name, set())
            all_real_versions_on_disk = real_bubbled_versions | ({real_active_version} if real_active_version else set())
            cached_versions_in_kb = self.cache_client.smembers(f'{main_key}:installed_versions')
            context_cached_versions = set()
            for version in cached_versions_in_kb:
                version_key = f'{main_key}:{version}'
                indexed_by_python = self.cache_client.hget(version_key, 'indexed_by_python')
                if indexed_by_python == current_python_version:
                    context_cached_versions.add(version)
            ghost_versions = context_cached_versions - all_real_versions_on_disk
            if ghost_versions:
                discrepancies += len(ghost_versions)
                for version in ghost_versions:
                    safe_print(f'   -> 👻 Exorcising ghost entry: {pkg_name}=={version}')
                    self._exorcise_ghost_entry(f'{pkg_name}=={version}')
                context_cached_versions = context_cached_versions - ghost_versions
            for version in context_cached_versions:
                version_key = f'{main_key}:{version}'
                stored_fields = set(self.cache_client.hkeys(version_key))
                missing_essential = ESSENTIAL_FIELDS - stored_fields
                if missing_essential:
                    safe_print(f"   -> Found incomplete KB entry for {pkg_name}=={version}. Missing essential fields: {', '.join(sorted(missing_essential))}")
                    packages_to_rebuild.add(f'{pkg_name}=={version}')
                    discrepancies += 1
                    continue
                if not stored_fields:
                    safe_print(f'   -> Found empty KB entry for {pkg_name}=={version}')
                    packages_to_rebuild.add(f'{pkg_name}=={version}')
                    discrepancies += 1
                    continue
                integrity_issues = []
                name_field = self.cache_client.hget(version_key, 'Name')
                if not name_field or name_field.strip() == '':
                    integrity_issues.append('Name is empty')
                version_field = self.cache_client.hget(version_key, 'Version')
                if not version_field or version_field != version:
                    integrity_issues.append(_('Version mismatch: stored={}, expected={}').format(version_field, version))
                path_field = self.cache_client.hget(version_key, 'path')
                if not path_field:
                    integrity_issues.append('Missing path')
                elif not Path(path_field).exists():
                    integrity_issues.append('Path does not exist on filesystem')
                elif current_site_packages and (not Path(path_field).is_relative_to(current_site_packages.parent)):
                    integrity_issues.append(_('Path outside current Python context: {}').format(path_field))
                checksum_field = self.cache_client.hget(version_key, 'checksum')
                if checksum_field and len(checksum_field) < 32:
                    integrity_issues.append('Invalid checksum format')
                audit_status = self.cache_client.hget(version_key, 'security.audit_status')
                if audit_status and audit_status not in ['checked_in_bulk', 'checked_individually', 'pending', 'skipped']:
                    integrity_issues.append(_('Invalid audit status: {}').format(audit_status))
                importable = self.cache_client.hget(version_key, 'health.import_check.importable')
                if importable and importable not in ['True', 'False']:
                    integrity_issues.append('Invalid import check result')
                dependencies = self.cache_client.hget(version_key, 'dependencies')
                if dependencies and (not (dependencies.startswith('[') and dependencies.endswith(']'))):
                    integrity_issues.append('Invalid dependencies format')
                if integrity_issues:
                    safe_print(f"   -> Found integrity issues for {pkg_name}=={version}: {'; '.join(integrity_issues)}")
                    packages_to_rebuild.add(f'{pkg_name}=={version}')
                    discrepancies += 1
                    continue
                missing_important = IMPORTANT_FIELDS - stored_fields
                if missing_important:
                    safe_print(_('   -> Note: {}=={} is missing some important fields but is functional: {}').format(pkg_name, version, ', '.join(sorted(missing_important))))
            missing_versions = all_real_versions_on_disk - context_cached_versions
            if missing_versions:
                discrepancies += len(missing_versions)
                safe_print(f"   -> Found versions missing from KB for {pkg_name} (Python {current_python_version}): {', '.join(sorted(missing_versions))}")
                for version in missing_versions:
                    packages_to_rebuild.add(f'{pkg_name}=={version}')
        all_disk_packages = set(live_active_versions.keys()) | set(packages_in_bubbles.keys())
        missing_from_index = all_disk_packages - context_filtered_kb_packages
        if missing_from_index:
            discrepancies += len(missing_from_index)
            safe_print(f"   -> Found packages missing from KB index (Python {current_python_version}): {', '.join(sorted(missing_from_index))}")
            for pkg_name in missing_from_index:
                self.cache_client.sadd(index_key, pkg_name)
                if pkg_name in live_active_versions:
                    packages_to_rebuild.add(f'{pkg_name}=={live_active_versions[pkg_name]}')
                if pkg_name in packages_in_bubbles:
                    for version in packages_in_bubbles[pkg_name]:
                        packages_to_rebuild.add(f'{pkg_name}=={version}')
        if packages_to_rebuild:
            safe_print(f'   -> Found {len(packages_to_rebuild)} missing or incomplete entries for Python {current_python_version}. Rebuilding...')
            self.rebuild_package_kb(list(packages_to_rebuild), target_python_version=current_python_version)
        if discrepancies > 0:
            safe_print(_('   ✅ Context-aware sync complete. Reconciled {} discrepancies for Python {}.').format(discrepancies, current_python_version))
        else:
            safe_print(_('   ✅ Knowledge base is already in sync with Python {} environment.').format(current_python_version))

    def _get_all_active_versions_live_for_context(self, site_packages_path, verbose: bool=False):
        """
        Get active versions only from the specified site-packages directory.
        This prevents cross-interpreter contamination.
        """
        start_time = time.time()
        active_versions = {}
        if not site_packages_path or not site_packages_path.exists():
            if verbose:
                safe_print(_(' ⚠️ Site-packages path does not exist: {}').format(site_packages_path))
            return active_versions
        if verbose:
            safe_print(f' 🔍 Scanning for packages in: {site_packages_path}')
        package_categories = defaultdict(list)
        failed_packages = []
        try:
            for dist_info_path in site_packages_path.glob('*.dist-info'):
                if dist_info_path.is_dir():
                    try:
                        dist = importlib.metadata.Distribution.at(dist_info_path)
                        pkg_name = canonicalize_name(dist.metadata['Name'])
                        active_versions[pkg_name] = dist.version
                        if pkg_name in ['flask', 'django', 'fastapi', 'tornado']:
                            package_categories['web_frameworks'].append(pkg_name)
                        elif pkg_name in ['requests', 'urllib3', 'httpx', 'aiohttp']:
                            package_categories['http_clients'].append(pkg_name)
                        elif pkg_name in ['numpy', 'pandas', 'scipy', 'matplotlib', 'seaborn']:
                            package_categories['data_science'].append(pkg_name)
                        elif pkg_name in ['pytest', 'unittest2', 'nose', 'tox']:
                            package_categories['testing'].append(pkg_name)
                        elif pkg_name in ['click', 'argparse', 'fire', 'typer']:
                            package_categories['cli_tools'].append(pkg_name)
                        else:
                            package_categories['other'].append(pkg_name)
                    except Exception as e:
                        failed_packages.append((dist_info_path.name, str(e)))
                        continue
        except Exception as e:
            if verbose:
                safe_print(_(' ❌ Error scanning site-packages: {}').format(e))
        scan_time = time.time() - start_time
        safe_print(f'    ⏱️  Scan completed in {scan_time:.2f}s')
        safe_print(_('    ✅ Found {} packages total').format(len(active_versions)))
        if verbose:
            safe_print(_(' 📊 Package Scan Summary:'))
            for category, packages in package_categories.items():
                if packages and category != 'other':
                    count = len(packages)
                    sample = packages[:3]
                    sample_str = ', '.join(sample)
                    if count > 3:
                        sample_str += f' (+{count - 3} more)'
                    safe_print(_('    📦 {}: {} ({})').format(category.replace('_', ' ').title(), count, sample_str))
            if package_categories['other']:
                other_count = len(package_categories['other'])
                safe_print(_('    📦 Other packages: {}').format(other_count))
            if failed_packages:
                safe_print(_('    ⚠️  Failed to process {} packages').format(len(failed_packages)))
        return active_versions

    def _get_packages_in_bubbles_for_context(self, python_version, verbose: bool=False):
        """
        Get packages in bubbles, but only those created for the current Python version.
        """
        start_time = time.time()
        packages_in_bubbles = {}
        if not self.multiversion_base.exists():
            if verbose:
                safe_print(_(' ⚠️ Multiversion base does not exist: {}').format(self.multiversion_base))
            return packages_in_bubbles
        safe_print(f' 🫧 Scanning bubble packages for Python {python_version}...')
        package_categories = defaultdict(list)
        failed_bubbles = []
        skipped_version_count = 0
        total_bubbles_found = 0
        version_mismatches = defaultdict(int)
        python_version_key = f"python_{python_version.replace('.', '_')}"
        for dist_info_path in self.multiversion_base.rglob('*.dist-info'):
            if dist_info_path.is_dir():
                total_bubbles_found += 1
                try:
                    bubble_root = dist_info_path.parent
                    bubble_info_file = bubble_root / '.omnipkg_bubble_info'
                    bubble_python_version = None
                    if bubble_info_file.exists():
                        try:
                            with open(bubble_info_file, 'r') as f:
                                bubble_info = json.load(f)
                                bubble_python_version = bubble_info.get('python_version')
                        except:
                            pass
                    if bubble_python_version and bubble_python_version != python_version:
                        skipped_version_count += 1
                        version_mismatches[bubble_python_version] += 1
                        continue
                    dist = importlib.metadata.Distribution.at(dist_info_path)
                    pkg_name = canonicalize_name(dist.metadata['Name'])
                    if pkg_name not in packages_in_bubbles:
                        packages_in_bubbles[pkg_name] = set()
                    packages_in_bubbles[pkg_name].add(dist.version)
                    if pkg_name in ['flask', 'django', 'fastapi', 'tornado', 'bottle']:
                        package_categories['web_frameworks'].append(pkg_name)
                    elif pkg_name in ['requests', 'urllib3', 'httpx', 'aiohttp']:
                        package_categories['http_clients'].append(pkg_name)
                    elif pkg_name in ['numpy', 'pandas', 'scipy', 'matplotlib', 'seaborn', 'plotly']:
                        package_categories['data_science'].append(pkg_name)
                    elif pkg_name in ['pytest', 'unittest2', 'nose', 'tox', 'coverage']:
                        package_categories['testing'].append(pkg_name)
                    elif pkg_name in ['click', 'argparse', 'fire', 'typer']:
                        package_categories['cli_tools'].append(pkg_name)
                    elif pkg_name in ['sqlalchemy', 'psycopg2', 'pymongo', 'redis']:
                        package_categories['databases'].append(pkg_name)
                    elif pkg_name in ['jinja2', 'markupsafe', 'pyyaml', 'toml', 'configparser']:
                        package_categories['templating_config'].append(pkg_name)
                    elif pkg_name in ['cryptography', 'pycryptodome', 'bcrypt', 'passlib']:
                        package_categories['security'].append(pkg_name)
                    else:
                        package_categories['other'].append(pkg_name)
                except Exception as e:
                    failed_bubbles.append((dist_info_path.name, str(e)))
                    continue
        scan_time = time.time() - start_time
        safe_print(f'    ⏱️  Scan completed in {scan_time:.2f}s')
        safe_print(f'    📊 Total .dist-info directories found: {total_bubbles_found}')
        safe_print(_('    ✅ Matching Python {} packages: {}').format(python_version, len(packages_in_bubbles)))
        if verbose:
            safe_print(_(' 🫧 Bubble Package Scan Summary:'))
            if skipped_version_count > 0:
                safe_print(f'    ⏭️  Skipped {skipped_version_count} packages from other Python versions:')
                for version, count in sorted(version_mismatches.items()):
                    safe_print(_('        • Python {}: {} packages').format(version, count))
            for category, packages in package_categories.items():
                if packages and category != 'other':
                    count = len(packages)
                    unique_packages = list(set(packages))
                    sample = unique_packages[:3]
                    sample_str = ', '.join(sample)
                    if len(unique_packages) > 3:
                        sample_str += f' (+{len(unique_packages) - 3} more)'
                    safe_print(_('    📦 {}: {} instances ({})').format(category.replace('_', ' ').title(), count, sample_str))
            if package_categories['other']:
                other_count = len(set(package_categories['other']))
                safe_print(_('    📦 Other packages: {} unique types').format(other_count))
            if failed_bubbles:
                safe_print(_('    ⚠️  Failed to process {} bubbles').format(len(failed_bubbles)))
                if len(failed_bubbles) <= 3:
                    for name, error in failed_bubbles:
                        safe_print(_('        • {}: {}').format(name, error))
            multi_version_packages = {k: v for k, v in packages_in_bubbles.items() if len(v) > 1}
            if multi_version_packages:
                safe_print(f'    🔄 Packages with multiple bubble versions: {len(multi_version_packages)}')
                for pkg, versions in sorted(multi_version_packages.items()):
                    if len(multi_version_packages) <= 5:
                        version_list = ', '.join(sorted(versions))
                        safe_print(_('        • {}: {}').format(pkg, version_list))
        return packages_in_bubbles

    def _update_hash_index_for_delta(self, before: Dict, after: Dict):
        """Surgically updates the cached hash index in Redis after an install."""
        if not self.cache_client:
            self._connect_cache()
        redis_key = _('{}main_env:file_hashes').format(self.redis_key_prefix)
        if not self.cache_client.exists(redis_key):
            return
        safe_print(_('🔄 Updating cached file hash index...'))
        uninstalled_or_changed = {name: ver for name, ver in before.items() if name not in after or after[name] != ver}
        installed_or_changed = {name: ver for name, ver in after.items() if name not in before or before[name] != ver}
        with self.cache_client.pipeline() as pipe:
            for name, ver in uninstalled_or_changed.items():
                try:
                    dist = importlib.metadata.distribution(name)
                    if dist.files:
                        for file in dist.files:
                            pipe.srem(redis_key, self.bubble_manager._get_file_hash(dist.locate_file(file)))
                except (importlib.metadata.PackageNotFoundError, FileNotFoundError):
                    continue
            for name, ver in installed_or_changed.items():
                try:
                    dist = importlib.metadata.distribution(name)
                    if dist.files:
                        for file in dist.files:
                            pipe.sadd(redis_key, self.bubble_manager._get_file_hash(dist.locate_file(file)))
                except (importlib.metadata.PackageNotFoundError, FileNotFoundError):
                    continue
            pipe.execute()
        safe_print(_('✅ Hash index updated.'))

    def get_installed_packages(self, live: bool=False) -> Dict[str, str]:
        if live:
            try:
                cmd = [self.config['python_executable'], '-I', '-m', 'pip', 'list', '--format=json']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                live_packages = {pkg['name'].lower(): pkg['version'] for pkg in json.loads(result.stdout)}
                self._installed_packages_cache = live_packages
                return live_packages
            except Exception as e:
                safe_print(_('    ⚠️  Could not perform live package scan: {}').format(e))
                return self._installed_packages_cache or {}
        if self._installed_packages_cache is None:
            if not self.cache_client:
                self._connect_cache()
            self._installed_packages_cache = self.cache_client.hgetall(_('{}versions').format(self.redis_key_prefix))
        return self._installed_packages_cache

    def _detect_downgrades(self, before: Dict[str, str], after: Dict[str, str]) -> List[Dict]:
        downgrades = []
        for pkg_name, old_version in before.items():
            if pkg_name in after:
                new_version = after[pkg_name]
                try:
                    if parse_version(new_version) < parse_version(old_version):
                        downgrades.append({'package': pkg_name, 'good_version': old_version, 'bad_version': new_version})
                except InvalidVersion:
                    continue
        return downgrades

    def _detect_upgrades(self, before: Dict[str, str], after: Dict[str, str]) -> List[Dict]:
        """Identifies packages that were upgraded."""
        upgrades = []
        for pkg_name, old_version in before.items():
            if pkg_name in after:
                new_version = after[pkg_name]
                try:
                    if parse_version(new_version) > parse_version(old_version):
                        upgrades.append({'package': pkg_name, 'old_version': old_version, 'new_version': new_version})
                except InvalidVersion:
                    continue
        return upgrades

    def _run_metadata_builder_for_delta(self, before: Dict, after: Dict):
        """
        FIXED: Atomically updates the knowledge base by directly invoking the metadata
        gatherer in-process for all targeted updates, mirroring the robust logic
        from the successful rebuild_knowledge_base function.
        """
        changed_specs = [f'{name}=={ver}' for name, ver in after.items() if name not in before or before[name] != ver]
        uninstalled = {name: ver for name, ver in before.items() if name not in after}
        if not changed_specs and (not uninstalled):
            safe_print(_('✅ Knowledge base is already up to date.'))
            return
        safe_print(_('🧠 Updating knowledge base for changes...'))
        try:
            if changed_specs:
                safe_print(_('   -> Processing {} changed/new package(s)...').format(len(changed_specs)))
                gatherer = omnipkgMetadataGatherer(config=self.config, env_id=self.env_id, force_refresh=True)
                gatherer.cache_client = self.cache_client
                newly_active_packages = {canonicalize_name(spec.split('==')[0]): spec.split('==')[1] for spec in changed_specs if canonicalize_name(spec.split('==')[0]) in after}
                gatherer.run(targeted_packages=changed_specs, newly_active_packages=newly_active_packages)
            if uninstalled:
                safe_print(_('   -> Cleaning up {} uninstalled package(s) from Redis...').format(len(uninstalled)))
                with self.cache_client.pipeline() as pipe:
                    for pkg_name, uninstalled_version in uninstalled.items():
                        c_name = canonicalize_name(pkg_name)
                        main_key = f'{self.redis_key_prefix}{c_name}'
                        version_key = f'{main_key}:{uninstalled_version}'
                        versions_set_key = f'{main_key}:installed_versions'
                        pipe.delete(version_key)
                        pipe.srem(versions_set_key, uninstalled_version)
                        if self.cache_client.hget(main_key, 'active_version') == uninstalled_version:
                            pipe.hdel(main_key, 'active_version')
                        pipe.hdel(main_key, f'bubble_version:{uninstalled_version}')
                    pipe.execute()
            self._info_cache.clear()
            self._installed_packages_cache = None
            safe_print(_('✅ Knowledge base updated successfully.'))
        except Exception as e:
            safe_print(_('    ⚠️ Failed to update knowledge base for delta: {}').format(e))
            import traceback
            traceback.print_exc()

    def show_package_info(self, package_spec: str) -> int:
        if not self._connect_cache():
            return 1
        self._synchronize_knowledge_base_with_reality()
        try:
            pkg_name, requested_version = self._parse_package_spec(package_spec)
            if requested_version:
                safe_print('\n' + '=' * 60)
                safe_print(_('📄 Detailed info for {} v{}').format(pkg_name, requested_version))
                safe_print('=' * 60)
                self._show_version_details(pkg_name, requested_version)
            else:
                self._show_enhanced_package_data(pkg_name)
            return 0
        except Exception as e:
            safe_print(_('❌ An unexpected error occurred while showing package info: {}').format(e))
            import traceback
            traceback.print_exc()
            return 1

    def _clean_and_format_dependencies(self, raw_deps_json: str) -> str:
        """Parses the raw dependency JSON, filters out noise, and formats it for humans."""
        try:
            deps = json.loads(raw_deps_json)
            if not deps:
                return 'None'
            core_deps = [d.split(';')[0].strip() for d in deps if ';' not in d]
            if len(core_deps) > 5:
                return _('{}, ...and {} more').format(', '.join(core_deps[:5]), len(core_deps) - 5)
            else:
                return ', '.join(core_deps)
        except (json.JSONDecodeError, TypeError):
            return 'Could not parse.'

    def _show_enhanced_package_data(self, package_name: str):
        r = self.cache_client
        overview_key = '{}{}'.format(self.redis_key_prefix, package_name.lower())
        if not r.exists(overview_key):
            safe_print(_("\n📋 KEY DATA: No Redis data found for '{}'").format(package_name))
            return
        safe_print(_("\n📋 KEY DATA for '{}':").format(package_name))
        safe_print('-' * 40)
        overview_data = r.hgetall(overview_key)
        active_ver = overview_data.get('active_version', 'Not Set')
        safe_print(_('🎯 Active Version: {}').format(active_ver))
        bubble_versions = [key.replace('bubble_version:', '') for key in overview_data if key.startswith('bubble_version:') and overview_data[key] == 'true']
        if bubble_versions:
            safe_print(_('🫧 Bubbled Versions: {}').format(', '.join(sorted(bubble_versions))))
        available_versions = []
        if active_ver != 'Not Set':
            available_versions.append(active_ver)
        available_versions.extend(sorted(bubble_versions))
        if available_versions:
            safe_print(_('\n📦 Available Versions:'))
            for i, ver in enumerate(available_versions, 1):
                status_indicators = []
                if ver == active_ver:
                    status_indicators.append('active')
                if ver in bubble_versions:
                    status_indicators.append('in bubble')
                status_str = f" ({', '.join(status_indicators)})" if status_indicators else ''
                safe_print(_('  {}) {}{}').format(i, ver, status_str))
            safe_print(_('\n💡 Want details on a specific version?'))
            try:
                choice = input(_('Enter number (1-{}) or press Enter to skip: ').format(len(available_versions)))
                if choice.strip():
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(available_versions):
                            selected_version = available_versions[idx]
                            safe_print('\n' + '=' * 60)
                            safe_print(_('📄 Detailed info for {} v{}').format(package_name, selected_version))
                            safe_print('=' * 60)
                            self._show_version_details(package_name, selected_version)
                        else:
                            safe_print(_('❌ Invalid selection.'))
                    except ValueError:
                        safe_print(_('❌ Please enter a number.'))
            except KeyboardInterrupt:
                safe_print(_('\n   Skipped.'))
        else:
            safe_print(_('📦 No installed versions found in Redis.'))

    def get_all_versions(self, package_name: str) -> List[str]:
        """Get all versions (active + bubbled) for a package"""
        overview_key = f'{self.redis_key_prefix}{package_name.lower()}'
        overview_data = self.cache_client.hgetall(overview_key)
        active_ver = overview_data.get('active_version')
        bubble_versions = [key.replace('bubble_version:', '') for key in overview_data if key.startswith('bubble_version:') and overview_data[key] == 'true']
        versions = []
        if active_ver:
            versions.append(active_ver)
        versions.extend(bubble_versions)
        return sorted(versions, key=lambda v: v)

    def _show_version_details(self, package_name: str, version: str):
        r = self.cache_client
        version_key = f'{self.redis_key_prefix}{package_name.lower()}:{version}'
        if not r.exists(version_key):
            safe_print(_('❌ No detailed data found for {} v{}').format(package_name, version))
            return
        data = r.hgetall(version_key)
        important_fields = [('name', '📦 Package'), ('Version', '🏷️  Version'), ('Summary', '📝 Summary'), ('Author', '👤 Author'), ('Author-email', '📧 Email'), ('License', '⚖️  License'), ('Home-page', '🌐 Homepage'), ('path', '📂 Path'), ('Platform', '💻 Platform'), ('dependencies', '🔗 Dependencies'), ('Requires-Dist', '📋 Requires')]
        safe_print(_('The data is fetched from Redis key: {}').format(version_key))
        for field_name, display_name in important_fields:
            if field_name in data:
                value = data[field_name]
                if field_name == 'License' and len(value) > 100:
                    value = value.split('\n')[0] + '... (truncated)'
                if field_name in ['dependencies', 'Requires-Dist']:
                    try:
                        dep_list = json.loads(value)
                        safe_print(_('{}: {}').format(display_name.ljust(18), ', '.join(dep_list) if dep_list else 'None'))
                    except (json.JSONDecodeError, TypeError):
                        safe_print(_('{}: {}').format(display_name.ljust(18), value))
                else:
                    safe_print(_('{}: {}').format(display_name.ljust(18), value))
        security_fields = [('security.issues_found', '🔒 Security Issues'), ('security.audit_status', '🛡️  Audit Status'), ('health.import_check.importable', '✅ Importable')]
        safe_print(_('\n---[ Health & Security ]---'))
        for field_name, display_name in security_fields:
            value = data.get(field_name, 'N/A')
            safe_print(_('   {}: {}').format(display_name.ljust(18), value))
        meta_fields = [('last_indexed', '⏰ Last Indexed'), ('checksum', '🔐 Checksum'), ('Metadata-Version', '📋 Metadata Version')]
        safe_print(_('\n---[ Build Info ]---'))
        for field_name, display_name in meta_fields:
            value = data.get(field_name, 'N/A')
            if field_name == 'checksum' and len(value) > 24:
                value = f'{value[:12]}...{value[-12:]}'
            safe_print(_('   {}: {}').format(display_name.ljust(18), value))
        safe_print(_('\n💡 For all raw data, use Redis key: "{}"').format(version_key))

    def _save_last_known_good_snapshot(self):
        """Saves the current environment state to Redis."""
        safe_print(_("📸 Saving snapshot of the current environment as 'last known good'..."))
        try:
            current_state = self.get_installed_packages(live=True)
            snapshot_key = f'{self.redis_key_prefix}snapshot:last_known_good'
            self.cache_client.set(snapshot_key, json.dumps(current_state))
            safe_print(_('   ✅ Snapshot saved.'))
        except Exception as e:
            safe_print(_('   ⚠️ Could not save environment snapshot: {}').format(e))

    def _sort_packages_for_install(self, packages: List[str], strategy: str) -> List[str]:
        """
        Sorts packages for installation based on the chosen strategy.
        - 'latest-active': Sorts oldest to newest to ensure the last one installed is the latest.
        - 'stable-main': Sorts newest to oldest to minimize environmental changes.
        """
        from packaging.version import parse as parse_version, InvalidVersion
        import re

        def get_version_key(pkg_spec):
            """Extracts a sortable version key from a package spec."""
            match = re.search('(==|>=|<=|>|<|~=)(.+)', pkg_spec)
            if match:
                version_str = match.group(2).strip()
                try:
                    return parse_version(version_str)
                except InvalidVersion:
                    return parse_version('0.0.0')
            return parse_version('9999.0.0')
        should_reverse = strategy == 'stable-main'
        return sorted(packages, key=get_version_key, reverse=should_reverse)

    def adopt_interpreter(self, version: str) -> int:
        """
        Safely adopts a Python version by checking the registry, then trying to copy
        from the local system, and finally falling back to download.
        A rescan is forced after any successful filesystem change to ensure registration.
        """
        safe_print(_('🐍 Attempting to adopt Python {} into the environment...').format(version))
        managed_interpreters = self.interpreter_manager.list_available_interpreters()
        if version in managed_interpreters:
            safe_print(_('   - ✅ Python {} is already adopted and managed.').format(version))
            return 0
        discovered_pythons = self.config_manager.list_available_pythons()
        source_path_str = discovered_pythons.get(version)
        if not source_path_str:
            safe_print(_('   - No local Python {} found. Falling back to download strategy.').format(version))
            result = self._fallback_to_download(version)
            if result == 0:
                safe_print(_('🔧 Forcing rescan to register the new interpreter...'))
                self.rescan_interpreters()
            return result
        source_exe_path = Path(source_path_str)
        try:
            cmd = [str(source_exe_path), '-c', 'import sys; safe_print(sys.prefix)']
            cmd_result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            source_root = Path(os.path.realpath(cmd_result.stdout.strip()))
            current_venv_root = self.config_manager.venv_path.resolve()
            if self._is_same_or_child_path(source_root, current_venv_root) or not self._is_valid_python_installation(source_root, source_exe_path) or self._estimate_directory_size(source_root) > 2 * 1024 * 1024 * 1024 or self._is_system_critical_path(source_root):
                safe_print(_('   - ⚠️  Safety checks failed for local copy. Falling back to download.'))
                result = self._fallback_to_download(version)
                if result == 0:
                    safe_print(_('🔧 Forcing rescan to register the downloaded interpreter...'))
                    self.rescan_interpreters()
                return result
            dest_root = self.config_manager.venv_path / '.omnipkg' / 'interpreters' / f'cpython-{version}'
            if dest_root.exists():
                safe_print(_('   - ✅ Adopted copy of Python {} already exists. Ensuring it is registered.').format(version))
                self.rescan_interpreters()
                return 0
            safe_print(_('   - Starting safe copy operation...'))
            result = self._perform_safe_copy(source_root, dest_root, version)
            if result == 0:
                safe_print(_('🔧 Forcing rescan to register the copied interpreter...'))
                self.rescan_interpreters()
            return result
        except Exception as e:
            safe_print(_('   - ❌ An error occurred during the copy attempt: {}. Falling back to download.').format(e))
            result = self._fallback_to_download(version)
            if result == 0:
                safe_print(_('🔧 Forcing rescan to register the downloaded interpreter...'))
                self.rescan_interpreters()
            return result

    def _is_interpreter_directory_valid(self, path: Path) -> bool:
        """
        Checks if a directory contains a valid, runnable Python interpreter structure.
        This is the core of the integrity check.
        """
        if not path.exists():
            return False
        bin_dir = path / 'bin'
        if bin_dir.is_dir():
            for name in ['python', 'python3', 'python3.9', 'python3.10', 'python3.11', 'python3.12']:
                exe_path = bin_dir / name
                if exe_path.is_file() and os.access(exe_path, os.X_OK):
                    try:
                        result = subprocess.run([str(exe_path), '--version'], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            return True
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
                        continue
        scripts_dir = path / 'Scripts'
        if scripts_dir.is_dir():
            exe_path = scripts_dir / 'python.exe'
            if exe_path.is_file():
                try:
                    result = subprocess.run([str(exe_path), '--version'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
                    pass
        for name in ['python', 'python.exe', 'python3', 'python3.exe']:
            exe_path = path / name
            if exe_path.is_file() and os.access(exe_path, os.X_OK):
                try:
                    result = subprocess.run([str(exe_path), '--version'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
                    continue
        return False

    def _fallback_to_download(self, version: str) -> int:
        """
        Fallback to downloading Python. This function now surgically detects an incomplete
        installation by checking for a valid executable, cleans it up if broken,
        and includes a safety stop to prevent deleting the active interpreter.
        """
        safe_print(_('\n--- Running robust download strategy ---'))
        try:
            full_versions = {'3.13': '3.13.7', '3.12': '3.12.11', '3.11': '3.11.9', '3.10': '3.10.18', '3.9': '3.9.23'}
            full_version = full_versions.get(version)
            if not full_version:
                safe_print(f'❌ Error: No known standalone build for Python {version}.')
                safe_print(_('   Available versions: {}').format(', '.join(full_versions.keys())))
                return 1
            dest_path = self.config_manager.venv_path / '.omnipkg' / 'interpreters' / f'cpython-{full_version}'
            if dest_path.exists():
                safe_print(_('   - Found existing directory for Python {}. Verifying integrity...').format(full_version))
                if self._is_interpreter_directory_valid(dest_path):
                    safe_print(_('   - ✅ Integrity check passed. Installation is valid and complete.'))
                    return 0
                else:
                    safe_print(_('   - ⚠️  Integrity check failed: Incomplete installation detected (missing or broken executable).'))
                    try:
                        active_interpreter_root = Path(sys.executable).resolve().parents[1]
                        if dest_path.resolve() == active_interpreter_root:
                            safe_print(_('   - ❌ CRITICAL ERROR: The broken interpreter is the currently active one!'))
                            safe_print(_('   - Aborting to prevent self-destruction. Please fix the environment manually.'))
                            return 1
                    except (IndexError, OSError):
                        pass
                    safe_print(_('   - Preparing to clean up broken directory...'))
                    try:
                        shutil.rmtree(dest_path)
                        safe_print(_('   - ✅ Removed broken directory successfully.'))
                    except Exception as e:
                        safe_print(_('   - ❌ FATAL: Failed to remove existing broken directory: {}').format(e))
                        return 1
            safe_print(_('   - Starting fresh download and installation...'))
            download_success = False
            if version == '3.13':
                safe_print(_('   - Using python-build-standalone for Python 3.13...'))
                download_success = self._download_python_313_alternative(dest_path, full_version)
            if not download_success:
                if hasattr(self.config_manager, '_install_managed_python'):
                    try:
                        self.config_manager._install_managed_python(self.config_manager.venv_path, full_version)
                        download_success = True
                    except Exception as e:
                        safe_print(_('   - Warning: _install_managed_python failed: {}').format(e))
                elif hasattr(self.config_manager, 'install_managed_python'):
                    try:
                        self.config_manager.install_managed_python(self.config_manager.venv_path, full_version)
                        download_success = True
                    except Exception as e:
                        safe_print(_('   - Warning: install_managed_python failed: {}').format(e))
                elif hasattr(self.config_manager, 'download_python'):
                    try:
                        self.config_manager.download_python(full_version)
                        download_success = True
                    except Exception as e:
                        safe_print(_('   - Warning: download_python failed: {}').format(e))
            if not download_success:
                safe_print(_('❌ Error: All download methods failed for Python {}').format(full_version))
                return 1
            if dest_path.exists() and self._is_interpreter_directory_valid(dest_path):
                safe_print(_('   - ✅ Download and installation completed successfully.'))
                self.config_manager._set_rebuild_flag_for_version(version)
                return 0
            else:
                safe_print(_('   - ❌ Installation completed but integrity check still fails.'))
                return 1
        except Exception as e:
            safe_print(_('❌ Download and installation process failed: {}').format(e))
            return 1

    def _download_python_313_alternative(self, dest_path: Path, full_version: str) -> bool:
        """
        Alternative download method specifically for Python 3.13 using python-build-standalone releases.
        Downloads from the December 5, 2024 release builds.
        """
        import urllib.request
        import tarfile
        import platform
        import tempfile
        import shutil
        try:
            safe_print(_('   - Attempting Python 3.13 download from python-build-standalone...'))
            system = platform.system().lower()
            machine = platform.machine().lower()
            base_url = 'https://github.com/indygreg/python-build-standalone/releases/download/20241205/'
            build_filename = None
            if system == 'windows':
                if '64' in machine or machine == 'amd64' or machine == 'x86_64':
                    build_filename = 'cpython-3.13.1+20241205-x86_64-pc-windows-msvc-install_only.tar.gz'
                else:
                    build_filename = 'cpython-3.13.1+20241205-i686-pc-windows-msvc-install_only.tar.gz'
            elif system == 'darwin':
                if 'arm' in machine or 'm1' in machine.lower() or 'arm64' in machine:
                    build_filename = 'cpython-3.13.1+20241205-aarch64-apple-darwin-install_only.tar.gz'
                else:
                    build_filename = 'cpython-3.13.1+20241205-x86_64-apple-darwin-install_only.tar.gz'
            elif system == 'linux':
                if 'aarch64' in machine or 'arm64' in machine:
                    build_filename = 'cpython-3.13.1+20241205-aarch64-unknown-linux-gnu-install_only.tar.gz'
                elif 'arm' in machine:
                    if 'hf' in machine or platform.processor().find('hard') != -1:
                        build_filename = 'cpython-3.13.1+20241205-armv7-unknown-linux-gnueabihf-install_only.tar.gz'
                    else:
                        build_filename = 'cpython-3.13.1+20241205-armv7-unknown-linux-gnueabi-install_only.tar.gz'
                elif 'ppc64le' in machine:
                    build_filename = 'cpython-3.13.1+20241205-ppc64le-unknown-linux-gnu-install_only.tar.gz'
                elif 's390x' in machine:
                    build_filename = 'cpython-3.13.1+20241205-s390x-unknown-linux-gnu-install_only.tar.gz'
                elif 'x86_64' in machine or 'amd64' in machine:
                    try:
                        import subprocess
                        result = subprocess.run(['ldd', '--version'], capture_output=True, text=True, timeout=5)
                        if 'musl' in result.stderr.lower():
                            build_filename = 'cpython-3.13.1+20241205-x86_64-unknown-linux-musl-install_only.tar.gz'
                        else:
                            build_filename = 'cpython-3.13.1+20241205-x86_64-unknown-linux-gnu-install_only.tar.gz'
                    except:
                        build_filename = 'cpython-3.13.1+20241205-x86_64-unknown-linux-gnu-install_only.tar.gz'
                elif 'i686' in machine or 'i386' in machine:
                    build_filename = 'cpython-3.13.1+20241205-i686-unknown-linux-gnu-install_only.tar.gz'
                else:
                    build_filename = 'cpython-3.13.1+20241205-x86_64-unknown-linux-gnu-install_only.tar.gz'
            if not build_filename:
                safe_print(_('   - ❌ Could not determine appropriate build for platform: {} {}').format(system, machine))
                return False
            download_url = base_url + build_filename
            safe_print(_('   - Selected build: {}').format(build_filename))
            safe_print(_('   - Downloading from: {}').format(download_url))
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as temp_file:
                temp_path = Path(temp_file.name)
            try:

                def show_progress(block_num, block_size, total_size):
                    if total_size > 0:
                        percent = min(100, block_num * block_size * 100 // total_size)
                        if block_num % 100 == 0 or percent >= 100:
                            safe_print(_('   - Download progress: {}%').format(percent), end='\r')
                urllib.request.urlretrieve(download_url, temp_path, reporthook=show_progress)
                safe_print(_('\n   - Download completed, extracting...'))
                with tarfile.open(temp_path, 'r:gz') as tar_ref:
                    with tempfile.TemporaryDirectory() as temp_extract_dir:
                        tar_ref.extractall(temp_extract_dir)
                        extracted_items = list(Path(temp_extract_dir).iterdir())
                        if len(extracted_items) == 1 and extracted_items[0].is_dir():
                            extracted_dir = extracted_items[0]
                            if dest_path.exists():
                                shutil.rmtree(dest_path)
                            shutil.move(str(extracted_dir), str(dest_path))
                        else:
                            dest_path.mkdir(parents=True, exist_ok=True)
                            for item in extracted_items:
                                dest_item = dest_path / item.name
                                if dest_item.exists():
                                    if dest_item.is_dir():
                                        shutil.rmtree(dest_item)
                                    else:
                                        dest_item.unlink()
                                shutil.move(str(item), str(dest_item))
                safe_print(_('   - Extraction completed'))
                if system in ['linux', 'darwin']:
                    python_exe = dest_path / 'bin' / 'python3'
                    if python_exe.exists():
                        python_exe.chmod(493)
                        python_versioned = dest_path / 'bin' / 'python3.13'
                        if python_versioned.exists():
                            python_versioned.chmod(493)
                safe_print(_('   - ✅ Python 3.13.1 installation completed successfully'))
                safe_print(_('   - Bootstrapping the new Python 3.13 environment...'))
                python_exe = self._find_python_executable_in_dir(dest_path)
                if not python_exe:
                    safe_print(_('   - ❌ CRITICAL: Could not find Python executable in {} after extraction.').format(dest_path))
                    return False
                self.config_manager._install_essential_packages(python_exe)
                safe_print(_('   - ✅ Alternative Python 3.13 download and bootstrap completed'))
                return True
            finally:
                temp_path.unlink(missing_ok=True)
        except Exception as e:
            safe_print(_('   - ❌ Python 3.13 download failed: {}').format(e))
            import traceback
            safe_print(_('   - Error details: {}').format(traceback.format_exc()))
            return False

    def rescan_interpreters(self) -> int:
        """
        Forces a full, clean re-scan of the managed interpreters directory
        and rebuilds the registry from scratch. This is a repair utility.
        """
        safe_print(_('Performing a full re-scan of managed interpreters...'))
        try:
            self.config_manager._register_all_interpreters(self.config_manager.venv_path)
            safe_print(_('\n✅ Interpreter registry successfully rebuilt.'))
            return 0
        except Exception as e:
            safe_print(_('\n❌ An error occurred during the re-scan: {}').format(e))
            import traceback
            traceback.print_exc()
            return 1

    def _is_same_or_child_path(self, source: Path, target: Path) -> bool:
        """Check if source is the same as target or a child of target."""
        try:
            source = source.resolve()
            target = target.resolve()
            if source == target:
                return True
            try:
                source.relative_to(target)
                return True
            except ValueError:
                return False
        except (OSError, RuntimeError):
            return True

    def _is_valid_python_installation(self, root: Path, exe_path: Path) -> bool:
        """Validate that the source looks like a proper Python installation."""
        try:
            if not exe_path.exists():
                return False
            try:
                exe_path.resolve().relative_to(root.resolve())
            except ValueError:
                return False
            expected_dirs = ['lib', 'bin']
            if sys.platform == 'win32':
                expected_dirs = ['Lib', 'Scripts']
            has_expected_structure = any(((root / d).exists() for d in expected_dirs))
            test_cmd = [str(exe_path), '-c', 'import sys, os']
            test_result = subprocess.run(test_cmd, capture_output=True, timeout=5)
            return has_expected_structure and test_result.returncode == 0
        except Exception:
            return False

    def _estimate_directory_size(self, path: Path, max_files_to_check: int=1000) -> int:
        """Estimate directory size with early termination for safety."""
        total_size = 0
        file_count = 0
        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith(('.git', '__pycache__', '.mypy_cache', 'node_modules'))]
                for file in files:
                    if file_count >= max_files_to_check:
                        return total_size * 10
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except (OSError, IOError):
                        continue
        except Exception:
            return float('inf')
        return total_size

    def _is_system_critical_path(self, path: Path) -> bool:
        """Check if path is a system-critical directory that shouldn't be copied."""
        critical_paths = [Path('/'), Path('/usr'), Path('/usr/local'), Path('/System'), Path('/Library'), Path('/opt'), Path('/bin'), Path('/sbin'), Path('/etc'), Path('/var'), Path('/tmp'), Path('/proc'), Path('/dev'), Path('/sys')]
        if sys.platform == 'win32':
            critical_paths.extend([Path('C:\\Windows'), Path('C:\\Program Files'), Path('C:\\Program Files (x86)'), Path('C:\\System32')])
        try:
            resolved_path = path.resolve()
            for critical in critical_paths:
                if resolved_path == critical.resolve():
                    return True
            return False
        except Exception:
            return True

    def _perform_safe_copy(self, source: Path, dest: Path, version: str) -> int:
        """Perform the actual copy operation with additional safety measures."""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)

            def ignore_patterns(dir, files):
                ignored = []
                for file in files:
                    if file in {'.git', '__pycache__', '.mypy_cache', '.pytest_cache', '.tox', '.coverage', 'node_modules', '.DS_Store'}:
                        ignored.append(file)
                    try:
                        filepath = os.path.join(dir, file)
                        if os.path.isfile(filepath) and os.path.getsize(filepath) > 50 * 1024 * 1024:
                            ignored.append(file)
                    except OSError:
                        pass
                return ignored
            safe_print(_('   - Copying {} -> {}').format(source, dest))
            shutil.copytree(source, dest, symlinks=True, ignore=ignore_patterns, dirs_exist_ok=False)
            copied_python = self._find_python_executable_in_dir(dest)
            if not copied_python or not copied_python.exists():
                safe_print(_('   - ❌ Copy completed but Python executable not found in destination'))
                shutil.rmtree(dest, ignore_errors=True)
                return self._fallback_to_download(version)
            test_cmd = [str(copied_python), '-c', 'import sys; safe_print(sys.version)']
            test_result = subprocess.run(test_cmd, capture_output=True, timeout=10)
            if test_result.returncode != 0:
                safe_print(_('   - ❌ Copied Python executable failed basic test'))
                shutil.rmtree(dest, ignore_errors=True)
                return self._fallback_to_download(version)
            safe_print(_('   - ✅ Copy successful and verified!'))
            self.config_manager._register_all_interpreters(self.config_manager.venv_path)
            safe_print(f'\n🎉 Successfully adopted Python {version} from local source!')
            safe_print(_("   You can now use 'omnipkg swap python {}'").format(version))
            return 0
        except Exception as e:
            safe_print(_('   - ❌ Copy operation failed: {}').format(e))
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
            return self._fallback_to_download(version)

    def _find_python_executable_in_dir(self, directory: Path) -> Path:
        """Find the Python executable in a copied directory."""
        possible_names = ['python', 'python3', 'python.exe']
        possible_dirs = ['bin', 'Scripts', '.']
        for subdir in possible_dirs:
            for name in possible_names:
                candidate = directory / subdir / name
                if candidate.exists() and candidate.is_file():
                    return candidate
        return None

    def _get_redis_key_prefix_for_version(self, version: str) -> str:
        """Generates the Redis key prefix for a specific Python version string."""
        py_ver_str = f'py{version}'
        base_prefix = self.config.get('redis_key_prefix', 'omnipkg:pkg:')
        base = base_prefix.split(':')[0]
        return f'{base}:env_{self.config_manager.env_id}:{py_ver_str}:pkg:'

    def remove_interpreter(self, version: str, force: bool=False) -> int:
        """
        Forcefully removes a managed Python interpreter directory, purges its
        knowledge base from Redis, and updates the registry.
        """
        safe_print(_('🔥 Attempting to remove managed Python interpreter: {}').format(version))
        active_python_version = f'{sys.version_info.major}.{sys.version_info.minor}'
        if version == active_python_version:
            safe_print(_('❌ SAFETY LOCK: Cannot remove the currently active Python interpreter ({}).').format(version))
            safe_print(_("   Switch to a different Python version first using 'omnipkg swap python <other_version>'."))
            return 1
        managed_interpreters = self.interpreter_manager.list_available_interpreters()
        interpreter_path = managed_interpreters.get(version)
        if not interpreter_path:
            safe_print(_('🤷 Error: Python version {} is not a known managed interpreter.').format(version))
            return 1
        interpreter_root_dir = interpreter_path.parent.parent
        safe_print(f'   Target directory for deletion: {interpreter_root_dir}')
        if not interpreter_root_dir.exists():
            safe_print(_('   Directory does not exist. It may have already been cleaned up.'))
            self.rescan_interpreters()
            return 0
        if not force:
            confirm = input(_('🤔 Are you sure you want to permanently delete this directory? (y/N): ')).lower().strip()
            if confirm != 'y':
                safe_print(_('🚫 Removal cancelled.'))
                return 1
        try:
            safe_print(_('🗑️ Deleting directory: {}').format(interpreter_root_dir))
            shutil.rmtree(interpreter_root_dir)
            safe_print(_('✅ Directory removed successfully.'))
        except Exception as e:
            safe_print(_('❌ Failed to remove directory: {}').format(e))
            return 1
        safe_print(f'🧹 Cleaning up Knowledge Base for Python {version}...')
        try:
            keys_to_delete_pattern = self._get_redis_key_prefix_for_version(version) + '*'
            keys = self.cache_client.keys(keys_to_delete_pattern)
            if keys:
                safe_print(_('   -> Found {} stale entries in Redis. Purging...').format(len(keys)))
                delete_command = self.cache_client.unlink if hasattr(self.cache_client, 'unlink') else self.cache_client.delete
                delete_command(*keys)
                safe_print(f'   ✅ Knowledge Base for Python {version} has been purged.')
            else:
                safe_print(f'   ✅ No Knowledge Base entries found for Python {version}. Nothing to clean.')
        except Exception as e:
            safe_print(f'   ⚠️  Warning: Could not clean up Knowledge Base for Python {version}: {e}')
        safe_print(_('🔧 Rescanning interpreters to update the registry...'))
        self.rescan_interpreters()
        return 0

    def smart_install(self, packages: List[str], dry_run: bool=False, force_reinstall: bool=False, target_directory: Optional[Path]=None) -> int:
        if not self._connect_cache():
            return 1
        if dry_run:
            safe_print(_('🔬 Running in --dry-run mode. No changes will be made.'))
            return 0
        if not packages:
            safe_print('🚫 No packages specified for installation.')
            return 1
        install_strategy = self.config.get('install_strategy', 'stable-main')
        packages_to_process = list(packages)
        for pkg_spec in list(packages_to_process):
            pkg_name, requested_version = self._parse_package_spec(pkg_spec)
            self._synchronize_knowledge_base_with_reality()
            if pkg_name.lower() == 'omnipkg':
                packages_to_process.remove(pkg_spec)
                active_omnipkg_version = self._get_active_version_from_environment('omnipkg')
                if not active_omnipkg_version:
                    safe_print('⚠️ Warning: Cannot determine active omnipkg version. Proceeding with caution.')
                if requested_version and active_omnipkg_version and (parse_version(requested_version) == parse_version(active_omnipkg_version)):
                    safe_print('✅ omnipkg=={} is already the active omnipkg. No bubble needed.'.format(requested_version))
                    continue
                safe_print("✨ Special handling: omnipkg '{}' requested.".format(pkg_spec))
                if not requested_version:
                    safe_print("  Skipping bubbling of 'omnipkg' without a specific version for now.")
                    continue
                bubble_dir_name = 'omnipkg-{}'.format(requested_version)
                target_bubble_path = Path(self.config['multiversion_base']) / bubble_dir_name
                wheel_url = self.get_wheel_url_from_pypi(pkg_name, requested_version)
                if not wheel_url:
                    safe_print('❌ Could not find a compatible wheel for omnipkg=={}. Cannot create bubble.'.format(requested_version))
                    continue
                if not self.extract_wheel_into_bubble(wheel_url, target_bubble_path, pkg_name, requested_version):
                    safe_print('❌ Failed to create bubble for omnipkg=={}.'.format(requested_version))
                    continue
                self.register_package_in_knowledge_base(pkg_name, requested_version, str(target_bubble_path), 'bubble')
                safe_print('✅ omnipkg=={} successfully bubbled.'.format(requested_version))
                fake_before = {}
                fake_after = {pkg_name: requested_version}
                self.run_metadata_builder_for_delta(fake_before, fake_after)
        if not packages_to_process:
            safe_print(_('\n🎉 All package operations complete.'))
            return 0
        safe_print("🚀 Starting install with policy: '{}'".format(install_strategy))
        resolved_packages = self._resolve_package_versions(packages_to_process)
        if not resolved_packages:
            safe_print(_('❌ Could not resolve any packages to install. Aborting.'))
            return 1
        sorted_packages = self._sort_packages_for_install(resolved_packages, strategy=install_strategy)
        if sorted_packages != resolved_packages:
            safe_print('🔄 Reordered packages for optimal installation: {}'.format(', '.join(sorted_packages)))
        user_requested_cnames = {canonicalize_name(self._parse_package_spec(p)[0]) for p in packages}
        any_installations_made = False
        main_env_kb_updates = {}
        bubbled_kb_updates = {}
        kb_deletions = set()
        for package_spec in sorted_packages:
            safe_print('\n' + '─' * 60)
            safe_print('📦 Processing: {}'.format(package_spec))
            if force_reinstall:
                safe_print(_('   - 🛡️  Force reinstall triggered by auto-repair.'))
            safe_print('─' * 60)
            if not force_reinstall:
                satisfaction_check = self._check_package_satisfaction([package_spec], strategy=install_strategy)
                if satisfaction_check['all_satisfied']:
                    safe_print('✅ Requirement already satisfied: {}'.format(package_spec))
                    continue
            packages_to_install = [package_spec]
            packages_before = self.get_installed_packages(live=True)
            safe_print('⚙️ Running pip install for: {}...'.format(', '.join(packages_to_install)))
            return_code = self._run_pip_install(packages_to_install, target_directory=target_directory, force_reinstall=force_reinstall)
            if return_code != 0:
                safe_print('❌ Pip installation failed for {}. Continuing...'.format(package_spec))
                continue
            any_installations_made = True
            packages_after = self.get_installed_packages(live=True)
            replacements = self._detect_version_replacements(packages_before, packages_after)
            if replacements:
                for rep in replacements:
                    kb_deletions.add(rep['package'])
                    self._cleanup_version_from_kb(rep['package'], rep['old_version'])
            if install_strategy == 'stable-main':
                downgrades_to_fix = self._detect_downgrades(packages_before, packages_after)
                upgrades_to_fix = self._detect_upgrades(packages_before, packages_after)
                all_changes_to_fix = []
                for fix in downgrades_to_fix:
                    all_changes_to_fix.append({'package': fix['package'], 'old_version': fix['good_version'], 'new_version': fix['bad_version'], 'change_type': 'downgraded'})
                for fix in upgrades_to_fix:
                    all_changes_to_fix.append({'package': fix['package'], 'old_version': fix['old_version'], 'new_version': fix['new_version'], 'change_type': 'upgraded'})
                if all_changes_to_fix:
                    safe_print(_('🛡️ STABILITY PROTECTION ACTIVATED!'))
                    replaced_packages_count = len({fix['package'] for fix in all_changes_to_fix})
                    safe_print(_('   -> Found {} package(s) downgraded by pip. Bubbling them to preserve stability...').format(replaced_packages_count))
                    main_env_hashes = self.bubble_manager._get_or_build_main_env_hash_index()
                    for fix in all_changes_to_fix:
                        bubble_created = self.bubble_manager.create_isolated_bubble(fix['package'], fix['new_version'])
                        if bubble_created:
                            bubbled_kb_updates[fix['package']] = fix['new_version']
                            bubble_path_str = str(self.multiversion_base / f"{fix['package']}-{fix['new_version']}")
                            self.hook_manager.refresh_bubble_map(fix['package'], fix['new_version'], bubble_path_str)
                            self.hook_manager.validate_bubble(fix['package'], fix['new_version'])
                            restore_result = subprocess.run([self.config['python_executable'], '-m', 'pip', 'install', '--quiet', f"{fix['package']}=={fix['old_version']}"], capture_output=True, text=True)
                            if restore_result.returncode == 0:
                                main_env_kb_updates[fix['package']] = fix['old_version']
                                safe_print('   ✅ Bubbled {} v{}, restored stable v{}'.format(fix['package'], fix['new_version'], fix['old_version']))
                            else:
                                safe_print('   ❌ Failed to restore {} v{}'.format(fix['package'], fix['old_version']))
                        else:
                            safe_print('   ❌ Failed to create bubble for {} v{}'.format(fix['package'], fix['new_version']))
                    safe_print(_('   -> Stability protection complete.'))
                else:
                    for pkg_name, version in packages_after.items():
                        if pkg_name not in packages_before:
                            main_env_kb_updates[pkg_name] = version
            elif install_strategy == 'latest-active':
                versions_to_bubble = []
                for pkg_name in set(packages_before.keys()) | set(packages_after.keys()):
                    old_version = packages_before.get(pkg_name)
                    new_version = packages_after.get(pkg_name)
                    if old_version and new_version and (old_version != new_version):
                        change_type = 'upgraded' if parse_version(new_version) > parse_version(old_version) else 'downgraded'
                        versions_to_bubble.append({'package': pkg_name, 'version_to_bubble': old_version, 'version_staying_active': new_version, 'change_type': change_type, 'user_requested': canonicalize_name(pkg_name) in user_requested_cnames})
                    elif not old_version and new_version:
                        main_env_kb_updates[pkg_name] = new_version
                if versions_to_bubble:
                    safe_print(_('🛡️ LATEST-ACTIVE STRATEGY: Preserving replaced versions'))
                    for item in versions_to_bubble:
                        bubble_created = self.bubble_manager.create_isolated_bubble(item['package'], item['version_to_bubble'])
                        if bubble_created:
                            bubbled_kb_updates[item['package']] = item['version_to_bubble']
                            bubble_path_str = str(self.multiversion_base / f"{item['package']}-{item['version_to_bubble']}")
                            self.hook_manager.refresh_bubble_map(item['package'], item['version_to_bubble'], bubble_path_str)
                            self.hook_manager.validate_bubble(item['package'], item['version_to_bubble'])
                            main_env_kb_updates[item['package']] = item['version_staying_active']
                            safe_print('    ✅ Bubbled {} v{}, keeping v{} active'.format(item['package'], item['version_to_bubble'], item['version_staying_active']))
                        else:
                            safe_print('    ❌ Failed to bubble {} v{}'.format(item['package'], item['version_to_bubble']))
        if not any_installations_made:
            safe_print(_('\n✅ All requirements were already satisfied.'))
            self._synchronize_knowledge_base_with_reality()
            return 0
        safe_print(_('\n🧠 Updating knowledge base (consolidated)...'))
        all_changed_specs = set()
        final_main_state = self.get_installed_packages(live=True)
        initial_packages_before = self.get_installed_packages(live=True) if not any_installations_made else packages_before
        for name, ver in final_main_state.items():
            if name not in initial_packages_before or initial_packages_before[name] != ver:
                all_changed_specs.add(f'{name}=={ver}')
        for pkg_name, version in bubbled_kb_updates.items():
            all_changed_specs.add(f'{pkg_name}=={version}')
        for pkg_name, version in main_env_kb_updates.items():
            all_changed_specs.add(f'{pkg_name}=={version}')
        if all_changed_specs:
            safe_print('    Targeting {} package(s) for KB update...'.format(len(all_changed_specs)))
            try:
                from .package_meta_builder import omnipkgMetadataGatherer
                from .package_meta_builder import omnipkgMetadataGatherer
                gatherer = omnipkgMetadataGatherer(config=self.config, env_id=self.env_id, force_refresh=True, omnipkg_instance=self)
                gatherer.cache_client = self.cache_client
                gatherer.run(targeted_packages=list(all_changed_specs))
                self._info_cache.clear()
                self._installed_packages_cache = None
                self._update_hash_index_for_delta(initial_packages_before, final_main_state)
                safe_print(_('    ✅ Knowledge base updated successfully.'))
            except Exception as e:
                safe_print('    ⚠️ Failed to run consolidated knowledge base update: {}'.format(e))
                import traceback
                traceback.print_exc()
        else:
            safe_print(_('    ✅ Knowledge base is already up to date.'))
        if not force_reinstall:
            safe_print(_('\n🧹 Cleaning redundant bubbles...'))
            final_active_packages = self.get_installed_packages(live=True)
            cleaned_count = 0
            for pkg_name, active_version in final_active_packages.items():
                bubble_path = self.multiversion_base / f'{pkg_name}-{active_version}'
                if bubble_path.exists() and bubble_path.is_dir():
                    try:
                        shutil.rmtree(bubble_path)
                        cleaned_count += 1
                        if hasattr(self, 'hook_manager'):
                            self.hook_manager.remove_bubble_from_tracking(pkg_name, active_version)
                    except Exception as e:
                        safe_print(_('    ❌ Failed to remove bubble directory: {}').format(e))
            if cleaned_count > 0:
                safe_print('    ✅ Removed {} redundant bubbles'.format(cleaned_count))
        safe_print(_('\n🎉 All package operations complete.'))
        self._save_last_known_good_snapshot()
        self._synchronize_knowledge_base_with_reality()
        return 0

    def _brute_force_package_cleanup(self, pkg_name: str, site_packages: Path):
        """
        Performs a manual, brute-force deletion of a corrupted package's files
        in a specific site-packages directory.
        """
        safe_print(_("🧹 Performing brute-force cleanup of corrupted package '{}' in {}...").format(pkg_name, site_packages))
        try:
            c_name_dash = canonicalize_name(pkg_name)
            c_name_under = c_name_dash.replace('-', '_')
            for name_variant in {c_name_dash, c_name_under}:
                for path in site_packages.glob(f'{name_variant}'):
                    if path.is_dir():
                        safe_print(_('   - Deleting library directory: {}').format(path))
                        shutil.rmtree(path, ignore_errors=True)
            for path in site_packages.glob(f'{c_name_dash}-*.dist-info'):
                if path.is_dir():
                    safe_print(_('   - Deleting metadata: {}').format(path))
                    shutil.rmtree(path, ignore_errors=True)
            safe_print(_('   - ✅ Brute-force cleanup complete.'))
            return True
        except Exception as e:
            safe_print(_('   - ❌ Brute-force cleanup FAILED: {}').format(e))
            return False

    def _get_active_version_from_environment(self, pkg_name: str) -> Optional[str]:
        """
        Gets the version of a package actively installed in the current Python environment
        using pip show.
        """
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', pkg_name], capture_output=True, text=True, check=True)
            output = result.stdout
            for line in output.splitlines():
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
            return None
        except subprocess.CalledProcessError:
            return None
        except Exception as e:
            safe_print(_('Error getting active version of {}: {}').format(pkg_name, e))
            return None

    def _detect_version_replacements(self, before: Dict, after: Dict) -> List[Dict]:
        """
        Identifies packages that were replaced (uninstalled and a new version installed).
        This is different from a simple upgrade/downgrade list.
        """
        replacements = []
        for pkg_name, old_version in before.items():
            if pkg_name in after and after[pkg_name] != old_version:
                replacements.append({'package': pkg_name, 'old_version': old_version, 'new_version': after[pkg_name]})
        return replacements

    def _cleanup_version_from_kb(self, package_name: str, version: str):
        """
        Surgically removes all traces of a single, specific version of a package
        from the Redis knowledge base.
        """
        safe_print(_('   -> Cleaning up replaced version from knowledge base: {} v{}').format(package_name, version))
        c_name = canonicalize_name(package_name)
        main_key = f'{self.redis_key_prefix}{c_name}'
        version_key = f'{main_key}:{version}'
        versions_set_key = f'{main_key}:installed_versions'
        with self.cache_client.pipeline() as pipe:
            pipe.delete(version_key)
            pipe.srem(versions_set_key, version)
            pipe.hdel(main_key, f'bubble_version:{version}')
            if self.cache_client.hget(main_key, 'active_version') == version:
                pipe.hdel(main_key, 'active_version')
            pipe.execute()

    def _restore_from_snapshot(self, snapshot: Dict, current_state: Dict):
        """Restores the main environment to the exact state of a given snapshot."""
        safe_print(_('🔄 Restoring main environment from snapshot...'))
        snapshot_keys = set(snapshot.keys())
        current_keys = set(current_state.keys())
        to_uninstall = [pkg for pkg in current_keys if pkg not in snapshot_keys]
        to_install_or_fix = ['{}=={}'.format(pkg, ver) for pkg, ver in snapshot.items() if pkg not in current_keys or current_state.get(pkg) != ver]
        if not to_uninstall and (not to_install_or_fix):
            safe_print(_('   ✅ Environment is already in its original state.'))
            return
        if to_uninstall:
            safe_print(_('   -> Uninstalling: {}').format(', '.join(to_uninstall)))
            self._run_pip_uninstall(to_uninstall)
        if to_install_or_fix:
            safe_print(_('   -> Installing/Fixing: {}').format(', '.join(to_install_or_fix)))
            self._run_pip_install(to_install_or_fix + ['--no-deps'])
        safe_print(_('   ✅ Environment restored.'))

    def _extract_wheel_into_bubble(self, wheel_url: str, target_bubble_path: Path, pkg_name: str, pkg_version: str) -> bool:
        """
        Downloads a wheel and extracts its content directly into a bubble directory.
        Does NOT use pip install.
        """
        safe_print(_('📦 Downloading wheel for {}=={}...').format(pkg_name, pkg_version))
        try:
            response = self.http_session.get(wheel_url, stream=True)
            response.raise_for_status()
            target_bubble_path.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                for member in zf.namelist():
                    if member.startswith((_('{}-{}.dist-info').format(pkg_name, pkg_version), _('{}-{}.data').format(pkg_name, pkg_version))):
                        continue
                    try:
                        zf.extract(member, target_bubble_path)
                    except Exception as extract_error:
                        safe_print(_('⚠️ Warning: Could not extract {}: {}').format(member, extract_error))
                        continue
            safe_print(_('✅ Extracted {}=={} to {}').format(pkg_name, pkg_version, target_bubble_path.name))
            return True
        except http_requests.exceptions.RequestException as e:
            safe_print(_('❌ Failed to download wheel from {}: {}').format(wheel_url, e))
            return False
        except zipfile.BadZipFile:
            safe_print(_('❌ Downloaded file is not a valid wheel: {}').format(wheel_url))
            return False
        except Exception as e:
            safe_print(_('❌ Error extracting wheel for {}=={}: {}').format(pkg_name, pkg_version, e))
            return False

    def _get_wheel_url_from_pypi(self, pkg_name: str, pkg_version: str) -> Optional[str]:
        """Fetches the wheel URL for a specific package version from PyPI."""
        pypi_url = f'https://pypi.org/pypi/{pkg_name}/{pkg_version}/json'
        try:
            response = self.http_session.get(pypi_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            py_major = sys.version_info.major
            py_minor = sys.version_info.minor
            wheel_priorities = [lambda f: f'py{py_major}{py_minor}' in f and 'manylinux' in f, lambda f: any((compat in f for compat in [f'py{py_major}', 'py2.py3', 'py3'])) and 'manylinux' in f, lambda f: 'py2.py3-none-any' in f or 'py3-none-any' in f, lambda f: True]
            for priority_check in wheel_priorities:
                for url_info in data.get('urls', []):
                    if url_info['packagetype'] == 'bdist_wheel' and priority_check(url_info['filename']):
                        safe_print(_('🎯 Found compatible wheel: {}').format(url_info['filename']))
                        return url_info['url']
            for url_info in data.get('urls', []):
                if url_info['packagetype'] == 'sdist':
                    safe_print(_('⚠️ Only source distribution available for {}=={}').format(pkg_name, pkg_version))
                    safe_print(_('   This may require compilation and is not recommended for bubbling.'))
                    return None
            safe_print(_('❌ No compatible wheel or source found for {}=={} on PyPI.').format(pkg_name, pkg_version))
            return None
        except http_requests.exceptions.RequestException as e:
            safe_print(_('❌ Failed to fetch PyPI data for {}=={}: {}').format(pkg_name, pkg_version, e))
            return None
        except KeyError as e:
            safe_print(_('❌ Unexpected PyPI response structure: missing {}').format(e))
            return None
        except Exception as e:
            safe_print(_('❌ Error parsing PyPI data: {}').format(e))
            return None

    def _parse_package_spec(self, pkg_spec: str) -> tuple[str, Optional[str]]:
        """
        Parse a package specification like 'package==1.0.0' or 'package>=2.0'
        Returns (package_name, version) where version is None if no version specified.
        """
        version_separators = ['==', '>=', '<=', '>', '<', '~=', '!=']
        for separator in version_separators:
            if separator in pkg_spec:
                parts = pkg_spec.split(separator, 1)
                if len(parts) == 2:
                    pkg_name = parts[0].strip()
                    version = parts[1].strip()
                    if separator == '==':
                        return (pkg_name, version)
                    else:
                        safe_print(_("⚠️ Version specifier '{}' detected in '{}'. Exact version required for bubbling.").format(separator, pkg_spec))
                        return (pkg_name, None)
        return (pkg_spec.strip(), None)

    def _exorcise_ghost_entry(self, package_spec: str):
        """
        Surgically removes a non-existent package entry from the KB.
        If it's the last version of the package, it removes all traces,
        including the main package key and the index entry.
        """
        try:
            pkg_name, version = self._parse_package_spec(package_spec)
            if not pkg_name or not version:
                return
            c_name = canonicalize_name(pkg_name)
            safe_print(f'   -> 👻 Exorcising ghost entry: {c_name}=={version}')
            main_key = f'{self.redis_key_prefix}{c_name}'
            version_key = f'{main_key}:{version}'
            versions_set_key = f'{main_key}:installed_versions'
            index_key = f'{self.redis_env_prefix}index'
            with self.cache_client.pipeline() as pipe:
                pipe.delete(version_key)
                pipe.srem(versions_set_key, version)
                if self.cache_client.hget(main_key, 'active_version') == version:
                    pipe.hdel(main_key, 'active_version')
                pipe.hdel(main_key, f'bubble_version:{version}')
                pipe.execute()
            if self.cache_client.scard(versions_set_key) == 0:
                safe_print(f"    -> Last version of '{c_name}' removed. Deleting all traces from KB.")
                with self.cache_client.pipeline() as pipe:
                    pipe.delete(main_key)
                    pipe.delete(versions_set_key)
                    pipe.srem(index_key, c_name)
                    pipe.execute()
        except Exception as e:
            safe_print(_('   ⚠️  Warning: Could not exorcise ghost {}: {}').format(package_spec, e))

    def rebuild_package_kb(self, packages: List[str], force: bool=True, target_python_version: Optional[str]=None) -> int:
        """
        Forces a targeted KB rebuild and now intelligently detects and
        deletes "ghost" entries by comparing CANONICAL package names.
        """
        if not packages:
            return 0
        safe_print(_('🧠 Forcing targeted KB rebuild for: {}...').format(', '.join(packages)))
        if not self.cache_client:
            return 1
        try:
            gatherer = omnipkgMetadataGatherer(config=self.config, env_id=self.env_id, force_refresh=force, omnipkg_instance=self, target_context_version=target_python_version)
            found_distributions = gatherer.run(targeted_packages=packages)
            if found_distributions is None:
                found_distributions = []
            requested_specs_canonical = set()
            for spec in packages:
                try:
                    name, version = self._parse_package_spec(spec)
                    if name and version:
                        requested_specs_canonical.add(f'{canonicalize_name(name)}=={version}')
                except Exception:
                    continue
            found_specs_canonical = {f"{canonicalize_name(dist.metadata['Name'])}=={dist.version}" for dist in found_distributions}
            ghost_specs_canonical = requested_specs_canonical - found_specs_canonical
            if ghost_specs_canonical:
                original_spec_map = {f'{canonicalize_name(self._parse_package_spec(s)[0])}=={self._parse_package_spec(s)[1]}': s for s in packages if '==' in s}
                for canonical_spec in ghost_specs_canonical:
                    original_spec = original_spec_map.get(canonical_spec, canonical_spec)
                    self._exorcise_ghost_entry(original_spec)
            self._info_cache.clear()
            self._installed_packages_cache = None
            safe_print(f'   ✅ Knowledge base for {len(found_specs_canonical)} package(s) successfully rebuilt.')
            if ghost_specs_canonical:
                safe_print(_('   ✅ Exorcised {} ghost entries.').format(len(ghost_specs_canonical)))
            return 0
        except Exception as e:
            safe_print(_('    ❌ An unexpected error occurred during targeted KB rebuild: {}').format(e))
            traceback.print_exc()
            return 1

    def _register_package_in_knowledge_base(self, pkg_name: str, version: str, bubble_path: str, install_type: str):
        """
        Register a bubbled package in the knowledge base.
        This integrates with your existing knowledge base system.
        """
        try:
            package_info = {'name': pkg_name, 'version': version, 'install_type': install_type, 'path': bubble_path, 'created_at': self._get_current_timestamp()}
            key = 'package:{}:{}'.format(pkg_name, version)
            if hasattr(self, 'cache_client') and self.cache_client:
                import json
                self.cache_client.set(key, json.dumps(package_info))
                safe_print(_('📝 Registered {}=={} in knowledge base').format(pkg_name, version))
            else:
                safe_print(_('⚠️ Could not register {}=={}: No Redis connection').format(pkg_name, version))
        except Exception as e:
            safe_print(_('❌ Failed to register {}=={} in knowledge base: {}').format(pkg_name, version, e))

    def _get_current_timestamp(self) -> str:
        """Helper to get current timestamp for knowledge base entries."""
        import datetime
        return datetime.datetime.now().isoformat()

    def _find_package_installations(self, package_name: str) -> List[Dict]:
        """
        Find all installations of a package by querying the Redis knowledge base.
        This is the single source of truth for omnipkg's state.
        """
        found = []
        c_name = canonicalize_name(package_name)
        main_key = f'{self.redis_key_prefix}{c_name}'
        package_data = self.cache_client.hgetall(main_key)
        if not package_data:
            return []
        for key, value in package_data.items():
            if key == 'active_version':
                found.append({'name': package_data.get('name', c_name), 'version': value, 'type': 'active', 'path': 'Main Environment'})
            elif key.startswith('bubble_version:') and value == 'true':
                version = key.replace('bubble_version:', '')
                bubble_path = self.multiversion_base / '{}-{}'.format(package_data.get('name', c_name), version)
                found.append({'name': package_data.get('name', c_name), 'version': version, 'type': 'bubble', 'path': str(bubble_path)})
        return found

    def smart_uninstall(self, packages: List[str], force: bool=False, install_type: Optional[str]=None) -> int:
        if not self._connect_cache():
            return 1
        self._synchronize_knowledge_base_with_reality()
        core_deps = _get_core_dependencies()
        for pkg_spec in packages:
            safe_print(_('\nProcessing uninstall for: {}').format(pkg_spec))
            pkg_name, specific_version = self._parse_package_spec(pkg_spec)
            exact_pkg_name = canonicalize_name(pkg_name)
            all_installations_found = self._find_package_installations(exact_pkg_name)
            if all_installations_found:
                all_installations_found.sort(key=lambda x: (x['type'] != 'active', parse_version(x.get('version', '0'))), reverse=False)
            if not all_installations_found:
                safe_print(_("🤷 Package '{}' not found.").format(pkg_name))
                continue
            to_uninstall = all_installations_found
            if specific_version:
                to_uninstall = [inst for inst in to_uninstall if inst['version'] == specific_version]
                if not to_uninstall:
                    safe_print(_("🤷 Version '{}' of '{}' not found.").format(specific_version, pkg_name))
                    continue
            if install_type:
                to_uninstall = [inst for inst in to_uninstall if inst['type'] == install_type]
                if not to_uninstall:
                    safe_print(_('🤷 No installations match the specified criteria.').format(pkg_name))
                    continue
            elif not force and len(all_installations_found) > 1 and (not (specific_version or install_type)):
                safe_print(_("Found multiple installations for '{}':").format(pkg_name))
                numbered_installations = []
                for i, inst in enumerate(to_uninstall):
                    is_protected = inst['type'] == 'active' and (canonicalize_name(inst['name']) == 'omnipkg' or canonicalize_name(inst['name']) in core_deps)
                    status_tags = [inst['type']]
                    if is_protected:
                        status_tags.append('PROTECTED')
                    numbered_installations.append({'index': i + 1, 'installation': inst, 'is_protected': is_protected})
                    safe_print(_('  {}) v{} ({})').format(i + 1, inst['version'], ', '.join(status_tags)))
                if not numbered_installations:
                    safe_print(_('🤷 No versions available for selection.'))
                    continue
                try:
                    choice = input(_("🤔 Enter numbers to uninstall (e.g., '1,2'), 'all', or press Enter to cancel: ")).lower().strip()
                    if not choice:
                        safe_print(_('🚫 Uninstall cancelled.'))
                        continue
                    selected_indices = []
                    if choice == 'all':
                        selected_indices = [item['index'] for item in numbered_installations if not item['is_protected']]
                    else:
                        try:
                            selected_indices = {int(idx.strip()) for idx in choice.split(',')}
                        except ValueError:
                            safe_print(_('❌ Invalid input.'))
                            continue
                    to_uninstall = [item['installation'] for item in numbered_installations if item['index'] in selected_indices]
                except (KeyboardInterrupt, EOFError):
                    safe_print(_('\n🚫 Uninstall cancelled.'))
                    continue
            final_to_uninstall = []
            for item in to_uninstall:
                is_protected = item['type'] == 'active' and (canonicalize_name(item['name']) == 'omnipkg' or canonicalize_name(item['name']) in core_deps)
                if is_protected:
                    safe_print(_('⚠️  Skipping protected package: {} v{} (active)').format(item['name'], item['version']))
                else:
                    final_to_uninstall.append(item)
            if not final_to_uninstall:
                safe_print(_('🤷 No versions selected for uninstallation after protection checks.'))
                continue
            safe_print(_("\nPreparing to remove {} installation(s) for '{}':").format(len(final_to_uninstall), exact_pkg_name))
            for item in final_to_uninstall:
                safe_print(_('  - v{} ({})').format(item['version'], item['type']))
            if not force:
                confirm = input(_('🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
                if confirm != 'y':
                    safe_print(_('🚫 Uninstall cancelled.'))
                    continue
            for item in final_to_uninstall:
                if item['type'] == 'active':
                    safe_print(_("🗑️ Uninstalling '{}=={}' from main environment via pip...").format(item['name'], item['version']))
                    self._run_pip_uninstall([f"{item['name']}=={item['version']}"])
                elif item['type'] == 'bubble':
                    bubble_dir = Path(item['path'])
                    if bubble_dir.exists():
                        safe_print(_('🗑️  Deleting bubble directory: {}').format(bubble_dir.name))
                        shutil.rmtree(bubble_dir)
                safe_print(_('🧹 Cleaning up knowledge base for {} v{}...').format(item['name'], item['version']))
                c_name = canonicalize_name(item['name'])
                main_key = f'{self.redis_key_prefix}{c_name}'
                version_key = f"{main_key}:{item['version']}"
                versions_set_key = f'{main_key}:installed_versions'
                with self.cache_client.pipeline() as pipe:
                    pipe.delete(version_key)
                    pipe.srem(versions_set_key, item['version'])
                    if item['type'] == 'active':
                        pipe.hdel(main_key, 'active_version')
                    else:
                        pipe.hdel(main_key, f"bubble_version:{item['version']}")
                    pipe.execute()
                if self.cache_client.scard(versions_set_key) == 0:
                    safe_print(_("    -> Last version of '{}' removed. Deleting all traces.").format(c_name))
                    self.cache_client.delete(main_key, versions_set_key)
                    self.cache_client.srem(f'{self.redis_key_prefix}index', c_name)
            safe_print(_('✅ Uninstallation complete.'))
            self._save_last_known_good_snapshot()
        return 0

    def revert_to_last_known_good(self, force: bool=False):
        """Compares the current env to the last snapshot and restores it."""
        if not self._connect_cache():
            return 1
        snapshot_key = f'{self.redis_key_prefix}snapshot:last_known_good'
        snapshot_data = self.cache_client.get(snapshot_key)
        if not snapshot_data:
            safe_print(_("❌ No 'last known good' snapshot found. Cannot revert."))
            safe_print(_('   Run an `omnipkg install` or `omnipkg uninstall` command to create one.'))
            return 1
        safe_print(_('⚖️  Comparing current environment to the last known good snapshot...'))
        snapshot_state = json.loads(snapshot_data)
        current_state = self.get_installed_packages(live=True)
        snapshot_keys = set(snapshot_state.keys())
        current_keys = set(current_state.keys())
        to_install = ['{}=={}'.format(pkg, ver) for pkg, ver in snapshot_state.items() if pkg not in current_keys]
        to_uninstall = [pkg for pkg in current_keys if pkg not in snapshot_keys]
        to_fix = [f'{pkg}=={snapshot_state[pkg]}' for pkg in snapshot_keys & current_keys if snapshot_state[pkg] != current_state[pkg]]
        if not to_install and (not to_uninstall) and (not to_fix):
            safe_print(_('✅ Your environment is already in the last known good state. No action needed.'))
            return 0
        safe_print(_('\n📝 The following actions will be taken to restore the environment:'))
        if to_uninstall:
            safe_print(_('  - Uninstall: {}').format(', '.join(to_uninstall)))
        if to_install:
            safe_print(_('  - Install: {}').format(', '.join(to_install)))
        if to_fix:
            safe_print(_('  - Fix Version: {}').format(', '.join(to_fix)))
        if not force:
            confirm = input(_('\n🤔 Are you sure you want to proceed? (y/N): ')).lower().strip()
            if confirm != 'y':
                safe_print(_('🚫 Revert cancelled.'))
                return 1
        safe_print(_('\n🚀 Starting revert operation...'))
        original_strategy = self.config.get('install_strategy', 'multiversion')
        strategy_changed = False
        try:
            if original_strategy != 'latest-active':
                safe_print(_('   ⚙️  Temporarily setting install strategy to latest-active for revert...'))
                try:
                    result = subprocess.run(['omnipkg', 'config', 'set', 'install_strategy', 'latest-active'], capture_output=True, text=True, check=True)
                    strategy_changed = True
                    safe_print(_('   ✅ Install strategy temporarily set to latest-active'))
                    from omnipkg.core import ConfigManager
                    self.config = ConfigManager().config
                except Exception as e:
                    safe_print(_('   ⚠️  Failed to set install strategy to latest-active: {}').format(e))
                    safe_print(_('   ℹ️  Continuing with current strategy: {}').format(original_strategy))
            else:
                safe_print(_('   ℹ️  Install strategy already set to latest-active'))
            if to_uninstall:
                self.smart_uninstall(to_uninstall, force=True)
            packages_to_install = to_install + to_fix
            if packages_to_install:
                self.smart_install(packages_to_install)
            safe_print(_('\n✅ Environment successfully reverted to the last known good state.'))
            return 0
        finally:
            if strategy_changed and original_strategy != 'latest-active':
                safe_print(_('   🔄 Restoring original install strategy: {}').format(original_strategy))
                try:
                    result = subprocess.run(['omnipkg', 'config', 'set', 'install_strategy', original_strategy], capture_output=True, text=True, check=True)
                    safe_print(_('   ✅ Install strategy restored to: {}').format(original_strategy))
                    from omnipkg.core import ConfigManager
                    self.config = ConfigManager().config
                except Exception as e:
                    safe_print(_('   ⚠️  Failed to restore install strategy to {}: {}').format(original_strategy, e))
                    safe_print(_('   💡 You may need to manually restore it with: omnipkg config set install_strategy {}').format(original_strategy))
            elif not strategy_changed:
                safe_print(_('   ℹ️  Install strategy unchanged: {}').format(original_strategy))

    def _check_package_satisfaction(self, packages: List[str], strategy: str) -> dict:
        """
        ### THE DEFINITIVE FIX ###
        Checks if a list of requirements is satisfied by querying the Redis Knowledge Base,
        which is the single source of truth for omnipkg.
        """
        satisfied_specs = set()
        needs_install_specs = []
        for package_spec in packages:
            is_satisfied = False
            try:
                pkg_name, requested_version = self._parse_package_spec(package_spec)
                if not requested_version:
                    needs_install_specs.append(package_spec)
                    continue
                c_name = canonicalize_name(pkg_name)
                main_key = f'{self.redis_key_prefix}{c_name}'
                version_key = f'{main_key}:{requested_version}'
                if not self.cache_client.exists(version_key):
                    needs_install_specs.append(package_spec)
                    continue
                package_data = self.cache_client.hgetall(main_key)
                if package_data.get('active_version') == requested_version:
                    is_satisfied = True
                if not is_satisfied and strategy == 'stable-main':
                    if package_data.get(f'bubble_version:{requested_version}') == 'true':
                        is_satisfied = True
                if is_satisfied:
                    satisfied_specs.add(package_spec)
                else:
                    needs_install_specs.append(package_spec)
            except Exception:
                needs_install_specs.append(package_spec)
        return {'all_satisfied': len(needs_install_specs) == 0, 'satisfied': sorted(list(satisfied_specs)), 'needs_install': needs_install_specs}

    def get_package_info(self, package_name: str, version: str) -> Optional[Dict]:
        if not self.cache_client:
            self._connect_cache()
        main_key = f'{self.redis_key_prefix}{package_name.lower()}'
        if version == 'active':
            version = self.cache_client.hget(main_key, 'active_version')
            if not version:
                return None
        version_key = f'{main_key}:{version}'
        return self.cache_client.hgetall(version_key)

    def switch_active_python(self, version: str) -> int:
        """
        Switches the active Python context for the entire environment.
        This updates the config file and the default `python` symlinks.
        """
        safe_print(_('🐍 Switching active Python context to version {}...').format(version))
        managed_interpreters = self.interpreter_manager.list_available_interpreters()
        target_interpreter_path = managed_interpreters.get(version)
        if not target_interpreter_path:
            safe_print(_('❌ Error: Python version {} is not managed by this environment.').format(version))
            safe_print(_("   Run 'omnipkg list python' to see managed interpreters."))
            safe_print(f"   If Python {version} is 'Discovered', first adopt it with: omnipkg python adopt {version}")
            return 1
        target_interpreter_str = str(target_interpreter_path)
        safe_print(_('   - Found managed interpreter at: {}').format(target_interpreter_str))
        new_paths = self.config_manager._get_paths_for_interpreter(target_interpreter_str)
        if not new_paths:
            safe_print(f'❌ Error: Could not determine paths for Python {version}. Aborting switch.')
            return 1
        safe_print(_('   - Updating configuration to new context...'))
        self.config_manager.set('python_executable', new_paths['python_executable'])
        self.config_manager.set('site_packages_path', new_paths['site_packages_path'])
        self.config_manager.set('multiversion_base', new_paths['multiversion_base'])
        safe_print(_('   - ✅ Configuration saved.'))
        safe_print(_('   - Updating default `python` symlinks...'))
        venv_path = Path(sys.prefix)
        try:
            self.config_manager._update_default_python_links(venv_path, target_interpreter_path)
        except Exception as e:
            safe_print(_('   - ❌ Failed to update symlinks: {}').format(e))
        safe_print(_('\n🎉 Successfully switched omnipkg context to Python {}!').format(version))
        safe_print('   The configuration has been updated. To activate the new interpreter')
        safe_print(_('   in your shell, you MUST re-source your activate script:'))
        safe_print(_('\n      source {}\n').format(venv_path / 'bin' / 'activate'))
        safe_print(_('Just kidding, omnipkg handled it for you automatically!'))
        return 0

    def _resolve_package_versions(self, packages: List[str]) -> List[str]:
        """
        Takes a list of packages and ensures every entry has an explicit version.
        Uses the PyPI API to find the latest version for packages specified without one.
        """
        safe_print(_('🔎 Resolving package versions via PyPI API...'))
        resolved_packages = []
        for pkg_spec in packages:
            if '==' in pkg_spec:
                resolved_packages.append(pkg_spec)
                continue
            pkg_name = self._parse_package_spec(pkg_spec)[0]
            safe_print(_("    -> Finding latest version for '{}'...").format(pkg_name))
            target_version = self._get_latest_version_from_pypi(pkg_name)
            if target_version:
                new_spec = f'{pkg_name}=={target_version}'
                safe_print(_("    ✅ Resolved '{}' to '{}'").format(pkg_name, new_spec))
                resolved_packages.append(new_spec)
            else:
                safe_print(_("    ⚠️  Could not resolve a version for '{}' via PyPI. Skipping.").format(pkg_name))
        return resolved_packages

    def _find_python_executable_in_dir(self, directory: Path) -> Optional[Path]:
        """Find the Python executable in a directory, checking common locations."""
        # Check standard locations first
        if platform.system() == "Windows":
            search_paths = [
                directory / 'python.exe',
                directory / 'Scripts' / 'python.exe',
            ]
        else:
            search_paths = [
                directory / 'bin' / 'python3',
                directory / 'bin' / 'python',
            ]

        for path in search_paths:
            if path.is_file() and os.access(path, os.X_OK):
                return path

        # If not found, do a broader search
        for exe in directory.rglob('python.exe' if platform.system() == "Windows" else 'python3'):
            if exe.is_file() and os.access(exe, os.X_OK):
                return exe
        
        return None

    def _get_file_list_for_packages_live(self, package_names: List[str]) -> Dict[str, List[str]]:
        """
        Runs a subprocess in the configured Python context to get the
        authoritative file list for a batch of packages. This is the ONLY
        safe way to inspect a different Python environment.
        """
        if not package_names:
            return {}
        python_exe = self.config.get('python_executable', sys.executable)
        script = f'\nimport sys, json, importlib.metadata\nresults = {{}}\nfor pkg_name in {package_names!r}:\n    try:\n        dist = importlib.metadata.distribution(pkg_name)\n        if dist.files:\n            results[pkg_name] = [str(dist.locate_file(f)) for f in dist.files if dist.locate_file(f).is_file()]\n    except Exception:\n        results[pkg_name] = []\nprint(json.dumps(results))\n'
        try:
            cmd = [python_exe, '-I', '-c', script]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError, Exception) as e:
            safe_print(f'   ⚠️  Could not get file list from live environment: {e}')
            return {name: [] for name in package_names}

    def _run_pip_install(self, packages: List[str], force_reinstall: bool=False, target_directory: Optional[Path]=None) -> int:
        """
        Runs `pip install` with LIVE, STREAMING output and automatic recovery
        from corrupted 'no RECORD file' errors. Can now target a specific directory.
        """
        if not packages:
            return 0
        cmd = [self.config['python_executable'], '-u', '-m', 'pip', 'install']
        if force_reinstall:
            cmd.append('--upgrade')
        if target_directory:
            safe_print(_('   - Targeting installation to: {}').format(target_directory))
            cmd.extend(['--target', str(target_directory)])
        cmd.extend(packages)
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', bufsize=1, universal_newlines=True)
            stdout_lines, stderr_lines = ([], [])
            for line in process.stdout:
                safe_print(line, end='')
                stdout_lines.append(line)
            for line in process.stderr:
                safe_print(line, end='', file=sys.stderr)
                stderr_lines.append(line)
            return_code = process.wait()
            if return_code == 0:
                return 0
            full_stderr = ''.join(stderr_lines)
            record_file_pattern = 'no RECORD file was found for ([\\w\\-]+)'
            match = re.search(record_file_pattern, full_stderr)
            if match:
                package_name = match.group(1)
                safe_print('\n' + '=' * 60)
                safe_print(_("🛡️  AUTO-RECOVERY: Detected corrupted package '{}'.").format(package_name))
                cleanup_path = target_directory if target_directory else Path(self.config.get('site_packages_path'))
                if self._brute_force_package_cleanup(package_name, cleanup_path):
                    safe_print(_('   - Retrying installation on clean environment...'))
                    retry_process = subprocess.run(cmd, capture_output=True, text=True)
                    if retry_process.returncode == 0:
                        safe_print(retry_process.stdout)
                        safe_print(_('   - ✅ Recovery successful!'))
                        return 0
                    else:
                        safe_print(_('   - ❌ Recovery failed. Pip error after cleanup:'))
                        safe_print(retry_process.stderr)
                        return 1
                else:
                    return 1
            return return_code
        except Exception as e:
            safe_print(_('    ❌ An unexpected error occurred during pip install: {}').format(e))
            return 1

    def _run_pip_uninstall(self, packages: List[str]) -> int:
        """Runs `pip uninstall` with LIVE, STREAMING output."""
        if not packages:
            return 0
        try:
            cmd = [self.config['python_executable'], '-u', '-m', 'pip', 'uninstall', '-y'] + packages
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', bufsize=1, universal_newlines=True)
            safe_print()
            for line in iter(process.stdout.readline, ''):
                safe_print(line, end='')
            process.stdout.close()
            return_code = process.wait()
            return return_code
        except Exception as e:
            safe_print(_('    ❌ An unexpected error occurred during pip uninstall: {}').format(e))
            return 1

    def _run_uv_install(self, packages: List[str]) -> int:
        """Runs `uv install` for a list of packages."""
        if not packages:
            return 0
        try:
            cmd = [self.config['uv_executable'], 'install', '--quiet'] + packages
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            safe_print(result.stdout)
            return result.returncode
        except FileNotFoundError:
            safe_print(_("❌ Error: 'uv' executable not found. Please ensure uv is installed and in your PATH."))
            return 1
        except subprocess.CalledProcessError as e:
            safe_print(_('❌ uv install command failed with exit code {}:').format(e.returncode))
            safe_print(e.stderr)
            return e.returncode
        except Exception as e:
            safe_print(_('    ❌ An unexpected error toccurred during uv install: {}').format(e))
            return 1

    def _run_uv_uninstall(self, packages: List[str]) -> int:
        """Runs `uv pip uninstall` for a list of packages."""
        if not packages:
            return 0
        try:
            cmd = [self.config['uv_executable'], 'pip', 'uninstall'] + packages
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            safe_print(result.stdout)
            return result.returncode
        except FileNotFoundError:
            safe_print(_("❌ Error: 'uv' executable not found. Please ensure uv is installed and in your PATH."))
            return 1
        except subprocess.CalledProcessError as e:
            safe_print(_('❌ uv uninstall command failed with exit code {}:').format(e.returncode))
            safe_print(e.stderr)
            return e.returncode
        except Exception as e:
            safe_print(_('    ❌ An unexpected error occurred during uv uninstall: {}').format(e))
            return 1

    def _test_install_to_get_compatible_version(self, package_name: str) -> Optional[str]:
        """
        Test-installs a package to a temporary directory to get pip's actual compatibility
        error messages, then parses them to find the latest truly compatible version.
        
        OPTIMIZED: If installation starts succeeding, we IMMEDIATELY detect it and cancel
        to avoid wasting time, then return the version info for the main smart installer.
        """
        safe_print(_(" -> Test-installing '{}' to discover latest compatible version...").format(package_name))
        temp_dir = None
        process = None
        try:
            temp_dir = tempfile.mkdtemp(prefix=f'omnipkg_test_{package_name}_')
            temp_path = Path(temp_dir)
            safe_print(_('    Using temporary directory: {}').format(temp_path))
            cmd = [self.config['python_executable'], '-m', 'pip', 'install', '--target', str(temp_path), '--no-deps', '--no-cache-dir', package_name]
            safe_print(_('    Running: {}').format(' '.join(cmd)))
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            stdout_lines = []
            stderr_lines = []
            success_detected = False
            detected_version = None

            def read_stdout():
                nonlocal stdout_lines, success_detected, detected_version
                for line in iter(process.stdout.readline, ''):
                    if line:
                        stdout_lines.append(line)
                        safe_print(_('    [STDOUT] {}').format(line.strip()))
                        early_success_patterns = [f'Collecting\\s+{re.escape(package_name)}==([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)', f'Downloading\\s+{re.escape(package_name)}-([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)-', f'Successfully downloaded\\s+{re.escape(package_name)}-([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)']
                        for pattern in early_success_patterns:
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match and (not success_detected):
                                detected_version = match.group(1)
                                safe_print(_('    🚀 EARLY SUCCESS DETECTED! Version {} is compatible!').format(detected_version))
                                safe_print(_('    ⚡ Canceling temp install to save time - will use smart installer'))
                                success_detected = True
                                break
                        if success_detected:
                            break
                process.stdout.close()

            def read_stderr():
                nonlocal stderr_lines
                for line in iter(process.stderr.readline, ''):
                    if line:
                        stderr_lines.append(line)
                        safe_print(_('    [STDERR] {}').format(line.strip()))
                process.stderr.close()
            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            start_time = time.time()
            timeout = 180
            while process.poll() is None and time.time() - start_time < timeout:
                if success_detected:
                    safe_print(_('    ⚡ Terminating test install process (PID: {})').format(process.pid))
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    break
                time.sleep(0.1)
            stdout_thread.join(timeout=2)
            stderr_thread.join(timeout=2)
            if success_detected and detected_version:
                safe_print(_('    ✅ Early success! Latest compatible version: {}').format(detected_version))
                safe_print('    🎯 This version will be passed to smart installer for main installation')
                return detected_version
            if process.poll() is None:
                safe_print(_('    ⏰ Test installation timed out, terminating...'))
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                return None
            return_code = process.returncode
            full_stdout = ''.join(stdout_lines)
            full_stderr = ''.join(stderr_lines)
            full_output = full_stdout + full_stderr
            if return_code == 0:
                safe_print(_('    ✅ Test installation completed successfully'))
                install_patterns = [_('Installing collected packages:\\s+{}-([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)').format(re.escape(package_name)), f'Successfully installed\\s+{re.escape(package_name)}-([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)', f'Collecting\\s+{re.escape(package_name)}==([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)']
                for pattern in install_patterns:
                    match = re.search(pattern, full_output, re.IGNORECASE | re.MULTILINE)
                    if match:
                        version = match.group(1)
                        safe_print(_('    ✅ Successfully installed latest compatible version: {}').format(version))
                        return version
                try:
                    for item in temp_path.glob(f"{package_name.replace('-', '_')}-*.dist-info"):
                        try:
                            dist_info_name = item.name
                            version_match = re.search(f"^{re.escape(package_name.replace('-', '_'))}-([0-9a-zA-Z.+-]+)\\.dist-info", dist_info_name)
                            if version_match:
                                version = version_match.group(1)
                                safe_print(f'    ✅ Found installed version from dist-info: {version}')
                                return version
                        except Exception as e:
                            safe_print(_('    Warning: Could not check dist-info: {}').format(e))
                except Exception as e:
                    safe_print(_('    Warning: Could not check dist-info: {}').format(e))
                safe_print(_("    ⚠️ Installation succeeded but couldn't determine version"))
                return None
            else:
                safe_print(_('    ❌ Test installation failed (exit code {})').format(return_code))
                safe_print('    📋 Parsing error output for available versions...')
                version_list_patterns = ['from versions:\\s*([^)]+)\\)', 'available versions:\\s*([^\\n\\r]+)', '\\(from versions:\\s*([^)]+)\\)']
                compatible_versions = []
                for pattern in version_list_patterns:
                    match = re.search(pattern, full_output, re.IGNORECASE | re.DOTALL)
                    if match:
                        versions_text = match.group(1).strip()
                        safe_print(_('    Found versions string: {}').format(versions_text))
                        raw_versions = [v.strip() for v in versions_text.split(',')]
                        for raw_version in raw_versions:
                            clean_version = raw_version.strip(' \'"')
                            if re.match('^[0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?$', clean_version):
                                compatible_versions.append(clean_version)
                        break
                if compatible_versions:
                    try:
                        from packaging.version import parse as parse_version
                        stable_versions = [v for v in compatible_versions if not re.search('[a-zA-Z]', v)]
                        versions_to_sort = stable_versions if stable_versions else compatible_versions
                        sorted_versions = sorted(versions_to_sort, key=parse_version, reverse=True)
                        latest_compatible = sorted_versions[0]
                        safe_print(_('    ✅ Found {} compatible versions').format(len(compatible_versions)))
                        safe_print(_('    ✅ Latest compatible version: {}').format(latest_compatible))
                        return latest_compatible
                    except Exception as e:
                        safe_print(_('    ❌ Error sorting versions: {}').format(e))
                        if compatible_versions:
                            fallback_version = compatible_versions[-1]
                            safe_print(_('    ⚠️ Using fallback version: {}').format(fallback_version))
                            return fallback_version
                python_req_pattern = 'Requires-Python\\s*>=([0-9]+\\.[0-9]+)'
                python_req_matches = re.findall(python_req_pattern, full_output)
                if python_req_matches:
                    safe_print(_('    📋 Found Python version requirements: {}').format(', '.join(set(python_req_matches))))
                safe_print('    ❌ Could not extract compatible versions from error output')
                return None
        except Exception as e:
            safe_print(_('    ❌ Unexpected error during test installation: {}').format(e))
            return None
        finally:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    try:
                        process.kill()
                        process.wait()
                    except:
                        pass
            if temp_dir and Path(temp_dir).exists():
                try:
                    shutil.rmtree(temp_dir)
                    safe_print(_('    🧹 Cleaned up temporary directory'))
                except Exception as e:
                    safe_print(_('    ⚠️ Warning: Could not clean up temp directory {}: {}').format(temp_dir, e))

    def _quick_compatibility_check(self, package_name: str, version_to_test: str=None) -> Optional[str]:
        """
        Quickly test if a specific version (or latest) is compatible by attempting
        a pip install and parsing any compatibility errors for available versions.
        
        Returns the latest compatible version found, or None if can't determine.
        """
        safe_print(f'    💫 Quick compatibility check for {package_name}' + (_('=={}').format(version_to_test) if version_to_test else ''))
        try:
            package_spec = f'{package_name}=={version_to_test}' if version_to_test else package_name
            cmd = [self.config['python_executable'], '-m', 'pip', 'install', '--dry-run', '--no-deps', package_spec]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            full_output = result.stdout + result.stderr
            if result.returncode == 0:
                install_patterns = [f'Would install\\s+{re.escape(package_name)}-([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)', f'Collecting\\s+{re.escape(package_name)}==([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)']
                for pattern in install_patterns:
                    match = re.search(pattern, full_output, re.IGNORECASE)
                    if match:
                        compatible_version = match.group(1)
                        safe_print(_('    ✅ Latest version {} is compatible!').format(compatible_version))
                        return compatible_version
                return version_to_test if version_to_test else None
            else:
                safe_print('    📋 Parsing compatibility error for available versions...')
                version_list_patterns = ['from versions:\\s*([^)]+)\\)', 'available versions:\\s*([^\\n\\r]+)', '\\(from versions:\\s*([^)]+)\\)']
                for pattern in version_list_patterns:
                    match = re.search(pattern, full_output, re.IGNORECASE | re.DOTALL)
                    if match:
                        versions_text = match.group(1).strip()
                        safe_print(_('    📋 Found versions: {}').format(versions_text))
                        compatible_versions = []
                        raw_versions = [v.strip(' \'"') for v in versions_text.split(',')]
                        for raw_version in raw_versions:
                            if re.match('^[0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?$', raw_version):
                                compatible_versions.append(raw_version)
                        if compatible_versions:
                            try:
                                from packaging.version import parse as parse_version
                                stable_versions = [v for v in compatible_versions if not re.search('[a-zA-Z]', v)]
                                versions_to_sort = stable_versions if stable_versions else compatible_versions
                                latest_compatible = sorted(versions_to_sort, key=parse_version, reverse=True)[0]
                                safe_print(_('    🎯 Latest compatible version: {}').format(latest_compatible))
                                return latest_compatible
                            except Exception as e:
                                safe_print(_('    ⚠️ Error sorting versions: {}').format(e))
                                return compatible_versions[-1] if compatible_versions else None
                safe_print('    ❌ Could not parse compatible versions from error')
                return None
        except Exception as e:
            safe_print(_('    ❌ Quick compatibility check failed: {}').format(e))
            return None

    def _get_latest_version_from_pypi(self, package_name: str) -> Optional[str]:
        """
        Gets the latest *compatible* version of a package by leveraging pip's own
        dependency resolver with optimized test installation that cancels early on success.
        
        OPTIMIZED FLOW:
        1. Get latest version from PyPI
        2. Check if that exact version is already installed in main environment
        3. If yes: return it immediately (fastest path!)
        4. If no: Test install in temp directory with early success detection
        5. If compatible: immediately cancel temp install, return version for smart installer
        6. If incompatible: parse error output for latest compatible version
        7. Fallback to dry-run method if needed
        """
        safe_print(f" -> Finding latest COMPATIBLE version for '{package_name}' using super-optimized approach...")
        latest_pypi_version = None
        compatible_version = None
        try:
            safe_print(f"    🌐 Fetching latest version from PyPI for '{package_name}'...")
            response = http_requests.get(f'https://pypi.org/pypi/{package_name}/json', timeout=10)
            if response.status_code == 200:
                pypi_data = response.json()
                latest_pypi_version = pypi_data['info']['version']
                safe_print(_('    📦 Latest PyPI version: {}').format(latest_pypi_version))
                safe_print(f'    🔍 Checking if version {latest_pypi_version} is already installed...')
                cmd_check = [self.config['python_executable'], '-m', 'pip', 'show', package_name]
                result_check = subprocess.run(cmd_check, capture_output=True, text=True, check=False, timeout=30)
                if result_check.returncode == 0:
                    version_match = re.search('^Version:\\s*([^\\s\\n\\r]+)', result_check.stdout, re.MULTILINE | re.IGNORECASE)
                    if version_match:
                        installed_version = version_match.group(1).strip()
                        safe_print(_('    📋 Currently installed version: {}').format(installed_version))
                        if installed_version == latest_pypi_version:
                            safe_print(_('    🚀 JACKPOT! Latest PyPI version {} is already installed!').format(latest_pypi_version))
                            safe_print(_('    ⚡ Skipping all test installations - using installed version'))
                            return latest_pypi_version
                        else:
                            safe_print(f'    📋 Installed version ({installed_version}) differs from latest PyPI ({latest_pypi_version})')
                            safe_print('    🧪 Will test if latest PyPI version is compatible...')
                    else:
                        safe_print('    ⚠️ Could not parse installed version from pip show output')
                else:
                    safe_print(_("    📋 Package '{}' is not currently installed").format(package_name))
                    safe_print('    🧪 Will test if latest PyPI version is compatible...')
            elif response.status_code == 404:
                safe_print(_("    ❌ Package '{}' not found on PyPI (404 error)").format(package_name))
                safe_print(_("    💡 This usually means the package name doesn't exist or contains invalid characters"))
                safe_print(_('    📝 Please check the package name spelling and format'))
                return None
            else:
                safe_print(_('    ❌ Could not fetch PyPI data (status: {})').format(response.status_code))
                safe_print(_('    🧪 Falling back to test installation approach...'))
        except http_requests.exceptions.RequestException as e:
            safe_print(_('    ❌ Network error checking PyPI: {}').format(e))
            safe_print(_('    🧪 Falling back to test installation approach...'))
        except Exception as e:
            safe_print(_('    ❌ Error checking PyPI: {}').format(e))
            safe_print(_('    🧪 Falling back to test installation approach...'))
        if latest_pypi_version:
            safe_print('    🧪 Testing latest PyPI version compatibility with quick install attempt...')
            try:
                compatible_version = self._quick_compatibility_check(package_name, latest_pypi_version)
                if compatible_version:
                    safe_print(f'    🎯 Found compatible version {compatible_version} - passing directly to smart installer!')
                    return compatible_version
            except Exception as e:
                safe_print(_('    ⚠️ Quick compatibility check failed: {}').format(e))
                compatible_version = None
        if not compatible_version:
            safe_print('    🧪 Starting optimized test installation with early success detection...')
            try:
                test_result = self._test_install_to_get_compatible_version(package_name)
                if test_result:
                    safe_print(f'    🎯 Test approach successful! Version {test_result} ready for smart installer')
                    return test_result
            except Exception as e:
                safe_print(_('    ⚠️ Test installation approach failed: {}').format(e))
        safe_print(_(" -> Optimized test installation didn't work, falling back to dry-run method..."))
        try:
            cmd = [self.config['python_executable'], '-m', 'pip', 'install', '--dry-run', '--verbose', '--no-deps', f'{package_name}']
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=120, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            output_to_search = result.stdout + result.stderr
            if result.returncode != 0:
                error_patterns = ['No matching distribution found', 'Could not find a version', 'ERROR: No matching distribution found', 'Package .* not found', 'Invalid requirement']
                for pattern in error_patterns:
                    if re.search(pattern, output_to_search, re.IGNORECASE):
                        safe_print(_("    ❌ Package '{}' appears to not exist or be accessible").format(package_name))
                        safe_print(f'    💡 Pip error suggests no compatible version was found')
                        return None
            if result.returncode != 0 or not output_to_search.strip():
                safe_print(_('    [pip debug] Exit code: {}, investigating alternative methods...').format(result.returncode))
            already_satisfied_patterns = [_('Requirement already satisfied:\\s+{}\\s+in\\s+[^\\s]+\\s+\\(([^)]+)\\)').format(re.escape(package_name)), _('Requirement already satisfied:\\s+{}==([^\\s]+)').format(re.escape(package_name)), _('Requirement already satisfied:\\s+{}-([^\\s]+)').format(re.escape(package_name))]
            for pattern in already_satisfied_patterns:
                match = re.search(pattern, output_to_search, re.IGNORECASE | re.MULTILINE)
                if match:
                    version = match.group(1).strip()
                    safe_print(f' ✅ Package already installed with version: {version}')
                    if re.match('^[0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?$', version):
                        return version
                    else:
                        safe_print(f" ⚠️  Version '{version}' has invalid format, continuing search...")
                        continue
            if not output_to_search.strip() or result.returncode != 0:
                safe_print(_(' -> Trying alternative approach: pip index versions...'))
                cmd_alt = [self.config['python_executable'], '-m', 'pip', 'index', 'versions', package_name]
                result_alt = subprocess.run(cmd_alt, capture_output=True, text=True, check=False, timeout=60)
                if result_alt.returncode == 0 and result_alt.stdout.strip():
                    version_match = re.search(f'{re.escape(package_name)}\\s*\\(([^,)]+)', result_alt.stdout)
                    if version_match:
                        version = version_match.group(1).strip()
                        safe_print(_(' ✅ Found latest version via pip index: {}').format(version))
                        return version
                else:
                    alt_output = result_alt.stdout + result_alt.stderr
                    if re.search('No matching distribution found|Package .* not found', alt_output, re.IGNORECASE):
                        safe_print(_("    ❌ Package '{}' not found via pip index versions").format(package_name))
                        return None
                safe_print(_(' -> Trying pip download approach...'))
                cmd_download = [self.config['python_executable'], '-m', 'pip', 'download', '--dry-run', '--no-deps', package_name]
                result_download = subprocess.run(cmd_download, capture_output=True, text=True, check=False, timeout=60)
                output_to_search = result_download.stdout + result_download.stderr
                if result_download.returncode != 0:
                    safe_print(_('    [pip download debug] Exit code: {}').format(result_download.returncode))
                    if re.search('No matching distribution found|Could not find a version', output_to_search, re.IGNORECASE):
                        safe_print(_("    ❌ Package '{}' not found via pip download").format(package_name))
                        return None
            patterns = [_('(?:Would install|Installing collected packages:|Collecting)\\s+{}-([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)').format(re.escape(package_name)), f'{re.escape(package_name)}==([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)', f'Downloading\\s+{re.escape(package_name)}-([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)-', f'{re.escape(package_name)}\\s+([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)', f'{re.escape(package_name)}>=([0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?)']
            for i, pattern in enumerate(patterns, 1):
                match = re.search(pattern, output_to_search, re.IGNORECASE | re.MULTILINE)
                if match:
                    version = match.group(1)
                    safe_print(_(' ✅ Pip resolver identified latest compatible version: {} (pattern {})').format(version, i))
                    if re.match('^[0-9]+(?:\\.[0-9]+)*(?:[a-zA-Z0-9\\.-_]*)?$', version):
                        return version
                    else:
                        safe_print(f" ⚠️  Version '{version}' has invalid format, continuing search...")
                        continue
            if 'Requirement already satisfied' in output_to_search:
                safe_print(' -> Package appears to be installed, checking with pip list...')
                try:
                    result_list = subprocess.run(f"{self.config['python_executable']} -m pip list --format=freeze | grep -i '^{package_name}=='", shell=True, capture_output=True, text=True, timeout=30)
                    if result_list.returncode == 0 and result_list.stdout.strip():
                        list_match = re.search(f'^{re.escape(package_name)}==([^\\s]+)', result_list.stdout, re.IGNORECASE | re.MULTILINE)
                        if list_match:
                            version = list_match.group(1).strip()
                            safe_print(_(' ✅ Found installed version via pip list: {}').format(version))
                            return version
                except Exception as e:
                    safe_print(_(' -> pip list approach failed: {}').format(e))
            safe_print(f" ❌ Could not find or resolve a compatible version for package '{package_name}'.")
            safe_print(_(' ❌ This might indicate:'))
            safe_print(_("   1) Package doesn't exist on PyPI"))
            safe_print(_('   2) Package name is misspelled or contains invalid characters'))
            safe_print('   3) No compatible version exists for your Python environment')
            safe_print(_('   4) Network connectivity issues'))
            safe_print(_('   5) Package requires different installation method'))
            return None
        except subprocess.TimeoutExpired:
            safe_print(f" ❌ Pip resolver timed out while resolving '{package_name}'.")
            safe_print(_(' 💡 This might indicate network issues or a very complex dependency tree.'))
            return None
        except Exception as e:
            safe_print(f" ❌ An unexpected error occurred while running the pip resolver for '{package_name}': {e}")
            return None

    def get_available_versions(self, package_name: str) -> List[str]:
        """
        Correctly gets all available versions (active and bubbled) for a package
        by checking all relevant keys in the knowledge base.
        """
        c_name = canonicalize_name(package_name)
        main_key = f'{self.redis_key_prefix}{c_name}'
        versions = set()
        try:
            versions.update(self.cache_client.smembers(_('{}:installed_versions').format(main_key)))
            active_version = self.cache_client.hget(main_key, 'active_version')
            if active_version:
                versions.add(active_version)
            return sorted(list(versions), key=parse_version, reverse=True)
        except Exception as e:
            safe_print(_('⚠️ Could not retrieve versions for {}: {}').format(package_name, e))
            return []

    def list_packages(self, pattern: str=None) -> int:
        if not self._connect_cache():
            return 1
        self._synchronize_knowledge_base_with_reality()
        all_pkg_names = self.cache_client.smembers(f'{self.redis_key_prefix}index')
        if pattern:
            all_pkg_names = {name for name in all_pkg_names if pattern.lower() in name.lower()}
        safe_print(_('📋 Found {} matching package(s):').format(len(all_pkg_names)))
        for pkg_name in sorted(list(all_pkg_names)):
            main_key = f'{self.redis_key_prefix}{pkg_name}'
            package_data = self.cache_client.hgetall(main_key)
            display_name = package_data.get('name', pkg_name)
            active_version = package_data.get('active_version')
            all_versions = self.get_available_versions(pkg_name)
            safe_print(_('\n- {}:').format(display_name))
            if not all_versions:
                safe_print(_('  (No versions found in knowledge base)'))
                continue
            for version in all_versions:
                if version == active_version:
                    safe_print(_('  ✅ {} (active)').format(version))
                else:
                    safe_print(_('  🫧 {} (bubble)').format(version))
        return 0

    def show_multiversion_status(self) -> int:
        if not self._connect_cache():
            return 1
        self._synchronize_knowledge_base_with_reality(verbose=True)
        safe_print(_('🔄 omnipkg System Status'))
        safe_print('=' * 50)
        safe_print(_("🛠️ Environment broken by pip or uv? Run 'omnipkg revert' to restore the last known good state! 🚑"))
        try:
            pip_version = version('pip')
            safe_print(_('\n🔒 Pip in Jail (main environment)'))
            safe_print(_('    😈 Locked up for causing chaos in the main env! 🔒 (v{})').format(pip_version))
        except importlib.metadata.PackageNotFoundError:
            safe_print(_('\n🔒 Pip in Jail (main environment)'))
            safe_print(_('    🚫 Pip not found in the main env. Escaped or never caught!'))
        try:
            uv_version = version('uv')
            safe_print(_('🔒 UV in Jail (main environment)'))
            safe_print(_('    😈 Speedy troublemaker locked up in the main env! 🔒 (v{})').format(uv_version))
        except importlib.metadata.PackageNotFoundError:
            safe_print(_('🔒 UV in Jail (main environment)'))
            safe_print(_('    🚫 UV not found in the main env. Too fast to catch!'))
        safe_print(_('\n🌍 Main Environment:'))
        site_packages = Path(self.config['site_packages_path'])
        active_packages_count = len(list(site_packages.glob('*.dist-info')))
        safe_print(_('  - Path: {}').format(site_packages))
        safe_print(_('  - Active Packages: {}').format(active_packages_count))
        safe_print(_('\n📦 izolasyon Alanı (Bubbles):'))
        if not self.multiversion_base.exists() or not any(self.multiversion_base.iterdir()):
            safe_print(_('  - No isolated package versions found.'))
            return 0
        safe_print(_('  - Bubble Directory: {}').format(self.multiversion_base))
        safe_print(_('  - Import Hook Installed: {}').format('✅' if self.hook_manager.hook_installed else '❌'))
        version_dirs = list(self.multiversion_base.iterdir())
        total_bubble_size = 0
        safe_print(_('\n📦 Isolated Package Versions ({} bubbles):').format(len(version_dirs)))
        for version_dir in sorted(version_dirs):
            if version_dir.is_dir():
                size = sum((f.stat().st_size for f in version_dir.rglob('*') if f.is_file()))
                total_bubble_size += size
                size_mb = size / (1024 * 1024)
                warning = ' ⚠️' if size_mb > 100 else ''
                formatted_size_str = '{:.1f}'.format(size_mb)
                safe_print(_('  - 📁 {} ({} MB){}').format(version_dir.name, formatted_size_str, warning))
                if 'pip' in version_dir.name.lower():
                    safe_print(_('    😈 Pip is locked up in a bubble, plotting chaos like a Python outlaw! 🔒'))
                elif 'uv' in version_dir.name.lower():
                    safe_print(_('    😈 UV is locked up in a bubble, speeding toward trouble! 🔒'))
        total_bubble_size_mb = total_bubble_size / (1024 * 1024)
        formatted_total_size_str = '{:.1f}'.format(total_bubble_size_mb)
        safe_print(_('  - Total Bubble Size: {} MB').format(formatted_total_size_str))
        return 0