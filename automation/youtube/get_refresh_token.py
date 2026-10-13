"""One-time, on your own computer: sign in to the channel's Google account and print a refresh token.

    pip install google-auth-oauthlib
    python get_refresh_token.py path/to/client_secret.json
"""

import sys

from google_auth_oauthlib.flow import InstalledAppFlow

from upload import SCOPES

flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
print("\nYT_CLIENT_ID     =", creds.client_id)
print("YT_CLIENT_SECRET =", creds.client_secret)
print("YT_REFRESH_TOKEN =", creds.refresh_token)
