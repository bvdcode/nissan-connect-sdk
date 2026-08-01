# Authentication and tokens

`NissanClient` accepts MyNISSAN credentials only when `async_authenticate()` is called. The
returned `Tokens` object contains the access, refresh, and optional ID tokens used by later
requests.

```python
tokens = await client.async_authenticate(email, password)
```

Applications should store replacement tokens whenever the listener is called. The listener
may be synchronous or asynchronous.

```python
from pynissan import Country, NissanClient, Tokens


async def save_tokens(tokens: Tokens) -> None:
    await token_store.save(tokens)


client = NissanClient(
    session,
    country=Country.US,
    tokens=await token_store.load(),
    token_listener=save_tokens,
    oauth_device_id=stored_device_id,
)
```

The client refreshes expired access tokens before authenticated requests. Concurrent requests
share one refresh operation, and `token_listener` receives the replacement token set.

Persist `client.oauth_device_id` with the account record so a later client instance can reuse
the same OAuth device identity. Treat credentials, tokens, and the device identifier as
sensitive application data. Do not log or commit them.
