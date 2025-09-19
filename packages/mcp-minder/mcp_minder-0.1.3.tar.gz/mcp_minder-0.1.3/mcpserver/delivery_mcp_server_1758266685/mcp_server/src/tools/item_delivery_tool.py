from typing import Any, Dict, Optional


def register_item_delivery_tool(mcp_instance):
    @mcp_instance.tool()
    def item_delivery(
        delivery_point:  Optional[str] = None,
        pickup_point: Optional[str] = None,
        pickup_phone: Optional[str] = None,
        receiver_phone: Optional[str] = None,
        delivery_item: Optional[str] = None,
        delivery_type: Optional[str] = None,
        collected_result: int = 0,
    ) -> str:
        """
        物品配送工具，机器人可以完成各种"物品或者东西"的配送任务
        Args:
            delivery_point: 配送点信息
            pickup_point: 取货点信息
            pickup_phone: 取货人手机号
            receiver_phone: 接收人手机号
            delivery_item: 配送的物品、东西
            delivery_type: 配送物品类型（水，文件，咖啡，其它）
            collected_result: 收集结果状态: 0=必填项未填, 1=全部必填项完整, 2=用户确认, 3=用户取消 
        
        Returns:
            str: 配送任务执行结果
        """
        # 构建配送数据
        delivery_data = {
            "delivery_point": delivery_point,
            "pickup_point": pickup_point,
            "pickup_phone": pickup_phone,
            "receiver_phone": receiver_phone,
            "delivery_item": delivery_item or "未知",
            "delivery_type": delivery_type or "其它",
            "collected_result": collected_result
        }
        summary = build_delivery_summary(delivery_data)
        return f"配送任务信息已收集完整：{summary}\n请确认信息是否正确。"
        # # 根据收集结果状态返回不同的响应
        # if collected_result == 0:
        #     return "配送任务创建失败：必填项未填写完整"
        # elif collected_result == 1:
        #     summary = build_delivery_summary(delivery_data)
        #     return f"配送任务信息已收集完整：{summary}\n请确认信息是否正确。"
        # elif collected_result == 2:
        #     summary = build_delivery_summary(delivery_data)
        #     # 这里可以添加实际的配送逻辑，如调用配送API等
        #     return f"配送任务已确认并开始执行：{summary}\n配送任务已分配，预计30分钟内送达。"
        # elif collected_result == 3:
        #     return "配送任务已取消"
        # else:
        #     return "未知的操作状态"
    
    def build_delivery_summary(data: dict) -> str:
        """构建配送信息摘要"""
        details = []
        if data.get("pickup_point"):
            pickup_point = data['pickup_point']
            details.append(f"取货点：{pickup_point}")
        if data.get("pickup_phone"):
            details.append(f"取货电话：{data['pickup_phone']}")
        if data.get("delivery_point"):
            delivery_point = data['delivery_point']
            details.append(f"配送至：{delivery_point}")
        if data.get("receiver_phone"):
            details.append(f"收件电话：{data['receiver_phone']}")
        
        # Modified part: Handle delivery_type mapping to numeric code
        if data.get("delivery_type"):
            delivery_type_str = data.get("delivery_type")
            # delivery_type_code = DELIVERY_TYPE_MAPPING.get(delivery_type_str, 1)  # Default to 1 (其它)
            details.append(f'物品类型：{delivery_type_str}')
        
        if data.get("delivery_item"):
            details.append(f'物品：{data.get("delivery_item")}')

        #     # 显示4位数字提货码
        # if data.get("collection_verification_code"):
        #     details.append(f'收件验证码：{data.get("collection_verification_code")}')
            
        return "\n" + "\n".join(details) 
    
    return mcp_instance