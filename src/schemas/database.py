from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.ext.asyncio import AsyncAttrs

# FILE STORING ONLY ORM SCHEMAS USED AS PERSISTANCE MODELS
# NOTE: CASCADE ON DELETE behavior not resolved as no resources are to be deleted in this project

metadata = sa.MetaData(
    naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s',
    }
)


class Base(AsyncAttrs, so.DeclarativeBase):
    metadata = metadata

    def to_dict(self) -> dict:
        """Serialize row values to a dictionary."""
        return {
            col_name: getattr(self, col_name) for col_name in self.__mapper__.c.keys()
        }

    def update(self, data: dict) -> None:
        table_columns = self.__mapper__.c.keys()
        for column, value in data.items():
            if column in table_columns:
                setattr(self, column, value)


class CountryName(Base):
    __tablename__ = 'country_names'

    id_: so.Mapped[int] = so.mapped_column('id', primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True)

    country_code_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('country_codes.id')
    )
    country_code: so.Mapped[CountryCode] = so.relationship(
        back_populates='country_names'
    )


class CountryCode(Base):
    """Conforms to ISO 3166-1 alpha-3."""

    __tablename__ = 'country_codes'

    id_: so.Mapped[int] = so.mapped_column('id', primary_key=True)
    code: so.Mapped[str] = so.mapped_column(sa.String(3), unique=True)

    country_names: so.Mapped[list[CountryName]] = so.relationship(
        back_populates='country_name'
    )
