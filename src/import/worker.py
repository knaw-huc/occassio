import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from import_workflow import ImportArchive, ImportArticles
from activities import unzip_file, parse_file, save_bulk


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue='occassio-import',
        workflows=[ImportArchive, ImportArticles],
        activities=[unzip_file, parse_file, save_bulk],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
