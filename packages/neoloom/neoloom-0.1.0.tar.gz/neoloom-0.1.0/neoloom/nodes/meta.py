from neoloom.fields.base import BaseField, BaseRelation


class NodeMeta(type):
    def __new__(cls, name, bases, dct):
        fields = {k: v for k, v in dct.items() if isinstance(v, (BaseField, BaseRelation))}
        for field_name, field in fields.items():
            field.name = field_name
        dct["_fields"] = {k: v for k, v in fields.items() if isinstance(v, BaseField)}
        dct["_relationships"] = {k: v for k, v in fields.items() if isinstance(v, BaseRelation)}
        return super().__new__(cls, name, bases, dct)