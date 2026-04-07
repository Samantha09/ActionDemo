from typing import Any, Callable, Optional, TypedDict, Type, Union, TypeVar


class ActionMeta(TypedDict):
    """action 的元数据"""
    name: str                                        # action 名称
    is_system_action: bool                           # 是否系统内部 action
    output_mapping: Optional[Callable[[Any], bool]]  # 返回值转换函数


T = TypeVar("T", bound=Union[Callable[..., Any], Type[Any]])


def action(
    is_system_action: bool = False,
    name: Optional[str] = None,
    output_mapping: Optional[Callable[[Any], bool]] = None,
) -> Callable[[T], T]:
    """注册一个 action 的装饰器。

    只在函数/类上挂载 action_meta 元数据，不做实际注册。
    注册由 ActionDispatcher.load_actions_from_path 完成。

    用法：
        @action
        def my_func(): ...

        @action(name="custom name", output_mapping=lambda r: not r)
        def my_func2(): ...

    Args:
        is_system_action: 是否系统 action（不暴露给用户）
        name: action 名称，flow 里用这个名字调用。默认用函数名
        output_mapping: 返回值转换函数，把 action 返回值转为 bool（True=拦截）
    """
    def decorator(fn_or_cls: Union[Callable, Type]) -> Union[Callable, Type]:
        action_name = name or fn_or_cls.__name__

        meta: ActionMeta = {
            "name": action_name,
            "is_system_action": is_system_action,
            "output_mapping": output_mapping,
        }

        setattr(fn_or_cls, "action_meta", meta)
        return fn_or_cls

    return decorator
