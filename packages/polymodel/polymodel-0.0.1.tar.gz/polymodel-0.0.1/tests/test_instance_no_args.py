from typing import Optional

import pytest
from pydantic import ValidationError
from polymodel import Field, Session, Model, create_engine, select


def test_allow_instantiation_without_arguments(clear_sqlmodel):
    class Item(Model, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str
        description: Optional[str] = None

    engine = create_engine("sqlite:///:memory:")
    Model.metadata.create_all(engine)
    with Session(engine) as db:
        item = Item()
        item.name = "Rick"
        db.add(item)
        db.commit()
        statement = select(Item)
        result = db.exec(statement).all()
    assert len(result) == 1
    assert isinstance(item.id, int)
    Model.metadata.clear()


def test_not_allow_instantiation_without_arguments_if_not_table():
    class Item(Model):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str
        description: Optional[str] = None

    with pytest.raises(ValidationError):
        Item()
