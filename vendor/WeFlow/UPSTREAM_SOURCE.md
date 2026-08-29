# WeFlow upstream source provenance

This directory vendors a complete WeFlow source snapshot so the repository contains the graphical WeChat export tool it documents.

- Project: `hicccc77/WeFlow`
- Snapshot version: `v5.0.0`
- Commit: `a7656bf26776f6e0026b754de90fd07d2f037966`
- Commit date: `2026-07-07T14:58:36+08:00`
- Retrieved on: `2026-08-29`
- Recovery source: GitHub fork network repository `Orderization/WeFlow`, whose commit retains the original upstream author and history
- Integrity check: all 482 paths from `git ls-tree -r --name-only` were restored; missing paths: 0; unexpected paths: 0 before adding this provenance file

The current upstream default branch had replaced its earlier source history with a DMCA notice, so the original commit was no longer reachable from that branch. Keep this exact commit identifier when auditing or updating the vendored snapshot.

The snapshot includes native Windows components that access local WeChat data. Build and run it only on data the user is authorized to access. Do not commit exported chats, decrypted databases, credentials, logs containing private data, or generated analysis reports.

On `2026-08-29`, `npm ci` and `npm run typecheck` succeeded with Node.js 24.16.0 and npm 11.13.0. `npm audit` reported 10 high-severity advisories in the historical lockfile (no critical advisories). Keep the application local-only, leave its HTTP API and external AI integrations disabled unless explicitly needed, and review dependency updates before exposing it to untrusted network input. The lockfile is intentionally preserved unchanged so this snapshot remains reproducible.

The upstream `LICENSE` file is retained unchanged in this directory.
