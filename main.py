from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import logging
import requests

from utils.crawler import search_arxiv, search_serper
from utils.pdf import generate_pdf
from utils.summarizer import categorize_papers


def main(num_papers=None):
    # Step 1: Extract all titles from the EMNLP 2024 accepted papers page
    emnlp_url = "https://2024.emnlp.org/program/accepted_main_conference/"
    response = requests.get(emnlp_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Assuming each title is in a <strong> or <h3> tag
    titles = [tag.text for tag in soup.find_all(['strong', 'h3'])]

    # Set this logger to DEBUG to see more detailed logs
    # logging.basicConfig(level=logging.DEBUG,
    #                    format='%(asctime)s - %(levelname)s - %(message)s')  # logging.INFO, logging.DEBUG

    # Step 2: Search for each title on arXiv / google and extract the abstract
    data = []
    found_arxiv = 0
    found_serper = 0
    not_found = 0
    save_frequency = 50

    # Limit the number of papers to process
    if num_papers:
        titles = titles[:num_papers]

    # Loop through each title and search for it
    logging.debug(f'Start search for {len(titles)} titles')
    with tqdm(total=len(titles)) as pbar:
        for title in titles:
            # Extract the top result's title and abstract, if available
            found_paper = False

            # Search on Serper
            if not found_paper:
                found_serper, found_paper = search_serper(title, found_serper, data)

            # Search on arXiv
            if not found_paper:
                found_arxiv, found_paper = search_arxiv(title, found_arxiv, data)

            # We could not find the paper
            if not found_paper:
                logging.debug(f"Title '{title}' not found.")
                data.append(
                    {
                        "Original Title": title,
                        "Found Title": None,
                        "Abstract": None,
                        "PaperUrl": None
                    }
                )
                not_found += 1

            # Update tqdm description with counts
            pbar.set_description(f"Found: {found_arxiv} (arXiv), {found_serper} (Serper), Not Found: {not_found}")
            pbar.update(1)

            if (len(data) % save_frequency) == 0:
                logging.debug(f"Saving data to parquet")
                df = pd.DataFrame(data)
                df.to_parquet(f"./data/emnlp_abstracts_{len(data)}.parquet", index=False)

    # Step 3: Save results to a DataFrame
    df = pd.DataFrame(data)
    df.to_parquet("./data/emnlp_abstracts.parquet", index=False)
    logging.debug("Data saved to emnlp_arxiv_abstracts.parquet")

    # Step 4 Summarize Content from the Abstracts and Categorize
    logging.debug("Summarizing and categorizing papers...")
    summarized_df = categorize_papers(df)

    # Step 5 Generate Nice looking PDF with all the abstracts and links to the papers
    logging.debug("Generating PDF...")
    generate_pdf(summarized_df)


if __name__ == "__main__":
    main()