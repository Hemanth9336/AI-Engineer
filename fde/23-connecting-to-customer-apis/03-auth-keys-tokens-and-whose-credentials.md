---
type: lesson
title: "Auth: keys, tokens, and whose credentials"
minutes: 5
---

Real customer APIs require authentication. The technical part is easy - usually one header. The important part is deciding **whose** credentials the assistant uses and **how** they're stored.

## Common schemes

| Scheme | Looks like | Notes |
|---|---|---|
| API key | `X-API-Key: abc123` or `?api_key=` | Simple, long-lived; often all-powerful |
| Bearer token | `Authorization: Bearer eyJ...` | Often OAuth access tokens, short-lived and scoped |
| OAuth 2.0 client credentials | Exchange a client id/secret for a token | Service-to-service; tokens expire, refresh automatically |
| OAuth on behalf of a user | The user signs in, the app gets a token for *them* | The API applies that user's permissions |
| mTLS, signed requests | Certificates, HMAC signatures | Banks and regulated industries |

## Whose credentials?

- **A service account** for the assistant: one identity, with exactly the permissions the assistant needs - for example, read-only on orders. The usual choice for support bots.
- **The end user's own token** (on-behalf-of): the API enforces what *this user* may see. Best for internal assistants over sensitive data, and it solves the permissions problem from topic 19 at the source.
- **An admin or personal key**: never. If the assistant is tricked into calling an endpoint it shouldn't, an admin key makes it possible.

## Storing secrets

- **Environment variables or a secrets manager** (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault). Never in code, prompts, git or logs.
- **Never send credentials to the model.** The model sees the tool name and arguments; your code adds the header. A token in the prompt can be repeated in an answer or leaked through injection.
- **Fail loudly when a secret is missing** - a clear startup error beats mysterious 401s later.
- **Plan for rotation**: tokens expire and keys get rotated. Your code reads the current value; nothing is baked in.

```python
token = os.environ.get("MERIDIAN_API_TOKEN")
if not token:
    raise RuntimeError("MERIDIAN_API_TOKEN is not set")
headers = {"Authorization": f"Bearer {token}"}
```
