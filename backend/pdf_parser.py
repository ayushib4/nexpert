import os
import requests
import tempfile
from functools import lru_cache

from PyPDF2 import PdfReader


@lru_cache(maxsize=1000)
def pdf_url_to_text(url: str) -> str:
    tempfile = download_pdf(url)
    text = pdf_to_text(tempfile)
    return text


@lru_cache(maxsize=1000)
def pdf_to_text(path_to_pdf: str) -> str:
    reader = PdfReader(path_to_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


@lru_cache(maxsize=30)
def download_pdf(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to download the file.")
        return None

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Determine the file name from the URL
    filename = os.path.join(temp_dir, url.split("/")[-1])

    # Write the content to a PDF file
    with open(filename, "wb") as file:
        file.write(response.content)

    print(f"Downloaded file saved in {filename}")
    return filename
