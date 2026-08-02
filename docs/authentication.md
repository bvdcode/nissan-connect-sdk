# Authentication and tokens

`NissanClient` accepts MyNISSAN credentials only when `async_authenticate()` is called. The
returned `Tokens` object contains the access, refresh, and optional ID tokens used by later
requests.

Select the account market with `Country.US`, `Country.CA`, or `Country.MX`. The country must
match the market where the Nissan account is registered.

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

## Request verification

Some account onboarding and connected-service operations require request proof. Supply either
a static pair or an async provider when constructing the client.

```python
from pynissan import NissanClient, RequestProof

client = NissanClient(
    session,
    tokens=tokens,
    request_proof=RequestProof(api_attestation, device_status),
)
```

For long-running applications, a provider can load or refresh the pair on demand:

```python
async def request_proof_provider(force_refresh: bool) -> RequestProof:
    return await proof_store.load(force_refresh=force_refresh)


client = NissanClient(
    session,
    tokens=tokens,
    request_proof_provider=request_proof_provider,
)
```

The provider receives `False` for a normal request and `True` after the service rejects the
current proof. A static value and a provider cannot be supplied together.
