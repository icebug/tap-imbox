"""Stream type classes for tap-imbox."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_imbox.client import ImboxStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ListTicketsStream(ImboxStream):
    """Define custom stream."""

    schema_filepath = SCHEMAS_DIR / "list_tickets.json"
    records_jsonpath = "$.json[*]"

    name = "list_tickets"
    primary_keys = ["ticketID"]
    path = "listTickets"

    replication_key = "updatedDate"
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
