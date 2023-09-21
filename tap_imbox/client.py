"""REST client handling, including ImboxStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ImboxStream(RESTStream):
    """Imbox stream class."""

    records_jsonpath = "$[*]"

    # The endpoint path comes before the API key and user ID
    @property
    def url_base(self) -> str:
        url_base = "https://apiv2.imbox.io/message"
        return (
            f"{url_base}/{self.path}/{self.config['api_key']}/{self.config['user_id']}"
        )

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """As needed, append or transform raw data to match expected structure."""
        # TODO: Delete this method if not needed.
        return row
