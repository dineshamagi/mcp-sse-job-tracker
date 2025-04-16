import asyncio 
from mcp import ClientSession
from mcp.client.sse import sse_client


async def run():
    async with sse_client(url="http://localhost:8000/sse") as streams:
        async with ClientSession(*streams) as session:

            await session.initialize()  
            
            '''Prints the available Tools & Resources'''
            # tools = await session.list_tools()
            # print(tools)
            
            # resources = await session.list_resources()
            # print(resources)
            

            job_name = "ExampleJob" 
            response = await session.call_tool("submit_job",{"job_name":job_name})
            print(response)   #Receives Job Id from sse_server

            job_id = str(response.content[0].text)
            print(f"Submitted Job '{job_name}' with ID: {job_id}")

            lat_uri = "status:/"+job_id     #transforming jobid to uri --> supported by resources

            while True:
                status = await session.read_resource(lat_uri)
                status = status.contents[0].text
                print(f"Job Status: {status}")
                if status == "completed":
                    break
                await asyncio.sleep(1) #wait before checking again.
            
if __name__ == "__main__":
    asyncio.run(run())