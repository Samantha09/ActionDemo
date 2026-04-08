import asyncio

import pytest

from action import action
from dispatcher import ActionDispatcher
from executor import ExecutorManager


@pytest.fixture(autouse=True)
def reset_executor():
    ExecutorManager._instance = None
    yield
    manager = ExecutorManager._instance
    if manager:
        manager.shutdown(wait=False)
    ExecutorManager._instance = None


class TestActionDecorator:
    """@action 装饰器测试"""

    def test_default_executor(self):
        @action()
        def my_action():
            pass

        assert my_action.action_meta["executor"] == "default"

    def test_custom_executor(self):
        @action(executor="heavy")
        def my_action():
            pass

        assert my_action.action_meta["executor"] == "heavy"

    def test_all_meta_fields(self):
        @action(
            is_system_action=True,
            name="my custom action",
            output_mapping=lambda r: not r,
            executor="heavy",
        )
        def my_action():
            pass

        meta = my_action.action_meta
        assert meta["name"] == "my custom action"
        assert meta["is_system_action"] is True
        assert meta["output_mapping"] is not None
        assert meta["executor"] == "heavy"


class TestDispatcherExecute:
    """Dispatcher 执行测试"""

    @pytest.mark.asyncio
    async def test_execute_async_action(self):
        dispatcher = ActionDispatcher()

        @action()
        async def hello(name: str) -> str:
            return f"hello {name}"

        dispatcher.register_action(hello)
        result = await dispatcher.execute("hello", name="world")
        assert result == "hello world"

    @pytest.mark.asyncio
    async def test_execute_sync_action(self):
        """同步函数应通过线程池执行"""
        dispatcher = ActionDispatcher()

        @action()
        def add(a: int, b: int) -> int:
            return a + b

        dispatcher.register_action(add)
        result = await dispatcher.execute("add", a=1, b=2)
        assert result == 3