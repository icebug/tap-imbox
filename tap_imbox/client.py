"""REST client handling, including ImboxStream base class."""

from __future__ import annotations

from pathlib import Path

from singer_sdk.streams import RESTStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ImboxStream(RESTStream):
    """Imbox stream class."""

    @property
    def url_base(self) -> str:
        """
        Add the endpoint path to the base URL before the API key and user ID.
        """
        url_base = "https://apiv2.imbox.io/message"
        return (
            f"{url_base}/{self.path}/{self.config['api_key']}/{self.config['user_id']}"
        )

    records_jsonpath = "$[*]"
