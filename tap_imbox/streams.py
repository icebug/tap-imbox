"""Stream type classes for tap-imbox."""

from __future__ import annotations

from datetime import datetime, timedelta
import re

import typing as t
from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_imbox.client import ImboxStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ListTicketsStream(ImboxStream):
    name = "list_tickets"
    path = "listTickets"
    primary_keys: t.ClassVar[list[str]] = ["ticketID"]

    replication_key = "latestUpdated"
    is_sorted = False

    schema_filepath = SCHEMAS_DIR / "list_tickets.json"
    records_jsonpath = "$.json[*]"

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        # The API parameter is inclusive, so add the smallest recognized unit
        # of time to only fetch new data.
        return {
            "latestUpdatedAfter": (
                self.get_starting_timestamp(context) + timedelta(milliseconds=1)
            ).isoformat()
        }

    def get_child_context(
        self,
        record: dict,
        context: dict | None,
    ) -> dict | None:
        """Return a context dictionary for child streams."""
        return {"ticketID": record["ticketID"]}

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        row["extracted_at"] = datetime.utcnow().isoformat()
        return row


class GrabTicketStream(ImboxStream):
    name = "grab_ticket"
    path = "grabTicket"
    primary_keys: t.ClassVar[list[str]] = ["ticketID"]

    schema_filepath = SCHEMAS_DIR / "grab_ticket.json"
    records_jsonpath = "$.json[*]"

    parent_stream_type = ListTicketsStream
    ignore_parent_replication_key = False
    replication_key = "date"
    is_sorted = False

    # Use a single state for all ticket IDs
    state_partitioning_keys = []

    def get_url(self, context: Optional[dict]) -> str:
        """Add the ticket ID to the endpoint URL."""
        return f"{self.url_base}/{context['ticketID']}"

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        """
        Only extract order ID and other useful information from the message
        body and disregard the rest, since it contains PI. The order ID is only present in the first message of the ticket, and if the client has used
        the web form.

        Logs do not contain PI, so keep their messages.
        """

        # Do not return all rows in json - only those that are newer than the
        # state.
        state = self.get_starting_timestamp(context)
        if state:
            if row["date"] <= state.isoformat():
                return

        row["extracted_at"] = datetime.utcnow().isoformat()

        message = row.pop("messagePlain")
        if row["messageType"] == "log":
            row["message"] = message
            return row

        # Try different versions of the message format to be back-compatible.
        # This search only works for Swedish web form claims.
        # Other languages and other message topics will not be parsed.
        s = None

        # Claims message format since ca 2024-01-02.
        s3 = re.search(
            r"Hur kan vi hjälpa dig\?: ([^\n$]+)\nProdukt: ([^\n$]+)\nVersion: ([^\n$]+)\nOrsak: ([^\n$]+)\nFactory no\. \(finns på insidan av plösen\): ([^\n$]+)\nOrdernummer: ([^\n$]+)",
            message,
        )

        # Claims message format since ca 2023-10-11.
        s2 = re.search(
            r"Hur kan vi hjälpa dig\?: ([^\n$]+)\nProdukt: ([^\n$]+)\nOrsak: ([^\n$]+)\nFactory no\. \(finns på insidan av plösen\): ([^\n$]+)\nOrdernummer: ([^\n$]+)",
            message,
        )

        # Claims message format since ca 2023-10-03.
        s1 = re.search(
            r"Hur kan vi hjälpa dig\?: ([^\n$]+)\nProdukt: ([^\n$]+)\nOrsak: ([^\n$]+)\nFabrikationskod: ([^\n$]+)\nOrdernummer: ([^\n$]+)",
            message,
        )

        if s3:
            s = s3
            row["messageTopic"] = s.group(1)
            row["product"] = s.group(2)
            row["version"] = s.group(3)
            row["reason"] = s.group(4)
            row["manufacturingCode"] = s.group(5)
            row["orderNumber"] = s.group(6)
        elif s2 or s1:
            s = s2 or s1
            row["messageTopic"] = s.group(1)
            row["product"] = s.group(2)
            row["reason"] = s.group(3)
            row["manufacturingCode"] = s.group(4)
            row["orderNumber"] = s.group(5)

        # Rougher search for older messages and non-claims.
        # Ignore everything except the order number.
        else:
            s = re.search(
                r"Hur kan vi hjälpa dig\?: [^\n$]+\nOrdernummer: ([^\n$]+)",
                message,
            )
            row["orderNumber"] = s.group(1) if s else None

        return row
