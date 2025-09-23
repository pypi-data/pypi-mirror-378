"""
数据传输对象（DTO）模块
"""
from .base import (
    PaginationInfoDTO,
    StandardResponseDTO,
    StandardListResponseDTO,
    TimestampFields,
    IdFields
)
from .margin_analysis import (
    MarginAnalysisItem,
    MarginAnalysisListResponse,
    MarginAnalysisResponse
)
from .margin_account import (
    MarginAccountItem,
    MarginAccountListResponse,
    MarginAccountResponse
)
from .margin_detail import (
    MarginDetailItem,
    MarginDetailListResponse
)
from .margin_summary import (
    MarginSummaryItem,
    MarginSummaryListResponse,
    MarginSummaryResponse
)
from .a_stock import (
    AStockItem,
    AStockListResponse,
    AStockResponse,
    AStockSummary,
    AStockSummaryResponse
)
from .hk_stock import (
    HKStockItem,
    HKStockListResponse,
    HKStockResponse,
    HKStockSummary,
    HKStockSummaryResponse
)
from .hs_industry import (
    HSIndustryItem,
    HSIndustryListResponse,
    HSIndustryResponse,
    HSIndustrySummary,
    HSIndustrySummaryResponse
)

__all__ = [
    # 基础DTO
    "PaginationInfoDTO",
    "StandardResponseDTO",
    "StandardListResponseDTO",
    "TimestampFields",
    "IdFields",
    
    # 融资融券分析
    "MarginAnalysisItem",
    "MarginAnalysisListResponse",
    "MarginAnalysisResponse",
    
    # 融资融券账户
    "MarginAccountItem",
    "MarginAccountListResponse",
    "MarginAccountResponse",
    
    # 融资融券详情
    "MarginDetailItem",
    "MarginDetailListResponse",
    
    # 融资融券汇总
    "MarginSummaryItem",
    "MarginSummaryListResponse",
    "MarginSummaryResponse",
    
    # A股
    "AStockItem",
    "AStockListResponse",
    "AStockResponse",
    "AStockSummary",
    "AStockSummaryResponse",
    
    # 港股
    "HKStockItem",
    "HKStockListResponse",
    "HKStockResponse",
    "HKStockSummary",
    "HKStockSummaryResponse",
    
    # 申万行业
    "HSIndustryItem",
    "HSIndustryListResponse",
    "HSIndustryResponse",
    "HSIndustrySummary",
    "HSIndustrySummaryResponse"
]