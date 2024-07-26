from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.database as db


async def test_upsert_countries(
    client: AsyncClient, db_session: AsyncSession, countries_input: str
) -> None:
    """Test successful upsertion."""
    response = await client.post('/countries', json=countries_input)
    assert response.status_code == 201
    assert response.json() is None

    country_codes_added = await db_session.scalar(
        select(func.count(db.CountryCode.id_))
    )
    assert country_codes_added == 5
    country_names_added = await db_session.scalar(
        select(func.count(db.CountryName.id_))
    )
    assert country_names_added == 23

    canada_names_added = await db_session.scalar(
        select(func.count(db.CountryName.id_))
        .join(db.CountryCode, db.CountryName.country_code_id == db.CountryCode.id_)
        .where(db.CountryCode.code == 'CAN')
    )
    assert (
        canada_names_added == 3
    )  # Some languages have the same name for Canada, duplicates are omitted

    # Test upsertion of the same data - no new rows should be added
    response = await client.post('/countries', json=countries_input)

    country_codes_added = await db_session.scalar(
        select(func.count(db.CountryCode.id_))
    )
    assert country_codes_added == 5
    country_names_added = await db_session.scalar(
        select(func.count(db.CountryName.id_))
    )
    assert country_names_added == 23

    canada_names_added = await db_session.scalar(
        select(func.count(db.CountryName.id_))
        .join(db.CountryCode, db.CountryName.country_code_id == db.CountryCode.id_)
        .where(db.CountryCode.code == 'CAN')
    )
    assert canada_names_added == 3


async def test_match_country(client: AsyncClient, populate_db) -> None:
    """Test successful country name matching."""
    response = await client.post(
        '/match_country',
        json={
            'iso': 'CAN',
            'countries': [
                'Canada',
                'Kanada',
                'Mexico',
                'Brazil',
                'qweqerg',
                'Estados Unidos',
            ],
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data['iso'] == 'CAN'
    assert data['match_count'] == 2
    assert data['matches'] == ['Canada', 'Kanada']
