# CFManager — Code Review & Improvement Report

**Date:** 2026-06-17
**Reviewed version:** 0.3.0 (working tree, with uncommitted changes)
**Scope:** Full source tree (`src/cfmanager`), tests, packaging.

---

## 1. Executive Summary

CFManager is a well-structured Cloudflare CLI + TUI built on a clean three-layer
architecture (`core` → `services` → `cli`/`tui`). The separation of concerns is
good, error wrapping is consistent in spirit, and the TUI is thoughtfully built
on Textual. The codebase is approachable and the README/Makefile are solid.

The main issues are: **a broken test suite in the current working tree**, a
**config-precedence bug that contradicts its own documentation**, a **latent
Cloudflare API bug around proxied DNS records**, and a **large amount of
sync/async duplication** that inflates maintenance cost. None are architectural
dead-ends; all are fixable incrementally.

**Overall grade: B+ (solid foundation, a few real bugs, high duplication).**

| Area | Assessment |
| --- | --- |
| Architecture & layering | Strong |
| Correctness | 4 failing tests + 2 latent bugs |
| Consistency | Mixed (error-handling patterns diverge) |
| Test coverage | Good breadth, brittle async mocks |
| Security | Reasonable for a CLI; minor notes |
| Maintainability | Hurt by ~50% sync/async duplication |

---

## 2. Critical / Correctness Findings

### 2.1 The test suite is currently red (4 failures) 🔴
Running the suite on the working tree yields **4 failed, 67 passed**:

```
FAILED tests/test_services/test_r2.py::test_list_buckets_async
FAILED tests/test_services/test_ssl.py::test_get_ssl_setting
FAILED tests/test_services/test_ssl.py::test_set_ssl_mode
FAILED tests/test_services/test_ssl.py::test_get_ssl_setting_async
```

Root cause: the uncommitted changes in [src/cfmanager/services/ssl.py](src/cfmanager/services/ssl.py)
switched the SDK call surface from `zones.settings.ssl.get(...)` /
`zones.settings.ssl.edit(...)` to `zones.settings.get("ssl", ...)` /
`zones.settings.edit("ssl", ...)`, but [tests/test_services/test_ssl.py](tests/test_services/test_ssl.py)
still mocks the old surface. Similarly [src/cfmanager/services/r2.py](src/cfmanager/services/r2.py#L179)
changed `async for` → `for` in `list_buckets_async`, but the test still feeds an
async-only iterator.

**Action:** update the tests to match the new SDK surface before committing. The
service changes look correct for `cloudflare>=5.x`; the tests are the stale half.
This must be fixed or CI ([the Tests badge](README.md)) will break.

### 2.2 Config precedence contradicts its documented behavior 🔴
[src/cfmanager/core/config.py:11-18](src/cfmanager/core/config.py#L11-L18) documents:

```
# 1. ~/.cfmanager/.env  (user-level)
# 2. .env in cwd        (project-level override)   ← claims to override #1
```

But both are loaded with `load_dotenv()`, whose default is `override=False`
(verified). The user-level file is loaded *first*, so it wins; the cwd `.env`
loaded second **cannot** override it. The actual precedence is the **opposite**
of the comment — a project-local `.env` is silently ignored if the user-level
file sets the same key.

**Action:** either load cwd `.env` first, or pass `override=True` on the cwd
call, to match the documented "last wins" intent. Add a test for precedence.

### 2.3 Proxied DNS records with a non-Auto TTL will be rejected 🟠
Cloudflare requires `ttl=1` (Auto) whenever `proxied=true`. Both
[create_dns_record](src/cfmanager/services/dns.py#L55) and the TUI form default
`ttl=3600` and let the user set `proxied=True` independently. The API will
reject `proxied=true, ttl=3600` with an opaque error. There is no client-side
guard or coercion.

**Action:** when `proxied` is true, coerce `ttl` to `1` (or validate and emit a
clear message). Apply in `_validate_record` / the service layer so both CLI and
TUI benefit.

### 2.4 Account selection silently picks the first account 🟠
[CloudflareClient.get_account_id](src/cfmanager/core/client.py#L43) does
`self._account_id = accounts[0].id`. Tokens scoped to multiple accounts will
operate on whichever account Cloudflare returns first, with no way to choose.

**Action:** honor a `CLOUDFLARE_ACCOUNT_ID` env var and/or a global
`--account` option; fall back to `accounts[0]` only when unambiguous.

### 2.5 Minor correctness / hygiene
- [tui/app.py:71](src/cfmanager/tui/app.py#L71) reaches into `self.cf_client._account_name`
  (private). Add a public `account_name` property on `CloudflareClient`.
- [tui/app.py:74](src/cfmanager/tui/app.py#L74) formats the error as raw `{e}`
  while the rest of the TUI uses `format_error(e)`. Make it consistent.
- The 6-way `if/elif` ladder in [navigate_to](src/cfmanager/tui/app.py#L78-L105)
  repeats the same cache-TTL pattern per screen. Drive it from a dict
  (`{screen: refresh_coro_name}`) to remove the duplication and the risk of one
  branch drifting.

---

## 3. Design & Maintainability

### 3.1 Sync/async duplication (~50% of the services layer)
Every service method exists twice — a sync version for the CLI and a near-
identical `*_async` version for the TUI — differing only by `await` and the
client attribute. Example: [dns.py](src/cfmanager/services/dns.py) is 242 lines,
roughly half of which is mechanical duplication. The same is true for zones,
ssl, r2, pages, and loadbalancers.

**Options (in order of effort):**
1. **Write async-only services**, and have the CLI call them via
   `asyncio.run(...)`. Eliminates the duplicate sync methods entirely.
2. Extract the field-mapping into shared serializers
   (`_serialize_zone(obj) -> dict`) so sync/async paths share the dict-building.
3. At minimum, factor the repeated try/except/log/wrap boilerplate into a
   decorator: `@cf_api("listing zones")`. This alone removes ~200 lines and
   guarantees uniform error wrapping.

### 3.2 Inconsistent exception handling across services
- `zones.py` and `dns.py` catch a bare `except Exception` and wrap.
- `r2.py`, `ssl.py`, `pages.py`, `loadbalancers.py` first re-raise
  `(APIError, ValidationError)` and then catch `Exception`.

The second pattern is the better one (it avoids double-wrapping domain errors).
Standardize on it everywhere — ideally via the decorator in 3.1.

### 3.3 Repeated dict-construction blocks
The `{"id": ..., "name": ..., "status": ...}` builders are duplicated between
list/get and sync/async in every service. Centralizing them (3.1 option 2) keeps
the field set in one place and prevents the kind of drift seen between
`list_deployments` and `list_deployments_async` in
[pages.py:80-83 vs 178-184](src/cfmanager/services/pages.py#L80-L84) (one used a
fragile `and` expression that was later cleaned up in the async variant only).

### 3.4 Smaller structural notes
- `format_error` re-imports `cloudflare` on every call
  ([core/errors.py:14](src/cfmanager/core/errors.py#L14)). Functionally fine, but
  a module-level import guarded by a flag would be cleaner.
- Services are re-instantiated on every CLI invocation and every TUI keypress
  (`DNSService(self.app.cf_client)`). Cheap today, but a per-view cached instance
  would be tidier.
- `OutputFormatter` ([core/output.py](src/cfmanager/core/output.py)) silently
  drops keys not in `keys` for CSV (`extrasaction="ignore"`) — fine, but worth a
  comment so it isn't mistaken for a bug.

---

## 4. Security Review

No high-severity issues. Notes:

- **Token at rest:** stored plaintext in `~/.cfmanager/.env` with `0600` and the
  dir `0700` ([core/config.py:46-57](src/cfmanager/core/config.py#L46-L57)).
  Acceptable for a developer CLI. Consider an optional OS-keyring backend
  (`keyring`) for users who want it.
- **R2 credentials:** only read from env, never persisted — good, but
  inconsistent with the persisted CF token. Document the asymmetry, or offer to
  persist both.
- **Logging:** the API token is never logged; DEBUG logs include zone/account IDs
  only. Good. Keep the token out of any future `cfm config show --raw`.
- **TUI token entry** is password-masked ([dialogs.py:46](src/cfmanager/tui/widgets/dialogs.py#L46)) — good.
- **Token placeholder** `cf_xxxxxxxxxx` ([dialogs.py:46](src/cfmanager/tui/widgets/dialogs.py#L46))
  is misleading — Cloudflare API tokens have no `cf_` prefix. Cosmetic.

---

## 5. Testing

- **Breadth is good:** services and CLI each have a test module.
- **Async mocks are brittle:** hand-rolled `__aiter__/__anext__` classes and
  per-attribute `AsyncMock` assignment break whenever the SDK call surface
  changes (exactly what happened in §2.1). Consider a small helper/fixture that
  builds async-iterable mocks, and a `respx`-based layer (already a dev dep) for
  end-to-end HTTP-level tests that don't couple to the SDK's method names.
- **Gaps:** no test for config precedence (§2.2), no test for the proxied/TTL
  rule (§2.3), and the TUI has only `test_app.py`. Textual ships a `Pilot`
  test harness — worth adding a couple of key-driven flows (navigate, open
  dialog, cancel).
- **Environment friction:** the venv has broken shebangs (documented in project
  memory). Worth a `make test` note or a fresh `uv sync` to make `pytest`
  runnable directly.

---

## 6. Packaging & Tooling

- `requires-python = ">=3.12"` is aggressive and limits adoption. Nothing in the
  code obviously needs 3.12; lowering to 3.10/3.11 would widen the audience.
- **`boto3` is a hard dependency** (~50 MB) but only used for R2 *object*
  operations. Move it to an optional extra: `pip install cfmanager[r2]`, and the
  code already degrades gracefully when `boto3 is None`
  ([r2.py:27](src/cfmanager/services/r2.py#L27)). This shrinks the default
  install and the PyInstaller binary substantially.
- Ruff is configured well (`E,F,W,I`). Consider adding `B` (bugbear) and `UP`
  (pyupgrade) for extra signal.

---

## 7. Proposed New Features

Grouped by value/effort. The highest-leverage items are at the top.

### High value
1. **Bulk DNS import/export** — read/write BIND zone files or CSV. This is the
   single most-requested capability for a DNS CLI and pairs naturally with the
   existing record CRUD.
2. **Zone backup / "GitOps" export** — dump a zone's DNS + SSL + settings to
   YAML/JSON and re-apply it. Enables version-controlled infrastructure.
3. **Multi-account / profiles** — named profiles in config, `--account` flag,
   and a TUI account switcher (resolves §2.4 properly).
4. **Cross-zone DNS search** — `cfm dns find <name>` across all zones.

### Medium value (new Cloudflare surfaces)
5. **Workers & KV / R2 bindings** — list/deploy/tail Workers, manage KV
   namespaces.
6. **Firewall / WAF & IP Access Rules** — list and toggle rules; high demand.
7. **Page Rules / Transform Rules / Redirect Rules**.
8. **Cloudflare Tunnels (cloudflared)** — list and inspect tunnels.
9. **Email Routing** — manage routing rules and destination addresses.
10. **Analytics** — zone traffic and R2 usage summaries (the R2 `get_bucket_usage`
    plumbing already exists but isn't surfaced richly).

### UX / workflow
11. **R2 object browser in the TUI** — currently only bucket-level ops are async;
    the sync object ops (list/upload/delete) exist in the service but aren't in
    the TUI.
12. **Shell completion installer** — `cfm completion install` (Typer supports it).
13. **Cache purge by tag/hostname/prefix** in the CLI (today only zone-wide and
    by-file exist in the service).
14. **Watch mode** — `cfm zones list --watch` / live-refresh panels in the TUI.
15. **Typed-name confirmation** for destructive ops (delete zone) — require the
    user to type the zone name, matching Cloudflare's own dashboard guardrail.

---

## 8. Recommended Action Order

1. **Fix the red tests** (§2.1) — unblocks CI. *(small)*
2. **Fix config precedence** (§2.2) + add a test. *(small)*
3. **Guard proxied/TTL** (§2.3). *(small)*
4. **Add account selection** (§2.4). *(small–medium)*
5. **De-duplicate services** via async-only core or an error decorator (§3.1). *(medium)*
6. **Make `boto3` an optional extra** + lower `requires-python` (§6). *(small)*
7. Then pursue feature work, starting with **bulk DNS import/export** (§7.1).

---

*Generated as part of a full code review. All file references are clickable and
point at the current working tree.*
