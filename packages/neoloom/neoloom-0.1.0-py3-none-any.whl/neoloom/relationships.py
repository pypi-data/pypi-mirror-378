import re
from typing import List

import neo4j

from .fields.base import BaseField
from .serializers import BaseSerializer


class RelationshipMeta(type):
    def __new__(cls, name, bases, dct):
        fields = {k: v for k, v in dct.items() if isinstance(v, BaseField)}
        for field_name, field in fields.items():
            field.name = field_name
        dct["_fields"] = fields
        dct["_relationships"] = {
            k: v for k, v in fields.items() if isinstance(v, BaseRelationship)
        }
        return super().__new__(cls, name, bases, dct)


class BaseRelationship(BaseSerializer, metaclass=RelationshipMeta):
    direction: str = "BOTH"  # Default direction is "TO". Can be "FROM" or "BOTH".

    def __init__(self, related_node=None, **kwargs):
        """
        Initialize the relationship instance and assign property values.
        """
        self.related_node = related_node
        self.target_model = None
        for key, field in self.__class__.__dict__.items():
            if isinstance(field, BaseField):
                value = kwargs.get(key, field.default)
                setattr(self, key, value)

    # def __set__(self, instance, value):
    #     """
    #     Temporarily store the related node(s) until save() is called.
    #
    #     :param instance: The owner node instance.
    #     :param value: The target node instance or a list of instances.
    #     """
    #     self.resolve_target_model()

    def resolve_target_model(self):
        """
        Resolve the target model string to an actual class.
        """
        if isinstance(self.related_node, str):
            module_globals = (
                globals()
            )  # Access the global namespace of the current module
            if self.related_node in module_globals:
                self.target_model = module_globals[self.related_node]
            else:
                raise ImportError(f"Cannot resolve target model: {self.related_node}")

    def serialize(self, exclude: List[str] = None):
        """
        Serializes the relationship instance into a dictionary.
        Includes its fields, connected node, and nested relationships.
        """
        data = {
            "type": re.sub(r"(?<!^)(?=[A-Z])", "_", self.__class__.__name__).upper()
        }

        # Serialize fields
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)
            if isinstance(value, neo4j.time.DateTime):
                value = self._neo4j_datetime_to_python(value)
            data[field_name] = value

        if exclude:
            for field_name in exclude:
                if field_name in data:
                    del data[field_name]

        # Serialize related node
        # if hasattr(self, "related_node") and self.related_node:
        #     data["related_node"] = self.related_node.serialize()

        return data

    @classmethod
    def create(cls, ogm, from_node, to_node, **kwargs):
        """
        Create a relationship in the database.

        :param ogm: ORM instance for executing queries.
        :param from_node: Starting node of the relationship.
        :param to_node: Ending node of the relationship.
        :param kwargs: Additional properties for the relationship.
        """
        # Determine start and end nodes based on the relationship direction
        if cls.direction == "TO":
            start_node = from_node
            end_node = to_node
        elif cls.direction == "FROM":
            start_node = to_node
            end_node = from_node
        elif cls.direction == "BOTH":
            raise ValueError(
                "BOTH is not a valid direction for creation. Use specific TO or FROM."
            )

        relationship_instance = cls(**kwargs)
        relationship_data = relationship_instance.serialize(exclude=["direction"])

        ogm.add_relationship(
            from_node=start_node,
            to_node=end_node,
            properties=relationship_data,
        )
        return relationship_instance

    @classmethod
    def delete(cls, ogm, from_node, to_node):
        if cls.direction == "TO":
            start_node = from_node
            end_node = to_node
        elif cls.direction == "FROM":
            start_node = to_node
            end_node = from_node
        else:
            raise ValueError("BOTH is not a valid direction for deletion.")
        rel_type = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).upper()
        (
            ogm.match_node(alias="a", label=start_node.__class__.__name__, new=True)
            .match_relation(alias="r", rel_type=rel_type, direction="to")
            .match_node(alias="b", label=end_node.__class__.__name__)
            .filter("a", start_node.serialize())
            .filter("b", to_node.serialize())
            .delete_node("r", detach=False)
            .execute()
        )


class RelationshipTo(BaseRelationship):
    direction = "TO"


class RelationshipFrom(BaseRelationship):
    direction = "FROM"


class RelationshipBoth(BaseRelationship):
    direction = "BOTH"
