# Python await 详解

## 1. await 是什么

`await` 是一个关键字，作用只有一个：**暂停当前协程，等待一个异步操作完成，拿到结果后再继续往下执行。**

```python
async def fetch():
    print("1. 开始")                    # 立刻执行
    data = await read_db()              # 暂停，等 read_db 完成
    print("3. 拿到数据:", data)          # 恢复后继续执行
    return data

# 执行流程：1. 开始 → 暂停等待 → (其他协程运行) → 3. 拿到数据
```

可以把 `await` 理解为一个**断点**：执行到这里就停下，把 CPU 让给别的协程，等结果回来了再从断点处继续。

## 2. await 的规则

### 规则一：await 只能用在 async 函数里

```python
# ✅ 正确：在 async def 里用 await
async def correct():
    result = await some_async()
    return result

# ❌ 错误：普通函数里不能用 await
def wrong():
    result = await some_async()    # SyntaxError
```

### 规则二：await 后面只能跟"可等待对象"（Awaitable）

`await` 后面只能跟实现了 `__await__()` 方法的对象。Python 内置三种：

```python
async def demo():
    # 1. Coroutine（协程）—— 另一个 async def 函数的返回值（最常用）
    result = await fetch_data()

    # 2. Task —— 用 create_task 包装的协程
    task = asyncio.create_task(fetch_data())
    result = await task
    # Task 本质是对协程的包装，加了调度和状态管理
    # await 一个协程时，事件循环内部也会自动把它包装成 Task

    # 3. Future —— 底层对象，代表一个未来的结果
    future = asyncio.Future()
    future.set_result("done")
    result = await future           # "done"
    # Task 就是 Future 的子类
    # 日常开发很少直接用 Future，主要是 asyncio 内部和库作者使用

    # ❌ 普通值不行
    result = await 42              # TypeError
    result = await "hello"         # TypeError
    result = await [1, 2, 3]       # TypeError
```

#### 自定义 Awaitable 对象

任何实现了 `__await__()` 方法的类都可以被 `await`：

```python
class MyAwaitable:
    def __await__(self):
        # __await__ 必须返回一个生成器
        yield
        return "自定义结果"

async def main():
    result = await MyAwaitable()    # "自定义结果"
```

实际开发中几乎不需要自己实现，了解即可。

#### Awaitable 类型总结

```
Awaitable（实现了 __await__() 的对象）
├── Coroutine    ← 最常用，async def 的返回值
├── Task         ← create_task 包装的协程
└── Future       ← 底层，代表未来结果
    └── 自定义   ← 实现 __await__() 的类（极少用）
```

日常写代码，`await` 后面 99% 的情况都是跟一个协程函数调用。

### 规则三：await 会拿到结果

`await` 后面的异步操作完成后，`await` 整个表达式的值就是那个结果：

```python
async def get_name():
    return "Alice"

async def main():
    name = await get_name()    # name = "Alice"
    print(name)                # Alice
```

如果异步操作抛了异常，`await` 也会抛出同样的异常：

```python
async def fail():
    raise ValueError("出错了")

async def main():
    try:
        result = await fail()
    except ValueError as e:
        print(e)               # 出错了
```

## 3. await 的执行过程

用时间线来看 await 发生了什么：

```python
async def task_a():
    print("A1")
    await asyncio.sleep(2)
    print("A2")

async def task_b():
    print("B1")
    await asyncio.sleep(1)
    print("B2")

# 假设两个任务并发运行：
# 时间 0s:  A1 → A遇到await，挂起
#           B1 → B遇到await，挂起
# 时间 1s:  B的sleep完成 → B2
# 时间 2s:  A的sleep完成 → A2
```

```
时间线：
0s       1s       2s
A: [A1]───等待────────[A2]
B: [B1]──等待──[B2]
    ^      ^
    |      |
  await   await
  让出     让出
```

**关键**：每个 `await` 都是一个让出点。如果没有 `await`，协程就会一直跑到函数结束，中间不会被打断。

## 4. await 的常见用法

### 等待另一个协程

```python
async def read_file(path):
    # 模拟异步读文件
    await asyncio.sleep(0.5)
    return f"content of {path}"

async def main():
    content = await read_file("/tmp/a.txt")
    print(content)
```

### 等待多个协程并发完成

```python
async def main():
    # await + gather：并发执行，等待全部完成
    results = await asyncio.gather(
        read_file("a.txt"),
        read_file("b.txt"),
        read_file("c.txt"),
    )
    # results = ["content of a.txt", "content of b.txt", "content of c.txt"]
```

### 等待超时

```python
async def main():
    try:
        # 最多等 3 秒，超时抛 TimeoutError
        result = await asyncio.wait_for(
            read_file("slow.txt"),
            timeout=3.0,
        )
    except asyncio.TimeoutError:
        print("超时了")
```

### 等待手动创建的 Task

```python
async def main():
    # 创建任务，但不立刻等它
    task = asyncio.create_task(read_file("a.txt"))

    # 可以先做别的事
    print("先干点别的")

    # 需要结果时再 await
    result = await task
```

## 5. await vs 普通函数调用

这是初学者最容易困惑的地方：

```python
# 普通函数调用：立刻执行，阻塞等到返回
def sync_read():
    time.sleep(2)        # 阻塞 2 秒，什么都不能做
    return "data"

result = sync_read()     # 调用后等 2 秒才拿到 result
print("这里要等 2 秒后才能执行")

# ---- 分隔线 ----

# async 函数 + await：挂起当前协程，不阻塞事件循环
async def async_read():
    await asyncio.sleep(2)   # 让出 2 秒，其他协程可以运行
    return "data"

result = await async_read()  # 调用后挂起，2 秒后恢复
print("这 2 秒内事件循环在执行其他协程")
```

| | 普通调用 | await |
|---|---|---|
| 执行方式 | 阻塞，一直等到返回 | 挂起协程，让出事件循环 |
| 其他任务 | 等待期间全部阻塞 | 等待期间正常运行 |
| 返回值 | 直接拿到 | await 表达式的值就是结果 |

## 6. 常见错误

### 忘记 await

```python
async def get_data():
    return "hello"

async def main():
    # ❌ 没有 await，result 是一个 coroutine 对象，不是 "hello"
    result = get_data()
    print(result)    # <coroutine object get_data at 0x...>
    print(len(result))  # TypeError，coroutine 没有 len

    # ✅ 加上 await
    result = await get_data()
    print(result)    # "hello"
```

### 在同步函数里用 await

```python
# ❌ SyntaxError
def process():
    result = await get_data()

# ✅ 整个函数改为 async
async def process():
    result = await get_data()
```

### await 顺序导致性能浪费

```python
async def main():
    # ❌ 顺序 await，总共 2 秒
    a = await fetch("url_a")   # 等 1 秒
    b = await fetch("url_b")   # 再等 1 秒

    # ✅ 并发 await，总共 1 秒
    a, b = await asyncio.gather(
        fetch("url_a"),
        fetch("url_b"),
    )
```

### 把 async 函数传给同步 API

```python
import threading

# ❌ 同步回调里不能 await
def on_message(msg):
    result = await process(msg)    # SyntaxError

# ✅ 用 asyncio.run_coroutine_threadsafe 从同步世界提交协程
def on_message(msg):
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(process(msg), loop)
```

## 7. 一句话总结

`await` = **在这里暂停，等结果回来再继续。暂停期间其他协程可以运行。**
