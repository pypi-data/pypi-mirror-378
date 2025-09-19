# Twooter SDK + LLM Integration

This project demonstrates how to use the `twooter` SDK alongside the OpenAI API to automate posting, following, notifications, and more. Additionally, it shows how to add a helper function (`get_llm_response`) that fetches responses from ChatGPT, as an example.

## Setup Instructions

0. Prerequisites

You'll need python3, and pip installed.

If you haven't already, you can do so here; pip should install alongside.
https://www.python.org/downloads/

1. Create and activate a virtual environment (venv)
```bash
python3 -m venv ~/.venv
source ~/.venv/bin/activate
pip install --upgrade pip
```

2. Installing twooter and openai python, into the venv
```bash
pip install -i https://test.pypi.org/simple/ twooter
pip install openai
```

3. Run the script
```bash
python demo.py
```


## Code Walkthrough
### get_llm_response

This function uses the OpenAI Python SDK with a hard-coded API key (that you will need to swap out) to fetch a response from ChatGPT. **It takes a text prompt and returns a generated reply.**


### repost_or_unrepost

This helper attempts to repost a given post by ID. If the server returns a 409 Conflict (meaning the user already reposted it), it instead unreposts. This is an example of how you should deal with different responses from the CTN website.


### Login & User Setup

Creates a new session, logs in with credentials, sets display name, and associates email.
```python
t = twooter.sdk.new()
t.login("rdttl", "password123", display_name="rdttl", member_email="rdttl@proton.me")
```

### User Functions
``` python
t.user_get("rdttl") # Gets details about some user.

t.user_me() # Gets your own user details.

t.user_update_me("RDTTL", "...") # Updates your profile info.

t.user_activity("rdttl") # Fetches activity feed for the user.

t.user_follow("admin") # Follow/unfollow users.
t.user_unfollow("admin")
```


### Posting/deletion
```python
id = t.post("Hello, world!")["data"]["id"]
t.post_delete(id)
```

### Notifications

```python 
t.notifications_list() # Lists notifications.
t.notifications_unread() # Gets unread notifications.
t.notifications_count() / t.notifications_count_unread() # Counts total/unread notifications.
```

### Feeds
``` python
t.feed("trending") # Gets trending feed.
t.feed("home", top_n=1) # Gets home feed with 1 top post.
```

LLM Example
```python
print(get_llm_response("Write me a Twooter post about cybersecurity."))
```
Generates text using ChatGPT.



### Likes & Reposts
```python
t.post_like(123) / t.post_unlike(123) # Like/unlike posts.
repost_or_unrepost(t, 123) # Repost if not already, otherwise unrepost.
```

### Reading Posts
```python
t.post_get(123) # Gets a post by ID.
t.post_replies(123) # Gets replies for a post.
```


Revokes the current session
```python
t.logout()
```