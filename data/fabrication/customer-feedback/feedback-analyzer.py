# Install necessary libraries
# pip install pandas transformers torch

import pandas as pd
from transformers import pipeline

# Path to the fabricated data CSV file
fabricated_data_path = "data/fabricated_feedback.csv"

# Load the fabricated feedback data
fabricated_df = pd.read_csv(fabricated_data_path)

# Initialize the Hugging Face sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Function to get sentiment score from feedback text
def get_sentiment_score(feedback):
    result = sentiment_analyzer(feedback[:512])  # Truncate to 512 characters for efficiency
    score = result[0]['score'] if result[0]['label'] == 'POSITIVE' else -result[0]['score']
    return score


# Apply sentiment analysis to each feedback row and create a 'Score' column
fabricated_df['Score'] = fabricated_df['Feedback'].apply(get_sentiment_score)


# Confirmation of Model Working
def run_confirmation():
    def score_ranking(score):
        return -1 if score < 0 else 1

    def source_ranking(source):
        return -1 if source == 'NEGATIVE' else 1

    fabricated_df['Score_Rank'] = fabricated_df['Score'].apply(score_ranking)
    fabricated_df['Source_Rank'] = fabricated_df['Source'].apply(source_ranking)
    fabricated_df['Confirmation'] = fabricated_df['Score_Rank'] == fabricated_df['Source_Rank']

    false_count = (fabricated_df['Confirmation'] == False).sum()

    print(f'\nRan Confirmation! \nTotal wrong values: {false_count}')



# Save the updated DataFrame with the 'Score' column
fabricated_df.to_csv("scored_feedback.csv", index=False)

print("Feedback data with sentiment scores saved to 'scored_feedback.csv'.")

# run_confirmation()