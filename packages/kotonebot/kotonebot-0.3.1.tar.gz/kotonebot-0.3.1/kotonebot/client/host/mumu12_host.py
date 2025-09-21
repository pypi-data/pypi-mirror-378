from dataclasses import dataclass
import os
import json
import subprocess
from functools import lru_cache
from typing import Any, Literal, overload, TYPE_CHECKING
from typing_extensions import override

from kotonebot import logging
from kotonebot.client import Device
from kotonebot.client.device import AndroidDevice
from kotonebot.client.implements.adb import AdbImpl
from kotonebot.client.implements.nemu_ipc import NemuIpcImpl, NemuIpcImplConfig
from kotonebot.util import Countdown, Interval
from .protocol import HostProtocol, Instance, copy_type, AdbHostConfig
from .adb_common import AdbRecipes, CommonAdbCreateDeviceMixin, connect_adb, is_adb_recipe

if os.name == 'nt':
    from ...interop.win.reg import read_reg
else:
    def read_reg(key, subkey, name, *, default=None, **kwargs):
        """Stub for read_reg on non-Windows platforms."""
        return default

# Forward declarations for type hints
if TYPE_CHECKING:
    from typing import Type

logger = logging.getLogger(__name__)
MuMu12Recipes = AdbRecipes | Literal['nemu_ipc']

@dataclass
class MuMu12HostConfig(AdbHostConfig):
    """nemu_ipc 能力的配置模型。"""
    display_id: int | None = 0
    """目标显示器 ID，默认为 0（主显示器）。若为 None 且设置了 target_package_name，则自动获取对应的 display_id。"""
    target_package_name: str | None = None
    """目标应用包名，用于自动获取 display_id。"""
    app_index: int = 0
    """多开应用索引，传给 get_display_id 方法。"""

class Mumu12Host(HostProtocol[MuMu12Recipes]):
    InstanceClass: 'Type[Mumu12Instance]'

    @staticmethod
    @lru_cache(maxsize=1)
    def _read_install_path() -> str | None:
        r"""
        从注册表中读取 MuMu Player 12 的安装路径。

        返回的路径为根目录。如 `F:\Apps\Netease\MuMuPlayer-12.0`。

        :return: 若找到，则返回安装路径；否则返回 None。
        """
        if os.name != 'nt':
            return None

        uninstall_subkeys = [
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MuMuPlayer-12.0',
            # TODO: 支持国际版 MuMu
            # r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MuMuPlayerGlobal-12.0'
        ]

        for subkey in uninstall_subkeys:
            icon_path = read_reg('HKLM', subkey, 'DisplayIcon', default=None)
            if icon_path and isinstance(icon_path, str):
                icon_path = icon_path.replace('"', '')
                path = os.path.dirname(icon_path)
                logger.debug('MuMu Player 12 installation path: %s', path)
                # 返回根目录（去掉 shell 子目录）
                if os.path.basename(path).lower() == 'shell':
                    path = os.path.dirname(path)
                return path
        return None

    @classmethod
    def _invoke_manager(cls,args: list[str]) -> str:
        """
        调用 MuMuManager.exe。
        
        :param args: 命令行参数列表。
        :return: 命令执行的输出。
        """
        install_path = cls._read_install_path()
        if install_path is None:
            raise RuntimeError('MuMu Player 12 is not installed.')
        manager_path = os.path.join(install_path, 'shell', 'MuMuManager.exe')
        logger.debug('MuMuManager execute: %s', repr(args))
        output = subprocess.run(
            [manager_path] + args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            # https://stackoverflow.com/questions/6011235/run-a-program-from-python-and-have-it-continue-to-run-after-the-script-is-kille
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
        if output.returncode != 0:
            # raise RuntimeError(f'Failed to invoke MuMuManager: {output.stderr}')
            logger.warning('Failed to invoke MuMuManager: %s', output.stderr)
        return output.stdout

    @staticmethod
    def installed() -> bool:
        return Mumu12Host._read_install_path() is not None

    @classmethod
    def list(cls) -> list[Instance]:
        nemu_path = cls._read_install_path()
        if nemu_path is None:
            raise RuntimeError("Nemu path not found.")
        output = cls._invoke_manager(['info', '-v', 'all'])
        logger.debug('MuMuManager.exe output: %s', output)
        
        try:
            data: dict[str, dict[str, Any]] = json.loads(output)
            if 'name' in data.keys():
                # 这里有个坑：
                # 如果只有一个实例，返回的 JSON 结构是单个对象而不是数组
                data = { '0': data }
            instances = []
            for index, instance_data in data.items():
                instance = cls.InstanceClass(
                    id=index,
                    name=instance_data['name'],
                    adb_port=instance_data.get('adb_port'),  
                    adb_ip=instance_data.get('adb_host_ip', '127.0.0.1'), 
                    adb_name=None,
                )
                instance.nemu_path = nemu_path
                instance.index = int(index)
                instance.is_android_started = instance_data.get('is_android_started', False)
                logger.debug('Mumu12 instance: %s', repr(instance))
                instances.append(instance)
            return instances
        except json.JSONDecodeError as e:
            raise RuntimeError(f'Failed to parse output: {e}')
    
    @classmethod
    def query(cls, *, id: str) -> Instance | None:
        instances = cls.list()
        for instance in instances:
            if instance.id == id:
                return instance
        return None

    @staticmethod
    def recipes() -> 'list[MuMu12Recipes]':
        return ['adb', 'adb_raw', 'uiautomator2', 'nemu_ipc']

class Mumu12Instance(CommonAdbCreateDeviceMixin, Instance[MuMu12HostConfig]):
    HostClass: 'type[Mumu12Host]' = Mumu12Host

    @copy_type(Instance.__init__)
    def __init__(self, *args, **kwargs):
        if not hasattr(self.HostClass, 'InstanceClass'):
            raise RuntimeError(f"{self.HostClass.__name__}.InstanceClass not initialized")
        
        super().__init__(*args, **kwargs)
        self._args = args
        self.index: int | None = None
        self.is_android_started: bool = False
        self.nemu_path: str | None = None
    
    @override
    def refresh(self):
        ins = self.HostClass.query(id=self.id)
        if ins is not None and isinstance(ins, self.__class__):
            self.adb_port = ins.adb_port
            self.adb_ip = ins.adb_ip
            self.adb_name = ins.adb_name
            self.is_android_started = ins.is_android_started
            self.nemu_path = ins.nemu_path
            logger.debug('Refreshed MuMu12 instance: %s', repr(ins))
    
    @override
    def start(self):
        if self.running():
            logger.warning('Instance is already running.')
            return
        logger.info('Starting MuMu12 instance %s', self)
        self.HostClass._invoke_manager(['control', '-v', self.id, 'launch'])
        self.refresh()
    
    @override
    def stop(self):
        if not self.running():
            logger.warning('Instance is not running.')
            return
        logger.info('Stopping MuMu12 instance id=%s name=%s...', self.id, self.name)
        self.HostClass._invoke_manager(['control', '-v', self.id, 'shutdown'])
        self.refresh()
    
    @override
    def wait_available(self, timeout: float = 180):
        cd = Countdown(timeout)
        it = Interval(5)
        while not cd.expired() and not self.running():
            it.wait()
            self.refresh()
        if not self.running():
            raise TimeoutError(f'MuMu12 instance "{self.name}" is not available.')
    
    @override
    def running(self) -> bool:
        return self.is_android_started

    @overload
    def create_device(self, recipe: Literal['nemu_ipc'], host_config: MuMu12HostConfig) -> Device: ...
    @overload
    def create_device(self, recipe: AdbRecipes, host_config: AdbHostConfig) -> Device: ...

    @override
    def create_device(self, recipe: MuMu12Recipes, host_config: MuMu12HostConfig | AdbHostConfig) -> Device:
        """为MuMu12模拟器实例创建 Device。"""
        if self.adb_port is None:
            raise ValueError("ADB port is not set and is required.")

        if recipe == 'nemu_ipc' and isinstance(host_config, MuMu12HostConfig):
            # NemuImpl
            if self.nemu_path is None:
                raise RuntimeError("Nemu path is not set.")
            nemu_config = NemuIpcImplConfig(
                nemu_folder=self.nemu_path,
                instance_id=int(self.id),
                display_id=host_config.display_id,
                target_package_name=host_config.target_package_name,
                app_index=host_config.app_index
            )
            nemu_impl = NemuIpcImpl(nemu_config)
            # AdbImpl
            adb_impl = AdbImpl(connect_adb(
                self.adb_ip,
                self.adb_port,
                timeout=host_config.timeout,
                device_serial=self.adb_name
            ))
            device = AndroidDevice()
            device._screenshot = nemu_impl
            device._touch = nemu_impl
            device.commands = adb_impl

            return device
        elif isinstance(host_config, AdbHostConfig) and is_adb_recipe(recipe):
            return super().create_device(recipe, host_config)
        else:
            raise ValueError(f'Unknown recipe: {recipe}')

class Mumu12V5Host(Mumu12Host):
    InstanceClass: 'Type[Mumu12V5Instance]'

    @classmethod
    @lru_cache(maxsize=1)
    def _read_install_path(cls) -> str | None:
        r"""
        从注册表中读取 MuMu Player 12 v5.x 的安装路径。

        返回的路径为根目录。如 `F:\Apps\Netease\MuMuPlayer-12.0`。

        :return: 若找到，则返回安装路径；否则返回 None。
        """
        if os.name != 'nt':
            return None

        uninstall_subkeys = [
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MuMuPlayer',
        ]

        for subkey in uninstall_subkeys:
            icon_path = read_reg('HKLM', subkey, 'DisplayIcon', default=None)
            if icon_path and isinstance(icon_path, str):
                icon_path = icon_path.replace('"', '')
                path = os.path.dirname(icon_path)
                logger.debug('MuMu Player 12 installation path: %s', path)
                # 返回根目录（去掉 shell 子目录）
                if os.path.basename(path).lower() == 'nx_main':
                    path = os.path.dirname(path)
                return path
        return None

    @classmethod
    def _invoke_manager(cls, args: list[str]) -> str:
        """
        调用 MuMuManager.exe。
        
        :param args: 命令行参数列表。
        :return: 命令执行的输出。
        """
        install_path = cls._read_install_path()
        if install_path is None:
            raise RuntimeError('MuMu Player 12 v5.x is not installed.')
        manager_path = os.path.join(install_path, 'nx_main', 'MuMuManager.exe')
        logger.debug('MuMuManager execute: %s', repr(args))
        output = subprocess.run(
            [manager_path] + args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            # https://stackoverflow.com/questions/6011235/run-a-program-from-python-and-have-it-continue-to-run-after-the-script-is-kille
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
        if output.returncode != 0:
            # raise RuntimeError(f'Failed to invoke MuMuManager: {output.stderr}')
            logger.warning('Failed to invoke MuMuManager: %s', output.stderr)
        return output.stdout

    @classmethod
    def installed(cls) -> bool:
        return cls._read_install_path() is not None

    @classmethod
    def list(cls) -> list[Instance]:
        output = cls._invoke_manager(['info', '-v', 'all'])
        logger.debug('MuMuManager.exe output: %s', output)
        
        try:
            data: dict[str, dict[str, Any]] = json.loads(output)
            if 'name' in data.keys():
                # 这里有个坑：
                # 如果只有一个实例，返回的 JSON 结构是单个对象而不是数组
                data = { '0': data }
            instances = []
            for index, instance_data in data.items():
                instance = cls.InstanceClass(
                    id=index,
                    name=instance_data['name'],
                    adb_port=instance_data.get('adb_port'),  
                    adb_ip=instance_data.get('adb_host_ip', '127.0.0.1'), 
                    adb_name=None
                )
                instance.nemu_path = cls._read_install_path()
                instance.index = int(index)
                instance.is_android_started = instance_data.get('is_android_started', False)
                logger.debug('Mumu12 v5.x instance: %s', repr(instance))
                instances.append(instance)
            return instances
        except json.JSONDecodeError as e:
            raise RuntimeError(f'Failed to parse output: {e}')

class Mumu12V5Instance(Mumu12Instance):
    HostClass: 'type[Mumu12V5Host]' = Mumu12V5Host

# 延迟初始化 InstanceClass 变量
Mumu12Host.InstanceClass = Mumu12Instance
Mumu12V5Host.InstanceClass = Mumu12V5Instance


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    print(Mumu12Host._read_install_path())
    print(Mumu12Host.installed())
    print(Mumu12Host.list())
    print(ins:=Mumu12Host.query(id='2'))
    assert isinstance(ins, Mumu12Host.InstanceClass)
    ins.start()
    ins.wait_available()
    print('status', ins.running(), ins.adb_port, ins.adb_ip)
    ins.stop()
    print('status', ins.running(), ins.adb_port, ins.adb_ip)
