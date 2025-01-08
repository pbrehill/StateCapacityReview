#!/usr/bin/env python3

import argparse
import logging
import openai
import pandas as pd
from tqdm import tqdm
from config import OPENAI_API_KEY
from citation_counts import get_citation_count

openai.api_key = OPENAI_API_KEY

logging.basicConfig(filename='api_costs.log', level=logging.INFO)
pricing = 5.00 / 1000000

def fix_dataframe_encoding(df):
    def fix_text(text):
        if isinstance(text, str):
            try:
                # Encode the text as 'latin1' bytes, then decode it as 'utf-8'
                return text.encode('latin1').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                return text  # Return the text unchanged if there's an error
        else:
            return text  # Return non-string data unchanged

    # Apply the fix_text function to all string columns in the DataFrame
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(fix_text)
    return df

def calculate_cost(response):
    token_count = response.usage.total_tokens
    cost = token_count * pricing
    return cost, token_count

def classify_papers(csv_file, questions):
    # Load the CSV file
    data = pd.read_csv(csv_file, dtype=str)
    data = data.fillna('')
    data = fix_dataframe_encoding(data)

    print("Getting citations")
    data["Citations"] = [get_citation_count(doi) for doi in tqdm(data["DOI"])]

    print("Answering questions")

    for index, question in tqdm(enumerate(questions), desc="Outer loop"):
        # Concatenate Title and Abstract for the prompt
        prompt_bodies = "Title: " + data['Title'] + "\n\n" + \
                        "Abstract: " + data['Abstract'] + "\n\n"

        results = []
        tokens = 75  # Max tokens for each response
        total_cost = 0

        for text in tqdm(prompt_bodies, desc="Inner loop", leave=False):
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Classify the following description"},
                    {
                        "role": "user",
                        "content": text + "\n\n" + question + "If you are unsure, please just tell me that."
                    }
                ],
                max_tokens=tokens,
                temperature=0
            )

            cost, token_count = calculate_cost(response)
            logging.info(f"Prompt: {text}, Tokens used: {token_count}, Cost: ${cost:.4f}")
            total_cost += cost
            print(f"Current total cost for question {index+1}: {total_cost:.4f}")

            results.append(response.choices[0].message.content)

        # Store the results in the dataframe
        data[f'Q{index + 1}'] = results

    return data

def main():
    parser = argparse.ArgumentParser(description="Classify papers from a CSV using GPT-4o.")
    parser.add_argument("csv_file", help="Path to the CSV file.")
    parser.add_argument("questions_file", help="Path to the file containing questions (one question per line).")
    parser.add_argument("output_file", help="Output file path (e.g., output.xlsx).")

    args = parser.parse_args()

    # Read the questions from file
    with open(args.questions_file, 'r', encoding='utf-8') as f:
        questions = f.read().splitlines()

    # Classify papers
    classified_data = classify_papers(args.csv_file, questions)

    # Save to Excel
    classified_data.to_excel(args.output_file, index=False)
    print(f"Classification results saved to {args.output_file}")

if __name__ == "__main__":
    main()
