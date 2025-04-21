# c_mcp_server.py

import uuid
import asyncio
import logging
import httpx
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mcp_server")

mcp = FastMCP("demo_server")

@mcp.tool()
async def submit_job(job_name: str, callback_url: str) -> str:
    job_id = str(uuid.uuid4())
    logger.info(f"[RECEIVED] Job '{job_name}' submitted with ID {job_id}")
    asyncio.create_task(process_job(job_id, job_name, callback_url))
    return job_id

#Background job processor
async def process_job(job_id: str, job_name: str, callback_url: str):
    logger.info(f"[PROCESSING] Job '{job_name}' with ID {job_id} started.")
    await asyncio.sleep(5)  # Simulate long-running task
    logger.info(f"[COMPLETED] Job '{job_name}' with ID {job_id} completed.")
    
    # Send callback to client
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(callback_url, json={"job_id": job_id, "status": "completed"})
            logger.info(f"[CALLBACK] Sent completion status to {callback_url} -> {response.status_code}")
        except Exception as e:
            logger.error(f"[CALLBACK ERROR] Failed to call {callback_url}: {e}")

if __name__ == "__main__":
    mcp.run(transport="sse")
