import re
from datetime import datetime
from typing import Dict, Any
from neo4j import GraphDatabase, Driver


class Neo4jOGM:
    """
    A class to interact with a Neo4j database using the Object-Graph Mapping (OGM) approach.

    This class provides methods for building and executing Cypher queries while abstracting
    the complexity of the underlying database interactions. It allows for dynamic construction
    of queries with support for parameters, filtering, and property management.

    Attributes:
        driver (GraphDatabase.driver): The Neo4j database driver instance for managing sessions.
        __query (str): The current query being built.
        __parameters (dict): A dictionary of parameters to be used in the Cypher queries.
        __where_conditions (list): A list of conditions for filtering results in the queries.
        __match_parts (list): A list of MATCH clauses for constructing the query.
        __create_parts (list): A list of CREATE clauses for constructing the query.
        __set_parts (list): A list of SET clauses for updating properties in the query.
        __return_parts (list): A list of RETURN clauses for specifying what to return from the query.
        __tail_parts (list): A list for additional query components or modifications.

    Args:
        uri (str): The URI of the Neo4j database to connect to (e.g., "bolt://localhost:7687").
        user (str): The username for authentication.
        password (str): The password for authentication.
        graph_driver (optional): A pre-existing GraphDatabase driver instance. If provided, this will
                                 be used instead of creating a new driver.
    """

    def __init__(
        self,
        uri: str = None,
        user: str = None,
        password: str = None,
        graph_driver: Driver = None,
    ):
        self.driver = (
            graph_driver
            if graph_driver
            else GraphDatabase.driver(uri, auth=(user, password))
        )
        self.__query = ""
        self.__parameters = {}
        self.__where_conditions = []
        self.__match_parts = []
        self.__merge_parts = []
        self.__create_parts = []
        self.__set_parts = []
        self.__return_parts = []
        self.__tail_parts = []

    def get_cypher(self):
        return self.__query

    def get_parameters(self):
        return self.__parameters

    def execute_raw_cypher(self, cypher: str, parameters: Dict[str, Any]):
        """
        Executes a raw Cypher query with the provided parameters.

        :param cypher: The Cypher query string to be executed.
        :param parameters: A dictionary of parameters to be passed to the query.
        :return: The result of the query execution as a list of dictionaries.
        """
        with self.driver.session() as session:
            result = session.run(cypher, parameters)
            return result.data()

    def call_apoc_periodic_iterate(self, config: Dict[str, Any] = None):
        """
        Constructs a CALL apoc.periodic.iterate query using current read and write queries constructed with class methods.

        :param config: A dictionary of configuration parameters for the iterate function.
        :return: The updated query object for method chaining.
        """
        read_query = self.__build_read_query()
        write_query = (
            self.__build_write_query()
        )  # Create the write query using existing methods

        config_str = ", ".join(
            [f"{key}: {value}" for key, value in (config or {}).items()]
        )
        self.__query = f"""CALL apoc.periodic.iterate("{read_query.rstrip()}", "{write_query.rstrip()}", {{{config_str}}})
        """
        return self

    def __build_read_query(self):
        """
        Constructs the read portion of the Cypher query for retrieving data from the Neo4j database.

        This method combines the MATCH, WHERE, RETURN, and tail parts of the query into a single
        read query string. It ensures that all necessary components for executing a read operation
        are correctly formatted and included.

        :return: A string representing the complete read portion of the Cypher query. This includes
                 the MATCH, WHERE, RETURN, and any tail components. If no parts are defined, it returns
                 an empty string.
        """
        return (
            self.__build_match()
            + self.__build_where()
            + self.__build_return()
            + self.__build_tail()
        )

    def __build_write_query(self):
        """
        Constructs the write part of the apoc.periodic.iterate query.

        :return: The constructed write query string.
        """
        return self.__build_merge() + self.__build_create() + self.__build_set()

    @staticmethod
    def __is_valid_datetime_format(date_string: str) -> bool:
        # Define the expected format
        expected_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        try:
            datetime.strptime(date_string, expected_format)
            return True
        except ValueError:
            return False

    def __transform_datetime(self, datetime_value: datetime) -> str:
        if isinstance(datetime_value, datetime):
            return f"datetime({datetime_value.strftime('%Y-%m-%dT%H:%M:%S.000Z')})"
        if isinstance(datetime_value, str):
            if self.__is_valid_datetime_format(datetime_value):
                return f"datetime({datetime_value})"
        raise ValueError("Invalid datetime format")

    def __make_properties_query(self, properties: Dict[str, Any]) -> str:
        """
        Constructs a properties query string from a dictionary of properties.

        :param properties: A dictionary of properties where keys are property names and values are
                          the corresponding values to set in the query.
        :return: A string representation of the properties in the format {key: $param_key}, or an
                 empty string if the properties dictionary is empty or invalid.
        """
        if properties and isinstance(properties, dict):
            props_list = []
            for key, value in properties.items():
                param_key = f"param_{len(self.__parameters)}"
                props_list.append(f"{key}: ${param_key}")
                self.__parameters[param_key] = value
            props = "{" + ", ".join(props_list) + "}"
        else:
            props = ""
        return props

    def __add_match(
        self, match_type: str, cypher: str, new: bool = False, optional: bool = False
    ):
        """
        Adds a MATCH clause for nodes or relationships to the internal match parts of the query.

        This method is responsible for adding either a MATCH clause for a node or a relationship
        to the internal structure used to build a Cypher query. It handles both optional MATCHes
        and regular MATCHes, ensuring that the correct format is maintained.

        :param match_type: The type of match to add; should be either 'node' or 'relationship'.
        :param cypher: The Cypher string representing the node or relationship to be matched.
        :param new: A boolean flag indicating whether to start a new MATCH clause (True)
                     or append to the existing one (False). Default is False.
        :param optional: A boolean flag indicating whether the MATCH clause should be optional
                         (using OPTIONAL MATCH) or regular (using MATCH). Default is False.

        :return: None. This method modifies the internal state of the query by adding the
                 specified MATCH clause to the appropriate list.
        """

        def ends_with_relationship(s):
            # The regex pattern to match the specified structure without hardcoding "r" or "BelongsTo"
            pattern = r".*(<)?-\[.*?\]-(>)?$"
            return bool(re.match(pattern, s))

        optional_clause = "OPTIONAL " if optional else ""
        if match_type == "node":
            if new:
                self.__match_parts.append([f"{optional_clause}MATCH {cypher}"])
            else:
                if self.__match_parts:
                    comma = ","
                    if self.__match_parts[-1] and ends_with_relationship(
                        self.__match_parts[-1][-1].rstrip().lstrip()
                    ):
                        comma = ""
                    self.__match_parts[-1].append(comma + cypher)
        if match_type == "relationship":
            if self.__match_parts:
                self.__match_parts[-1][-1] += cypher

    def match_node(
        self, alias=None, label=None, new: bool = False, optional: bool = False
    ):
        """
        Adds a node to the MATCH clause.
        :param alias: Alias for the node.
        :param label: Label for the node.
        :param new: Whether the node should be added a new MATCH clause.
        :param optional: Whether the node should be added an OPTIONAL MATCH clause.
        """
        node = f"({alias or ''}:{label})" if label else f"({alias or ''})"
        self.__add_match(match_type="node", cypher=node, new=new, optional=optional)
        return self

    def set_properties(self, alias=None, properties: Dict[str, Any] = {}):
        """
        Sets properties for the given alias in the query.

        :param alias: The alias for the entity whose properties are being set.
        :param properties: A dictionary of properties where keys are property names and values are
                          the corresponding values to set.
        :return: The updated query object for method chaining.
        """
        for key, value in properties.items():
            param_key = f"param_{len(self.__parameters)}"
            if isinstance(value, datetime):
                value = f"datetime({value.isoformat()})"
            self.__parameters[param_key] = value
            self.__set_parts.append(f"{alias or ''}.{key} = ${param_key}")
        return self

    def match_relation(self, alias=None, rel_type=None, direction=None):
        """
        Adds a relationship to the MATCH clause.
        :param alias: Alias for the relationship.
        :param rel_type: Type of the relationship.
        :param direction: Direction of the relationship ('to', 'from', or None).
        """
        if direction == "to":
            relation = (
                f" -[{alias or ''}:{rel_type}]->" if rel_type else f"-[{alias or ''}]->"
            )
        elif direction == "from":
            relation = (
                f" <-[{alias or ''}:{rel_type}]-" if rel_type else f"<-[{alias or ''}]-"
            )
        else:
            relation = (
                f" -[{alias or ''}:{rel_type}]-" if rel_type else f"-[{alias or ''}]-"
            )
        self.__add_match(match_type="relationship", cypher=relation, new=False)
        return self

    def create_node(self, alias: str, label: str, properties: Dict[str, Any] = None):
        """
        Adds a CREATE clause for a node.

        :param alias: Alias for the node to be created.
        :param label: Label for the node (e.g., 'Basket').
        :param properties: A dictionary of properties for the node.
        """
        props = self.__make_properties_query(properties)
        if label:
            self.__create_parts.append(
                f"CREATE ({alias}:{label} {props}".rstrip() + ")"
            )
        else:
            self.__create_parts.append(f"CREATE ({alias} {props}".rstrip() + ")")

        return self

    def merge_node(self, alias: str, label: str, properties: Dict[str, Any] = None):
        """
        Adds a MERGE clause for a node.

        :param alias: Alias for the node to be merged.
        :param label: Label for the node (e.g., 'Basket').
        :param properties: A dictionary of properties for the node.
        :return: The updated query object for method chaining.
        """
        props = self.__make_properties_query(properties)
        if label:
            self.__merge_parts.append(f"MERGE ({alias}:{label} {props})")
        else:
            self.__merge_parts.append(f"MERGE ({alias} {props})")

        return self

    def delete_node(self, alias: str, detach: bool = True):
        """
        Adds a DELETE clause for a node.
        """
        if detach:
            self.__tail_parts.append(f"DETACH DELETE {alias} ")
        else:
            self.__tail_parts.append(f"DELETE {alias} ")
        return self

    def merge_relationship(
        self,
        start_alias: str,
        end_alias: str,
        rel_type: str,
        alias: str = None,
        properties: Dict[str, Any] = None,
    ):
        """
        Creates a MERGE relationship between two nodes.

        :param start_alias: Alias of the start node.
        :param end_alias: Alias of the end node.
        :param rel_type: Type of the relationship (e.g., "FRIENDS_WITH").
        :param alias: Alias for the relationship (optional).
        :param properties: Properties of the relationship (optional).
        """
        props = self.__make_properties_query(properties)
        if props:
            props = " " + props
        rel = f"({start_alias})-[{alias or ''}:{rel_type}{props}]->({end_alias})"
        self.__merge_parts.append(f"MERGE {rel}")

        return self

    def __create_relationship(
        self,
        start_alias: str,
        end_alias: str,
        rel_type: str,
        alias: str = None,
        properties: Dict[str, Any] = None,
    ):
        """
        Creates a relationship between two nodes.

        :param start_alias: Alias of the start node.
        :param end_alias: Alias of the end node.
        :param rel_type: Type of the relationship (e.g., "FRIENDS_WITH").
        :param alias: Alias for the relationship (optional).
        :param properties: Properties of the relationship (optional).
        """
        # Format relationship properties
        props = self.__make_properties_query(properties)

        # Construct the relationship creation query
        rel = f"({start_alias})-[{alias or ''}:{rel_type} {props}]->({end_alias})"
        self.__create_parts.append(f"CREATE {rel}")

        return self

    def add_relationship(self, from_node, to_node, properties):
        """
        Create a relationship between two nodes using a relationship model.

        :param from_node: The starting node of the relationship.
        :param to_node: The ending node of the relationship.
        :param properties: Additional properties for the relationship.
        :return: The relationship instance.
        """

        ogm_query = (
            self.match_node(alias="a", label=from_node.__class__.__name__)
            .match_node(alias="b", label=to_node.__class__.__name__)
            .filter(alias="a", filters=from_node.serialize())
            .filter(alias="b", filters=to_node.serialize())
            .__create_relationship(
                start_alias="a",
                end_alias="b",
                rel_type=properties["type"],
                properties=properties,
            )
        )

        ogm_query.execute()

    def where(
        self,
        alias: str,
        field: str,
        operator: str = "eq",
        value: str = None,
        condition_type: str = "AND",
    ):
        """
        Adds a structured condition to the WHERE clause.
        :param alias: Alias for the condition.
        :param field: The field name (e.g., "p1.name").
        :param operator: The operator (e.g., 'eq', 'gt', 'gte', 'lt', 'lte').
        :param value: The value to compare (e.g., "$name", 30).
        :param condition_type: The type of condition (e.g., 'AND', 'OR').
        """
        # Automatically generate parameter key
        operator_mapping = {"eq": "=", "gt": ">", "gte": ">=", "lt": "<", "lte": "<="}

        param_key = f"param_{len(self.__parameters)}"
        self.__parameters[param_key] = value
        condition = f"{alias or ''}.{field} {operator_mapping[operator]} ${param_key}"
        self.__add_condition(condition, condition_type)
        return self

    @staticmethod
    def field_function(function_name, field, *args):
        """
        Wraps a field in a Cypher function.
        :param function_name: Name of the Cypher function (e.g., COUNT, LOWER).
        :param field: The field to apply the function to.
        :param args: Additional arguments for the function.
        :return: The function-wrapped field (e.g., `COUNT(n)`).
        """
        args_str = ", ".join(map(str, args)) if args else ""
        return f"{function_name}({field}{', ' + args_str if args_str else ''})"

    def __add_condition(self, condition: str, condition_type: str):
        """
        Adds a condition to the internal list of where conditions.

        :param condition: The condition string to be added.
        :param condition_type: The type of condition ("AND" or "OR") that determines how to append
                               the condition to the existing conditions.
        :raises TypeError: If the condition_type is not "AND" or "OR", or if trying to add an "OR"
                           condition when the conditions list is empty.
        """
        if condition_type == "AND":
            if self.__where_conditions:
                self.__where_conditions[-1].append(condition)
            else:
                self.__where_conditions.append([condition])
        elif condition_type == "OR":
            if self.__where_conditions:
                self.__where_conditions.append([condition])
            else:
                raise TypeError("Condition array is empty. Can't add OR condition.")
        else:
            raise TypeError("Type can only be 'AND' or 'OR'.")

    def filter_to_conditions(
        self, alias: str, key: str, value: str, condition_type: str
    ):
        """
        Adds a filtering condition to the query.

        :param alias: The alias for the table or entity in the query.
        :param key: The field name to apply the condition.
        :param value: The value(s) for filtering, which can be:
                      - A single value (string or int) for equality.
                      - A dictionary for range filtering (with 'start' and 'end').
                      - A list for membership checking.
        :param condition_type: The type of condition (e.g., "AND", "OR").
        """
        condition = ""
        if isinstance(value, str) or isinstance(value, int):
            param_key = f"param_{len(self.__parameters)}"
            self.__parameters[param_key] = value
            condition = f"{alias or ''}.{key} = ${param_key}"
        if isinstance(value, dict):
            if value.get("start"):
                param_key = f"param_{len(self.__parameters)}"
                self.__parameters[param_key] = value["start"]
                condition = f"{alias or ''}.{key} >= datetime(${param_key})"
            if value.get("end"):
                param_key = f"param_{len(self.__parameters)}"
                self.__parameters[param_key] = value["end"]
                condition = f"{alias or ''}.{key} <= datetime(${param_key})"
        if isinstance(value, list):
            param_key = f"param_{len(self.__parameters)}"
            self.__parameters[param_key] = value
            condition = f"{alias or ''}.{key} in ${param_key}"
        if condition:
            self.__add_condition(condition, condition_type)

    def filter(self, alias: str, filters: Dict[str, Any], condition_type: str = "AND"):
        """
        Adds multiple filtering conditions to the query based on the provided filters.

        :param alias: The alias for the table or entity in the query.
        :param filters: A dictionary of filters where keys are field names and values are the corresponding
                        filter values. The values can be single values, ranges, or lists.
        :param condition_type: The type of condition to apply between the filters ("AND" or "OR").
                               Default is "AND".
        :return: The updated query object for method chaining.
        """
        if filters != {}:
            for i, key in enumerate(filters):
                if condition_type == "OR" and i == 0:
                    self.filter_to_conditions(alias, key, filters[key], condition_type)
                else:
                    self.filter_to_conditions(alias, key, filters[key], "AND")
        return self

    def order_by(self, alias: str, field: str, ascending: bool = True):
        """
        Adds an ORDER BY clause to the query.

        :param alias: The alias for the node in the query.
        :param field: The field by which to order results.
        :param ascending: Whether to order results in ascending order. Default is True.
        :return: The updated query object.
        """
        order_clause = f"{alias}.{field} {'ASC' if ascending else 'DESC'}"
        self.__tail_parts.append(order_clause)
        return self  # Allow method chaining

    def __build_match(self):
        """
        Constructs the MATCH clause of the Cypher query.

        This method combines all stored MATCH parts into a single MATCH clause. If no MATCH
        parts are present, it returns an empty string.

        :return: A string representing the MATCH clause of the query, or an empty string if
                 no parts are defined.
        """
        match_clause = ""
        for match_part in self.__match_parts:
            if match_part:
                match_clause += " ".join(match_part)
                match_clause += " "
        return match_clause

    def __build_merge(self):
        """
        Constructs the MERGE clause of the Cypher query.

        :return: A string representing the MERGE clause of the query, or an empty string if no parts are defined.
        """
        if self.__merge_parts:
            return " ".join(self.__merge_parts) + " "
        return ""

    def __build_where(self):
        """
        Constructs the WHERE clause of the Cypher query.

        This method combines all stored conditions into a single WHERE clause, grouping them
        appropriately. Each group of conditions is combined with 'AND', and different groups are
        combined with 'OR'. If no conditions are defined, it returns an empty string.

        :return: A string representing the WHERE clause of the query, or an empty string if
                 no conditions are defined.
        """
        if self.__where_conditions:
            conditions = []
            for i, cond_group in enumerate(self.__where_conditions):
                condition = f"({' AND '.join(cond_group)})"
                if i != len(self.__where_conditions) - 1:
                    condition += " OR "
                conditions.append(condition)
            return "WHERE " + " ".join(conditions) + " "
        return ""

    def __build_create(self):
        """
        Constructs the CREATE clause of the Cypher query.

        This method combines all stored CREATE parts into a single CREATE clause. If no CREATE
        parts are defined, it returns an empty string.

        :return: A string representing the CREATE clause of the query, or an empty string if
                 no parts are defined.
        """
        if self.__create_parts:
            return " ".join(self.__create_parts) + " "
        return ""

    def __build_set(self):
        """
        Constructs the SET clause of the Cypher query.

        This method combines all stored SET parts into a single SET clause. If no SET parts are
        defined, it returns an empty string.

        :return: A string representing the SET clause of the query, or an empty string if
                 no parts are defined.
        """
        if self.__set_parts:
            return f"""SET {", ".join(self.__set_parts)} """
        return ""

    def __build_return(self):
        """
        Constructs the RETURN clause of the Cypher query.

        This method combines all stored RETURN parts into a single RETURN clause. If no RETURN
        parts are defined, it returns an empty string.

        :return: A string representing the RETURN clause of the query, or an empty string if
                 no parts are defined.
        """
        if self.__return_parts:
            return f"RETURN {', '.join(self.__return_parts)} "
        return ""

    def __build_tail(self):
        """
        Constructs the tail part of the Cypher query.

        This method combines all stored tail parts into a single string. If no tail parts are
        defined, it returns an empty string.

        :return: A string representing the tail part of the query, or an empty string if
                 no parts are defined.
        """
        if self.__tail_parts:
            return "".join(self.__tail_parts)
        return ""

    def aggregate(
        self, alias: str, field: str, function: str, output_alias: str = None
    ):
        """
        Adds an aggregation to the RETURN clause.

        :param alias: The alias for the node or relationship.
        :param field: The field to aggregate on.
        :param function: The aggregation function (e.g., COUNT, SUM, AVG).
        :param output_alias: The alias for the aggregated result (optional).
        :return: The updated query object.
        """
        field_expr = f"{alias}.{field}" if field else "*"
        aggregation = f"{function}({field_expr})"
        if output_alias:
            aggregation += f" AS {output_alias}"
        self.__return_parts.append(aggregation)
        return self

    def return_(self, *fields_with_aliases):
        """
        Adds a RETURN clause with optional output aliases.

        :param fields_with_aliases: A list of fields, each either a string (field name)
                                    or a tuple (field, alias).
        :return: The updated query object.
        """
        for item in fields_with_aliases:
            if isinstance(item, tuple):
                field, alias = item
                self.__return_parts.append(f"{field} AS {alias}")
            else:
                self.__return_parts.append(item)
        return self

    def limit(self, limit: int):
        """
        Adds a LIMIT clause to the query to restrict the number of results returned.

        :param limit: The maximum number of results to return from the query.
        :return: The updated query object for method chaining.
        """
        self.__tail_parts.append(f"LIMIT {limit} ")
        return self

    def offset(self, offset: int):
        """
        Adds an OFFSET clause to the query to skip a specified number of results.

        :param offset: The number of results to skip before starting to return results.
        :return: The updated query object for method chaining.
        """
        self.__tail_parts.append(f"OFFSET {offset} ")
        return self

    def sync(self):
        """
        Constructs the complete Cypher query by combining all its parts.

        This method builds the query string using the current state of the various components
        (MATCH, WHERE, CREATE, SET, RETURN, and any additional tail parts) and stores it in
        the `__query` attribute.

        :return: The updated query object for method chaining.
        """
        self.__query = (
            self.__build_match()
            + self.__build_where()
            + self.__build_merge()
            + self.__build_create()
            + self.__build_set()
            + self.__build_return()
            + self.__build_tail()
        ).rstrip()
        return self

    def execute(self):
        """
        Executes the constructed Cypher query and returns the result.

        This method synchronizes the current state of the query by building it from its components
        and then executes it within a database session. After execution, it resets the query
        state for future use.

        :return: The result of the query execution as a list of dictionaries.
        """
        with self.driver.session() as session:
            self.sync()
            result = session.run(self.__query, self.__parameters)
            self.reset()
            return result.data()

    def reset(self):
        """
        Resets the query and parameters.
        """
        self.__query = ""
        self.__where_conditions = []
        self.__match_parts = []
        self.__tail_parts = []
        self.__parameters = {}
        self.__create_parts = []
        self.__return_parts = []
        self.__set_parts = []
        self.__merge_parts = []

        return self

    def close(self):
        self.driver.close()
