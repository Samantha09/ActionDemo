from action import action


@action(is_system_action=True)
async def detect_sensitive_data(text: str, **kwargs) -> dict:
    """检测敏感数据（模拟）"""
    import re

    # 简单正则检测
    phone = re.search(r"\d{11}", text)
    email = re.search(r"[\w.-]+@[\w.-]+\.\w+", text)
    id_card = re.search(r"\d{17}[\dXx]", text)

    detections = []
    if phone:
        detections.append({"type": "PHONE", "value": phone.group(), "position": phone.start()})
    if email:
        detections.append({"type": "EMAIL", "value": email.group(), "position": email.start()})
    if id_card:
        detections.append({"type": "ID_CARD", "value": id_card.group(), "position": id_card.start()})

    return {"has_sensitive_data": len(detections) > 0, "detections": detections}


@action(is_system_action=True)
async def mask_sensitive_data(text: str, **kwargs) -> str:
    """脱敏敏感数据（模拟）"""
    import re

    result = text
    result = re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", result)  # 手机号
    result = re.sub(r"([\w.-]+)@([\w.-]+\.\w+)", r"***@\2", result)  # 邮箱
    result = re.sub(r"(\d{6})\d{8}([\dXx])", r"\1********\2", result)  # 身份证

    return result
