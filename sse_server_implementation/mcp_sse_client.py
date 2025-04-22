import asyncio
import uuid
import httpx

async def listen_sse(client_id):   #async function to listen for SSE notifications for a given client ID.
    url = f"http://localhost:8000/notifications/{client_id}"
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", url) as response:   #Asynchronously iterate over each line received from the server.
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = line.removeprefix("data:").strip()
                    print(f"[Client] Notification received: {data}")        
                    break                                              #REMOVE BREAK TO KEEP LISTENING

async def main():

    client_id = str(uuid.uuid4())  #Generates an unique ID

    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/mcp/tool/submit_job", json={     #POST A JOB WITH client_id and JOB_NAME
            "job_name": "ExampleJob",
            "client_id": client_id
        })
        response.raise_for_status()
        job_id = response.json().get("job_id")
        print(f"[Client] Submitted job with ID: {job_id}")

    print(f"[Client] Listening for job completion via SSE (client_id={client_id})...")
    await listen_sse(client_id)

if __name__ == "__main__":
    asyncio.run(main())
