# Execute within the approved scope

## Local checks before spending

Run `validate_plan.py` on the machine plan. Complete the separate creative reviews in the brief. Confirm the chosen model profile matches the provider/account the user authorized, the referenced files are the reviewed versions, all role bindings are ordered, and the batch fits the remaining budget.

Read-only analysis, local rendering and downloads of existing artifacts can proceed within the task's authorization. Paid generation requires the applicable creative approvals and recorded spending authority. Do not ask again if the user has already authorized the exact stage and limits. A new provider, changed story or excess budget is a new decision.

## Journal protocol

Use `job_journal.py` to reserve the worst-case approved charge before a request, record the task ID immediately, record generation success before download, and reconcile billing independently of artifact retrieval. This helper makes no network calls and cannot prevent a separate client from bypassing it. Executors must follow the protocol.

One journal is shared across the project's workers. The helper uses a local exclusive lock and atomic replacement. Network filesystems and distributed workers require a transactional shared store instead. Never split the same budget into several independent journals.

A prepared job may be submitted once. The transition to `submitting` must be recorded before the network call. On restart, `submitting` means outcome unknown. Reconcile through provider lookup; do not submit again just because the task ID was not saved. With provider-supported idempotency, reuse the original key. Otherwise wait for reliable evidence.

Keep unknown costs reserved. A known failure does not prove zero charge. Record zero only with evidence. Image work can be billed even when the download or local processing fails.

A changed prompt/reference/model is a new request hash and a new job version. Explicit user-authorized variations can intentionally reuse the same content hash, but require an override reason so accidental duplicates are distinguishable.

The request file used for hashing contains the prompt, parameters, account alias and ordered reference content hashes or stable asset IDs. Keep temporary signed URLs and credentials out of that canonical file; renewing a URL must not disguise a duplicate creative request. The executor must verify that the submitted request matches this record.

## Recovery

| Observed condition | Next step |
|---|---|
| Authentication rejected | Check credential status and service error details without exposing values |
| Rate limit | Back off according to the provider; retry only if non-acceptance is known |
| Submission timeout | Keep reservation, query or reconcile, no blind retry |
| Generation running | Continue polling the same task within documented limits |
| Generation succeeded, download failed | Retrieve existing output again, retain billed cost |
| Output creatively rejected | Record the defect and proposed repair scope before another paid job |
| Quoted amount unavailable | Obtain a documented maximum and authority; unknown never becomes zero |

## Privacy and release

Keep originals immutable. Store derivatives and logs in a project directory outside the skill source. Read credentials through the host's approved secret mechanism; never ask for them in chat. Keep secret-bearing raw responses private and restrict local access.

Use `python3 scripts/redact_export.py INPUT_JSON OUTPUT_JSON` for a sanitized structured copy before sharing logs. It removes credential fields and signed/query-token URLs. It does not audit arbitrary prose, binary files or unrecognized credentials. Inspect the copy and run the repository check before release. Never export whole configuration directories or `.env` files.

Costs must preserve native currencies and state whether they are quoted, estimated or billed. Convert only using an explicitly recorded rate and date. Report cost of retained outputs and discarded attempts separately; include shared upstream inputs in the retained output's production cost. Unknown amounts remain visible.
