---
type: lesson
title: "Sources and pinning"
minutes: 14
---

Each entry's `source` says where that plugin's files come from. The source type also decides **what you are trusting**.

| Type | Fields | What "the same plugin" means |
|---|---|---|
| Relative path `"./plugins/x"` | the string | Whatever is in the marketplace repo at the commit you fetched |
| `github` | `repo`, `ref`, `sha` | `ref` is a branch or tag (it can move); `sha` is an exact commit |
| `url` | `url` (`https://`, `file://`, `git@`), `ref`, `sha` | The same, for any git host |
| `git-subdir` | `url`, `path`, `ref`, `sha` | One folder of a monorepo, fetched sparsely |
| `npm` | `package`, `version`, `registry` | A version, range, or dist-tag. Install scripts never run |
| `archive` | `url` (https), `sha256` | A zip. With `sha256` set, a download that doesn't match is refused |
| `command` | `command`, `timeout`, `mode` | Output of a command run on the user's machine, which asks for confirmation first |

## Pinning: tags move, digests don't

- A **branch** (`ref: main`) gives you whatever the branch points at today. Every update can bring new code.
- A **tag** (`ref: v1.0.0`) is a convention, not a guarantee: tags can be deleted and re-pointed.
- A **commit `sha`** (40 lowercase hex characters) names exact content. When both are set, Claude Code checks out `sha`, even if the tag later moves. Validation rejects anything shorter: `Must be a full 40-character lowercase git commit SHA`.
- An archive **`sha256`** pins the bytes of the zip. A compromised artifact server can't swap the file without the install failing.

**What pinning doesn't do:** a digest proves you got *the bytes you reviewed*. It says nothing about whether those bytes are safe. Pinning is only worth something if someone reviewed that exact commit or archive. Moving the pin is a deliberate act: review the diff, then update `sha` (or `sha256`) and bump the version.

```bash
git -C lint-kit rev-parse 'v1.0.0^{commit}'   # the commit a tag points at now
shasum -a 256 fmt-kit-1.0.0.zip               # digest for an archive entry (sha256sum on Linux)
```

## Updates under a pin

`claude plugin marketplace update` re-reads the catalog, and `claude plugin update` installs the version the catalog points at. With a pinned `sha`, upstream commits change nothing: the update reports `up_to_date`. Only editing the catalog moves users forward.

## Commands this node introduces

`ref` versus `sha`, `sha256` for archives, `git rev-parse <tag>^{commit}`, and `shasum -a 256`.
