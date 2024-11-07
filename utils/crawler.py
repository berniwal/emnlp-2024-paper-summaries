import os
import arxiv
from rapidfuzz import fuzz
import logging
import requests
import json

client = arxiv.Client()


def search_arxiv(title, found_arxiv, data):
    # Search for the title on arXiv
    logging.debug(f"Searching for '{title}' on arXiv")
    arxiv_search = arxiv.Search(
        query=title,
        max_results=10,
        sort_by=arxiv.SortCriterion.Relevance
    )

    results = client.results(arxiv_search)

    found_paper = False
    for result_idx, result in enumerate(results):
        paper_title = result.title

        # Check if paper_title is similar to title
        if fuzz.ratio(title, paper_title) < 80:
            logging.debug(f"Title '{title}' does not match '{paper_title}' - Try next: {result_idx}")
            continue
        else:
            logging.debug(f"Title '{title}' matches '{paper_title}, adding to list.'")

        found_arxiv += 1
        abstract = result.summary
        data.append({
            "Original Title": title,
            "Found Title": paper_title,
            "Abstract": abstract,
            "PaperUrl": result.entry_id
        })
        found_paper = True
        break  # Only take the top result

    return found_arxiv, found_paper


def search_serper(title, found_serper, data):
    # Define the Serper API endpoint and headers
    url = "https://google.serper.dev/search"
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': os.environ["SERPER_API_KEY"]  # Replace with your actual API key
    }

    # Prepare the payload with the search query
    payload = json.dumps({
        "q": f"{title} site:arxiv.org"
    })

    logging.debug(f"Searching for '{title}' using Serper API.")
    try:
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()

        # Process the response data
        found_paper = False
        for search_idx, result in enumerate(response_data.get("organic", [])):
            result_url = result.get("link")

            # Check if result matches a paper format, e.g., from arXiv or similar
            if "arxiv.org" in result_url:
                arxiv_id = result_url.split('/')[-1]
                try:
                    paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
                except Exception as e:
                    logging.error(f"Error fetching paper {result_url} - {arxiv_id} from arXiv: {e}")
                    continue

                paper_title = paper.title
                # Check if paper_title is similar to title
                if fuzz.ratio(title, paper_title) < 80:
                    logging.debug(
                        f"Serper - Title '{title}' does not match '{paper_title}' - Try next link - {search_idx}")
                    continue
                else:
                    logging.debug(f"Serper - Title '{title}' matches '{paper_title}, adding to list.'")

                data.append({
                    "Original Title": title,
                    "Found Title": paper_title,
                    "Abstract": paper.summary,
                    "PaperUrl": result_url
                })
                logging.debug(f"Found on Serper: '{paper.title}'")
                found_serper += 1
                found_paper = True
                break  # Only take the first matching result

    except Exception as e:
        logging.error(f"Error during Serper API search: {e}")
        found_paper = False

    return found_serper, found_paper
