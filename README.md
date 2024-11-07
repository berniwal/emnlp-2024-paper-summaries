# EMNLP 2024 Conference Paper Summarizer

This project automates the crawling and abstract summarization of papers presented at the EMNLP 2024 conference. 
The goal is to create a two sentence summary of all accepted papers to help researchers quickly identify papers of interest.
The final PDF can be found at [data/emnlp_2024_summary_demo.pdf](./data/emnlp_2024_summary_demo.pdf).

### List of Papers
The list of papers is presented here: https://2024.emnlp.org/program/accepted_main_conference/

#### Paper Matching
We crawl this page and search for the matching papers via the arXiv API and via Google search (using the Serper API).

#### Abstract Summarization and Category Assignment
If we find a matching paper by string-matching the title, we extract the abstract and categorize the paper into one of the categories defined by the EMNLP conference:
https://2024.emnlp.org/calls/main_conference_papers/
We then generate a two-sentence summary of the paper and assign a score to the paper based on how general or domain-specific the paper is.

#### PDF Report Generation
Finally, we generate a PDF report that lists all papers, their summaries, categories, and scores. The PDF also includes direct links to the full papers on arXiv.

#### Stats
We were able to find and summarize 974 papers out of 1269 papers listed on the EMNLP 2024 website.
```
Found: 71 (arXiv), 903 (Serper), Not Found: 295: 100%|██████████| 1269/1269 [1:24:16<00:00,  3.98s/it]
```

## Overview

The repository fetches paper titles from the EMNLP 2024 conference website, searches for their abstracts on **arXiv** and **Serper** (Google), and categorizes them into relevant NLP categories. Summaries and scores are generated to highlight general vs. domain-specific contributions, which are then compiled into a PDF for easy review.

### Key Features

- **Automated Paper Title Extraction**: Extracts paper titles from the EMNLP 2024 accepted papers page.
- **Multi-Source Abstract Retrieval**: Searches for abstracts on **arXiv** and **Google** (via Serper API).
- **Paper Categorization**: Categorizes papers into predefined EMNLP categories.
- **PDF Report Generation**: Creates a PDF of categorized papers, including summaries and links to full texts.

## Setup

### Prerequisites

- Python 3.x
- Required libraries: `beautifulsoup4`, `pandas`, `tqdm`, `requests`, `fpdf`, `pydantic`, `openai`, `arxiv`, `rapidfuzz`

Install the dependencies:
```bash
pip install requirements.txt
```

Environment Variables
Add your Serper API key as an environment variable:

```bash
export SERPER_API_KEY='Your_Serper_API_key_here'
export OPENAI_API_KEY='Your_OpenAI_API_key_here'
```

Directory Structure
The repository is structured as follows:

graphql
```
├── main.py                # Main script to extract, search, categorize, and summarize papers
├── utils/
│   ├── crawler.py         # Contains search functions for arXiv and Serper API
│   ├── pdf.py             # Generates a PDF report from summarized data
│   └── summarizer.py      # Categorizes and summarizes papers based on abstracts
├── data/                  # Directory for storing intermediate and final output files
└── README.md              # This readme file
```

Usage
Run the Main Script:
```
python main.py
```

This script fetches all paper titles, searches for abstracts, categorizes and summarizes the content, and saves the output to a PDF.

Script Workflow:

Step 1: Extracts paper titles from the EMNLP 2024 website.

Step 2: Searches for abstracts on arXiv and Google (using the Serper API).

Step 3: Categorizes papers into predefined categories based on the abstract.

Step 4: Summarizes the content, scores generality, and generates a categorized PDF report.

Checkpoints: Intermediate files are saved as Parquet files in the data/ directory every 50 papers to handle large datasets.

### Logging and Debugging

To view detailed logs, uncomment and set the logging level to DEBUG in main.py. Logs provide insights into missing papers, API search results, and errors.

### Output
The final categorized summary is saved as a PDF at ./data/emnlp_2024_summary.pdf. This PDF includes:

Paper titles
Summaries (if available)
Categories and scores
Direct links to full texts (if available)