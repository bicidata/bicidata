from typing import Union, Iterable, Optional
import dotenv
import os
import time

import tweepy

dotenv.load_dotenv()

auth = tweepy.OAuthHandler(
    os.environ.get("TWITTER_API_KEY"),
    os.environ.get("TWITTER_API_KEY_SECRET")
)
auth.set_access_token(
    os.environ.get("TWITTER_ACCESS_TOKEN"),
    os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)


def update_thread(
        api: tweepy.API,
        user: str,
        messages: Iterable[str],
        last_status_id: Optional[Union[str, int]] = None,
):
    for m in messages:
        new_status = api.update_status(
            status=f"@{user} {m}",
            in_reply_to_status_id=last_status_id,
        )

        print(new_status)

        last_status_id = new_status.id

        time.sleep(0.01)



