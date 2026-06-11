"""
Upwork Proposal Agent
---------------------
Paste a job description → get:
  1. Polished proposal body (via Claude)
  2. Mermaid workflow diagram (via Claude)
  3. Google Doc saved to your Drive (via Google Drive API)

Setup:
  pip install anthropic google-auth google-auth-oauthlib google-api-python-client

Required env vars:
  ANTHROPIC_API_KEY      — your Anthropic API key
  GOOGLE_CREDENTIALS     — path to your Google OAuth2 credentials JSON file
                           (download from Google Cloud Console → APIs & Services → Credentials)
"""

import os
import json
import anthropic
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ── Config ────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GOOGLE_CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS", "credentials.json")
GOOGLE_TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# ── Claude client ─────────────────────────────────────────────────────────────

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def call_claude(system: str, user: str, max_tokens: int = 1024) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text.strip()


# ── Tools ─────────────────────────────────────────────────────────────────────

def generate_proposal(job_description: str) -> str:
    print("  [1/3] Generating proposal...")
    return call_claude(
        system=(
            "You are an expert Upwork freelancer proposal writer. "
            "Write a compelling, concise proposal body (250-350 words) based on the job description. "
            "Structure: 1) Hook addressing their specific need, 2) Relevant experience and proof, "
            "3) Your approach/solution, 4) Call to action. "
            "Be direct and specific. Output ONLY the proposal body — no subject line, no greeting."
        ),
        user=f"Job description:\n\n{job_description}",
        max_tokens=600,
    )


def generate_mermaid_diagram(job_description: str) -> str:
    print("  [2/3] Generating Mermaid diagram...")
    return call_claude(
        system=(
            "You are a technical diagram expert. "
            "Generate a Mermaid flowchart (graph TD) that visualises the workflow or project "
            "described in the job description. Include steps, decision points, and deliverables. "
            "Output ONLY valid Mermaid code — no explanation, no markdown fences, no backticks."
        ),
        user=f"Job description:\n\n{job_description}",
        max_tokens=400,
    )


def get_google_drive_service():
    creds = None
    if os.path.exists(GOOGLE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def save_to_google_doc(title: str, proposal: str, diagram: str, job_description: str) -> str:
    print("  [3/3] Saving to Google Drive...")
    service = get_google_drive_service()

    content = (
        f"UPWORK PROPOSAL\n"
        f"{'=' * 40}\n\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"JOB DESCRIPTION\n"
        f"{'-' * 40}\n"
        f"{job_description[:500]}{'...' if len(job_description) > 500 else ''}\n\n"
        f"PROPOSAL BODY\n"
        f"{'-' * 40}\n"
        f"{proposal}\n\n"
        f"MERMAID WORKFLOW DIAGRAM\n"
        f"{'-' * 40}\n"
        f"{diagram}\n"
    )

    # Upload as plain text → auto-converts to Google Doc
    file_metadata = {"name": title, "mimeType": "application/vnd.google-apps.document"}
    from googleapiclient.http import MediaInMemoryUpload
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink",
    ).execute()

    return file.get("webViewLink", f"https://docs.google.com/document/d/{file['id']}")


# ── Agent ─────────────────────────────────────────────────────────────────────

def run_agent(job_description: str) -> dict:
    """
    Main agent entry point.
    Pass a job description string → returns dict with proposal, diagram, and doc URL.
    """
    print("\n🚀 Upwork Proposal Agent starting...\n")

    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    proposal = generate_proposal(job_description)
    diagram = generate_mermaid_diagram(job_description)

    title = f"Upwork Proposal — {datetime.now().strftime('%b %d, %Y')}"
    doc_url = save_to_google_doc(title, proposal, diagram, job_description)

    result = {
        "proposal": proposal,
        "mermaid_diagram": diagram,
        "google_doc_url": doc_url,
        "doc_title": title,
    }

    print("\n✅ Done!\n")
    print(f"  Google Doc: {doc_url}\n")
    print("─" * 60)
    print("PROPOSAL BODY\n")
    print(proposal)
    print("\n" + "─" * 60)
    print("MERMAID DIAGRAM\n")
    print(diagram)
    print("─" * 60)

    return result


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Upwork Proposal Agent")
    print("Paste your job description below. Press Enter twice when done.\n")

    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)

    job_description = "\n".join(lines).strip()
    run_agent(job_description)
