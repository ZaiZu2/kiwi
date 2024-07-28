import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.database as db


async def test_upsert_countries(
    client: AsyncClient, db_session: AsyncSession, countries_input: str
) -> None:
    """Test `upsert_countries` endpoint."""
    response = await client.post('/countries', json=countries_input)
    assert response.status_code == 201
    data = response.json()
    assert len(data['codes']) == 5
    assert len(data['names']) == 23

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
    # Some languages have the same name for Canada, duplicates are omitted
    assert canada_names_added == 3

    # Test upsertion of the same data - no new rows should be added
    response = await client.post('/countries', json=countries_input)
    assert response.status_code == 204

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

@pytest.mark.usefixtures('_populate_db')
async def test_match_country(client: AsyncClient) -> None:
    """Test `match_country` endpoint - successful country name matching."""
    response = await client.post(
        '/match_country',
        json={
            'iso': 'CAN',
            'countries': [
                'Canada',
                'Kanada',
                'Mexico',
                'Brazil',
                'qweqerg',  # Invalid country name
                'Estados Unidos',
            ],
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data['iso'] == 'CAN'
    assert data['match_count'] == 2
    assert set(data['matches']) == {'Canada', 'Kanada'}


@pytest.mark.usefixtures('_populate_db')
async def test_wrong_iso_code(client: AsyncClient) -> None:
    """Test `match_country` endpoint - incorrect request."""
    response = await client.post(
        '/match_country',
        json={
            'iso': 'WRONG',  # Invalid ISO code
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
    assert response.status_code == 422

    response = await client.post(
        '/match_country',
        json={
            'iso': 'XXX',  # invalid ISO code
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
    assert response.status_code == 404
