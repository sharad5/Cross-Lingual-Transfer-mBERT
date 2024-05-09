import asyncio
from twscrape import API, gather
from twscrape.logger import set_log_level
import pandas as pd
import os
import json
from tqdm import tqdm

input_file_path = 'hate_speech_turkish_part1'
output_file_path = 'scraped_tweets_tr1.csv'
last_id_file_path = 'last_tweet_id.txt'

if os.path.exists(output_file_path):
    input_file_path = output_file_path

tr_df = pd.read_csv(input_file_path, dtype={'TweetID': 'string'})

if not 'tweet_text' in tr_df.columns:
    tr_df['tweet_text'] = None
print(tr_df.head())

last_id = None
if os.path.exists(last_id_file_path):
    with open(last_id_file_path, 'r') as file:
        last_id = file.read().strip()
start_index = tr_df[tr_df['TweetID'] == last_id].index[0] + 1 if last_id else 0
print(f"Scraping starting from index: {start_index}")


# print(len(ids))

tweet_op = []
tweet_full_json = []

kv = {
	"referrer": "tweet",  # tweet, profile
	"with_rux_injections": False,
	"includePromotedContent": False,
	"withCommunity": False,
	"withQuickPromoteEligibilityTweetFields": False,
	"withBirdwatchNotes": False,
	"withVoice": False,
	"withV2Timeline": False,
	"withDownvotePerspective": False,
	"withReactionsMetadata": False,
	"withReactionsPerspective": False,
	"withSuperFollowsTweetFields": False,
	"withSuperFollowsUserFields": False
}

async def main():
	api = API()
	await api.pool.add_account("user2", "pass2", "u2@example.com", "mail_pass2")
	await api.pool.login_all()
	ids = tr_df['TweetID'].values[start_index:]
	for idx,t_id in tqdm(enumerate(ids), total=len(ids)):
		try:
			kv["focalTweetId"] = t_id
			print(t_id)
			rep = await api.tweet_details(int(t_id))
			print(rep)
			# rep is httpx.Response object
			tr_df.loc[tr_df["TweetID"] == t_id, 'tweet_text'] = rep.rawContent
		except Exception as e:
			print("Error for ID: ", t_id, e)
			tr_df.loc[tr_df["TweetID"] == t_id, 'tweet_text'] = ""  # Use empty string for errors
		
        # Save the last scraped tweet for resuming later
		with open(last_id_file_path, 'w') as file:
			file.write(t_id)
        
        # Save to CSV every 20 tweets or at the end
		if (idx + 1) % 20 == 0 or (idx + 1) == len(ids):
			tr_df.to_csv(output_file_path, mode='w', index=False)



if __name__ == "__main__":
    asyncio.run(main())
