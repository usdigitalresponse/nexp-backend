# nexp.clients.data

from typing import Any, Generator, List
from json import dumps, loads
from functools import cached_property
import sqlite3

from airtable import Airtable

from nexp.aliases import OptionalString, GenAny
from nexp.config import config

ModelIterator = Generator[Any, None, None]


class Model:
    @classmethod
    def fix_key(cls, key: str) -> str:
        """Given a string, lowercase, strip, and turn spaces into underscores"""
        return "_".join(key.lower().strip().split())

    @classmethod
    def from_airtable(cls, raw: Any) -> Any:
        """Given airtable data, turn it into a Model"""
        id_ = raw["id"]
        fields = {cls.fix_key(k): v for k, v in raw["fields"].items()}
        return cls(id_, fields)

    @classmethod
    def from_row(cls, row: List[str]) -> Any:
        """Given a SQL row, turn it into a Model"""
        return cls(row[0], loads(row[1]))

    def __init__(self, id_: str, fields: dict) -> None:
        self.id_ = id_
        self.fields = fields
        [setattr(self, k, v) for k, v in self.fields.items()]

    def to_row(self) -> List[str]:
        """Return a dbapi compatible row"""
        return [self.id_, dumps(self.fields)]


class Data:
    """Provides methods to access data from and update data in our backend data
    store. We're currently using airtable, but other implementations of this class
    could use something else.
    """

    def __init__(
        self,
        api_key: OptionalString = None,
        base_id: OptionalString = None,
        db_filepath: OptionalString = None,
    ) -> None:
        self.__api_key = api_key or config.airtable_api_key
        self.__base_id = base_id or config.airtable_base_id
        self.db_filepath = db_filepath or ":memory:"
        self.__filled = False

    @cached_property
    def candidates_api(self) -> Airtable:
        return Airtable(
            self.__base_id, config.airtable_candidates_table, self.__api_key
        )

    @cached_property
    def facilities_api(self) -> Airtable:
        return Airtable(
            self.__base_id, config.airtable_facilities_table, self.__api_key
        )

    @cached_property
    def needs_api(self) -> Airtable:
        return Airtable(self.__base_id, config.airtable_needs_table, self.__api_key)

    @cached_property
    def config_api(self) -> Airtable:
        return Airtable(self.__base_id, config.airtable_config_table, self.__api_key)

    def fetchall(self, api: Airtable, **kwargs) -> GenAny:
        """Given an airtable api object, generate all of the records in the
        associated table
        """
        for page in api.get_iter(**kwargs):
            for record in page:
                yield Model.from_airtable(record)

    def list_facilities(self) -> ModelIterator:
        """List all of the facilities"""
        for facility in self.fetchall(self.facilities_api):
            if hasattr(facility, "approved") and facility.approved:
                yield facility

    @cached_property
    def config(self) -> dict:
        return {
            r.key.lower().strip(): r.value.strip()
            for r in self.fetchall(self.config_api)
        }

    @cached_property
    def needs_form_url(self) -> str:
        return self.config["needs_form_url"]

    @cached_property
    def feedback_form_url(self) -> str:
        return self.config["feedback_form_url"]

    @cached_property
    def candidates_template_id(self) -> str:
        return self.config["candidates_template_id"]

    @cached_property
    def needs_template_id(self) -> str:
        return self.config["needs_template_id"]

    @cached_property
    def no_candidates_template_id(self) -> str:
        return self.config["no_candidates_template_id"]

    @cached_property
    def send_email_from(self) -> str:
        return self.config["send_email_from"]

    @cached_property
    def unsubscribe_group_id(self) -> str:
        return self.config["unsubscribe_group_id"]

    def update_facility_no_candidates_suppression(
        self, facility: Any, value: bool
    ) -> None:
        """Given a facility object and a boolean value, update the "Suppress
        No candidates Email" field in Airtable for that facility"""
        self.facilities_api.update(
            facility.id_, {"Suppress No Candidates Email": value}
        )

    def track(self, facility: Any, event_type: str, **kwargs) -> None:
        return

    @cached_property
    def __connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_filepath)

    def __create_table_sql(self, table_name: str) -> str:
        return """
            CREATE TABLE IF NOT EXISTS {table_name} (
                id     VARCHAR(63) PRIMARY KEY,
                fields JSON        NOT NULL
            );
        """.format(
            table_name=table_name
        )

    def __init_db(self) -> None:
        for table in ("candidates", "facilities", "needs"):
            with self.__connection:
                self.__connection.execute(self.__create_table_sql(table))

    def __insert_record_sql(self, table_name: str) -> str:
        return """
            INSERT OR REPLACE INTO {table_name} VALUES (?, ?);
        """.format(
            table_name=table_name
        )

    def __fill_table(self, table_name: str, batch_size: int = 1000) -> None:
        """Given the name of a table and an optional batch size, fill our
        local sqlite with the data in that airtable table
        """
        buffer = []
        for count, model in enumerate(
            self.fetchall(getattr(self, f"{table_name}_api"))
        ):
            buffer.append(model.to_row())

            if not count % batch_size:
                with self.__connection:
                    self.__connection.executemany(
                        self.__insert_record_sql(table_name), buffer
                    )
                buffer = []

        if len(buffer):
            with self.__connection:
                self.__connection.executemany(
                    self.__insert_record_sql(table_name), buffer
                )

    def fill(self) -> None:
        """Fill a sqlite database with all of the data we need to generate matches
        in airtable
        """
        self.__init_db()

        for table_name in ("candidates", "facilities", "needs"):
            self.__fill_table(table_name)
        self.__filled = True

    def __run_select_query(self, sql: str, args: List[Any]) -> ModelIterator:
        if not self.__filled:
            self.fill()

        with self.__connection:
            cursor = self.__connection.cursor()
            cursor.execute(sql, args)
            for row in cursor.fetchall():
                yield Model.from_row(row)

    def facilities_in_need(self) -> ModelIterator:
        sql = """
            WITH needs_extrapolated AS (

               SELECT n.*
                    , json_each.value as facility_id

                 FROM needs n, json_each(n.fields, "$.facility")

            ), facility_needs AS (

               SELECT f.id as id
                    , datetime(json_extract(n.fields, "$.time_requested")) as time_requested
                    , json_extract(n.fields, "$.needs_met") as needs_met

                 FROM facilities f

                 JOIN needs_extrapolated n
                   ON f.id = n.facility_id

             ORDER BY time_requested DESC
                LIMIT 1

            )
            SELECT *
              FROM facilities f
              JOIN facility_needs n USING ( id )
             WHERE needs_met is null
                OR needs_met  = "No"
            """
        return self.__run_select_query(sql, [])

    def candidates_for_facility(self, facility_id: str) -> ModelIterator:
        """Given the name of a facility, find all the candidates that match
        its most recent staffing request. This is quite sensitve to the structure
        of the data we collect. Returns a generator over the models that come
        back"""

        # This is probably not an ideal way to do this, but during development
        # I felt that the airtable api wasn't going to give me quite what I
        # needed or wanted. Perhaps that was unwise, and maybe we reassess that at
        # a later date. This needs to run in 15 minutes, and I'm completely
        # guessing that pulling all of the tables out of Airtable into sqlite
        # and then querying that would be a bit quicker than going back and forth
        # over the network 100s of times a run (when we take this state-wide).
        # Also definitely found the airtable apis for doing non-trivial queries
        # frustrating to work with.
        #
        # Look to my works and despair
        sql = """
            WITH needs_extrapolated AS (

               SELECT n.*
                    , json_each.value as facility_id

                 FROM needs n, json_each(n.fields, "$.facility")

            ), facility_needs AS (

               SELECT datetime(json_extract(n.fields, "$.time_requested")) as time_requested
                    , json_extract(n.fields, "$.practice_area_1") as practice_area_1
                    , json_extract(n.fields, "$.practice_area_2") as practice_area_2
                    , json_extract(n.fields, "$.practice_area_3") as practice_area_3
                    , r.value as region

                 FROM facilities f, json_each(f.fields, "$.region") r

                 JOIN needs_extrapolated n
                   ON f.id = n.facility_id

                WHERE f.id = ?
                  AND practice_area_1 is not null

             ORDER BY time_requested DESC
                LIMIT 1

            ), distinct_candidate_ids AS  (

               SELECT DISTINCT
                      c.id

                 FROM candidates c
                    , json_each(c.fields, "$.high_priority_health_care_practice") p
                    , json_each(c.fields, "$.regional_availability") r

                 JOIN facility_needs f
                   ON r.value = f.region
                  AND (    p.value = f.practice_area_1
                        OR p.value = f.practice_area_2
                        OR p.value = f.practice_area_3 )

                WHERE json_extract(c.fields, "$.hired")       is null
                  AND json_extract(c.fields, "$.unavailable") is null

            )
            SELECT *

              FROM candidates c

              JOIN distinct_candidate_ids USING (id)
            ;
        """
        return self.__run_select_query(sql, [facility_id])
