# Python 协程使用指南

## 1. 基础语法

### 定义和调用

```python
import asyncio

# async def 定义协程函数
async def fetch_data(url):
    print(f"开始请求 {url}")
    await asyncio.sleep(1)       # 模拟 IO 等待（非阻塞）
    print(f"请求完成 {url}")
    return f"data from {url}"

# ❌ 直接调用不会执行，只是返回一个 coroutine 对象
coro = fetch_data("http://a.com")
print(coro)  # <coroutine object fetch_data at 0x...>

# ✅ 三种执行方式

# 方式 1：await（在另一个 async 函数里）
async def main():
    result = await fetch_data("http://a.com")

# 方式 2：asyncio.run（入口，从同步世界进入异步世界）
result = asyncio.run(fetch_data("http://a.com"))

# 方式 3：asyncio.create_task（不等待，让它后台跑）
async def main():
    task = asyncio.create_task(fetch_data("http://a.com"))
    # 可以先干别的事
    print("做其他事...")
    # 需要结果时再 await
    result = await task
```

### await 的规则

```python
# await 只能用在 async 函数里
async def correct():
    await asyncio.sleep(1)  # ✅

def wrong():
    await asyncio.sleep(1)  # ❌ SyntaxError

# await 后面只能跟"可等待对象"（awaitable）
# 三种：coroutine、Task、Future
async def demo():
    # 1. await coroutine
    result = await fetch_data("url")

    # 2. await Task
    task = asyncio.create_task(fetch_data("url"))
    result = await task

    # 3. await asyncio.sleep
    await asyncio.sleep(1)

    # ❌ await 普通值没意义
    result = await 42  # TypeError
```

## 2. 并发执行

### 顺序 vs 并发

```python
async def fetch(url):
    await asyncio.sleep(1)
    return f"data from {url}"

# ❌ 顺序执行，总共 3 秒
async def sequential():
    r1 = await fetch("a.com")   # 等 1 秒
    r2 = await fetch("b.com")   # 再等 1 秒
    r3 = await fetch("c.com")   # 再等 1 秒
    return [r1, r2, r3]

# ✅ 并发执行，总共 1 秒
async def concurrent():
    r1, r2, r3 = await asyncio.gather(
        fetch("a.com"),
        fetch("b.com"),
        fetch("c.com"),
    )
    return [r1, r2, r3]
```

```
顺序执行：     [a █████] → [b █████] → [c █████]    总 3 秒
并发执行：     [a █████]
               [b █████]                             总 1 秒
               [c █████]
```

### asyncio.gather 详解

```python
async def demo():
    # gather 等所有完成，按顺序返回结果
    results = await asyncio.gather(
        fetch("a.com"),   # results[0]
        fetch("b.com"),   # results[1]
        fetch("c.com"),   # results[2]
    )

    # 一个失败全部失败（默认行为）
    # return_exceptions=True 则异常作为结果返回，不中断其他
    results = await asyncio.gather(
        fetch("a.com"),
        fetch("bad.com"),  # 可能抛异常
        fetch("c.com"),
        return_exceptions=True,
    )
    # results = ["data from a", RuntimeError(...), "data from c"]
```

## 3. 并发控制（Semaphore）

```python
async def fetch_with_limit(urls, max_concurrency=3):
    semaphore = asyncio.Semaphore(max_concurrency)

    async def limited_fetch(url):
        async with semaphore:        # 获取许可
            print(f"开始: {url}")
            result = await fetch(url)
            print(f"完成: {url}")
            return result

    # 10 个任务，同时最多跑 3 个
    tasks = [limited_fetch(url) for url in urls]
    return await asyncio.gather(*tasks)

# 执行过程：
# 时间 0s:  url1 url2 url3 开始（3个许可用完）
# 时间 1s:  url1 完成 → url4 开始
#           url2 完成 → url5 开始
#           ...
```

## 4. 同步代码混用（run_in_executor）

### 为什么需要

`async def` 只是声明协程，内部如果调用同步阻塞操作（requests、time.sleep、CPU 计算），
仍然会阻塞事件循环。需要用 `run_in_executor` 把同步函数投递到线程池执行。

```python
# async 函数内部没有 await → 和同步函数没区别，会阻塞事件循环
async def bad():
    time.sleep(5)          # 阻塞整个事件循环 5 秒
    result = heavy_cpu()   # 阻塞事件循环
    return result
```

### 正确用法

```python
import time

def sync_heavy_work(n):        # 普通同步函数
    time.sleep(2)              # 阻塞
    return n * n

async def main():
    loop = asyncio.get_running_loop()

    # 把同步函数丢到线程池执行，不阻塞事件循环
    result = await loop.run_in_executor(
        None,                  # None = 默认线程池
        sync_heavy_work,       # 同步函数
        42                     # 位置参数
    )
    print(result)  # 1764

    # 也可以指定自定义线程池
    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor(max_workers=4)
    result = await loop.run_in_executor(pool, sync_heavy_work, 42)

    # 带关键字参数要用 partial
    from functools import partial
    result = await loop.run_in_executor(
        pool,
        partial(sync_heavy_work, n=42),
    )
```

### 为什么协程不走线程池

协程需要事件循环驱动。线程池线程里没有事件循环，要跑协程得嵌套 `asyncio.run()` 创建新循环，
开销大、状态隔离、并发控制混乱。async 函数直接在主事件循环里 await 即可。

## 5. 超时和取消

```python
async def demo():
    # 超时控制
    try:
        result = await asyncio.wait_for(
            fetch("slow.com"),
            timeout=3.0,
        )
    except asyncio.TimeoutError:
        print("超时了")

    # 手动取消
    task = asyncio.create_task(fetch("a.com"))
    await asyncio.sleep(0.5)
    task.cancel()  # 取消任务
    try:
        await task
    except asyncio.CancelledError:
        print("任务被取消了")
```

## 6. 实际项目典型模式

```python
import asyncio
import aiohttp

class Service:
    def __init__(self, max_concurrency=5):
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._session: aiohttp.ClientSession = None

    async def start(self):
        """初始化资源（在 async 上下文中调用）"""
        self._session = aiohttp.ClientSession()

    async def close(self):
        """清理资源"""
        if self._session:
            await self._session.close()

    async def fetch(self, url):
        async with self._semaphore:
            async with self._session.get(url) as resp:
                return await resp.json()

    async def batch_fetch(self, urls):
        tasks = [self.fetch(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)


# 使用
async def main():
    svc = Service(max_concurrency=3)
    await svc.start()
    try:
        results = await svc.batch_fetch(["url1", "url2", "url3"])
    finally:
        await svc.close()

asyncio.run(main())
```

## 7. 常见陷阱

| 陷阱 | 说明 | 正确做法 |
|---|---|---|
| `async def` 里写同步阻塞代码 | 没有 await 就不会让出，阻塞事件循环 | 用 `run_in_executor` |
| `asyncio.run()` 嵌套调用 | 已经在事件循环里不能再 run | 用 `await` |
| 忘记 `await` | 调用协程函数不 await，不会执行 | 始终 `await coro()` |
| 在同步函数里调 async 函数 | 同步函数不能 await | 重构为 async 或用 `asyncio.run` |
| 共享可变状态不加锁 | 多个协程并发修改同一变量 | 用 `asyncio.Lock` |
