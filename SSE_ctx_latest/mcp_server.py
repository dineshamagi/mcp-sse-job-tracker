from mcp.server.fastmcp import FastMCP, Context
import logging
import uuid
import asyncio



# Setup logging
logging.basicConfig(
    level=logging.DEBUG,  # Set log level to DEBUG to see more messages
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("mcp_server")


#create an MCP server 
mcp = FastMCP("Background task server")


@mcp.tool()
async def submit_job(ctx: Context, job_name: str) -> str:
    job_id = str(uuid.uuid4())
    await ctx.info(f"Received Job {job_name} with ID {job_id}")
    asyncio.create_task(process_job(ctx, job_id, job_name))
    return job_id

async def process_job(ctx: Context, job_id: str, job_name: str):
    await ctx.info(f"Processing job {job_name} with ID {job_id}")
    await asyncio.sleep(5)  # Simulate long processing
    await ctx.info(f"Job {job_name} with ID {job_id} has been completed")

if __name__ == "__main__":
    mcp.run(transport="sse")

