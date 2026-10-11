---
name: youtube
description: Ingest a YouTube URL, pull subtitles and metadata with yt-dlp, verify claims with web research, and write transcript and research markdown artifacts under youtube/. Use when the user says `/youtube <url>`, "youtube knowledge extract", "pull this youtube and extract", "extract from youtube", or wants video claims captured and cross-checked.
---


# YouTube Knowledge Extract

Use this skill to ingest one YouTube video, extract claims from its subtitle track, and cross-check those claims against primary sources on the web. Deliver **two separate** markdown documents:

- `transcript-extract.md` — video/subtitle-derived claims only.
- `web-research.md` — external web evidence only.

This separation is mandatory so readers can distinguish creator claims from verified facts.

## Input

User provides a single YouTube URL, such as:

- `https://youtu.be/<id>`
- `https://www.youtube.com/watch?v=<id>`
- `https://www.youtube.com/shorts/<id>`

If URL is missing, ask:

```text
Please provide a YouTube URL.
```

## Flow

1. Validate input.
2. Pull subtitles and metadata with `yt-dlp`.
3. Parse metadata.
4. Create artifact directory.
5. Write `transcript-extract.md`.
6. Do web verification and write `web-research.md`.
7. Present concise handoff with artifact paths.

Do **not** mix transcript-derived claims into `web-research.md`. Do **not** mix web-derived claims into `transcript-extract.md`.

## Step 1: Input Handling

1. Validate URL shape. It must contain one of:
   - `youtu.be/`
   - `youtube.com/watch`
   - `youtube.com/shorts/`

   If shape does not match, stop and ask user to confirm URL.

2. Extract 11-character video ID from:
   - path segment after `youtu.be/`
   - `v` query parameter
   - path segment after `youtube.com/shorts/`

   Hold as `VIDEO_ID` for filename suffixing.

## Step 2: Pull Subtitles and Metadata with `yt-dlp`

1. Pre-flight: detect OS, then confirm `yt-dlp` exists before creating temp or artifact directories.

   Detect platform first:

   ```bash
   uname -s
   ```

   Treat results as:

   - `Darwin` → macOS
   - `Linux` → Linux
   - `MINGW*`, `MSYS*`, `CYGWIN*`, or PowerShell `$env:OS -eq "Windows_NT"` → Windows

   If shell/platform detection is unclear, ask user which OS they are running before offering install commands.

2. Check for `yt-dlp`:

   ```bash
   command -v yt-dlp
   ```

   On Windows PowerShell, use:

   ```powershell
   Get-Command yt-dlp -ErrorAction SilentlyContinue
   ```

   If missing, do **not** create temp or artifact directories. Ask before installing anything. Offer OS-appropriate options only.

   macOS:

   ```text
   yt-dlp not found. I can install it and needed Python tooling, but need approval first.

   Options:
   1. Install with Homebrew: brew install yt-dlp
   2. Install with pipx: python3 -m pip install --user pipx && python3 -m pipx ensurepath && pipx install yt-dlp
   3. Stop here; you will install it manually.

   Reply with 1, 2, or 3.
   ```

   Windows:

   ```text
   yt-dlp not found. I can install it and needed tooling, but need approval first.

   Options:
   1. Install with winget: winget install --id yt-dlp.yt-dlp -e
   2. Install with pipx: py -m pip install --user pipx && py -m pipx ensurepath && pipx install yt-dlp
   3. Stop here; you will install it manually.

   Reply with 1, 2, or 3.
   ```

   Linux:

   ```text
   yt-dlp not found. I can install it and needed Python tooling, but need approval first.

   Options:
   1. Install with pipx: python3 -m pip install --user pipx && python3 -m pipx ensurepath && pipx install yt-dlp
   2. Stop here; you will install it manually.

   Reply with 1 or 2.
   ```

   Never install `yt-dlp`, Homebrew packages, Python packages, or dependencies without explicit user approval.

3. If user approves installation, use the selected OS-appropriate install method, then verify:

   ```bash
   command -v yt-dlp && yt-dlp --version
   ```

   On Windows PowerShell, verify with:

   ```powershell
   Get-Command yt-dlp -ErrorAction Stop
   yt-dlp --version
   ```

   If install succeeds, continue to subtitle pull. If install fails, report stderr and stop without creating artifact directory.

4. Stage into temp directory so failed pull leaves no half-written artifact directory.

   macOS/Linux shell:

   ```bash
   URL="<youtube-url>"
   TMPDIR="$(mktemp -d -t yt-extract-XXXXXX)"
   yt-dlp \
     --skip-download \
     --write-auto-sub \
     --write-sub \
     --sub-lang en \
     --sub-format vtt \
     --write-info-json \
     -o "${TMPDIR}/%(title)s [%(id)s].%(ext)s" \
     "$URL"
   ```

   Windows PowerShell:

   ```powershell
   $Url = "<youtube-url>"
   $TmpDir = New-Item -ItemType Directory -Path ([System.IO.Path]::Combine($env:TEMP, "yt-extract-$([guid]::NewGuid())"))
   yt-dlp `
     --skip-download `
     --write-auto-sub `
     --write-sub `
     --sub-lang en `
     --sub-format vtt `
     --write-info-json `
     -o "$($TmpDir.FullName)\%(title)s [%(id)s].%(ext)s" `
     "$Url"
   ```

   Mandatory exact flags:

   ```text
   --skip-download --write-auto-sub --write-sub --sub-lang en --sub-format vtt --write-info-json
   ```

   - `--skip-download` keeps it subtitles-only. No media file.
   - `--write-auto-sub` provides fallback when no human-uploaded English subtitles exist.
   - `--sub-lang en --sub-format vtt` constrains to English VTT.

5. Handle pull failures:

   - Age-restricted, region-blocked, or private: messages like `ERROR: Sign in to confirm`, `Video unavailable`, `is not available`. Delete the temp directory, report reason, stop.
   - No English subtitles: if no `.en.vtt` exists in the temp directory after successful pull, delete the temp directory, report unavailable, stop. Audio transcription fallback is out of scope unless user explicitly asks.
   - Network, DNS, or transient errors: report stderr verbatim, delete the temp directory, stop.

6. Locate files in the temp directory:

   - One `.info.json`.
   - One English `.en.vtt`. With both `--write-sub` and `--write-auto-sub`, pick whichever English VTT exists. Do not assume both exist.

## Step 3: Parse Metadata

Run Python over `.info.json` and hold fixed fields for both docs. Description is truncated to 500 characters.

macOS/Linux shell:

```bash
python3 - <<'PY' "${TMPDIR}"/*.info.json
import json, sys
m = json.load(open(sys.argv[1]))
desc = (m.get("description") or "")[:500]
print(f"title:        {m.get('title')}")
print(f"uploader:     {m.get('uploader')}")
print(f"channel:      {m.get('channel')}")
print(f"upload_date:  {m.get('upload_date')}")
print(f"duration:     {m.get('duration')}")
print(f"view_count:   {m.get('view_count')}")
print(f"like_count:   {m.get('like_count')}")
print(f"description:  {desc}")
PY
```

Windows PowerShell:

```powershell
$InfoJson = Get-ChildItem -Path $TmpDir.FullName -Filter *.info.json | Select-Object -First 1
@'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
desc = (m.get("description") or "")[:500]
print(f"title:        {m.get('title')}")
print(f"uploader:     {m.get('uploader')}")
print(f"channel:      {m.get('channel')}")
print(f"upload_date:  {m.get('upload_date')}")
print(f"duration:     {m.get('duration')}")
print(f"view_count:   {m.get('view_count')}")
print(f"like_count:   {m.get('like_count')}")
print(f"description:  {desc}")
'@ | py - $InfoJson.FullName
```

## Step 4: Create Artifact Directory

After pull and metadata parse succeed, compute final output path and move temp files.

1. Compute slug from `info.json.title`:
   - Lowercase.
   - Replace any run of non-alphanumerics with `-`.
   - Strip leading/trailing `-`.
   - Cap around 60 characters.
   - Suffix with `-<VIDEO_ID>`.

2. Create `youtube/` at workspace root if it does not already exist, then create video-specific layout:

   ```text
   youtube/<slug>-<videoId>/
   ├── transcript-extract.md
   ├── web-research.md
   └── raw/
       ├── <title>.en.vtt
       └── <title>.info.json
   ```

3. Create directories and move pulled files. Quote every path because titles may contain spaces and brackets.

   macOS/Linux shell:

   ```bash
   OUT_DIR="youtube/<slug>-<VIDEO_ID>"
   mkdir -p "${OUT_DIR}/raw"
   mv "${TMPDIR}"/*.en.vtt    "${OUT_DIR}/raw/"
   mv "${TMPDIR}"/*.info.json "${OUT_DIR}/raw/"
   rm -rf "${TMPDIR}"
   ```

   Windows PowerShell:

   ```powershell
   $OutDir = "youtube\<slug>-<VIDEO_ID>"
   New-Item -ItemType Directory -Force -Path "$OutDir\raw" | Out-Null
   Move-Item -Path (Join-Path $TmpDir.FullName "*.en.vtt") -Destination "$OutDir\raw"
   Move-Item -Path (Join-Path $TmpDir.FullName "*.info.json") -Destination "$OutDir\raw"
   Remove-Item -Recurse -Force $TmpDir.FullName
   ```

## Step 5: Write `transcript-extract.md`

Read English VTT from `raw/` and produce transcript-grounded knowledge doc. This file represents creator claims only. No external verification. No primary-source corrections.

Required sections, in order:

```markdown
---
date: {current ISO timestamp}
author: {workspace user or author if known}
source: youtube
url: {original URL}
video_id: {VIDEO_ID}
title: {info.json title}
channel: {info.json channel}
uploader: {info.json uploader}
upload_date: {info.json upload_date}
duration_seconds: {info.json duration}
view_count: {info.json view_count}
like_count: {info.json like_count}
status: transcript-only
last_updated: {same ISO timestamp}
last_updated_by: {author}
---

# Transcript Extract: {title}

## Source Posture
{One paragraph framing what this video is. Call out reach signals: view count, like count, channel size if known. For low-view and/or single-creator videos, state: "This is creator interpretation, not a primary source — claims below are recorded as the creator presented them and require independent verification (see web-research.md)."}

## Core Claim
{Single load-bearing claim in one or two sentences.}

## Mechanics
{How video says thing works. Stay faithful to video framing even if it sounds wrong; corrections belong in web-research.md.}

## Architecture
{System shape, diagrams in text form, named modules/services/models. Bullet form.}

## When It Applies
{Use cases, workloads, scenarios video says this is for. Include what video says it is not for, if mentioned.}

## Builder Takeaway
{What developer could build, try, or measure after watching. One short paragraph.}

## Description (truncated)
{First 500 chars of info.json description, verbatim.}
```

Rules:

- Quote transcript wording where exact phrasing matters.
- Do **not** cite external sources.
- Flag low-reach or single-creator videos in `## Source Posture`.

## Step 6: Write `web-research.md`

Cross-check transcript extract against open web. This file represents external evidence only. Every non-trivial claim ends with markdown hyperlink.

1. Derive 3–5 search queries from transcript extract:
   - Named feature(s) video introduces.
   - Core marketing claim.
   - Upload date plus feature name.
   - Vendor/product name plus release notes/blog/docs.

2. Use available web tools:
   - Prefer this workspace's browser search when search results are needed.
   - Use `web_fetch` for direct URL fetches when URL is known and reachable.
   - Use browser screenshots only if visual evidence matters.

3. Capture top 3–5 results per query in working state:
   - title
   - URL
   - one-line snippet or relevance note

4. Fetch most authoritative sources per topic:
   - vendor blogs
   - official product pages
   - release notes
   - docs
   - original GitHub repositories
   - standards bodies or primary announcements

5. Handle source failures:
   - 403 forbidden: do not retry same URL repeatedly. Fall back to highest-signal secondary coverage and note gap.
   - Paywall/login wall: note it, fall back to secondary.
   - 404/link rot: drop source and search replacement.
   - Timeout: retry once with slight URL variant, then drop.

6. Cross-reference transcript against web evidence. Answer explicitly:
   - What did video get right?
   - What did video oversell?
   - What did video omit?

Required sections, in order:

```markdown
---
date: {current ISO timestamp}
author: {workspace user or author if known}
source: web-verification
video_url: {original URL}
video_id: {VIDEO_ID}
topic: "{Feature / claim being verified}"
status: complete
last_updated: {same ISO timestamp}
last_updated_by: {author}
---

# Web Research: {Feature / claim being verified}

## Verification Question
{One sentence stating what was verified against external sources.}

## Verdict
**Real / Partially real / Overstated / Fabricated:** {choose one}
{One paragraph. Lead with what primary sources confirm, then what video oversold, then what it omitted.}

## What the Video Got Right
- {Claim} — confirmed by [Source title](url)

## What the Video Oversold
- {Marketing claim} — primary sources say {what they actually say} — [Source title](url)

## What the Video Omitted
- {Material fact} — [Source title](url)

## Primary Sources Attempted
- `https://example.com/primary-source` — fetched-ok
- `https://example.com/blocked-source` — 403-blocked, fell back to secondary

## Sources
- [Source title 1](https://...)
- [Source title 2](https://...)
```

Rules:

- Every non-trivial claim ends with markdown hyperlink.
- No transcript paraphrasing without external source. If only video says it, keep it in `transcript-extract.md`.
- `## Sources` is flat bibliography. Duplicate inline links are fine.

## Step 7: Present and Hand Off

Final response must be terse and include exact workspace-relative paths:

```text
Pulled: {title}
{channel} · {duration_seconds}s · {view_count} views · uploaded {upload_date}

Wrote:
- youtube/{slug}/transcript-extract.md
- youtube/{slug}/web-research.md

Raw VTT + info.json under youtube/{slug}/raw/.

Verdict: {Real / Partially real / Overstated / Fabricated}
Primary sources unreachable: {N} (see web-research.md → Primary Sources Attempted)
```

## Important Notes

- Two artifacts, hard separation. Transcript-derived claims only in `transcript-extract.md`; web-derived claims only in `web-research.md`.
- Read-only network posture. Never upload, post, authenticate, or download video media. `yt-dlp` uses `--skip-download`.
- Create `youtube/` if missing; only writes go under `youtube/` at workspace root.
- Stage pull in an OS temp directory (`mktemp -d` on macOS/Linux, `$env:TEMP` with a GUID folder on Windows); never write directly into `youtube/` before pull succeeds.
- Idempotent reruns use `<slug>-<VIDEO_ID>` suffix.
- English only, v1. Cross-language subtitle support and audio transcription fallback are out of scope unless user asks.
- Critical ordering:
  - Always detect OS and check `yt-dlp` exists before staging pull.
  - If missing, always ask before installing `yt-dlp` or dependencies.
  - Offer only OS-appropriate install commands.
  - Always stage into an OS temp directory first.
  - Always write `transcript-extract.md` with no external citations.
  - Always write `web-research.md` with cited external claims.
  - Never mix transcript-only and web-verified claims in same file.
