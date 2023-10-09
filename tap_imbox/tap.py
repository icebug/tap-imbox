"""Imbox tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_imbox import streams


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

    def discover_streams(self) -> list[streams.ImboxStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.ListTicketsStream(self),
            streams.GrabTicketStream(self),
        ]


if __name__ == "__main__":
    TapImbox.cli()
