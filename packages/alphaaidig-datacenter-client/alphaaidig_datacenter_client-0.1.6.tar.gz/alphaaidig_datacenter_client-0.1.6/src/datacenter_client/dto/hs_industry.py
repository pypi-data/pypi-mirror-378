"""
申万行业相关的数据传输对象（DTO）
"""
from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from .base import PaginationInfoDTO, StandardResponseDTO, StandardListResponseDTO, TimestampFields, IdFields


class HSIndustryItem(BaseModel, TimestampFields, IdFields):
    """申万行业项"""
    industry_code: str = Field(..., description="行业代码")
    industry_name: str = Field(..., description="行业名称")
    parent_code: Optional[str] = Field(None, description="父级行业代码")
    level: Optional[int] = Field(None, description="行业级别(1-3)")
    stock_count: Optional[int] = Field(None, description="包含股票数量")
    total_market_cap: Optional[int] = Field(None, description="总市值(分)")
    avg_pe_ratio: Optional[float] = Field(None, description="平均市盈率")
    avg_pb_ratio: Optional[float] = Field(None, description="平均市净率")
    description: Optional[str] = Field(None, description="行业描述")


class HSIndustryListResponse(StandardListResponseDTO):
    """申万行业列表响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，但有items或pagination字段，则将整个数据作为data
        if "data" not in data and ("items" in data or "pagination" in data):
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def items(self) -> List[HSIndustryItem]:
        """获取申万行业项列表"""
        if isinstance(self.data, dict) and "items" in self.data:
            return [HSIndustryItem(**item) if isinstance(item, dict) else item for item in self.data["items"]]
        elif isinstance(self.data, list):
            # 如果data直接是列表
            return [HSIndustryItem(**item) if isinstance(item, dict) else item for item in self.data]
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


class HSIndustryResponse(StandardResponseDTO):
    """申万行业响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，则将整个数据作为data
        if "data" not in data:
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def industry(self) -> HSIndustryItem:
        """获取申万行业项"""
        if isinstance(self.data, dict):
            return HSIndustryItem(**self.data)
        # 如果data不是字典，返回空对象
        return HSIndustryItem.model_construct()


class HSIndustrySummary(BaseModel):
    """申万行业统计摘要"""
    total_industries: Optional[int] = Field(None, description="总行业数")
    level_distribution: Optional[Dict[int, int]] = Field(None, description="级别分布")
    total_market_cap: Optional[int] = Field(None, description="总市值(分)")
    avg_pe_ratio: Optional[float] = Field(None, description="平均市盈率")
    avg_pb_ratio: Optional[float] = Field(None, description="平均市净率")
    top_industries_by_market_cap: Optional[List[Dict[str, Any]]] = Field(None, description="市值前几的行业")
    top_industries_by_stock_count: Optional[List[Dict[str, Any]]] = Field(None, description="股票数前几的行业")


class HSIndustrySummaryResponse(StandardResponseDTO):
    """申万行业统计摘要响应"""
    
    def __init__(self, **data):
        """初始化方法，处理没有data字段的情况"""
        # 如果传入的数据没有data字段，则将整个数据作为data
        if "data" not in data:
            super().__init__(status=data.get("status", "success"), data=data)
        else:
            super().__init__(**data)
    
    @property
    def summary(self) -> HSIndustrySummary:
        """获取申万行业统计摘要"""
        if isinstance(self.data, dict):
            return HSIndustrySummary(**self.data)
        # 如果data不是字典，返回空对象
        return HSIndustrySummary.model_construct()