# Cache
Some files will be stored in this directory for server use:
## `recentEventKey`
The most recent event key used to update data.
## `alliance`
Alliance data from The Blue Alliance
- `rawData`: Raw data from The Blue Alliance, as recieved from `/event/{event_key}/alliances`. Check out the [API docs](https://www.thebluealliance.com/apidocs/v3) for more info.
- `eventKey`: The event key alliance data was pulled for.
- `Alliance X`: The name `Alliance X` is pulled directly from The Blue Alliance, and is usually in this format, where X is a number between 1 and 8 inclusive. Each is an array with all teams on said alliance, usually with 3 or 4 items.