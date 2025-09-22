from datetime import datetime


class BaseSerializer:
    @classmethod
    def _neo4j_datetime_to_python(cls, neo4j_datetime):
        """
        Converts a neo4j.time.DateTime object to a Python datetime object.
        """
        if neo4j_datetime is None:
            return None

        microsecond = int(neo4j_datetime.nanosecond / 1000)
        dt = datetime(
            neo4j_datetime.year,
            neo4j_datetime.month,
            neo4j_datetime.day,
            neo4j_datetime.hour,
            neo4j_datetime.minute,
            neo4j_datetime.second,
            microsecond,
        )

        if neo4j_datetime.tzinfo:
            offset = neo4j_datetime.tzinfo.utcoffset(None)
            if offset:
                dt -= offset

        return dt