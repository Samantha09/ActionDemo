from action import action


# === 示例 1：最简单的 action ===

@action(is_system_action=True)
async def check_toxicity(text: str, **kwargs) -> dict:
    """检测文本毒性，返回原始结果（无 output_mapping）"""
    # 模拟模型推理
    is_toxic = any(word in text for word in ["傻", "蠢", "去死"])
    return {"is_toxic": is_toxic, "score": 0.9 if is_toxic else 0.1}


# === 示例 2：带 output_mapping 的 action ===

def safety_mapping(result: dict) -> bool:
    """把 dict 转换为 bool。True = 拦截"""
    return result.get("is_toxic", False)

@action(
    is_system_action=True,
    name="check content safety",
    output_mapping=safety_mapping,
)
async def check_content_safety(text: str, **kwargs) -> dict:
    """检测内容安全。返回值经过 safety_mapping 转为 bool"""
    is_unsafe = any(word in text for word in ["暴力", "色情", "赌博"])
    return {"is_toxic": is_unsafe, "category": "unsafe_content" if is_unsafe else "safe"}


# === 示例 3：带依赖注入的 action ===

@action(is_system_action=True)
async def self_check_output(
    context: dict,   # 框架自动注入
    config: dict,    # 框架自动注入
    **kwargs,
) -> bool:
    """用 LLM 自检输出。context 和 config 由 dispatcher 注入"""
    bot_message = context.get("bot_message", "")
    threshold = config.get("threshold", 0.5)

    # 模拟 LLM 审核
    is_safe = len(bot_message) > 0 and "不行" not in bot_message

    print(f"    [self_check_output] 审核: '{bot_message}' → 安全={is_safe}")
    return is_safe  # True=安全


# === 示例 4：output_mapping 反转（和 NeMo 一样的模式）===
# self_check_output 返回 True=安全
# 但 flow 层面需要 True=拦截，所以用 output_mapping 反转

@action(
    is_system_action=True,
    name="self check output with block",
    output_mapping=lambda value: not value,  # True→False(放行), False→True(拦截)
)
async def self_check_output_v2(
    context: dict = None,
    **kwargs,
) -> bool:
    """自检输出（反转版）。返回 True=安全，mapping 反转后 True=拦截"""
    bot_message = context.get("bot_message", "") if context else ""
    is_safe = len(bot_message) > 0 and "不行" not in bot_message

    print(f"    [self_check_output_v2] 审核: '{bot_message}' → 安全={is_safe}")
    return is_safe
