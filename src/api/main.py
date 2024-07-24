from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.validation as v
from src.database import get_db_session
from src.utils import TagsEnum

router = APIRouter(tags=[TagsEnum.MAIN])


@router.get('/match_country', status_code=status.HTTP_200_OK)
async def get_client_player(
    matched_countries_in: v.MatchedCountriesIn,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> v.MatchedCountriesOut:
    return v.Player(**player_db.to_dict())
