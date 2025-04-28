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
job_results = {}



@mcp.tool()               # Tool returns a job ID and immediately responds 
async def submit_job(ctx: Context, job_name: str) -> str:
    job_id = str(uuid.uuid4())
    ctx.info(f"Received Job {job_name} with ID {job_id}")
    #Schedule job processing in the background without blocking   
    asyncio.create_task(process_job(ctx, job_id, job_name))
    return job_id

async def process_job(ctx: Context, job_id: str, job_name: str):
    ctx.info(f"Processing job {job_name} with ID {job_id}")
    await asyncio.sleep(5)  # Simulate long processing
    job_results[job_id] = f"Job {job_name} with ID {job_id} completed!"
  
#Client polls with another tool to check the progress.
@mcp.tool()
def get_job_status(job_id: str) -> str:
    return job_results.get(job_id,"Job pending")

if __name__ == "__main__":
    mcp.run(transport="sse")

