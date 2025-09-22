# neoloom

A lightweight Data Mapper-based OGM for Neo4j featuring:
- Unit of Work and Repository patterns
- Identity Map
- Lazy-loading relationships
- Simple Query Builder with a `QuerySet` and `Q` filters
- Field descriptors with validation

This README shows how to use the published PyPI package `neoloom` in your application code.

## Install

```bash
pip install neoloom
```

Requirements:
- Python 3.10+
- A running Neo4j instance (e.g., bolt://localhost:7687) and credentials

## Quick start

```python
from neoloom import Session, Repository
from neoloom.nodes.node import BaseNode
from neoloom.fields.node import StringField, IntegerField

class User(BaseNode):
    name = StringField(nullable=False)
    age = IntegerField(nullable=True)

session = Session(uri="bolt://localhost:7687", user="neo4j", password="password")
users = Repository(session, User)

# Create
alice = User(name="Alice", age=30)
users.add(alice)
session.commit()

# Read
fetched = users.get(name="Alice")
print(fetched.name)
```

## Defining nodes and fields

Use `BaseNode` and field descriptors from `neoloom.fields.node`:

```python
from neoloom.nodes.node import BaseNode
from neoloom.fields.node import StringField, IntegerField, BooleanField, FloatField, DateTimeField

class Product(BaseNode):
    sku = StringField(unique=True, nullable=False)
    title = StringField(nullable=False)
    price = FloatField(nullable=False)
    in_stock = BooleanField(default=True)
```

Notes:
- **Validation**: Fields enforce types and optional constraints (e.g., max_length for `StringField`, min/max for `IntegerField`).
- **Defaults**: If a field has `default`, it is applied on instantiation.
- **Uniqueness**: Unique fields are validated during `save()` for inserts.

## Relationships

neoloom supports two relationship layers you can choose from:
- Descriptor-based lazy relationships via `neoloom.fields.relation.Relationship` and `BaseRelation` (recommended for navigation/lazy-load).
- Explicit relationship models via `neoloom.relationships` (for creating/deleting relationships with properties).

### Lazy relationships (descriptor)
Define relationships on nodes using `Relationship`. To avoid forward-reference issues, reference a class defined earlier:

```python
from neoloom.nodes.node import BaseNode
from neoloom.fields.node import StringField
from neoloom.fields.relation import Relationship

class Group(BaseNode):
    name = StringField(nullable=False)

class User(BaseNode):
    name = StringField(nullable=False)
    # Outgoing relationship to Group via type MEMBER_OF
    groups = Relationship(related_node=Group, rel_type="MEMBER_OF", direction="->")
```

Access is lazy and requires the instance to be attached to a session (repositories do this automatically via an internal hint). Example traversal:

```python
from neoloom import Session, Repository

session = Session(uri="bolt://localhost:7687", user="neo4j", password="password")
users = Repository(session, User)

alice = users.get(name="Alice")
for g in alice.groups:  # triggers a lazy query
    print(g.name)
```

To assign relationships for creation during save, set the descriptor value to a node or list of nodes before `session.commit()`:

```python
devs = Group(name="Developers")
groups = Repository(session, Group)
groups.add(devs)

# Link Alice -> Developers on commit
alice.groups = devs
users.update(alice)

session.commit()  # creates the MEMBER_OF relationship
```

### Relationship models (create/delete with properties)
If you need to create/delete relationships with properties, use `neoloom.relationships`:

```python
from neoloom.relationships import RelationshipTo

class MemberOf(RelationshipTo):
    pass  # optionally define relationship property fields here

# Create relationship
MemberOf.create(session.ogm(), from_node=alice, to_node=devs)

# Delete relationship
MemberOf.delete(session.ogm(), from_node=alice, to_node=devs)
```

## Sessions and repositories

`Session` wraps the database driver and coordinates:
- Unit of Work (`add`, `update`, `delete` via `Repository`)
- Identity Map (basic caching by element id)
- Attaching an OGM hint to instances for lazy relationships

```python
from neoloom import Session, Repository

session = Session(uri="bolt://localhost:7687", user="neo4j", password="password")
users = Repository(session, User)

# Add
users.add(User(name="Carol"))
# Update (marks dirty)
carol = users.get(name="Carol")
carol.name = "Caroline"
users.update(carol)

# Commit all pending changes
session.commit()
```

## Querying

There are two ways to query:
- High-level repository methods (`get`, `find`)
- Low-level `QuerySet` using `Q` objects for compound conditions and ordering

### Repository queries

```python
# Find many (equality filters)
matches = users.find(name="Caroline")

# Get single (first match)
caroline = users.get(name="Caroline")
```

### QuerySet + Q filters

```python
from neoloom import Q
from neoloom.query import QuerySet

qs = QuerySet(User, session.ogm())
# Basic filters
qs = qs.filter(name="Alice").order_by("-age").limit(10)

# Using Q for complex filters
q = Q.from_kwargs(age__gte=18) & Q.from_kwargs(name="Alice")
qs = QuerySet(User, session.ogm()).filter(q)

results = list(qs)
```

Supported lookups in `Q` keys:
- `field` (equals)
- `field__gt`, `field__gte`, `field__lt`, `field__lte`
- Combine with `&` (AND) and `|` (OR)

## Creating and updating nodes directly

You can also operate through mappers and `save` on models:

```python
from neoloom.mappers import NodeMapper

mapper = NodeMapper(User)
alice = User(name="Alice")
mapper.insert(session.ogm(), alice)  # create

alice.age = 31
mapper.update(session.ogm(), alice)  # update (uses unique fields if defined)
```

Or by calling `save` through the Unit of Work via `Repository` as shown earlier.

## Serialization

Nodes provide `serialize()` and `deserialize()` to convert to/from Python dicts. DateTime values returned from Neo4j are normalized to Python `datetime` via the built-in serializer.

```python
payload = alice.serialize()
clone = User.deserialize(payload)
```

## Raw Cypher and APOC iterate

For advanced needs:

```python
from datetime import datetime

ogm = session.ogm()
# Build a query
rows = (
    ogm.match_node(alias="u", label="User")
       .where(alias="u", field="age", operator="gte", value=18)
       .return_("u{.*}")
       .execute()
)

# Execute raw cypher
rows = ogm.execute_raw_cypher("MATCH (u:User) RETURN u LIMIT $n", {"n": 5})

# Use APOC periodic iterate with currently built read/write parts
ogm.match_node(alias="u", label="User")
   .return_("u")
   .create_node(alias="x", label="Log", properties={"ts": datetime.utcnow()})
   .call_apoc_periodic_iterate({"batchSize": 1000})
   .execute()
```

## Best practices

- **Unique fields**: Set `unique=True` on fields you’ll use to locate/update nodes reliably.
- **Lazy relations**: Access relationship descriptors after fetching instances via a `Repository` so the session hint is present.
- **Unit of Work**: Prefer `Repository.add/update` followed by `session.commit()` to group writes.
- **Small batches**: Chain builder methods and call `execute()` once per logical operation.
- **Closing**: Call `session.close()` when done.

## License

MIT
