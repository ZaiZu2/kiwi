from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
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
        upsert_code_query = (
            sqlite_upsert(db.CountryCode)
            .values({'code': country_obj.iso})
            .on_conflict_do_nothing()
            .returning(db.CountryCode.id_)
        )
        country_code_id = await db_session.scalar(upsert_code_query)

        country_names = [
            {'name': country_name, 'country_code_id': country_code_id}
            for country_name in country_obj.names
        ]
        sqlite_upsert(db.CountryName).values(country_names).on_conflict_do_nothing()


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
