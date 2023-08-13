import tweepy
import re
import datetime
import pandas as pd
import pytz
from google.cloud import storage
import json
import io

def get_api_keys():
    # Retrieve the API keys from the JSON file in Google Cloud Storage
    bucket_name = "whale-alert-twitter"
    json_file_path = "api_keys.json"

    client = storage.Client(project='whale-alert-twitter')
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(json_file_path)

    # Download the JSON file as a string
    json_string = blob.download_as_text()

    # Parse the JSON string into a dictionary
    api_keys = json.loads(json_string)

    return api_keys

def whale_catching_tweets(): 
    # Fetch the API keys
    api_keys = get_api_keys()

    # Assign the API keys to variables
    consumer_key = api_keys["consumer_key"]
    consumer_secret = api_keys["consumer_secret"]
    access_token = api_keys["access_token"]
    access_token_secret = api_keys["access_token_secret"]

    # Set up authentication for tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Set up tweepy API
    api = tweepy.API(auth)

    # Specify the path to the CSV file to store the tweets
    csv_file_path = "whale_alert_tweets.csv"  # File path to store captured tweets
    junk_csv_file_path = "junk_whale_alert_tweets.csv"  # File path to store junk tweets

    # Specifies the duration of the tweets to capture to the last 24 hours
    tz = pytz.timezone('UTC')
    now = datetime.datetime.now(tz)
    twenty_four_hours_ago = now - datetime.timedelta(hours=24)

    # Set the user to extract tweets from
    username = "whale_alert"

    # Get the user's timeline tweets up to a maximum of 50
    timeline = api.user_timeline(screen_name=username, count=50)

    # Filter the tweets to keep only the ones within the last 24 hours
    recent_tweets = [tweet for tweet in timeline if tweet.created_at > twenty_four_hours_ago]

    # Create two lists from the recent tweets, one for text and one for date and append the recent tweets
    raw_tweets = []  # List to store raw tweet text
    raw_tweets_date = []  # List to store raw tweet dates
    # Loop through tweets to capture the tweet text and date times
    for tweet in recent_tweets:
        raw_tweets.append([tweet.text])
        raw_tweets_date.append([tweet.created_at])

    # Create a list to capture cleaned text removing non-standard characters and links
    clean_string_list = []
    for string in raw_tweets:
        clean_string = re.sub(r'[^\w\s]', '', string[0])
        clean_string = re.sub(r'\n\nhttp\S+', '', clean_string)
        clean_string_list.append(clean_string)

    # Split list of tweet sentences into lists of words to assign to suitalbe columns
    split_list = []
    for string in clean_string_list:
        words = string.split()
        split_list.append(words)

    # Initialize junk list for tweets which are not desired but needed for monitoring
    junk_list = []
    junk_dates = []
    junk_dates_index = []
    clean_split_list = split_list

    # Tweet structure validation: the first and third items must be passable as integers (quantity and $ amount) otherwise remove the tweet as junk
    for i, item in enumerate(split_list):
        try:
            int(item[0])
            int(item[2])
        except ValueError:
            junk_list.append(item)
            clean_split_list.remove(item)
            junk_dates_index.append(i)
            junk_dates.insert(i, raw_tweets_date[i])
            del raw_tweets_date[i]

    # Captures transaction sender name between strings 'from' and 'to' and receiver name after 'to', so the entity sits in suitable column
    for i, row in enumerate(split_list):
        try:
            from_index = row.index('from')
            to_index = row.index('to')
        except ValueError:
            from_index = None
            to_index = None
        # Do process only if 'from' and 'to' both found
        if from_index is not None and to_index is not None:
            from_elements = ' '.join(row[from_index+1:to_index])
            to_elements = ' '.join(row[to_index+1:])
            split_list[i] = row[:from_index] + [from_elements, to_elements]

    # Joins entity name strings after 'at', so the entity sits in one column
    for i, row in enumerate(split_list):
        try:
            at_index = row.index('at')
        except ValueError:
            at_index = None
        # Do process only if 'at' found
        if at_index is not None:
            at_elements = ' '.join(row[at_index+1:])
            split_list[i] = row[:at_index] + [at_elements]

    # Tweet structure validation: conforming to the structure of our table and capturing desired information 
    ## the length of tweets must be no less than 6 or more than 7 strings
    for i, item in enumerate(split_list):
        if len(item) < 6 or len(item) > 7:
            junk_list.append(item)
            clean_split_list.remove(item)
            junk_dates_index.append(i)
            junk_dates.insert(i, raw_tweets_date[i])
            del raw_tweets_date[i]

    # Create a list of tuples from the clean_split_list and tweets_date lists to pass into table structure
    data = [(date[0], *row) for date, row in zip(raw_tweets_date, clean_split_list)]
    df = pd.DataFrame(data, columns=['Date', 'Amount (No.)', 'Cryptocurrency', 'Amount ($)', 'Currency', 'Action', 'From', 'To'])

    # Append the new DataFrame to the existing CSV file or create a new file in Cloud Storage
    client = storage.Client(project='whale-alert-twitter')
    bucket_name = "whale-alert-twitter"  # Assign to appropriate bucket name
    blob_name = csv_file_path  # File name for the main tweet CSV file

    # Retrieve the bucket and blob objects from Google Cloud Storage
    bucket = client.get_bucket(bucket_name) # Get the specified bucket
    blob = bucket.blob(blob_name) # Get the specified blob within the bucket

    if blob.exists():
        csv_content = blob.download_as_text()
        existing_df = pd.read_csv(io.StringIO(csv_content))
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        blob.upload_from_string(combined_df.to_csv(index=False), content_type="text/csv")
    else:
        blob.upload_from_string(df.to_csv(index=False), content_type="text/csv")

    # Get the number of tweets captured for reporting
    num_tweets = len(df)

    # Print the number of tweets captured to monitor amount of tweets captured daily to adjust limitations if req.
    print(f"{num_tweets} tweets captured successfully!")

    if junk_list:
        # Create the DataFrame for junk tweets
        junk_data = [(date[0], ' '.join(row)) for date, row in zip(junk_dates, junk_list)]
        junk_df = pd.DataFrame(junk_data, columns=['Date', 'Junk'])

        junk_blob_name = junk_csv_file_path  
        junk_blob = bucket.blob(junk_blob_name) # Get the specified blob within the bucket

        if junk_blob.exists():
            existing_junk_df = pd.read_csv(junk_blob.download_as_text())
            combined_junk_df = pd.concat([existing_junk_df, junk_df], ignore_index=True)
            junk_blob.upload_from_string(combined_junk_df.to_csv(index=False), content_type="text/csv")
        else:
            junk_blob.upload_from_string(junk_df.to_csv(index=False), content_type="text/csv")
    else:
        print("No junk posts today")
    
# Call the function to run the code       
whale_catching_tweets()

def entry_point_function():
    get_api_keys()
    whale_catching_tweets()

if __name__ == "__main__":
    entry_point_function()
