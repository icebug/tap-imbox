"""Stream type classes for tap-imbox."""

from __future__ import annotations

from datetime import datetime
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
        return {"latestUpdatedAfter": self.get_starting_timestamp(context).isoformat()}

    def get_child_context(self, record: dict, context: dict | None) -> dict | None:
        """Return a context dictionary for child streams."""
        if not context:
            context = {}
        context["ticketID"] = record["ticketID"]
        context["latestUpdated"] = record["latestUpdated"]
        return context

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

    def get_url(self, context: Optional[dict]) -> str:
        """Add the ticket ID to the endpoint URL."""
        return f"{self.url_base}/{context['ticketID']}"

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        """
        Only extract order ID from the message body and disregard the rest,
        since it contains PI. The order ID is only present in the first message
        of the ticket, and if the client has used the web form.
        """

        # Do not return all rows in json - only those that are newer than the
        # state.
        if row["date"] <= context["latestUpdated"]:
            return

        row["extracted_at"] = datetime.utcnow().isoformat()
        message = row.pop("messagePlain")
        s = re.search(
            r"Hur kan vi hjälpa dig\?: [^\n$]+\nOrdernummer: ([^\n$]+)", message
        )

        row["orderNumber"] = s.group(1) if s else None

        return row
