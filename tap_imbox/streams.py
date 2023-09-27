"""Stream type classes for tap-imbox."""
import requests
import re

from pathlib import Path
from typing import Optional, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.helpers.jsonpath import extract_jsonpath

from tap_imbox.client import ImboxStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ListTicketsStream(ImboxStream):
    """Define custom stream."""

    schema_filepath = SCHEMAS_DIR / "list_tickets.json"
    records_jsonpath = "$.json[*]"

    name = "list_tickets"
    primary_keys = ["ticketID"]
    path = "listTickets"

    replication_key = "latestUpdated"
    is_sorted = False

    def get_url_params(self, context, next_page_token):
        params = {}

        starting_date = self.get_starting_timestamp(context)
        if starting_date:
            params["latestUpdatedAfter"] = starting_date.isoformat()
        else:
            params["latestUpdatedAfter"] = self.config.get("start_date")

        self.logger.info("QUERY PARAMS: %s", params)
        return params

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {"ticketID": record["ticketID"]}


class GrabTicketStream(ImboxStream):
    schema_filepath = SCHEMAS_DIR / "grab_ticket.json"
    records_jsonpath = "$.json[*]"

    name = "grab_ticket"
    primary_keys = ["ticketID"]

    replication_key = "date"
    is_sorted = False

    parent_stream_type = ListTicketsStream
    ignore_parent_replication_keys = False
    path = "grabTicket"

    def get_url(self, context: Optional[dict]) -> str:
        """Add the ticket ID to the endpoint URL."""
        return f"{self.url_base}/{context['ticketID']}"

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """
        Only extract order ID from the message body and disregard the rest,
        since it contains PI. The order ID is only present in the first message
        of the ticket, and if the client has used the web form.
        """

        message = row.pop("messagePlain")
        s = re.search(
            r"Hur kan vi hjälpa dig\?: [^\n$]+\nOrdernummer: ([^\n$]+)", message
        )

        row["orderNumber"] = s.group(1) if s else None

        return row
