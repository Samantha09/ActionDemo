import importlib.util
import inspect
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

from action import ActionMeta


class ActionDispatcher:
    """负责加载、注册、查找和执行 action。"""

    def __init__(self):
        self._registered_actions: Dict[str, Union[Callable, Type]] = {}

    @property
    def registered_actions(self) -> Dict[str, Union[Callable, Type]]:
        return self._registered_actions

    # ==================== 加载 ====================

    def load_actions_from_path(self, path: str):
        """从指定路径加载所有 action。

        会查找 path/actions/ 目录和 path/actions.py 文件。

        Args:
            path: 目录路径
        """
        path = Path(path).resolve()

        actions_dir = path / "actions"
        if actions_dir.exists():
            self._registered_actions.update(self._find_actions(actions_dir))

        actions_py = path / "actions.py"
        if actions_py.exists():
            self._registered_actions.update(self._load_actions_from_module(str(actions_py)))

    # ==================== 注册 ====================

    def register_action(self, action: Callable, name: Optional[str] = None, override: bool = True):
        """手动注册一个 action。

        Args:
            action: action 函数或类
            name: action 名称，默认从 action_meta 或函数名获取
            override: 已存在时是否覆盖
        """
        if name is None:
            action_meta = getattr(action, "action_meta", None)
            action_name = action_meta["name"] if action_meta else action.__name__
        else:
            action_name = name

        if action_name in self._registered_actions and not override:
            return

        self._registered_actions[action_name] = action

    # ==================== 查找 ====================

    def get_action(self, name: str) -> Optional[Callable]:
        """根据名称查找 action"""
        return self._registered_actions.get(name, None)

    def has_registered(self, name: str) -> bool:
        return name in self._registered_actions

    def get_registered_actions(self) -> List[str]:
        return list(self._registered_actions.keys())

    # ==================== 执行 ====================

    async def execute(self, action_name: str, **params) -> Any:
        """根据名称查找并执行 action。

        完整流程：
        1. 从注册表查找 action 函数和元数据
        2. 执行函数（支持 sync/async）
        3. 用 output_mapping 转换返回值

        Args:
            action_name: action 名称
            **params: 直接传给 action 的参数

        Returns:
            经过 output_mapping 转换后的结果（如果有的话）
        """
        if action_name not in self._registered_actions:
            available = ", ".join(self._registered_actions.keys())
            raise ValueError(f"Action '{action_name}' not found. Available: {available}")

        fn = self._registered_actions[action_name]

        # 如果是类，延迟实例化
        if inspect.isclass(fn):
            fn = fn()
            self._registered_actions[action_name] = fn

        meta: ActionMeta = getattr(fn, "action_meta", {})

        print(f"\n[Dispatcher] 执行 action: '{action_name}'")
        print(f"  函数: {fn.__name__ if hasattr(fn, '__name__') else fn.__class__.__name__}")
        print(f"  元数据: system={meta.get('is_system_action')}, has_mapping={meta.get('output_mapping') is not None}")
        print(f"  参数: {list(params.keys())}")

        # 执行
        if inspect.isfunction(fn) or inspect.ismethod(fn):
            result = fn(**params)
            if inspect.iscoroutine(result):
                result = await result
        elif hasattr(fn, "run") and callable(getattr(fn, "run")):
            result = fn.run(**params)
        else:
            result = fn(**params)

        print(f"  原始返回值: {result}")

        # output_mapping 转换
        output_mapping = meta.get("output_mapping")
        if output_mapping is not None:
            mapped = output_mapping(result)
            print(f"  output_mapping 转换后: {result} → {mapped}")
            return mapped

        return result

    # ==================== 内部方法 ====================

    @staticmethod
    def _load_actions_from_module(filepath: str) -> Dict[str, Any]:
        """从 Python 模块文件中加载所有带 @action 装饰器的对象。"""
        action_objects = {}

        if not os.path.isfile(filepath):
            print(f"[Dispatcher] 文件不存在: {filepath}")
            return action_objects

        filename = os.path.basename(filepath)
        spec = importlib.util.spec_from_file_location(filename, filepath)
        if not spec or not spec.loader:
            print(f"[Dispatcher] 无法加载模块: {filepath}")
            return action_objects

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module):
            if (inspect.isfunction(obj) or inspect.isclass(obj)) and hasattr(obj, "action_meta"):
                action_name = obj.action_meta["name"]
                action_objects[action_name] = obj
                print(f"[Dispatcher] 发现 action: {action_name} ({name})")

        return action_objects

    def _find_actions(self, directory: Path) -> Dict[str, Any]:
        """递归扫描目录，找出所有带 @action 的 Python 文件"""
        action_objects = {}

        for root, dirs, files in os.walk(directory):
            for filename in sorted(files):
                if filename.endswith(".py") and not filename.startswith("_"):
                    filepath = os.path.join(root, filename)
                    action_objects.update(self._load_actions_from_module(filepath))

        return action_objects
