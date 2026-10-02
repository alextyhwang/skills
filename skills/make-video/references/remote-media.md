# Remote media and Immich

Use the authorized server, account, album, and destination. Read credentials from session secrets/environment or secure storage; keep them out of logged commands, scripts, repos, and receipts. Keep authenticated requests on the intended host and inspect redirects before forwarding credentials.

## Ingest

Inspect current server API/version before implementation. Album responses may include counts without assets; use documented album-scoped asset search and paginate completely. Compare stable IDs/checksums with the local inventory. Download originals, verify supplied hashes, and preserve remote-ID-to-path mapping. When new clips arrive, reconcile and retrieve only missing/changed assets.

## Upload and share

Upload only when requested. Public sharing is a separate exposure decision: follow the requested audience, expiry, original-download access, and metadata visibility. Preserve old versions/shares unless replacement is authorized.

Before upload/retry, use available checksum/deduplication endpoints and prior receipts. Stream large files. Persist returned asset IDs immediately. After an uncertain upload, reconcile server assets by checksum before retrying. Persist share IDs immediately too; look up existing shares for that asset before another create.

Read back state after mutation. One Immich version ignored original-download permission during share creation; readback exposed this and a targeted update corrected the existing share. Treat this as version-dependent behavior to verify, not a reason to patch every share. Repeated verification failures must not cause unbounded duplicate uploads/shares.

Verify server checksum/size and processing readiness. For public links, use a fresh unauthenticated client to check page, asset access, playback, and requested original download. A range response can establish original byte size without a huge redownload. A browser preview may be transcoded/SDR while the original download remains HDR; distinguish these in the handoff. Keep private share keys and receipts outside public source control.
