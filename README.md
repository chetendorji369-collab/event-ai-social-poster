# 🎯 Event AI Social Poster

Generate professional social media posts from event photos using **NVIDIA Llama 4 Maverick** and queue them directly to **Buffer**.

<img width="1068" height="501" alt="image" src="https://github.com/user-attachments/assets/7a841130-2273-4aa7-bf64-837fd1ac8db0" />

## ✨ Features

- 📸 Upload event photos
- 🤖 AI analyzes image + your notes to write posts
- 📋 One-click publish to Buffer (Facebook, Instagram, LinkedIn)
- ✏️ Edit drafts before posting

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/chetendorji369-collab/event-ai-social-poster.git
cd event-ai-social-poster

```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Get API Keys
NVIDIA NIM → Generate API key for Llama 4 Maverick

Buffer → Get Access Token & Channel ID

### 4. Run the app
```bash
streamlit run App.py

```
🔑 Configuration
Enter API keys in the Streamlit sidebar, or create .streamlit/secrets.toml:
```bash
[nvidia]
api_key = "your-nvidia-key"

[buffer]
access_token = "your-buffer-token"
profile_id = "your-channel-id"
```
🛠️ Tech Stack

Frontend: Streamlit

AI Model: NVIDIA Llama 4 Maverick (multimodal)

Publishing: Buffer GraphQL API

Language: Python 3.10+

📄 License

MIT License - feel free to use and modify!


