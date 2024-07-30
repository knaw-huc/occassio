"""
This file defines a workflow for using Temporal for importing archives.
"""
import asyncio
import dataclasses
from datetime import timedelta

from temporalio import workflow
from temporalio.workflow import ParentClosePolicy

with (workflow.unsafe.imports_passed_through()):
    from activities import ParseFileArguments, SaveBulkArguments, UnzipFileConfiguration,parse_file, save_bulk, unzip_file
    from pathlib import Path
    import os


@dataclasses.dataclass
class ImportConfiguration:
    """
    Data class for storing configuration parameters for import.
    """
    zip_path: str
    data_path: str
    bulk_size: int


@dataclasses.dataclass
class ImportArticlesConfiguration:
    """
    Data clas for storing configuration parameters for import.
    """
    filenames: list[str]
    index: int


@workflow.defn
class ImportArchive:
    """
    Import workflow
    """

    @staticmethod
    def split_bulk(total: list, size: int) -> list:
        """
        Split bulk articles into chunks.
        :param total: complete set of items
        :param size: size of chunks
        :return: A list of lists, chunks of size :size: from :total:
        """
        for i in range(0, len(total), size):
            yield total[i:i + size]

    @staticmethod
    def files_in_dir(dirname: str) -> list[str]:
        """
        Import files from a directory.
        :param dirname:
        :return:
        """
        files = list(Path(dirname).rglob("*"))
        articles = []
        for file in files:
            if not os.path.isfile(file):
                continue
            articles.append(file.as_posix())
        return articles

    @workflow.run
    async def run(self, configuration: ImportConfiguration) -> None:
        """
        Execute the workflow
        :param configuration:
        :return:
        """
        # First we get the file contents from the zip
        files_location = await workflow.execute_activity(
            unzip_file,
            UnzipFileConfiguration(
                zip_path=configuration.zip_path,
                data_path=configuration.data_path,
            ),
            start_to_close_timeout=timedelta(minutes=5),
        )

        files = ImportArchive.files_in_dir(files_location)

        generator = self.split_bulk(list(files), configuration.bulk_size)

        threads = []
        i = 0
        for chunk in generator:
            threads.append(workflow.execute_child_workflow(
                ImportArticles.run,
                ImportArticlesConfiguration(filenames=chunk, index=i),
                id=f"import_{configuration.zip_path}_{i}",
                parent_close_policy=ParentClosePolicy.ABANDON
            ))
            i += 1

        results = await asyncio.gather(*threads)

@workflow.defn
class ImportArticles:
    """
    Child workflow for importing a bulk
    """
    @workflow.run
    async def run(self, configuration: ImportArticlesConfiguration):
        """

        :param configuration:
        :return:
        """
        args = ParseFileArguments(names=configuration.filenames)
        articles = await workflow.execute_activity(
            parse_file,
            args,
            start_to_close_timeout=timedelta(minutes=15),
            activity_id=f"parse_{configuration.index}",
        )

        await workflow.execute_activity(
            save_bulk,
            SaveBulkArguments(articles=articles),
            start_to_close_timeout=timedelta(minutes=15),
            activity_id=f"save_{configuration.index}",
        )
