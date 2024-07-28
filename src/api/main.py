from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.database as db
import src.schemas.validation as v
from src.database import dialect_upsert, get_db_session
from src.utils import TagsEnum

router = APIRouter(tags=[TagsEnum.MAIN])


@router.post('/countries', status_code=status.HTTP_201_CREATED)
async def upsert_countries(
    countries_list: list[v.CountryMapIn],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> v.CountryMapOut | None:
    """Update internal country/name map, used to match country names to ISO codes."""
    country_names_added: list[db.CountryName] = []
    country_codes_added: list[db.CountryCode] = []
    for country_obj in countries_list:
        upsert_code_query = (
            dialect_upsert(db.CountryCode)
            .values({'code': country_obj.iso})
            .on_conflict_do_nothing()
            .returning(db.CountryCode)
        )
        country_code = await db_session.scalar(upsert_code_query)
        # If the country code already exists, UPSERT will return None
        if country_code is None:
            country_code = await db_session.scalar(
                select(db.CountryCode).where(db.CountryCode.code == country_obj.iso)
            )
        else:
            country_codes_added.append(country_code)

        country_names = [
            {'name': country_name, 'country_code_id': country_code.id_}
            for country_name in country_obj.names
        ]
        upsert_name_query = (
            dialect_upsert(db.CountryName)
            .values(country_names)
            .on_conflict_do_nothing()
            .returning(db.CountryName)
        )
        country_names_result = await db_session.scalars(upsert_name_query)
        country_names_added.extend(list(country_names_result))

    if not country_codes_added and not country_names_added:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail='No new codes or countries were added.',
        )

    return v.CountryMapOut(
        codes=[
            v.CountryCode(**country_code.to_dict())
            for country_code in country_codes_added
        ],
        names=[
            v.CountryName(**country_name.to_dict())
            for country_name in country_names_added
        ],
    )


@router.post('/match_country', status_code=status.HTTP_200_OK)
async def match_country(
    matched_countries_in: v.MatchedCountriesIn,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> v.MatchedCountriesOut:
    """Filter country names from the provided ones, given an ISO code."""
    does_code_exist = await db_session.scalar(
        select(db.CountryCode.id_).where(
            db.CountryCode.code == matched_countries_in.iso
        )
    )
    if not does_code_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'ISO code {matched_countries_in.iso} not found in the database.',
        )

    name_result = await db_session.scalars(
        select(db.CountryName.name)
        .join(db.CountryCode, db.CountryName.country_code_id == db.CountryCode.id_)
        .where(
            db.CountryCode.code == matched_countries_in.iso,
            db.CountryName.name.in_(matched_countries_in.countries),
        )
    )
    country_names = list(name_result)

    return v.MatchedCountriesOut(
        iso=matched_countries_in.iso,
        match_count=len(country_names),
        matches=country_names,
    )
