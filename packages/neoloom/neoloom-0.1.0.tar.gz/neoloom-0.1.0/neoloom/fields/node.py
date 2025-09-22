from datetime import datetime

from neoloom.fields.base import BaseField


class StringField(BaseField):
    def __init__(self, default=None, unique=False, nullable=True, max_length=None):
        super().__init__(type_=str, default=default, unique=unique, nullable=nullable)
        self.max_length = max_length

    def __set__(self, instance, value):
        if self.max_length and value and len(value) > self.max_length:
            raise ValueError(f"Value length exceeds max_length of {self.max_length}")
        super().__set__(instance, value)


class IntegerField(BaseField):
    def __init__(self, default=None, unique=False, nullable=True, min_value=None, max_value=None):
        super().__init__(type_=int, default=default, unique=unique, nullable=nullable)
        self.min_value = min_value
        self.max_value = max_value

    def __set__(self, instance, value):
        if value is not None:
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"Value {value} is less than min_value {self.min_value}")
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"Value {value} exceeds max_value {self.max_value}")
        super().__set__(instance, value)


class FloatField(BaseField):
    def __init__(self, default=None, unique=False, nullable=True):
        super().__init__(type_=float, default=default, unique=unique, nullable=nullable)


class BooleanField(BaseField):
    def __init__(self, default=None, unique=False, nullable=True):
        super().__init__(type_=bool, default=default, unique=unique, nullable=nullable)


class DateTimeField(BaseField):
    def __init__(self, default=None, nullable=True):
        """
        A field representing a datetime value.

        :param default: A default value for the field (should be a datetime object or a callable like `datetime.now`).
        :param nullable: Whether this field allows null values.
        """
        super().__init__(type_=datetime, default=default, nullable=nullable)

    def validate(self, value):
        """
        Validates that the value is a valid datetime or None if nullable.

        :param value: The value to validate.
        :raises ValueError: If the value is invalid.
        """
        if value is None and not self.nullable:
            raise ValueError(f"{self.__class__.__name__} does not allow null values.")
        if value is not None and not isinstance(value, datetime):
            raise ValueError(f"{self.__class__.__name__} expects a datetime object, got {type(value)}.")
        return value

    def serialize(self, value):
        """
        Serializes the datetime value into a string format for storage.

        :param value: The datetime value to serialize.
        :return: A string representation of the datetime or None.
        """
        if value is None:
            return None
        return value.isoformat()

    def deserialize(self, value):
        """
        Deserializes a string value into a datetime object.

        :param value: The string value to deserialize.
        :return: A datetime object or None.
        """
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Invalid datetime string format: {value}")
        raise TypeError(f"Cannot deserialize value of type {type(value)} into a datetime.")
