import uuid 
import asyncio
import logging
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("mcp_server")

mcp = FastMCP("demo_sse_server")

job_status = {}  # job_id: status


async def process_job(job_id: str, job_name: str):
    logger.info(f"[PROCESSING] Job '{job_name}' with ID {job_id} started.")
    await asyncio.sleep(5)  # simulate time-consuming task

    job_status[job_id] = "completed"           #Update the Job Status
    logger.info(f"[COMPLETED] Job '{job_name}' with ID {job_id} completed.")


@mcp.resource("status:/{job_id}")
async def get_job_status(job_id: str) -> str:
    """Get the status of a job."""
    status = job_status.get(job_id, "not_found")
    logger.info(f"[STATUS CHECK] Job ID {job_id} -> Status: {status}")
    return status


#Sample resource to verify
@mcp.resource("greeting://{name}")      
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    logger.info(f"[GREETING] Generating greeting for {name}")
    return f"Hello, {name}!"


@mcp.tool()
async def submit_job(job_name: str) -> str:
    """Accepts a job request and returns a unique job ID."""
    job_id = str(uuid.uuid4())

    logger.info(f"[RECEIVED] Job '{job_name}' submitted with ID {job_id}")
    job_status[job_id] = "pending"

    asyncio.create_task(process_job(job_id, job_name))

    return job_id


if __name__ == "__main__":
    mcp.run(transport="sse")
