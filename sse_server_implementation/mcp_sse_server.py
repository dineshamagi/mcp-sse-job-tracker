'''
+-------------------------+              +----------------------------+
|     Client (client.py)  |              |   MCP Server (FastAPI)       |
|Generates unique client id              |receives job, generate job_id |
| 1. POST /mcp/tool/submit_job           |   return job_id              |
|------------------------>|              |                              |
|                         |              |                              |
| 2. Open SSE stream to:  |              |                              |
|    /notifications/{id}  |------------->| Setup async Queue            |
|                         |              |                              |
|                         |              | 3. process_job sleeps        |
|                         |              | 4. queue.put(message)        |
|                         |<-------------| 5. Server pushes SSE msg     |
| 6. Prints job complete  |              |                              |
+-------------------------+              +----------------------------+\
'''


import asyncio
import uuid
from typing import Dict
from fastapi import FastAPI, Request   
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse   #send SSE responses

app = FastAPI()     

client_queues: Dict[str, asyncio.Queue] = {}     #Dict mapping client_id strings to asyncio.Queue objects.

class JobSubmission(BaseModel):
    job_name: str
    client_id: str

@app.post("/mcp/tool/submit_job")          #Post endpoint to receive JobName & client id.
async def submit_job(job: JobSubmission):
    job_id = str(uuid.uuid4())
    print(f"Received job '{job.job_name}' with ID {job_id} from client {job.client_id}")
    asyncio.create_task(process_job(job.client_id, job_id, job.job_name))
    return {"job_id": job_id}   

async def process_job(client_id: str, job_id: str, job_name: str):    #receives client id , job id , job name
    await asyncio.sleep(5)  # Simulate work

    msg = f"Job '{job_name}' with ID {job_id} completed"

    queue = client_queues.get(client_id)  #retrieves client message queue from dict (could be none if client never connected or disconnected)
    if queue:
        await queue.put(msg)       #msg later sent to the client via SSE

@app.get("/notifications/{client_id}")    #client connects here to receive real time notification.
async def notifications(request: Request, client_id: str):
    queue = asyncio.Queue() 
    client_queues[client_id] = queue

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                msg = await queue.get()     #wait async for new message from client queue
                yield {"event": "job_complete", "data": msg}     #keep sending events as they come
        finally:
            client_queues.pop(client_id, None)

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pn_mcp_server:app", host="0.0.0.0", port=8000)
