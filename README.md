# tap-imbox

`tap-imbox` is a Singer tap for Imbox, that retriews data from the following
endpoints:
- `https://apiv2.imbox.io/message/listTickets`
- `https://apiv2.imbox.io/message/grabTicket`

Refer to
[the Imbox API documentation](https://imbox.se/docs/online/integration)
for more information.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

```bash
pipx install tap-imbox
```

## Configuration

### Accepted Config Options

The tap has the following obligatory configurations:
- `api_key` - the API key.
- `user_id` - the organization's user ID.
- `start_date` - the first date to extract data from if the state is empty.
This parameter is used for the `latestUpdatedAfter` parameter in `/listTickets`. 

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-imbox --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

## Usage

You can easily run `tap-imbox` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-imbox --version
tap-imbox --help
tap-imbox --config CONFIG --discover > ./catalog.json
```

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Run in Development Environment

You can test the `tap-imbox` CLI interface directly using `poetry run`:

```bash
poetry run tap-imbox --help
```

Now you can test and orchestrate using Meltano:

```bash
meltano invoke tap-imbox --version
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
