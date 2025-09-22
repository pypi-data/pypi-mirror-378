import enum
import uuid

from polymodel import Field, Model


class MyEnum1(str, enum.Enum):
    A = "A"
    B = "B"


class MyEnum2(str, enum.Enum):
    C = "C"
    D = "D"


class BaseModel(Model):
    id: uuid.UUID = Field(primary_key=True)
    enum_field: MyEnum2


class FlatModel(Model, table=True):
    id: uuid.UUID = Field(primary_key=True)
    enum_field: MyEnum1


class InheritModel(BaseModel, table=True):
    pass
