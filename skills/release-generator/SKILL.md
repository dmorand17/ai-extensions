---
name: release-generator
description: >
  Cut a GitHub release end-to-end — suggest the next semver tag from commit
  history, generate categorized user-facing release notes, and publish via
  `gh release create`. Also generates standalone changelogs/release notes
  without publishing. Use when the user mentions cutting a release, creating
  a GitHub release, drafting a release/tag, release notes, changelog,
  what's new, or product updates (e.g. "release v2.5.0", "what should the
  next version be").
user-invocable: true
argument-hint: "[version]"
---

# release-generator

Turn a git commit range into a versioned, user-facing GitHub release —
or just the notes, if that's all the user wants.

## Two modes

| Request                                                      | Mode          |
|--------------------------------------------------------------|---------------|
| "changelog", "release notes", "what's new since v2.4.0"      | Notes only    |
| "cut a release", "create a GitHub release", "release v2.5.0" | Full release  |

**Default to notes-only.** Only publish a GitHub release when the user
asks to release/tag/publish. When invoked as `/release-generator <version>`,
treat it as a full-release request with that version.

---

## Notes-only workflow

### 1. Determine the commit range

- Since last release: `git describe --tags --abbrev=0` for the previous
  tag, then read `git log <prevtag>..HEAD`.
- Explicit range/dates: use what the user gave (`v2.4.0..HEAD`, a date
  window, etc.).
- No tags yet: use the full history or ask for a starting point.

### 2. Read the commits

```bash
git log <range> --no-merges --pretty=format:"%h %s%n%b"
```

### 3. Categorize and translate

Group commits into user-facing sections. Map Conventional Commit types:

| Commits                          | Section              |
|----------------------------------|----------------------|
| `feat`                           | ✨ New Features       |
| `perf`, `refactor` (user-visible)| 🔧 Improvements      |
| `fix`                            | 🐛 Fixes             |
| `!` / `BREAKING CHANGE`          | ⚠️ Breaking Changes  |
| security fixes                   | 🔒 Security          |

- Rewrite subjects in customer language — *what changed and why it
  matters*, not the implementation.
- **Filter internal noise**: drop `chore`, `ci`, `build`, `test`,
  `style`, and pure-refactor commits with no user impact.
- Lead breaking changes with the migration impact.

### 4. Output

```markdown
# Updates — <version or date>

## ✨ New Features
- **<Feature>**: <user-facing benefit>

## 🔧 Improvements
- <improvement>

## 🐛 Fixes
- <fix>
```

Offer to save to `CHANGELOG.md` (prepend a new entry; don't clobber
existing history) or hand the text to the full-release workflow.

---

## Full-release workflow

Notes → version → tag → publish. Auto-progress through notes generation;
**pause for confirmation before creating the tag and before publishing**
(both are outward-facing and hard to undo).

### 1. Preflight

```bash
gh auth status          # confirm gh is authenticated
git status -sb          # working tree should be clean
git describe --tags --abbrev=0   # last release tag
```

- If `gh` is missing/unauthenticated, stop and tell the user.
- If the working tree is dirty, surface it and confirm before continuing.
- If the repo isn't on GitHub, stop — don't fall back to other tooling.

### 2. Ask the release type, then compute the version

If the user gave an explicit version, use it. Otherwise **ask the user
what type of release this is** so the version bump is intentional:

| Release type | Bump  | Use when                                    |
|--------------|-------|---------------------------------------------|
| Major        | major | Breaking changes / incompatible API changes |
| Minor        | minor | New backward-compatible features            |
| Patch        | patch | Backward-compatible bug fixes only          |

Inspect commits since the last tag and **recommend** the type, but let
the user choose. Suggest based on the highest-impact change:

- Breaking change (`!` / `BREAKING CHANGE`) present → suggest **major**
- New feature (`feat`) present → suggest **minor**
- Only fixes / patches → suggest **patch**

Present it like a question, e.g.:

> I see 3 feats and 0 breaking changes since `v2.4.0`, so I'd suggest a
> **minor** release → `v2.5.0`. What type of release do you want?
> (major / minor / patch)

Once the user picks, apply the bump to the last tag to get the new
version. Match the repo's existing tag style (`v`-prefixed vs bare;
check the last tag). **Confirm the resulting version** before tagging.

### 3. Generate the notes

Run the **Notes-only workflow** above over `<lasttag>..HEAD`, using the
chosen version as the heading. Show the user the notes for review.

### 4. Confirm, then tag and publish

Show the user: version/tag, target commit (HEAD), whether it's a
prerelease, and the notes. Wait for explicit approval.

Create an **annotated** tag (the convention for published releases — it
records the tagger, date, and message, and can be signed), push it, then
publish the release against it. Pass `--generate-notes` so GitHub appends
its auto-generated commit list, contributors, and **Full Changelog**
compare link (`<prevtag>...<tag>`) *below* the curated summary — you get
the readable human summary on top and the raw diff/compare link beneath:

```bash
git tag -a <tag> -m "Release <tag>"
git-c push origin <tag>
gh release create <tag> \
  --title "<title>" \
  --generate-notes \
  --notes "$(cat <<'EOF'
<generated notes>
EOF
)"
```

Pushing the tag first means `gh release create` reuses the annotated tag
instead of creating a lightweight one. Use `git-c` (not `git`) for the
push, per the project's git practices; if `git-c` fails with a
`failed to connect to the docker API` error, ask the user whether to
start colima via `colima start`.

**First release (no prior tag):** `--generate-notes` has no tag-to-tag
range, so GitHub generates from the *entire* history — which dumps every
commit (including noise like routine docs/content commits) below your
summary. For a first release, omit `--generate-notes` and ship the
curated notes alone; it becomes valuable from the second release on, when
the compare range is a tight `<prevtag>...<tag>`.

To sign the tag, use `git tag -s <tag> -m "..."` instead.

To tag a commit other than HEAD, point the `git tag -a` step at that
sha (`git tag -a <tag> <sha> -m "..."`) — `gh release create` then
uses wherever the tag points.

Useful `gh release create` flags:

- `--prerelease` — mark as a pre-release (alpha/beta/rc)
- `--draft` — create as a draft for manual review before going public
- `--latest` / `--latest=false` — control the "Latest" badge
- `--generate-notes` — append GitHub's auto notes (commit list +
  contributors + Full Changelog compare link) below yours. Default on,
  except for a first release with no prior tag (see above)

After creation, return the release URL.

### Error handling

- **Tag already exists**: stop. Don't overwrite or force — confirm the
  intended version with the user.
- **Auth failure**: stop and surface. Don't retry with different creds.
- **Not a maintainer / 403**: surface the permission error; the user may
  lack release rights on the repo.

---

## Safety rules

- Releases are public and outward-facing — always confirm version and
  notes before publishing.
- Never delete or overwrite an existing tag/release without explicit
  user direction.
- Prefer `--draft` when the user is unsure, so they can review on GitHub
  before going live.
- Never publish secrets — release notes are public; don't echo tokens,
  internal URLs, or credential-like strings from commit bodies.

## Tips

- Run from the repository root.
- Pair with [git-flow](../git-flow/) — ship the branch/PR first, merge,
  then cut the release from `main`.
- Review and edit generated notes before publishing; the categorization
  is a strong draft, not gospel.
