import re
import time
from pathlib import Path

import click
import h5py
import numpy as np

from pyrxiv.datamodel import ArxivPaper
from pyrxiv.download import ArxivDownloader
from pyrxiv.extract import TextExtractor
from pyrxiv.fetch import ArxivFetcher
from pyrxiv.logger import logger


def save_paper_to_hdf5(paper: "ArxivPaper", pdf_path: Path, hdf_path: Path) -> None:
    """
    Saves the arXiv paper metadata to an HDF5 file.

    Args:
        paper (ArxivPaper): The arXiv paper object containing metadata.
        pdf_path (Path): The path to the PDF file of the arXiv paper.
        hdf_path (Path): The path to the HDF5 file where the metadata will be saved.
    """
    with h5py.File(hdf_path, "a") as h5f:
        group = paper.to_hdf5(hdf_file=h5f)
        # Store PDF in the HDF5 file
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        # overwrite existing dataset
        if "pdf" in group:
            del group["pdf"]
        group.create_dataset("pdf", data=np.void(pdf_bytes))


def run_search_and_download(
    download_path: Path = Path("data"),
    category: str = "cond-mat.str-el",
    n_papers: int = 5,
    regex_pattern: str = "",
    start_id: str | None = None,
    start_from_filepath: bool = False,
    loader: str = "pdfminer",
    clean_text: bool = True,
    download_pdfs: bool = False,
) -> tuple[list[Path], list["ArxivPaper"]]:
    """
    Searches for a specific number of papers `n_papers` in arXiv for a specified `category` and downloads
    their metadata in an HDF5 file in `download_path`.

    If `regex_pattern` is specified, only the papers that contain the pattern will be downloaded.
    If `start_id` is specified, the search will start from that ID.
    If `start_from_filepath` is True, the search will start from the last downloaded paper's ID.
    If `loader` is specified, the text will be extracted using the corresponding loader.
    If `clean_text` is True, the extracted text will be cleaned by removing references and unnecessary whitespaces.
    If `download_pdfs` is True, the PDFs will be downloaded and saved in `download_path`.

    Args:
        download_path (Path, optional): The path for downloading the arXiv metadata. Defaults to Path("data").
        category (str, optional): The arXiv category on which the papers will be searched. Defaults to "cond-mat.str-el".
        n_papers (int, optional): The number of arXiv papers to be fetched and downloaded.
            If `regex_pattern` is not specified, this would correspond to the n_papers starting from the newest in the `category`. Defaults to 5.
        regex_pattern (str, optional): If specified, this regex pattern is searched in the arXiv papers so only the ones with
            the corresponding match will be downloaded. Defaults to "".
        start_id (str | None, optional): If specified, the search will start from this arXiv ID. Defaults to None.
        start_from_filepath (bool, optional): If True, the search will start from the last downloaded arXiv ID. Otherwise, it will start from the
            newest papers in the `category`. Defaults to False.
        loader (str, optional): PDF loader to use for extracting text from the downloaded PDFs.
            Defaults to "pdfminer". Available loaders: "pdfminer", "pypdf".
        clean_text (bool, optional): If True, the extracted text will be cleaned by removing references and unnecessary whitespaces.
            Defaults to True.
        download_pdfs (bool, optional): If True, the PDFs will be downloaded and saved in `download_path`. Defaults to False.

    Returns:
        tuple[list[Path], list[ArxivPaper]]: A tuple containing a list of Paths to the arXiv papers and a list of ArxivPaper objects
            with the extracted text.
    """
    if loader not in ["pdfminer", "pypdf"]:
        raise ValueError(
            f"Invalid loader: {loader}. Available loaders: 'pdfminer', 'pypdf'."
        )

    # check if `download_path` exists, and if not, create it
    download_path = Path(download_path)
    download_path.mkdir(parents=True, exist_ok=True)

    # Initializing classes
    fetcher = ArxivFetcher(
        download_path=download_path,
        category=category,
        start_id=start_id,
        start_from_filepath=start_from_filepath,
        logger=logger,
    )
    downloader = ArxivDownloader(download_path=download_path, logger=logger)
    extractor = TextExtractor(logger=logger)

    pattern_files: list[Path] = []
    pattern_papers: list[ArxivPaper] = []
    with click.progressbar(
        length=n_papers, label="Downloading and processing papers"
    ) as bar:
        while len(pattern_papers) < n_papers:
            papers = fetcher.fetch(
                n_papers=n_papers,
                n_pattern_papers=len(pattern_papers),
            )
            for paper in papers:
                pdf_path = downloader.download_pdf(arxiv_paper=paper)
                text = extractor.get_text(pdf_path=pdf_path, loader=loader)
                if not text:
                    logger.info("No text extracted from the PDF.")
                    continue
                if clean_text:
                    text = extractor.delete_references(text=text)
                    text = extractor.clean_text(text=text)

                # Deleting downloaded PDFS that do not match the regex pattern
                regex = re.compile(regex_pattern) if regex_pattern else None
                if regex and not regex.search(text):
                    pdf_path.unlink()
                    continue
                logger.info(
                    f"Paper {paper.id} matches the regex pattern: {regex_pattern}."
                    " Storing metadata and text in an HDF5 file."
                )

                # If the paper matches the regex_pattern, store text in the corresponding ArxivPaper object
                paper.text = text
                paper.pdf_loader = loader

                # Save the paper metadata to an HDF5 file
                hdf_path = download_path / f"{paper.id}.hdf5"
                with h5py.File(hdf_path, "a") as h5f:
                    _ = paper.to_hdf5(hdf_file=h5f)

                # Deleting the PDF file after storing it in HDF5
                if not download_pdfs:
                    pdf_path.unlink()

                # Appending the HDF5 file and paper to the lists
                pattern_files.append(hdf_path)
                pattern_papers.append(paper)
                bar.update(1)

                if len(pattern_papers) >= n_papers:
                    break
    return pattern_files, pattern_papers


@click.group(help="Entry point to run `pyrxiv` CLI commands.")
def cli():
    pass


@cli.command(
    name="search_and_download",
    help="Searchs papers in arXiv for a specified category and downloads them in a specified path.",
)
@click.option(
    "--download-path",
    "-path",
    type=str,
    default="data",
    required=False,
    help="""
    (Optional) The path for downloading the arXiv metadata in HDF5 files and, optionally (if set with download-pdfs), the PDFs. Defaults to "data".
    """,
)
@click.option(
    "--category",
    "-c",
    type=str,
    default="cond-mat.str-el",
    required=False,
    help="""
    (Optional) The arXiv category on which the papers will be searched. Defaults to "cond-mat.str-el".
    """,
)
@click.option(
    "--n-papers",
    "-n",
    type=int,
    default=5,
    required=False,
    help="""
    (Optional) The number of arXiv papers to be fetched and downloaded. If `regex-pattern` is not specified, this
    would correspond to the n_papers starting from the newest in the `category`. Defaults to 5.
    """,
)
@click.option(
    "--regex-pattern",
    "-regex",
    type=str,
    required=False,
    help="""
    (Optional) If specified, this regex pattern is searched in the arXiv papers so only the ones with
    the corresponding match will be downloaded.
    """,
)
@click.option(
    "--start-id",
    "-s",
    type=str,
    required=False,
    help="""
    (Optional) If specified, the search will start from this arXiv ID. This is useful for resuming the search
    from a specific point. If not specified, the search will start from the newest papers in the `category`.
    """,
)
@click.option(
    "--start-from-filepath",
    "-sff",
    type=bool,
    default=False,
    required=False,
    help="""
    (Optional) If specified, the search will start from the last downloaded arXiv ID. This is useful for resuming
    the search from a specific point. If not specified, the search will start from the newest papers in the `category`.
    """,
)
@click.option(
    "--loader",
    "-l",
    type=click.Choice(["pdfminer", "pypdf"], case_sensitive=False),
    default="pdfminer",
    required=False,
    help="""
    (Optional) PDF loader to use for extracting text from the downloaded PDFs. Defaults to "pdfminer".
    Available loaders: "pdfminer", "pypdf".
    """,
)
@click.option(
    "--clean-text",
    "-ct",
    type=bool,
    default=True,
    required=False,
    help="""
    (Optional) If True, the extracted text will be cleaned by removing references and unnecessary whitespaces.
    Defaults to True.
    """,
)
@click.option(
    "--download-pdfs",
    "-dp",
    is_flag=True,
    default=False,
    required=False,
    help="""
    (Optional) If True, the PDFs will be downloaded and saved in `download_path`. Defaults to False.
    """,
)
def search_and_download(
    download_path,
    category,
    n_papers,
    regex_pattern,
    start_id,
    start_from_filepath,
    loader,
    clean_text,
    download_pdfs,
):
    start_time = time.time()

    run_search_and_download(
        download_path=Path(download_path),
        category=category,
        n_papers=n_papers,
        regex_pattern=regex_pattern,
        start_id=start_id,
        start_from_filepath=start_from_filepath,
        loader=loader,
        clean_text=clean_text,
        download_pdfs=download_pdfs,
    )

    elapsed_time = time.time() - start_time
    click.echo(f"Downloaded arXiv papers in {elapsed_time:.2f} seconds\n\n")


@cli.command(
    name="download_pdfs",
    help="Downloads the PDFs of the arXiv papers stored in HDF5 files in a specified path.",
)
@click.option(
    "--data-path",
    "-path",
    type=str,
    default="data",
    required=False,
    help="""
    (Optional) The path where the HDF5 files with the arXiv papers metadata exist. The downloaded PDFs will be stored in there as well. Defaults to "data".
    """,
)
def download_pdfs(data_path):
    start_time = time.time()

    # check if `data_path` exists, and if not, returns an error
    data_path = Path(data_path)
    if not data_path.exists():
        raise click.ClickException(f"The specified path {data_path} does not exist.")
    downloader = ArxivDownloader(download_path=data_path, logger=logger)

    # Loops over all HDF5 files in the `data_path` and downloads the corresponding PDFs
    hdf5_files = list(data_path.glob("*.hdf5"))

    failed_downloads = []
    with click.progressbar(
        length=len(hdf5_files), label="Downloading papers PDFs"
    ) as bar:
        for file in hdf5_files:
            paper = ArxivPaper.from_hdf5(file=file)
            try:
                _ = downloader.download_pdf(arxiv_paper=paper)
            except Exception as e:
                failed_downloads.append(str(file))
                logger.error(f"Failed to download PDF for {file}: {e}")
            bar.update(1)

    elapsed_time = time.time() - start_time
    click.echo(f"Downloaded arXiv papers in {elapsed_time:.2f} seconds\n\n")

    if failed_downloads:
        click.echo("\nFailed to download PDFs for the following files:")
        for failed_file in failed_downloads:
            click.echo(f"  - {failed_file}")
