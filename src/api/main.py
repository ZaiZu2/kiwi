from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.database as db
import src.schemas.validation as v
from src.database import get_db_session
from src.utils import TagsEnum

router = APIRouter(tags=[TagsEnum.MAIN])


@router.get('/match_country', status_code=status.HTTP_200_OK)
async def get_client_player(
    matched_countries_in: v.MatchedCountriesIn,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> v.MatchedCountriesOut:
    country_names = await db_session.scalars(
        select(db.CountryName.name)
        .join(db.CountryCode, db.CountryName.country_code_id == db.CountryCode.id_)
        .where(db.CountryCode.code == matched_countries_in.iso)
    )
    name_intersection = set(country_names) & set(matched_countries_in.countries)

    return v.MatchedCountriesOut(
        iso=matched_countries_in.iso,
        match_count=len(name_intersection),
        matches=name_intersection,
    )
