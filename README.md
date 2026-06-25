# Upwork Proposal Agent

Paste an Upwork job description → get a tailored, ready-to-send proposal in
under 2 minutes (down from ~20 minutes by hand).

For each job posting, the agent:

1. **Drafts a polished proposal body** with the Claude API — tone-matched to
   the job post, with relevant experience pulled in
2. **Generates a Mermaid workflow diagram** illustrating the proposed
   solution, so the client sees the plan at a glance
3. **Saves everything to a Google Doc** in your Drive via the Google Drive
   API, ready to copy into Upwork

## Setup

```bash
pip install anthropic google-auth google-auth-oauthlib google-api-python-client
```

Required environment variables:

| Variable | What |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `GOOGLE_CREDENTIALS` | Path to your Google OAuth2 credentials JSON (Google Cloud Console → APIs & Services → Credentials) |

## Usage

```bash
python upwork_agent.py
```

Paste the job description when prompted. The first run opens a browser window
for Google OAuth; the token is cached locally afterwards.

## Stack

Python · Claude API · Google Docs/Drive API

---

Built by [Anup Katuwal](https://anupkat.com.np) — data analyst & automation
engineer. [More projects →](https://github.com/anupkatuwal)

## 🔗 Portfolio

Featured on my portfolio: **[https://anup-katuwal.com.np/projects/upwork-agent](https://anup-katuwal.com.np/projects/upwork-agent)**  
More of my work → [anup-katuwal.com.np](https://anup-katuwal.com.np)
