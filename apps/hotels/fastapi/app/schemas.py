from pydantic import BaseModel
from typing import Optional, List


class HotelsRequest(BaseModel):
    query: str
    page: int


class HotelData(BaseModel):
    id: int
    name: str
    description: Optional[str]
    url: str
    rating: Optional[float]
    reviews: Optional[int]
    rank: Optional[int]
    rank_total: Optional[int]
    stars: Optional[int]


class SaveHotelDataRequest(BaseModel):
    city_id: int
    data: List[HotelData]
