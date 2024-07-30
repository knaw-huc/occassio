"""
Start the import workflow.
"""
import asyncio
from pathlib import Path

from temporalio.client import Client

import import_workflow


async def main():
    """
    Create a workflow in Temporal.
    :return:
    """
    client = await Client.connect("localhost:7233")

    zipfiles = Path("data").rglob("*.zip")

    threads = []

    for file in zipfiles:
        args = import_workflow.ImportConfiguration(
            zip_path=file.as_posix(),
            data_path="data",
            bulk_size=10,
        )

        file_base = file.stem

        threads.append(client.execute_workflow(
            import_workflow.ImportArchive.run,
            args,
            id=f"import-{file_base}",
            task_queue='occassio-import',
        ))

    asyncio.gather(*threads)


if __name__ == "__main__":
    asyncio.run(main())
