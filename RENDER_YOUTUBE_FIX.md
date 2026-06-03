# Render YouTube Fix

Render servers are hosted on datacenter IPs. YouTube often blocks anonymous
audio downloads from those IPs, even when the app works locally.

This app supports authenticated YouTube requests through a Render secret:
`YOUTUBE_COOKIES_B64`.

## Set Up

1. Open YouTube in your browser while signed in.
2. Export YouTube cookies in Netscape `cookies.txt` format using a browser
   extension such as "Get cookies.txt LOCALLY".
3. Base64 encode the file.

   PowerShell:

   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("cookies.txt"))
   ```

4. In Render, open your service, then go to Environment.
5. Add this secret:

   ```text
   YOUTUBE_COOKIES_B64=<the base64 output>
   ```

6. Redeploy the service.

Do not commit `cookies.txt` to GitHub. Cookies are private account secrets.

## What This Changes

With `YOUTUBE_COOKIES_B64` set, the deployed app will:

- try normal YouTube captions first
- try `yt-dlp` subtitle metadata with your cookies
- if captions are unavailable, try audio download with your cookies
- transcribe the downloaded audio with Groq Whisper

Without cookies, Render can still process videos that expose captions, but
YouTube may block audio downloads for videos without usable captions.
