"""Imbox tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_imbox.streams import (
    ListTicketsStream,
    GrabTicketStream,
)

STREAM_TYPES = [
    ListTicketsStream,
    GrabTicketStream,
]


class TapImbox(Tap):
    """Imbox tap class."""

    name = "tap-imbox"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The organization's API key",
        ),
        th.Property(
            "user_id",
            th.IntegerType,
            required=True,
            description="The organization's user ID",
        ),
        th.Property(
            "start_date",
            th.DateType,
            required=True,
            description="First date to extract data from",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
