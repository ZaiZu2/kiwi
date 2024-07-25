from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.database as db
import src.schemas.validation as v
from src.database import get_db_session
from src.utils import TagsEnum

router = APIRouter(tags=[TagsEnum.MAIN])


@router.post('/update_country', status_code=status.HTTP_201_CREATED)
async def update_countries(
    countries_list: list[v.CountryMapIn],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Update internal country/name map, used to match country names to ISO codes."""
    for country_obj in countries_list:
        country_code = db.CountryCode(code=country_obj.iso)
        country_names = []
        for country_name in country_obj.names:
            country_name = db.CountryName(name=country_name, country_code=country_code)
            country_names.append(country_name)

        # Ideally should be executed as a bult insert. Current implementation will emit
        # separate INSERT statements for each iteration
        db_session.add_all([country_code, *country_names])
        await db_session.flush()


@router.post('/match_country', status_code=status.HTTP_200_OK)
async def match_country(
    matched_countries_in: v.MatchedCountriesIn,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> v.MatchedCountriesOut:
    """Match country names to a given ISO code."""
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
