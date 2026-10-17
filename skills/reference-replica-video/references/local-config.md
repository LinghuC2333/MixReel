# Local provider configuration and credentials

Use this reference when installing the skill or selecting paid services. Configuration is private and stays outside both the source checkout and film project exports. Never ask the user to paste a key into a chat or publish it to a document.

## Default files

- `~/.config/reference-replica-video/providers.json` records image generation, image editing and video generation profiles. Each role has an actual billed provider, model, endpoint allowlist and credential reference. These roles may share one service or use three different services.
- `~/.config/reference-replica-video/credentials.json` holds local plaintext credential values under named keys. On macOS/Linux the directory must be mode 700 and both files mode 600. This is file permission protection, not encryption. A host secret store or environment injection is preferable when already available.

Create blank files with `python3 scripts/init_config.py`, resolving that script from the installed skill. The initializer imports no keys, makes no network calls and preserves existing files. It does not load credentials into tools or configure a provider client. On Windows, use operating-system access controls to restrict these files to the user; POSIX mode checks are not available there.

Templates are [provider profiles](../assets/providers.example.json) and [empty credential slots](../assets/credentials.example.json). A custom directory can be supplied with `--directory`; record only its location, never its contents, in private project configuration. Do not copy real files back over public templates.

## Credential resolution contract for the host

Use exactly the profile chosen for the operation. Do not silently use an image reseller for video because it offers the same model. A changed provider/account requires the user's authorization; the selected profile alone grants no spending permission.

`auth.source` chooses one of these mechanisms.

- `credentials_file` reads the value at `keys[auth.name]` in the adjacent private credentials file.
- `env` reads exactly the named environment variable within the host process.
- `host_secret` delegates the name to the existing host secret manager.
- `host_tool` uses a tool whose existing authentication is managed by the host; no extra key file is required.

These fields are a configuration convention for the assistant or future adapter, not an implemented universal credential loader. When using an existing tool, verify that its real provider/account matches the selected profile. If it cannot accept this convention, configure it through its documented method and record only the credential source name.

Read only the selected credential inside the executing client. Do not dump the file, shell environment, Authorization headers, or raw authenticated requests into model context, logs or the journal. Do not put values into command-line arguments. Pass them through the host's protected secret mechanism or load them inside the client process.

Before a credential is transmitted, verify the HTTPS endpoint against `allowed_hosts` and the user's intended service. An empty key, endpoint or allowlist means unconfigured, not permission to guess. Do not forward authentication to artifact download hosts or cross-host redirects. Current documentation establishes authentication format, actual supported operations and billing behavior; see [providers](providers.md).

Keep prices, reference-mode capabilities and request schemas in the private project's verified provider record. A populated profile is not proof of connectivity or permission to test a billable endpoint. Record only service names, model IDs, credential reference names, redacted results and known costs in handoffs.
