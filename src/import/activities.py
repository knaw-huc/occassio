"""
Activities for the import Temporal workflow
"""
import dataclasses
import os
import zipfile

from pathlib import Path

from temporalio import activity

from article import Article
from test_import import import_bulk


@dataclasses.dataclass
class UnzipFileConfiguration:
    """
    Data class to hold the configuration for the unzip_file function.
    """
    zip_path: str
    data_path: str


@dataclasses.dataclass
class ParseFileArguments:
    """
    Data class containing configuration for the parse_file function.
    """
    names: list[str]


@dataclasses.dataclass
class SaveBulkArguments:
    """
    Data class containing configuration for the save_bulk function.
    """
    articles: list[dict]




@activity.defn
async def unzip_file(configuration: UnzipFileConfiguration) -> str:
    """
    Unzip a file and return the contents of its files.
    :param configuration:
    :return: The location of the unzipped files
    """
    with zipfile.ZipFile(configuration.zip_path, "r") as zip_ref:
        zip_name = Path(configuration.zip_path).stem
        unzip_dir = f"{configuration.data_path}/{zip_name}"
        Path(unzip_dir).mkdir(parents=True, exist_ok=True)
        zip_ref.extractall(unzip_dir)
    return unzip_dir


@activity.defn
async def parse_file(args: ParseFileArguments) -> list[dict]:
    """
    Parse file contents. We're not sure what is in the files so this is an action.
    :param args:
    :return:
    """
    # return Article.from_file(args.name)
    tmp = []
    for file in args.names:
        tmp.append(Article.from_file(file).to_dict())
    return tmp


@activity.defn
async def save_bulk(args: SaveBulkArguments):
    """
    Save a bulk of articles to elasticsearch
    :param args:
    :return:
    """
    import_bulk(args.articles)
