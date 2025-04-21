# c_mcp_client.py

import asyncio
from fastapi import FastAPI, Request
import uvicorn  # server to run the fastapi app
from mcp import ClientSession     #interact with MCP server
from mcp.client.sse import sse_client #connect SSE stream

app = FastAPI()
JOB_STATUS = {}  # job_id -> status

@app.post("/job_status_update") # Server will send a Post request when a job's status changes.
async def job_status_update(request: Request):
    data = await request.json()
    job_id = data.get("job_id")
    status = data.get("status")
    JOB_STATUS[job_id] = status
    print(f"Job {job_id} status updated to: {status}")
    return {"received": True}

async def submit_job_to_server():  
    async with sse_client(url="http://localhost:8000/sse") as streams:  #connects to MCP server via SSE, 
        async with ClientSession(*streams) as session:
            await session.initialize()

            job_name = "ExampleJob"
            callback_url = "http://localhost:9000/job_status_update"
            response = await session.call_tool("submit_job", {      #submit the job , registers a callback URl 
                "job_name": job_name,
                "callback_url": callback_url
            })

            job_id = str(response.content[0].text)     # receives the JOB ID 
            print(f"Submitted job '{job_name}' with ID: {job_id}")
            print("Waiting for callback...")

@app.on_event("startup") 
async def on_startup():
    # Start the submission task in the background
    asyncio.create_task(submit_job_to_server())   

if __name__ == "__main__":
    uvicorn.run("c_mcp_client:app", host="0.0.0.0", port=9000, reload=False)
