import os
import zipfile

import gdown

path = os.path.dirname(os.path.abspath(__file__))


def download_and_extract_dataset(gr_cache_file_id, trained_agents_file_id, extract_to):
    os.makedirs(extract_to, exist_ok=True)
    output1 = os.path.join(extract_to, "gr_cache.zip")
    output2 = os.path.join(extract_to, "trained_agents.zip")
    url1 = f"https://drive.google.com/uc?id={gr_cache_file_id}"
    url2 = f"https://drive.google.com/uc?id={trained_agents_file_id}"
    gdown.download(url1, output1, quiet=False)
    gdown.download(url2, output2, quiet=False)
    with zipfile.ZipFile(output1, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    with zipfile.ZipFile(output2, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(output1)
    os.remove(output2)


def download_and_extract_dataset_cli():
    import argparse

    parser = argparse.ArgumentParser(
        description="Download and extract the gr_libs dataset."
    )
    parser.add_argument(
        "--extract_to",
        type=str,
        default=path,
        help="Directory to extract the dataset to (default: current package directory)",
    )
    parser.add_argument(
        "--gr_cache_file_id",
        type=str,
        default="1ELmEpgmrmfwSCbfcCW_BJoKgCBjXsZqF",
        help="Google Drive file ID for gr_cache.zip",
    )
    parser.add_argument(
        "--trained_agents_file_id",
        type=str,
        default="12rBbaIa48sM-LPPucD5EEtV8dOsGGU7z",
        help="Google Drive file ID for trained_agents.zip",
    )
    args = parser.parse_args()
    download_and_extract_dataset(
        args.gr_cache_file_id, args.trained_agents_file_id, args.extract_to
    )


if __name__ == "__main__":
    gr_cache_file_id = "1ELmEpgmrmfwSCbfcCW_BJoKgCBjXsZqF"
    trained_agents_file_id = "12rBbaIa48sM-LPPucD5EEtV8dOsGGU7z"
    extract_to = path
    download_and_extract_dataset(gr_cache_file_id, trained_agents_file_id, extract_to)
