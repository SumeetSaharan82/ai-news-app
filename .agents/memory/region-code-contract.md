---
name: Region code contract
description: Frontend sends short ISO codes; backend RSS layer uses full names — always map between them
---

## Rule
The frontend stores and sends short region codes (`in`, `us`, `gb`, `au`, `ca`, `de`). The RSS fetcher (`RSSFetcher`) uses full names (`india`, `us`, `gb`, `au`, `ca`, `de`). Always apply `REGION_CODE_MAP` before passing a region to `fetcher.fetch_all_sources()`.

**Why:** Without mapping, `in` is passed literally and no RSS source matches, producing an empty feed for Indian users.

**How to apply:** `REGION_CODE_MAP` is defined in `backend/api/v1/news.py`. Both the general `/news` endpoint and the `/news/personalized` endpoint now apply it. Any new endpoint that accepts a region param must do the same.
