from typing import Any, Dict, List

import neo4j

from neoloom.db import Neo4jOGM
from neoloom.fields.base import BaseField
from neoloom.nodes.meta import NodeMeta
from neoloom.relationships import BaseRelationship
from neoloom.serializers import BaseSerializer

_ = None  # satisfy linter for previous duplicate import cleanup


class BaseNode(BaseSerializer, metaclass=NodeMeta):
    def __init__(self, **kwargs):
        # Relationship container for descriptor-backed relations
        self.__relationships__ = {}
        self.__unique__ = []
        self.__nullable__ = []
        self.__default__ = []
        for key, field in self._fields.items():
            if field.default:
                self.__default__.append(key)
            if field.nullable:
                self.__nullable__.append(key)
            if field.unique:
                self.__unique__.append(key)
            if key in kwargs:
                setattr(self, key, kwargs[key])
            elif isinstance(field, BaseField) and field.default is not None:
                setattr(self, key, field.default)

    def serialize(self, exclude: List[str] = []):
        """
        Serializes the node instance into a dictionary, converting types as needed.
        :return: A dictionary representation of the node.
        """
        data = {}
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)
            if isinstance(value, neo4j.time.DateTime):
                value = self._neo4j_datetime_to_python(value)
            elif isinstance(value, BaseRelationship):
                value = value.serialize()  # Serialize nested relationships, if any
            data[field_name] = value

        if exclude:
            for field_name in exclude:
                if field_name in data:
                    del data[field_name]
        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]):
        """
        Deserializes a dictionary into a node instance, handling special types.
        :param data: A dictionary containing the node data.
        :return: An instance of the node.
        """
        instance_data = {}
        for field_name, field in cls._fields.items():
            if field_name not in data:
                continue
            value = data.get(field_name, field.default)
            if isinstance(value, dict) and issubclass(
                field.__class__, BaseRelationship
            ):
                value = field.deserialize(value)  # Handle nested relationships
            elif isinstance(value, neo4j.time.DateTime):
                value = cls._neo4j_datetime_to_python(value)
            instance_data[field_name] = value
        return cls(**instance_data)

    def __validate_uniqueness(self, ogm: Neo4jOGM, properties: Dict[str, Any]):
        for field_key in self.__unique__:
            filter_conditions = {field_key: properties[field_key]}
            existing_node = type(self).find(ogm, **filter_conditions)
            if existing_node and not properties:
                raise ValueError(
                    f"A node with {field_key} = {properties[field_key]} already exists."
                )

    def __validate_nullables(self):
        for field in self._fields.keys():
            if field not in self.__nullable__ and getattr(self, field) in (None, ""):
                raise ValueError(f"Field {field} is not nullable.")

    def __update_node(self, ogm: Neo4jOGM, props: Dict[str, Any]):
        existing_node = None
        for key, value in props.items():
            existing_node = type(self).find(ogm, key=value)
            if existing_node:
                break
        if existing_node is None:
            raise ValueError("A node with such props does not exist.")
        class_name = self.__class__.__name__
        (
            ogm.match_node(alias=class_name.lower(), label=class_name)
            .filter(
                alias=class_name.lower(),
                filters=existing_node[0].serialize(
                    exclude=list(self._relationships.keys())
                ),
            )
            .set_properties(alias=class_name.lower(), properties=props)
            .return_(class_name.lower() + "{.*}")
            .execute()
        )

    def __add_relationships(self, ogm: Neo4jOGM):
        for rel_field_name, rel_field in self._relationships.items():
            relationship = getattr(self, rel_field_name, [])
            if relationship:
                # Create the relationship in the database
                relationship_instance: BaseRelationship = relationship
                relationship_properties = relationship_instance.serialize()
                from_node = self
                to_node = relationship_instance.related_node
                ogm.add_relationship(from_node, to_node, relationship_properties)

    def save(self, ogm: Neo4jOGM, update: bool = False):
        self.__validate_nullables()
        props = {
            key: getattr(self, key)
            for key in self._fields.keys()
            if isinstance(self._fields[key], BaseField)
        }
        action = self.__update_node if update else self.__validate_uniqueness
        action(ogm, props)
        if not update:
            ogm.create_node(
                alias=self.__class__.__name__.lower(),
                label=self.__class__.__name__,
                properties=props,
            ).execute()
        self.__add_relationships(ogm)

    @classmethod
    def find(cls, ogm: Neo4jOGM, **filters):
        records = (
            ogm.match_node(alias=cls.__name__.lower(), label=cls.__name__)
            .filter(alias=cls.__name__.lower(), filters=filters)
            .return_(cls.__name__.lower() + "{.*}")
            .execute()
        )
        return [cls.deserialize(record[cls.__name__.lower()]) for record in records]
