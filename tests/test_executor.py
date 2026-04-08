import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from executor import ExecutorManager


# 每个测试前重置单例，避免状态污染
@pytest.fixture(autouse=True)
def reset_singleton():
    ExecutorManager._instance = None
    yield
    manager = ExecutorManager._instance
    if manager:
        manager.shutdown(wait=False)
    ExecutorManager._instance = None


class TestExecutorManager:
    """ExecutorManager 单例测试"""

    def test_singleton(self):
        m1 = ExecutorManager.get_instance()
        m2 = ExecutorManager.get_instance()
        assert m1 is m2

    def test_default_pool_auto_created(self):
        manager = ExecutorManager.get_instance()
        pool = manager.get("default")
        assert pool is not None
        assert "default" in manager._executors

    def test_register_custom_pool(self):
        manager = ExecutorManager.get_instance()
        manager.register("heavy", max_workers=2, prefix="action")
        pool = manager.get("heavy")
        assert pool is not None
        assert "heavy" in manager._executors

    def test_get_auto_creates_missing_pool(self):
        manager = ExecutorManager.get_instance()
        pool = manager.get("non_exist")
        assert pool is not None
        assert "non_exist" in manager._executors

    def test_register_override(self):
        manager = ExecutorManager.get_instance()
        pool1 = manager.get("default")
        manager.register("default", max_workers=8)
        pool2 = manager.get("default")
        assert pool1 is not pool2

    def test_configure_multiple_pools(self):
        manager = ExecutorManager.get_instance()
        manager.configure(max_concurrency=4, prefix="action", default=4, heavy=2, light=8)
        assert "default" in manager._executors
        assert "heavy" in manager._executors
        assert "light" in manager._executors
        assert manager._max_concurrency == 4

    @pytest.mark.asyncio
    async def test_semaphore_lazy_creation(self):
        manager = ExecutorManager.get_instance()
        assert manager._semaphore is None
        sem = manager.get_semaphore()
        assert sem is not None
        assert sem._value == 8  # 默认 max_concurrency

    @pytest.mark.asyncio
    async def test_semaphore_reset_after_configure(self):
        manager = ExecutorManager.get_instance()
        sem1 = manager.get_semaphore()
        assert sem1._value == 8
        manager.configure(max_concurrency=2)
        sem2 = manager.get_semaphore()
        assert sem2._value == 2
        assert sem1 is not sem2

    def test_shutdown_clears_all(self):
        manager = ExecutorManager.get_instance()
        manager.register("heavy", max_workers=2)
        manager.shutdown()
        assert len(manager._executors) == 0

    @pytest.mark.asyncio
    async def test_run_sync_in_executor(self):
        """同步函数应正确在线程池中执行"""
        manager = ExecutorManager.get_instance()
        manager.register("default", max_workers=2)

        def sync_add(a, b):
            return a + b

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(manager.get("default"), sync_add, 1, 2)
        assert result == 3

    @pytest.mark.asyncio
    async def test_concurrent_execution(self):
        """多个任务应能并发执行"""
        manager = ExecutorManager.get_instance()
        manager.configure(max_concurrency=3, default=3)

        results = []

        async def task(n):
            results.append(f"start-{n}")
            await asyncio.sleep(0.1)
            results.append(f"end-{n}")
            return n

        values = await asyncio.gather(
            task(1), task(2), task(3),
        )
        assert values == [1, 2, 3]
        # 3 个 start 应在 3 个 end 之前
        starts = [i for i, v in enumerate(results) if v.startswith("start")]
        ends = [i for i, v in enumerate(results) if v.startswith("end")]
        assert max(starts) < min(ends)

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """Semaphore 应限制并发数"""
        manager = ExecutorManager.get_instance()
        manager.configure(max_concurrency=2)

        running = 0
        max_running = 0

        async def tracked_task():
            nonlocal running, max_running
            async with manager.get_semaphore():
                running += 1
                max_running = max(max_running, running)
                await asyncio.sleep(0.1)
                running -= 1

        await asyncio.gather(*[tracked_task() for _ in range(6)])
        assert max_running <= 2
