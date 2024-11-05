import pandas as pd
import random

# Paths to the base CSV files
positive_file_path = "data/fabrication/customer-feedback/positive.csv"
negative_file_path = "data/fabrication/customer-feedback/negative.csv"

# Load the positive and negative feedback data
positive_df = pd.read_csv(positive_file_path)
negative_df = pd.read_csv(negative_file_path)

# Function to generate random feedback data
def generate_random_feedback(total_rows=1000, positive_percentage=50):
    # Calculate the number of positive and negative rows based on the percentage
    positive_count = int((positive_percentage / 100) * total_rows)
    negative_count = total_rows - positive_count

    # Randomly select rows from the positive and negative datasets
    random_positive_df = positive_df.sample(n=positive_count, replace=True, random_state=None)
    random_negative_df = negative_df.sample(n=negative_count, replace=True, random_state=None)

    # Add the 'source' column to label positive and negative data
    random_positive_df['Source'] = 'POSITIVE'
    random_negative_df['Source'] = 'NEGATIVE'

    # Combine the positive and negative data into one DataFrame
    combined_df = pd.concat([random_positive_df, random_negative_df], ignore_index=True)

    # Shuffle the combined data for randomness
    combined_df = combined_df.sample(frac=1, random_state=None).reset_index(drop=True)

    return combined_df

# Example usage
fabricated_data = generate_random_feedback(total_rows=1000, positive_percentage=60)

# Optionally, save the generated data to a CSV file
fabricated_data.to_csv("data/fabrication/customer-feedback/fabricated_feedback.csv", index=False)

print(f"Done simulating customer feedback! \nFabricated {len(fabricated_data)} rows.")
