import logging

from openai import OpenAI
from pydantic import BaseModel
from enum import Enum
import pandas as pd
import numpy as np
import os
import logging

client = OpenAI()


# Define the Enum for submission categories
# https://2024.emnlp.org/calls/main_conference_papers/
class CategoryEnum(str, Enum):
    computational_social_science = "Computational Social Science and Cultural Analytics"
    dialogue_systems = "Dialogue and Interactive Systems"
    discourse_pragmatics = "Discourse and Pragmatics"
    low_resource_methods = "Low-resource Methods for NLP"
    ethics_bias_fairness = "Ethics, Bias, and Fairness"
    generation = "Generation"
    information_extraction = "Information Extraction"
    information_retrieval = "Information Retrieval and Text Mining"
    interpretability_analysis = "Interpretability and Analysis of Models for NLP"
    linguistic_theories = "Linguistic theories, Cognitive Modeling and Psycholinguistics"
    ml_for_nlp = "Machine Learning for NLP"
    machine_translation = "Machine Translation"
    multilinguality_diversity = "Multilinguality and Language Diversity"
    multimodality_grounding = "Multimodality and Language Grounding to Vision, Robotics and Beyond"
    phonology_morphology = "Phonology, Morphology and Word Segmentation"
    question_answering = "Question Answering"
    resources_evaluation = "Resources and Evaluation"
    semantics = "Semantics: Lexical, Sentence-level Semantics, Textual Inference and Other areas"
    sentiment_analysis = "Sentiment Analysis, Stylistic Analysis, and Argument Mining"
    speech_processing = "Speech processing and spoken language understanding"
    summarization = "Summarization"
    syntax_tagging = "Syntax: Tagging, Chunking and Parsing"
    nlp_applications = "NLP Applications"
    efficiency = "Special Theme: Efficiency in Model Algorithms, Training, and Inference"


# Parsed Paper Structure
class ParsedPaper(BaseModel):
    summary: str
    category: CategoryEnum
    score: int


# Parsed Paper Structure if we don't have a Abstract
class ParsedPaperWithoutSummary(BaseModel):
    category: CategoryEnum
    score: int


# Define the function to categorize each abstract and retrieve summary
def categorize_paper(row):
    title = row['Found Title']
    original_title = row['Original Title']
    abstract = row['Abstract']

    try:
        # Check if the abstract is missing
        if pd.isna(abstract):
            # System and user prompts for categorizing abstracts
            system_prompt = "Categorize the paper based on its title into one of the specified categories. Give them a generality score from 0-100 based on the following criterion: Low Generality: Very domain specific problem, High Generality: General methods."
            user_prompt = f"Paper Title: {original_title}\n\nPlease categorize this paper based on the abstract into one of the following categories: {', '.join([cat.value for cat in CategoryEnum])}."

            # Make the API request
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=ParsedPaperWithoutSummary,
            )

            # Extract the category from the response
            parsed_paper = completion.choices[0].message.parsed
            return parsed_paper.category, None, parsed_paper.score
        else:
            # System and user prompts for categorizing abstracts
            system_prompt = "Summarize each paper with two short sentences and categorize them based on its abstract into one of the specified categories. Give them a generality score from 0-100 based on the following criterion: Low Generality: Very domain specific problem, High Generality: General methods."
            user_prompt = f"Paper Title: {title}\nAbstract: {abstract}\n\nPlease categorize this paper based on the abstract into one of the following categories: {', '.join([cat.value for cat in CategoryEnum])}."

            # Make the API request
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=ParsedPaper,
                max_tokens=1000,
            )

            # Extract the summary and category from the response
            parsed_paper = completion.choices[0].message.parsed
            return parsed_paper.category, parsed_paper.summary, parsed_paper.score
    except Exception as e:
        logging.error(f"Error processing paper {title}: {e}")
        return None, None, None


def categorize_papers(input_df, num_batches=10):
    # Split into 10 batches
    input_df_batches = np.array_split(input_df, min(num_batches, len(input_df)))

    processed_list = []
    for batch_idx, sub_df in enumerate(input_df_batches):
        target_path_batch = f"./data/emnlp_2024_batch_{batch_idx}.parquet"

        # Check if the batch file already exists
        if os.path.exists(target_path_batch):
            logging.debug(f"Batch {batch_idx} already exists. Skipping...")
            sub_df = pd.read_parquet(target_path_batch)
            processed_list.append(sub_df)
            continue

        logging.debug(f"Processing batch {batch_idx} of length {len(sub_df)}...")
        sub_df[['Category', 'Summary', 'Score']] = sub_df.apply(categorize_paper, axis=1, result_type="expand")

        # Save the batch to a new Parquet file
        sub_df.to_parquet(target_path_batch)
        logging.debug(f"Batch {batch_idx} processed and saved as {target_path_batch}")

        processed_list.append(sub_df)

    summarized_df = pd.concat(processed_list, axis=0)
    summarized_df.to_parquet('./data/emnlp_2024_summary.parquet')
    return summarized_df
