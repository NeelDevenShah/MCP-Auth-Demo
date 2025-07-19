# Mastering Authentication in MCP: An AI Engineer's Comprehensive Guide

This repository contains the complete codebase for the blog **"Mastering Authentication in MCP: An AI Engineer's Comprehensive Guide"**. It demonstrates three authentication methods for securing Message Control Protocol (MCP) client-server communication:

- **API Key-Based Authentication**
- **JWT-Based Authentication (Custom Implementation)**
- **JWT-Based Authentication with FastMCP's Built-In RBAC**

Each method is implemented in a dedicated directory with both client and server code, along with example tools and usage patterns.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Authentication Methods](#authentication-methods)
  - [1. API Key-Based Authentication](#1-api-key-based-authentication)
  - [2. JWT-Based Authentication (Custom)](#2-jwt-based-authentication-custom)
  - [3. JWT-Based Authentication with FastMCP RBAC](#3-jwt-based-authentication-with-fastmcp-rbac)
- [Comparison Table](#comparison-table)
- [Best Practices & Considerations](#best-practices--considerations)
- [Setup & Usage](#setup--usage)
- [License](#license)

---

## Overview

The Message Control Protocol (MCP) enables real-time, tool-based interactions between AI agents (clients) and servers, often using Server-Sent Events (SSE) for communication. Authentication ensures that only authorized clients can access sensitive tools and data.

This repo provides hands-on, production-ready examples for each authentication method, including:

- Secure server endpoints (FastAPI/Starlette)
- Example tools (e.g., `TimeTool`, `weather_tool`)
- Client code for authenticating and invoking tools
- Role-based access control (RBAC) with FastMCP

---

## Project Structure

```
.
├── API-Key-Based-Authentication/
│   ├── client.py
│   └── server.py
├── JWT-Based-Authentication/
│   ├── client.py
│   └── server.py
├── JWT-Based-RBAC-Authentication/
│   ├── client.py
│   ├── generate_keys.py
│   └── mcp_tools/
│       ├── crm.py
│       ├── hr_management.py
│       └── project_management.py
├── OAuth-Based-Authentication/
├── requirements.txt
├── .env
└── README.md
```

---

## Authentication Methods

### 1. API Key-Based Authentication

**Summary:**  
Uses a static API key in the request headers. Simple, but best for prototypes or internal tools.

- **Client:** Sends `x-api-key` header with SSE requests.
- **Server:** Validates the key in `check_auth`. Supports Basic and Bearer for compatibility.

**Example:**

```python
# Client
headers = {"x-api-key": "secretkey"}
async with sse_client(url="http://localhost:8100/sse", headers=headers) as (in_stream, out_stream):
    async with ClientSession(in_stream, out_stream) as session:
        info = await session.initialize()
        tools = await session.list_tools()

# Server
def check_auth(request: Request):
    api_key = request.headers.get("x-api-key")
    if api_key == "secretkey":
        return True
    raise HTTPException(status_code=401, detail="Unauthorized")
```

**Pros:**

- Simple, minimal setup
- No token management
- Works with any HTTP client

**Cons:**

- Static keys are insecure
- No RBAC or fine-grained access
- Not scalable for large systems

**Use Case:**  
Internal tools, rapid prototypes, simple weather/time services.

---

### 2. JWT-Based Authentication (Custom)

**Summary:**  
Clients obtain a time-limited JWT from a `/token` endpoint using client credentials. JWT is sent as a Bearer token.

- **Client:** Requests token, then uses it in Authorization header.
- **Server:** Issues and validates JWTs using HS256 and a shared secret.

**Example:**

```python
# Client: Fetch and use JWT
async def get_token():
    payload = {"client_id": "test_client", "client_secret": "secret_1234"}
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8100/token", json=payload) as resp:
            data = await resp.json()
            return data["access_token"]

headers = {"Authorization": f"Bearer {await get_token()}"}
async with sse_client(url="http://localhost:8100/sse", headers=headers) as (in_stream, out_stream):
    async with ClientSession(in_stream, out_stream) as session:
        info = await session.initialize()

# Server: Issue and validate JWT
@app.post("/token")
def generate_token(request: TokenRequest):
    if request.client_id in CLIENTS and CLIENTS[request.client_id] == request.client_secret:
        payload = {
            "sub": request.client_id,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=60)
        }
        token = jwt.encode(payload, "my_super_secret_key", algorithm="HS256")
        return {"access_token": token}
```

> **Note:** Embedding credentials in source code risks unauthorized access. Use environment variables or a secure vault for secrets.

**Pros:**

- Expiring tokens improve security
- Customizable payloads
- Scalable for larger systems

**Cons:**

- Requires token endpoint and client store
- Slightly more complex
- Limited RBAC

**Use Case:**  
Secure APIs with moderate complexity, e.g., authenticated weather/time services.

---

### 3. JWT-Based Authentication with FastMCP RBAC

**Summary:**  
Uses FastMCP's `BearerAuthProvider` with RSA-signed JWTs and role-based access control (RBAC). Ideal for enterprise systems.

- **Key Generation:** Use `generate_keys.py` to create RSA key pairs.
- **Client:** Signs JWT with private key, includes claims (subject, role, etc.), sends as Bearer token.
- **Server:** Validates JWT with public key, enforces RBAC for tool/server access.

**Example:**

```python
# Client: Generate and use RSA-signed JWT
with open("mcp_auth/private.pem", "r") as f:
    private_key_pem = f.read()
key_pair = RSAKeyPair(private_key=SecretStr(private_key_pem), public_key=public_key_pem)
token = key_pair.create_token(
    subject="alice",
    issuer="https://dev-issuer.com",
    audience="my-mcp-server",
    additional_claims={"job_role": "Manager", "id": "123", "name": "Alice"}
)
headers = {"Authorization": f"Bearer {token}"}

# Server: Configure FastMCP with RBAC
with open("mcp_auth/public.pem", "r") as f:
    public_key = f.read()
auth = BearerAuthProvider(public_key=public_key, issuer="https://dev-issuer.com", audience="my-mcp-server")
mcp = FastMCP(name="ProjectManagementMCP", auth=auth)
```

**Pros:**

- Strong security (RSA signatures)
- Fine-grained RBAC
- Scalable, multi-server support
- Enterprise-ready

**Cons:**

- Key management overhead
- More complex setup
- Slightly slower than HS256/API key

**Use Case:**  
Enterprise systems (project management, HR, CRM) with multiple roles and strict access control.

---

## Comparison Table

| Aspect         | API Key-Based | JWT Custom  | FastMCP RBAC |
| -------------- | ------------- | ----------- | ------------ |
| Security       | Low           | Medium      | High         |
| Complexity     | Low           | Medium      | High         |
| Scalability    | Limited       | Good        | Excellent    |
| Access Control | None          | Basic       | Advanced     |
| Use Case       | Prototypes    | Secure APIs | Enterprise   |

---

## Best Practices & Considerations

- **Secure Storage:** Store API keys, JWT secrets, and RSA keys in environment variables or a secure vault.
- **Token Expiration:** Use short-lived tokens (e.g., 60 minutes) and refresh as needed.
- **HTTPS:** Always use HTTPS for MCP communication.
- **Logging:** Avoid logging sensitive data.
- **Centralized Auth:** Use a dedicated token service for JWT-based methods.
- **Rate Limiting:** Protect authentication endpoints from abuse.

---

## Setup & Usage

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**

   - Add your API keys and secrets to `.env`.

3. **Run the servers:**

   - For each authentication method, start the server in its directory:
     ```bash
     cd API-Key-Based-Authentication
     python server.py
     # or
     cd JWT-Based-Authentication
     python server.py
     # or
     cd JWT-Based-RBAC-Authentication
     python server.py
     ```

4. **Run the clients:**

   - Use the corresponding `client.py` in each directory to test authentication and tool invocation.

5. **Generate RSA keys (for RBAC):**
   ```bash
   cd JWT-Based-RBAC-Authentication
   python generate_keys.py
   ```

---

## License

This repository is provided as a reference implementation for the blog. See [LICENSE](LICENSE) for details.

---

For more details, code explanations, and best practices, see the accompanying blog post:  
**"Mastering Authentication in MCP: An AI Engineer's Comprehensive Guide"**.
