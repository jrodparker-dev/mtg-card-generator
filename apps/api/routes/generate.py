from fastapi import APIRouter

from shared.schema import GenerateRequest, GenerateResponse, GeneratedCard
from brains.Card_Creator_Brain.generate_card import generate_card_payload

router = APIRouter()

@router.post("/generate-card", response_model=GenerateResponse)
def generate_card(req: GenerateRequest) -> GenerateResponse:
    payload = generate_card_payload(req.name)
    return GenerateResponse(card=GeneratedCard(**payload))
