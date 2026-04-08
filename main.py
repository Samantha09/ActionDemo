import asyncio

from dispatcher import ActionDispatcher
from executor import ExecutorManager


async def demo():
    print("=" * 60)
    print("  Action 注解机制 + 线程池管理 演示")
    print("=" * 60)

    # ==================== 第 1 步：配置线程池 ====================
    print("\n📦 第 1 步：配置 ExecutorManager")
    print("-" * 40)
    manager = ExecutorManager.get_instance()
    manager.configure(
        max_concurrency=4,
        prefix="action",
        default=4,
        heavy=2,
    )
    print(f"  全局并发数: {manager._max_concurrency}")
    print(f"  已注册线程池: {list(manager._executors.keys())}")

    # ==================== 第 2 步：创建调度器并加载 ====================
    print("\n📦 第 2 步：创建调度器，自动加载 action")
    print("-" * 40)
    dispatcher = ActionDispatcher()
    dispatcher.load_actions_from_path(".")

    print(f"\n📋 已注册的 actions:")
    for name in dispatcher.get_registered_actions():
        fn = dispatcher.get_action(name)
        meta = getattr(fn, "action_meta", {})
        system = "系统" if meta.get("is_system_action") else "用户"
        mapping = "有" if meta.get("output_mapping") else "无"
        executor = meta.get("executor", "default")
        print(f"  [{system}] {name}  (executor={executor}, output_mapping={mapping})")

    # ==================== 第 3 步：单次调用演示 ====================
    print("\n🚀 第 3 步：单次调用演示")
    print("-" * 40)

    print("\n--- 3.1 check_toxicity（async action）---")
    result = await dispatcher.execute("check_toxicity", text="你好世界")
    print(f"  最终结果: {result}\n")

    print("--- 3.2 check content safety（带 output_mapping）---")
    result = await dispatcher.execute("check content safety", text="今天天气真好")
    print(f"  最终结果: {result}  (False=放行)\n")

    result = await dispatcher.execute("check content safety", text="这里有暴力内容")
    print(f"  最终结果: {result}  (True=拦截)\n")

    # ==================== 第 4 步：并发执行演示 ====================
    print("\n🔥 第 4 步：并发执行多个 action（Semaphore 控制并发数）")
    print("-" * 40)

    print("\n--- 4.1 同时发起 4 个请求（max_concurrency=4）---")
    results = await asyncio.gather(
        dispatcher.execute("check_toxicity", text="你好"),
        dispatcher.execute("check content safety", text="你好"),
        dispatcher.execute("detect_sensitive_data", text="手机13800138000"),
        dispatcher.execute("mask_sensitive_data", text="手机13800138000，邮箱test@example.com"),
    )
    print(f"\n  并发结果: {results}")

    # ==================== 第 5 步：查看注册表内部 ====================
    print("\n📊 第 5 步：查看注册表内部")
    print("-" * 40)
    for name in dispatcher.get_registered_actions():
        fn = dispatcher.get_action(name)
        meta = getattr(fn, "action_meta", {})
        mapping_desc = "有" if meta.get("output_mapping") else "无"
        print(f"  {name}")
        print(f"    函数: {fn.__name__ if hasattr(fn, '__name__') else fn.__class__.__name__}")
        print(f"    系统: {meta.get('is_system_action')}")
        print(f"    executor: {meta.get('executor')}")
        print(f"    output_mapping: {mapping_desc}")
        print()

    # ==================== 第 6 步：关闭线程池 ====================
    print("🛑 第 6 步：关闭线程池")
    print("-" * 40)
    manager.shutdown()
    print("  所有线程池已关闭")

    print("\n✅ 演示完成!")


if __name__ == "__main__":
    asyncio.run(demo())
