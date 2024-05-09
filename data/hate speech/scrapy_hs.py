import asyncio
from twscrape import API, gather
from twscrape.logger import set_log_level
import pandas as pd
import json
from tqdm import tqdm

df = pd.read_csv('hate_speech_dataset_v2.csv', dtype={'tweet_id': 'string'})
tr_df = df[df["LangID"]==0]
tr_df = tr_df[:200]
print(tr_df.head())

ids = tr_df['TweetID'].values

print(len(ids))

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
	await api.pool.add_account("user1", "pass1", "u1@example.com", "mail_pass1")
    # await api.pool.add_account("user2", "pass2", "u2@example.com", "mail_pass2")

	await api.pool.login_all()
 

	file = open('tr_tweet_texts_scraped.txt','w+')
	for idx,t_id in tqdm(enumerate(ids)):
		try:
			kv["focalTweetId"] = t_id
			print(t_id)
			rep = await api.tweet_details(int(t_id))
			print(rep)
			# rep is httpx.Response object
			# tweet_full_json.append(rep)
			tweet_op.append(rep.rawContent)
			file.write(rep.rawContent+"<<EOT>>\n")
		except Exception as e:
			print("Error for ID: ", t_id, e)
			tweet_op.append("")
			file.write("<<EOT>>\n")
		file.flush()
	file.close()

	tr_df['tweet_text'] = tweet_op
	tr_df.to_csv('scraped_tweets.csv')



if __name__ == "__main__":
    asyncio.run(main())
