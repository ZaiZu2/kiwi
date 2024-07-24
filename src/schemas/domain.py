from __future__ import annotations

from dataclasses import dataclass, fields

# FILE STORING ONLY DOMAIN SCHEMAS USED AS INTERNAL DATA STRUCTURES


@dataclass
class DataclassMixin:
    def update(self, **kwargs):
        field_names = {f.name for f in fields(self)}
        for key, value in kwargs.items():
            if key in field_names:
                setattr(self, key, value)


@dataclass(kw_only=True)
class CountryCode(DataclassMixin):
    id_: int
    code: str  # Conforms to ISO 3166-1 alpha-3


@dataclass(kw_only=True)
class CountryNames(DataclassMixin):
    id_: int
    name: str
    country_code: CountryCode
