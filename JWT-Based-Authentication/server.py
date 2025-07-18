import datetime
import os
from zoneinfo import ZoneInfo
from fastapi import  FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
from starlette.applications import Starlette
from starlette.routing import Route, Mount
import jwt
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from loguru import logger

from dotenv import load_dotenv

load_dotenv()


# Initialize the MCP server with your tools
mcp = FastMCP(
    name="Weather and Time SSE Server"
)


@mcp.tool()
def TimeTool(input_timezone):
    "Provides the current time for a given city's timezone like Asia/Kolkata, America/New_York etc. If no timezone is provided, it returns the local time."
    format = "%Y-%m-%d %H:%M:%S %Z%z"
    current_time = datetime.datetime.now()    
    if input_timezone:
        print("TimeZone", input_timezone)
        current_time =  current_time.astimezone(ZoneInfo(input_timezone))
    return f"The current time is {current_time}."

transport = SseServerTransport("/messages/")


@mcp.tool()
def weather_tool(location: str):
    """Provides weather information for a given location"""        
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data["cod"] == 200:
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"The weather in {location} is currently {description} with a temperature of {temp}°C."
    else:
        return f"Sorry, I couldn't find weather information for {location}."


SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"     
def check_auth(request: Request):
    auth = request.headers.get("authorization", "")        
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return True
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    raise HTTPException(status_code=401, detail="Unauthorized")

async def handle_sse(request):
    check_auth(request=request)
    # Prepare bidirectional streams over SSE
    async with transport.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as (in_stream, out_stream):
        # Run the MCP server: read JSON-RPC from in_stream, write replies to out_stream
        await mcp._mcp_server.run(
            in_stream,
            out_stream,
            mcp._mcp_server.create_initialization_options()
        )


#Build a small Starlette app for the two MCP endpoints
sse_app = Starlette(
    routes=[
        Route("/sse", handle_sse, methods=["GET"]),
        # Note the trailing slash to avoid 307 redirects
        Mount("/messages/", app=transport.handle_post_message)
    ]
)


app = FastAPI()

# Mock client store
CLIENTS = {
    "test_client": "secret_1234"
}


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


@app.post("/token")
def generate_token(request: TokenRequest):
    if request.client_id in CLIENTS and CLIENTS[request.client_id] == request.client_secret:
        payload = {
            "sub": request.client_id,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=60)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/health")
def read_root():
    return {"message": "MCP SSE Server is running"}

app.mount("/", sse_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
    