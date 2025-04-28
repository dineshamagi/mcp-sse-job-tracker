#It receives the events notification as SSE events but the connection is getting closed by the server. 
'''
Events are correctly received: 

The client successfully receives notifications about:

Job received

Job processing started

These are sent as JSONRPCNotification messages over SSE.

PROBLEM : MCP SERVER closes the SSE connection prematurely, right after sending initial events. AS a result client cannot receive further events.
Possible Fix : The BACKGROUND task has to be awaited in the SERVER

'''

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import logging

# Configure logging at the root level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)  # Get the logger for this module


async def run():
    async with sse_client(url="http://localhost:8000/sse") as streams:
        async with ClientSession(*streams) as session:

            await session.initialize()

            #List available tools 
            tools = await session.list_tools()
            print("===================================================")
            print(tools)
            print("==================================================")
            #Call the 'submit_job' tool
            job_name = "Example_job"
            response = await session.call_tool("submit_job",{"job_name":job_name})
            job_id = response.content
            print(f"Submitted job '{job_name}' with ID: {job_id}")

            #POll the server for job status every 1 second 
            
            while True:
                status_response = await session.call_tool("get_job_status",{"job_id":job_id})
                status = status_response.content
                print(f"Job status: {status}")

                if status != "Job pending":
                    print("===================Job Completed============================")
                    break

                await asyncio.sleep(1) #wait before polling again



            

if __name__ == "__main__":
    asyncio.run(run())