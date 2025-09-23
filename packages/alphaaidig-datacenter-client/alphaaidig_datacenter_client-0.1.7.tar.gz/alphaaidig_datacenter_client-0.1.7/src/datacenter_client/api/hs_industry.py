from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import BaseClient

from ..dto.hs_industry import (
    HSIndustryListResponse,
    HSIndustryResponse,
    HSIndustrySummaryResponse
)


class HSIndustryClient:
    """Client for HS-Industry related endpoints."""
    def __init__(self, client: "BaseClient"):
        self._client = client

    def page_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        business_category: Optional[str] = None
    ) -> HSIndustryListResponse:
        """
        Get a paginated list of HS-industries.
        Corresponds to GET /hs_industry/page_list
        
        Returns:
            HSIndustryListResponse containing paginated HS-industry data
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        if business_category:
            params["business_category"] = business_category
        
        response_data = self._client._request("GET", "/api/v1/hs_industry/page_list", params=params)
        return HSIndustryListResponse(**response_data)

    def get(self, industry_code: str) -> HSIndustryResponse:
        """
        Get details for a specific HS-industry by its code.
        Corresponds to GET /hs_industry/{industry_code}
        
        Returns:
            HSIndustryResponse containing HS-industry details
        """
        response_data = self._client._request("GET", f"/api/v1/hs_industry/{industry_code}")
        return HSIndustryResponse(**response_data)

    def summary(self) -> HSIndustrySummaryResponse:
        """
        Get statistical summary of HS-industries.
        Corresponds to GET /hs_industry/stats/summary
        
        Returns:
            HSIndustrySummaryResponse containing HS-industry statistical summary
        """
        response_data = self._client._request("GET", "/api/v1/hs_industry/stats/summary")
        return HSIndustrySummaryResponse(**response_data)