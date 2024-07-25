from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# FILE STORING ONLY VALIDATION SCHEMAS USED AS RESTAPI INPUTS/OUTPUTS


class GeneralBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CountryMapIn(GeneralBaseModel):
    iso: str = Field(..., min_length=3, max_length=3)
    names: set[str]


class MatchedCountriesIn(GeneralBaseModel):
    iso: str = Field(..., min_length=3, max_length=3)
    countries: set[str]


class MatchedCountriesOut(GeneralBaseModel):
    iso: str = Field(..., min_length=3, max_length=3)
    match_count: int
    matches: set[str]
