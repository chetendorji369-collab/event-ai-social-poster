import requests

URL = "https://api.buffer.com"

METADATA_BLOCKS = {
    "Facebook": "metadata: { facebook: { type: post } }",
    "Instagram": "metadata: { instagram: { type: post, shouldShareToFeed: true } }",
    "LinkedIn": "metadata: { linkedin: {} }"
}

def push_to_buffer(token: str, profile_id: str, text: str, platform: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    query = f"""
    mutation ($text: String!, $channelId: ChannelId!) {{
      createPost(input: {{
        text: $text,
        channelId: $channelId,
        mode: addToQueue,
        schedulingType: automatic,
        saveToDraft: true,
        {METADATA_BLOCKS[platform]}
      }}) {{
        __typename
        ... on PostActionSuccess {{ post {{ id }} }}
        ... on MutationError {{ message }}
      }}
    }}
    """
    
    payload = {
        "query": query,
        "variables": {
            "text": text,
            "channelId": str(profile_id).strip()
        }
    }
    
    res = requests.post(URL, headers=headers, json=payload)
    res.raise_for_status()
    return res.json()