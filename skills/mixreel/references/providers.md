# Replaceable provider contract

The host may expose image/video tools, a connector, a documented CLI or a configured API. This package does not bundle a paid provider client. Use available capabilities through a verified project-local profile. The same creative plan must survive changing that profile.

Read [local configuration](local-config.md) for private profiles, empty templates and credential storage. This package never ships real credential values.

## Before the first paid request

Read current official documentation or the host's documented integration. Record the source URL or local document hash and verification date. Verify actual gateway behavior separately from upstream model claims. User-specified provider and account are authoritative; do not replace them with a reseller exposing the same model name.

The profile records the following.

| Field | Meaning |
|---|---|
| Provider and model | Actual billed service, account alias without credentials, model identifier |
| Operations | Generate, edit, region-edit, animate, query, download and quote as supported |
| Conditioning | Accepted image/video/audio inputs and roles, ordering, count/duration limits, strict vs soft constraints, incompatible combinations and generated-sound behavior |
| Parameters | Supported duration range/increments, multi-shot support, size, aspect ratio, quality, count and accepted prompt format |
| Region edit | Mask polarity, alpha semantics and size requirements |
| Billing | Quote mechanism, currency, minimum billable duration and rounding, per-request vs per-second basis, estimate vs actual, chargeable failures and cancellation behavior |
| Recovery | Task ID, lookup and idempotency support, timeouts, rate limits and concurrency |
| Authorization | Credential source name and endpoint allowlist; values stay in the host's secret store |
| Output | Status states, artifact fields, expiry and download verification |

Unknown fields remain unknown. Unsupported parameters are omitted with their creative impact reported. A documentation example is not proof that a gateway forwards every parameter.

## Operations and local journal

Before `submit`, create a journal reservation with the approved request hash, provider, model, operation, quote and maximum authorized charge. Count batch members and trials individually. Quotes are read-only only when verified as such. An undocumented dry-run flag must never be tested on a live paid endpoint as if it were safe.

An adapter can be a host tool invocation or a project script. Its observable contract is the same.

- `quote` returns amount, currency, basis and expiry, or explicitly unavailable.
- `submit` returns a stable task ID; a timeout without evidence of rejection returns unknown outcome.
- `query` accepts the existing ID and reports status without submitting a new job.
- `download` retrieves an existing artifact and verifies it without regeneration.
- `reconcile` establishes the known cost or retains an estimated/unknown value.

No automatic paid fallback. A documented non-acceptance can permit retry within the same authorization. An unknown submission outcome stays reserved until lookup or support establishes what happened. Failed output download is a download retry, never a generation retry.

## Provider-specific notes

Keep parameter mappings and prompt formats in the private project's `providers/` directory until verified and sanitized for publication. A provider-specific reusable module belongs in an optional adapter package, not the core instructions. Do not import historical prices or fixed concurrency limits as global facts.

For bundled prompt writing, select [Seedance 2](../../mixreel-video-plan/references/prompt-seedance-2.md) or [MiniMax H3](../../mixreel-video-plan/references/prompt-minimax-h3.md) after verifying the endpoint. These are authoring rules, not API clients.

For a host that exposes an existing specialized prompt skill, read it only after the model is selected and preserve the approved scene. If that skill changes the shot plan, resolve the conflict explicitly. Its existence does not authorize generation.

Public adapter contributions require official-source links, dated capability evidence, mocked request/response tests, safe quote behavior and ambiguous-submission recovery. Never ship credentials, signed URLs or customer assets as examples.
