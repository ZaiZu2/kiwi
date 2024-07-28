from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# FILE STORING ONLY VALIDATION SCHEMAS USED AS RESTAPI INPUTS/OUTPUTS


class GeneralBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# MODEL SCHEMAS
class CountryCode(BaseModel):
    id_: int
    code: str


class CountryName(BaseModel):
    id_: int
    name: str
    country_code_id: int


# ENDPOINT SCHEMAS
class CountryMapIn(GeneralBaseModel):
    iso: str = Field(..., min_length=3, max_length=3)
    names: set[str]


class CountryMapOut(GeneralBaseModel):
    codes: list[CountryCode]
    names: list[CountryName]


class MatchedCountriesIn(GeneralBaseModel):
    iso: str = Field(..., min_length=3, max_length=3)
    countries: set[str]


class MatchedCountriesOut(GeneralBaseModel):
    iso: str = Field(..., min_length=3, max_length=3)
    match_count: int
    matches: set[str]
