# Crypto Whale Alert Tracker

## Overview

The **Crypto Whale Alert Tracker** is a Python project designed to capture, clean, and categorize tweets from the "whale_alert" Twitter account, creating a well-structured dataset that serves as a foundation for advanced data analysis. This project showcases skills in Python programming, API integration, data manipulation, and cloud storage management. It lays the groundwork for uncovering trends, patterns, and correlations which can then be leveraged to explore connections between transaction behavior of major players (whales) and the price movements of a specific cryptocurrency coin. These insights can guide investment decisions and enhance our understanding of the dynamics of the cryptocurrency market.

## Features

- **API Integration**: Utilizes Tweepy to access the Twitter API and fetch tweets from "whale_alert" from the last 24 hours.

- **Data Cleaning and Structuring**: Cleans tweets by removing special characters and organizes the data into a structured format, ensuring the dataset is ready for sophisticated analyses.

- **Junk Tweet Identification**: Identifies and stores tweets in a seperate csv not adhering to the expected format as "junk", enhancing data quality.

- **Google Cloud Storage**: Utilizes Google Cloud Storage for secure storage and retrieval of categorized tweet data.

- **File Management**: Stores cleaned data in CSV files, enabling seamless merging with existing data for comprehensive historical records.

## Usage

1. **API Key Retrieval**: Retrieve API keys from a JSON file in Google Cloud Storage for secure access to the Twitter API.

2. **Tweet Capture and Categorization**: Fetch recent tweets from "whale_alert," categorize based on criteria, and transform data into a format for in-depth analysis.

2. **Junk Capture Monitoring**: Monitor the junk tweets csv to identify if any important data that should be captured is being lost and adapt the script as required.
   
4. **Running & Scheduling the Script**: Execute the `whale_catching_tweets()` function to capture, clean, and categorize tweets. The script is designed to run on a  schedule every 24 hours.

## Getting Started

1. **Requirements**: Install required libraries with `pip install -r requirements.txt`.

2. **API Keys**: Store Twitter API keys in a JSON file and upload it to your Google Cloud Storage bucket. Update `bucket_name` and `json_file_path` variables.

3. **Customization**: Adapt the script to monitor different accounts, adjust categorization rules, or modify time ranges for tweet capture.

## Conclusion

The result is a relational database of transactions updating every 24 hours and a seperate junk database of tweets which don't meet transcation criteria. This database is now ready to be used for more in-depth analysis uncovering trends, patterns, and correlations which can then be leveraged to explore connections between transaction behavior of major players (whales) and the price movements of a specific cryptocurrency coin.

