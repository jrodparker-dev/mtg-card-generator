from typing import List, Optional
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    name: str = Field(default="", max_length=20)


class GeneratedCard(BaseModel):
    name: str
    mana_cost: str = ""
    mana_value: Optional[int] = 0
    type_line: str
    rarity: str
    colors: List[str] = []
    oracle_text: List[str]
    flavor_text: Optional[str] = None
    art_prompt: Optional[str] = None
    art_path: Optional[str] = None
    art_data_uri: Optional[str] = None
    generator_mode: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None


class GenerateResponse(BaseModel):
    ok: bool = True
    card: GeneratedCard
