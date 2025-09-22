from typing import Any, Callable, List, Optional, Type


class BaseField:
    def __init__(self, type_: Any = str, default=None, unique=False, nullable=True):
        self.type = type_
        self.default = default
        self.unique = unique
        self.nullable = nullable

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance, value):
        if not isinstance(value, self.type):
            raise TypeError(f"Expected {self.type}, got {type(value)}")
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class BaseRelation:
    def __init__(
        self,
        related_node: Any = None,
        rel_type: str = None,
        type_: Any = None,
        default=None,
        nullable=True,
        direction="->",
    ):
        self.default = default
        self.nullable = nullable
        self.type = type_
        self.related_node = related_node
        self.relationship_type = rel_type
        self.direction = direction

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # Lazy load: return cached proxy or create it
        existing = instance.__relationships__.get(self.name)
        if existing is not None:
            return existing
        from neoloom.proxy import LazyRelationshipProxy
        from neoloom.nodes.node import BaseNode

        # Create loader bound to instance
        def loader():
            # Find related nodes by traversing relationship type if available
            # Use the current OGM from a hint if present on the instance
            ogm = getattr(instance, "_ogm_hint", None)
            if ogm is None:
                return []
            start_alias = "a"
            end_alias = "b"
            label_a = instance.__class__.__name__
            label_b: str
            target_type: Optional[Type[Any]] = self.related_node
            if isinstance(target_type, type):
                label_b = target_type.__name__
            else:
                # Fallback to owner label for lack of better info
                label_b = "Node"
            rel_type = self.relationship_type
            direction = self.direction
            # Build: MATCH (a:LabelA)-[r:TYPE]->(b:LabelB) WHERE a.props = instance props RETURN b{.*}
            q = (
                ogm.match_node(alias=start_alias, label=label_a, new=True)
                .match_relation(
                    alias="r",
                    rel_type=rel_type,
                    direction="to"
                    if direction == "->"
                    else ("from" if direction == "<-" else None),
                )
                .match_node(alias=end_alias, label=label_b)
                .filter(alias=start_alias, filters=instance.serialize())
            )
            records = q.return_(end_alias + "{.*}").execute()
            model_cls = target_type if isinstance(target_type, type) else None
            if model_cls is None:
                return [rec[end_alias] for rec in records]
            return [model_cls.deserialize(rec[end_alias]) for rec in records]

        proxy = LazyRelationshipProxy(loader)
        instance.__relationships__[self.name] = proxy
        return proxy

    def __set__(self, instance, value):
        if not isinstance(value, list):
            value = [value]
        for v in value:
            if self.related_node and not isinstance(v, self.related_node):
                raise TypeError(f"Expected {self.related_node}, got {type(v)}")
        instance.__relationships__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
