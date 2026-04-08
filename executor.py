from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional


class ExecutorManager:
    """全局线程池管理器，管理多个命名线程池。

    使用方式：
        manager = ExecutorManager.get_instance()
        manager.configure(max_concurrency=8, default=4, heavy=2)

        # 获取线程池
        pool = manager.get("default")

        # 关闭所有线程池
        manager.shutdown()
    """

    _instance: Optional[ExecutorManager] = None

    def __init__(self):
        self._executors: Dict[str, ThreadPoolExecutor] = {}
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._max_concurrency: int = 8
        # 自动注册 default 线程池
        self.register("default", max_workers=4)

    @classmethod
    def get_instance(cls) -> ExecutorManager:
        """获取单例实例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: str, max_workers: int = 4, prefix: str = "pool"):
        """注册一个命名线程池。

        Args:
            name: 线程池名称
            max_workers: 最大线程数
            prefix: 线程名前缀，用于日志区分
        """
        if name in self._executors:
            self._executors[name].shutdown(wait=False)
        self._executors[name] = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=f"{prefix}-{name}",
        )

    def get(self, name: str = "default") -> ThreadPoolExecutor:
        """获取线程池，不存在则自动创建。"""
        if name not in self._executors:
            self.register(name)
        return self._executors[name]

    def configure(self, max_concurrency: int = 8, prefix: str = "pool", **pools: int):
        """一次性配置全局并发数和多个命名线程池。

        Args:
            max_concurrency: 全局最大并发数
            prefix: 线程名前缀
            **pools: 线程池配置，key=名称 value=线程数，如 default=4, heavy=2
        """
        self._max_concurrency = max_concurrency
        self._semaphore = None  # 重置，下次获取时按新的 max_concurrency 创建
        for name, workers in pools.items():
            self.register(name, max_workers=workers, prefix=prefix)

    def get_semaphore(self) -> asyncio.Semaphore:
        """获取全局并发信号量（惰性创建）。"""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self._max_concurrency)
        return self._semaphore

    def shutdown(self, wait: bool = True):
        """关闭所有线程池。"""
        for executor in self._executors.values():
            executor.shutdown(wait=wait)
        self._executors.clear()
        self._semaphore = None
