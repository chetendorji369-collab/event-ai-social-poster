import os
import sys
import base64

# Force Python to use UTF-8 globally on Windows
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
import requests


# Page Configuration & Layout
st.set_page_config(page_title="Event AI Social Poster", layout="centered")

st.title("Event Social Media Agent")
st.write("Upload an event photo, drop some quick raw notes, and let Llama 4 Maverick write your social posts.")

# Sidebar Configuration (API Credentials Input)

st.sidebar.header("API Configuration")
st.sidebar.write("Paste your developer credentials here:")

nvidia_key = st.sidebar.text_input("NVIDIA API Key", type="password")
buffer_token = st.sidebar.text_input("Buffer Access Token", type="password")
buffer_profile_id = st.sidebar.text_input("Buffer Channel ID", type="password")

# NEW: Platform selector so we know which metadata to send
platform = st.sidebar.selectbox("Select Channel Platform", options=["Facebook", "Instagram", "LinkedIn"], index=0)

# Main User Inputs (Image Upload & Text Notes)

uploaded_file = st.file_uploader("Choose an Event Photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Selected Event Photo", use_container_width=True)

raw_notes_input = st.text_area("What is happening at the event right now? (Raw notes)", placeholder="Type notes here...")

# Initialize Session State to safely hold generated draft across button clicks
if "generated_post" not in st.session_state:
    st.session_state.generated_post = ""

# Trigger Step One: Call NVIDIA Llama 4 Maverick API

if st.button("Generate Social Post", type="primary"):
    if not nvidia_key or not uploaded_file or not raw_notes_input:
        st.error("Please fill in your NVIDIA API Key, select an image, and jot down some notes first.")
    else:
        with st.spinner("Llama 4 Maverick is analyzing your image and writing copy..."):
            try:
                # Clean the input text string aggressively to protect Windows processing
                raw_notes = str(raw_notes_input).encode('ascii', 'ignore').decode('ascii')

                # Read image file bytes and encode to base64 for NVIDIA vision API
                image_bytes = uploaded_file.getvalue()
                mime_type = uploaded_file.type
                b64_image = base64.b64encode(image_bytes).decode('utf-8')
                data_uri = f"data:{mime_type};base64,{b64_image}"

                # NVIDIA API endpoint
                invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"

                # System instructions - more detailed for professional output
                system_prompt = (
                    "You are a senior social media strategist and content creator for a premium brand. "
                    "You craft compelling, professional social media posts that drive engagement. "
                    "Your writing style is sophisticated, vivid, and authoritative. "
                    "You write detailed posts with rich descriptions, not short summaries. "
                    "Each post feels like a mini-story that captivates the reader from start to finish."
                )

                # User prompt - enhanced for longer, professional content
                user_text = (
                    "You are covering a live event. I have provided you with an event photo and raw notes. "
                    "Analyze the photo carefully and cross-reference with these raw notes: "
                    f"'{raw_notes}'. "
                    "\n\n"
                    "Write a PROFESSIONAL, ENGAGING social media post with the following structure:\n\n"
                    "1. HEADLINE: A bold, attention-grabbing headline that makes people stop scrolling.\n"
                    "2. OPENING PARAGRAPH (2-3 sentences): Set the scene vividly. Describe the atmosphere, location, and energy. Use sensory details.\n"
                    "3. BODY (3-4 bullet points): Key highlights with relevant emojis. Each bullet should be a complete thought with detail, not just a phrase.\n"
                    "4. CLOSING PARAGRAPH (2-3 sentences): A reflective or inspiring takeaway that ties the experience together.\n"
                    "5. CALL TO ACTION: A strong, clear CTA that encourages engagement (comment, share, tag someone, etc.).\n"
                    "6. HASHTAGS: Exactly 4-5 strategic, trending hashtags relevant to the content.\n\n"
                    "REQUIREMENTS:\n"
                    "- Total length: 150-250 words minimum. Be descriptive and thorough.\n"
                    "- Tone: Professional yet warm, inspiring, and authentic.\n"
                    "- Do NOT use filler phrases like 'Here is your post' or 'I hope you enjoy'.\n"
                    "- Do NOT make up facts not in the photo or notes.\n"
                    "- Return ONLY the final post text, ready to publish.")

                # Multimodal payload: text + image
                payload = {
                    "model": "meta/llama-4-maverick-17b-128e-instruct",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_text},
                                {"type": "image_url", "image_url": {"url": data_uri}}
                            ]
                        }
                    ],
                    "max_tokens": 2048,  # INCREASED for longer output
                    "temperature": 0.7,   # LOWER for more focused, professional tone
                    "top_p": 0.9,
                    "stream": False
                }

                headers = {
                    "Authorization": f"Bearer {nvidia_key}",
                    "Content-Type": "application/json"
                }

                response = requests.post(invoke_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                # Store text string output securely
                st.session_state.generated_post = result["choices"][0]["message"]["content"]
                
            except Exception as e:
                st.error(f"Error generating text via NVIDIA API: {e}")

# Trigger Step Two: Review Copy & Export to Buffer Modern Engine

if st.session_state.generated_post:
    st.markdown("---")
    st.subheader("Review and Refine Draft")
    
    final_post_text = st.text_area(
        "Edit your post content text here if needed:", 
        value=st.session_state.generated_post, 
        height=300) # INCREASED height for longer text

    if st.button("Push to Social Queue"):
        if not buffer_token or not buffer_profile_id:
            st.error("Please provide your Buffer Access Token and Channel ID inside the sidebar.")
        else:
            with st.spinner("📡 Transmitting draft to your Buffer dashboard..."):
                try:
                    url = "https://api.buffer.com"
                    headers = {
                        "Authorization": f"Bearer {buffer_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Build metadata dynamically based on selected platform
                    # Buffer only allows ONE metadata key per request
                    if platform == "Facebook":
                        metadata_block = """
                        metadata: {
                          facebook: {
                            type: post
                          }
                        }
                        """
                    elif platform == "Instagram":
                        metadata_block = """
                        metadata: {
                          instagram: {
                            type: post,
                            shouldShareToFeed: true
                          }
                        }
                        """
                    else:  # LinkedIn
                        metadata_block = """
                        metadata: {
                          linkedin: {}
                        }
                        """
                    
                    # Inject the correct metadata block into the mutation
                    query = f"""
                    mutation ($text: String!, $channelId: ChannelId!) {{
                      createPost(input: {{
                        text: $text,
                        channelId: $channelId,
                        mode: addToQueue,
                        schedulingType: automatic,
                        saveToDraft: true,
                        {metadata_block}
                      }}) {{
                        __typename
                        ... on PostActionSuccess {{
                          post {{
                            id
                          }}
                        }}
                        ... on MutationError {{
                          message
                        }}
                      }}
                    }}
                    """
                    
                    payload = {
                        "query": query,
                        "variables": {
                            "text": final_post_text,
                            "channelId": str(buffer_profile_id).strip()
                        }
                    }
                    
                    res = requests.post(url, headers=headers, json=payload)
                    
                    if res.status_code == 200:
                        res_json = res.json()
                        
                        if "errors" in res_json:
                            st.error(f"❌ Buffer Schema Error: {res_json['errors'][0]['message']}")
                        else:
                            result = res_json.get("data", {}).get("createPost", {})
                            if result.get("__typename") == "MutationError" or "message" in result:
                                st.error(f"❌ Buffer rejection: {result.get('message', 'Validation error')}")
                            else:
                                st.success(f"🎉 Successfully pushed to your Buffer {platform} Drafts queue!")
                    else:
                        st.error(f"❌ API Failure: Connection returned status code {res.status_code}. Response text: {res.text}")
                        
                except Exception as buffer_err:
                    st.error(f"❌ Network Request Error linking to Buffer: {buffer_err}")