"""
港股相关的数据传输对象（DTO）
"""
from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from .base import PaginationInfoDTO, StandardResponseDTO, StandardListResponseDTO, TimestampFields, IdFields


class HKStockItem(BaseModel, TimestampFields, IdFields):
    """港股项"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    stock_name_en: Optional[str] = Field(None, description="股票英文名称")
    industry_code: Optional[str] = Field(None, description="行业代码")
    industry_name: Optional[str] = Field(None, description="行业名称")
    market_cap: Optional[int] = Field(None, description="市值(分)")
    total_shares: Optional[int] = Field(None, description="总股本")
    float_shares: Optional[int] = Field(None, description="流通股本")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    dividend_yield: Optional[float] = Field(None, description="股息率")
    list_date: Optional[str] = Field(None, description="上市日期(YYYY-MM-DD)")


class HKStockListResponse(StandardListResponseDTO):
    """港股列表响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，但有items或pagination字段，则将整个数据作为data
        if "data" not in data and ("items" in data or "pagination" in data):
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def items(self) -> List[HKStockItem]:
        """获取港股项列表"""
        if isinstance(self.data, dict) and "items" in self.data:
            return [HKStockItem(**item) if isinstance(item, dict) else item for item in self.data["items"]]
        elif isinstance(self.data, list):
            # 如果data直接是列表
            return [HKStockItem(**item) if isinstance(item, dict) else item for item in self.data]
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


class HKStockResponse(StandardResponseDTO):
    """港股响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，则将整个数据作为data
        if "data" not in data:
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def stock(self) -> HKStockItem:
        """获取港股项"""
        if isinstance(self.data, dict):
            return HKStockItem(**self.data)
        # 如果data不是字典，返回空对象
        return HKStockItem.model_construct()


class HKStockSummary(BaseModel):
    """港股统计摘要"""
    total_stocks: Optional[int] = Field(None, description="总股票数")
    total_market_cap: Optional[int] = Field(None, description="总市值(分)")
    avg_pe_ratio: Optional[float] = Field(None, description="平均市盈率")
    avg_pb_ratio: Optional[float] = Field(None, description="平均市净率")
    avg_dividend_yield: Optional[float] = Field(None, description="平均股息率")
    industry_distribution: Optional[Dict[str, int]] = Field(None, description="行业分布")


class HKStockSummaryResponse(StandardResponseDTO):
    """港股统计摘要响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，则将整个数据作为data
        if "data" not in data:
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def summary(self) -> HKStockSummary:
        """获取港股统计摘要"""
        if isinstance(self.data, dict):
            return HKStockSummary(**self.data)
        # 如果data不是字典，返回空对象
        return HKStockSummary.model_construct()