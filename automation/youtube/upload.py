"""Upload a video to YouTube with the Data API, using a stored OAuth refresh token."""

import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def upload(video: Path, script: dict) -> str:
    creds = Credentials(
        None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    tags = list(dict.fromkeys(script["tags"] + ["perfume", "fragrance", "Newmoda", "Shorts"]))
    body = {
        "snippet": {
            "title": f"{script['title'][:90]} #Shorts",
            "description": f"{script['description']}\n\nVoiceover and script generated with AI.\n\n"
                           "#perfume #fragrance #Shorts",
            "tags": tags[:30],
            "categoryId": "26",  # Howto & Style
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": os.environ.get("YT_PRIVACY", "public"),
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
        },
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(video), mimetype="video/mp4", resumable=True),
    )
    response = None
    while response is None:
        _, response = request.next_chunk()
    return response["id"]
