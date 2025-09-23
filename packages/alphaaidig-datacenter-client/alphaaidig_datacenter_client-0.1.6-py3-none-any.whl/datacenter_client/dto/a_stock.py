"""
A股相关的数据传输对象（DTO）
"""
from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from .base import PaginationInfoDTO, StandardResponseDTO, StandardListResponseDTO, TimestampFields, IdFields


class AStockItem(BaseModel, TimestampFields, IdFields):
    """A股项"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    exchange_id: str = Field(..., description="交易所代码")
    industry_code: Optional[str] = Field(None, description="行业代码")
    industry_name: Optional[str] = Field(None, description="行业名称")
    area_code: Optional[str] = Field(None, description="地区代码")
    area_name: Optional[str] = Field(None, description="地区名称")
    market_cap: Optional[int] = Field(None, description="市值(分)")
    total_shares: Optional[int] = Field(None, description="总股本")
    float_shares: Optional[int] = Field(None, description="流通股本")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    is_st: Optional[bool] = Field(None, description="是否ST股")
    list_date: Optional[str] = Field(None, description="上市日期(YYYY-MM-DD)")


class AStockListResponse(StandardListResponseDTO):
    """A股列表响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，但有items或pagination字段，则将整个数据作为data
        if "data" not in data and ("items" in data or "pagination" in data):
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def items(self) -> List[AStockItem]:
        """获取A股项列表"""
        if isinstance(self.data, dict) and "items" in self.data:
            items = []
            for item in self.data["items"]:
                if isinstance(item, dict):
                    # 处理字段映射，将exchange映射到exchange_id
                    if "exchange" in item and "exchange_id" not in item:
                        item["exchange_id"] = item["exchange"]
                    # 如果exchange_id仍然不存在，设置一个默认值
                    if "exchange_id" not in item:
                        item["exchange_id"] = "UNKNOWN"
                    items.append(AStockItem(**item))
                else:
                    items.append(item)
            return items
        elif isinstance(self.data, list):
            # 如果data直接是列表
            items = []
            for item in self.data:
                if isinstance(item, dict):
                    # 处理字段映射，将exchange映射到exchange_id
                    if "exchange" in item and "exchange_id" not in item:
                        item["exchange_id"] = item["exchange"]
                    # 如果exchange_id仍然不存在，设置一个默认值
                    if "exchange_id" not in item:
                        item["exchange_id"] = "UNKNOWN"
                    items.append(AStockItem(**item))
                else:
                    items.append(item)
            return items
        return []
    
    @property
    def pagination(self) -> Optional[PaginationInfoDTO]:
        """获取分页信息"""
        if isinstance(self.data, dict) and "pagination" in self.data and self.data["pagination"]:
            return PaginationInfoDTO(**self.data["pagination"])
        return None
    
    @property
    def total(self) -> int:
        """获取总记录数"""
        if isinstance(self.data, dict) and "total" in self.data:
            return self.data["total"]
        if self.pagination:
            return self.pagination.total
        return len(self.items)


class AStockResponse(StandardResponseDTO):
    """A股响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，则将整个数据作为data
        if "data" not in data:
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def stock(self) -> AStockItem:
        """获取A股项"""
        if isinstance(self.data, dict):
            # 复制数据以避免修改原始数据
            data_copy = self.data.copy()
            # 处理字段映射，将exchange映射到exchange_id
            if "exchange" in data_copy and "exchange_id" not in data_copy:
                data_copy["exchange_id"] = data_copy["exchange"]
            # 如果exchange_id仍然不存在，设置一个默认值
            if "exchange_id" not in data_copy:
                data_copy["exchange_id"] = "UNKNOWN"
            return AStockItem(**data_copy)
        # 如果data不是字典，返回空对象
        return AStockItem.model_construct()


class AStockSummary(BaseModel):
    """A股统计摘要"""
    total_stocks: Optional[int] = Field(None, description="总股票数")
    total_market_cap: Optional[int] = Field(None, description="总市值(分)")
    avg_pe_ratio: Optional[float] = Field(None, description="平均市盈率")
    avg_pb_ratio: Optional[float] = Field(None, description="平均市净率")
    st_count: Optional[int] = Field(None, description="ST股数量")
    industry_distribution: Optional[Dict[str, int]] = Field(None, description="行业分布")
    area_distribution: Optional[Dict[str, int]] = Field(None, description="地区分布")


class AStockSummaryResponse(StandardResponseDTO):
    """A股统计摘要响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，则将整个数据作为data
        if "data" not in data:
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def summary(self) -> AStockSummary:
        """获取A股统计摘要"""
        if isinstance(self.data, dict):
            return AStockSummary(**self.data)
        # 如果data不是字典，返回空对象
        return AStockSummary.model_construct()