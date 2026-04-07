# ActionDemo

基于 NeMo Guardrails 模式的 Action 注解与调度框架 Demo。

## 架构

```
action.py              @action 装饰器，只在函数上挂载 action_meta 元数据
dispatcher.py          ActionDispatcher：加载、注册、查找、执行 action
actions/               action 存放目录
  safety_actions.py    安全检查类 action（毒性检测、内容审核、自检输出）
  data_actions.py      数据脱敏类 action（敏感数据检测、脱敏）
main.py                演示入口
```

## 核心机制

**`@action` 装饰器** — 轻量级，只挂载元数据，不做注册：

```python
@action(is_system_action=True, name="check content safety", output_mapping=lambda r: r["is_toxic"])
async def check_content_safety(text: str) -> dict:
    ...
```

**`ActionDispatcher`** — 实例级注册表，统一管理 action 生命周期：

- `load_actions_from_path()` — 自动扫描目录，通过反射发现带 `action_meta` 的对象
- `register_action()` — 手动注册
- `execute()` — 查找、执行（sync/async 自动判断）、`output_mapping` 返回值转换

**`output_mapping`** — 将 action 返回值转为 bool（True=拦截），支持语义反转：

```python
# 函数返回 True=安全 → mapping 反转为 False=放行
output_mapping=lambda value: not value
```

## 运行

```bash
python3 main.py
```

## 参考

- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
