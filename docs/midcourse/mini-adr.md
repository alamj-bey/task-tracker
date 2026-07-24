# Mini ADR — Tags and Search + Combined Filters

## Chosen features
1. **Tags / Labels** — tasks can have 0-5 tags, each up to 20 characters, stored as a plain list on the task.
2. **Search + Combined Filters** — `GET /tasks` extended with `search`, combinable with existing `status`, `priority`, and the new `tag` filter.

## Key decisions and AI assumptions corrected

### 1. Tag storage shape: list of strings, not comma-separated
AI-generated model code initially could have gone either way (a raw comma-separated string field, or a `list[str]`). We chose `list[str]` on the Pydantic model, since it lets Pydantic validate each tag individually and keeps the frontend's job (splitting a comma-separated input) separate from the backend's job (validating structured data). The frontend converts its comma-separated text input into a list before sending.

### 2. Duplicate tag handling: silently de-duplicate, don't reject
When two tags differ only by case (e.g. `"Bug"` and `"bug"`), we chose to silently de-duplicate (keeping the first-seen casing) rather than reject the request with a 422. **This was a corrected assumption** — the first draft of the validator rejected duplicates outright, which felt too strict for a UI where a user might reasonably type the same tag twice while editing. De-duplicating is friendlier and still keeps the underlying data clean.

### 3. Combined filters use AND logic, not OR
When `search`, `status`, `priority`, and `tag` are all provided together, a task must satisfy **all** of them to appear in results. This was made explicit and locked in with `test_combined_filters_use_and_logic_not_or`, since OR logic was the most likely accidental behavior an AI-generated implementation could produce (e.g. by unioning per-filter result sets instead of intersecting them).

### 4. Tag filter: exact match → changed to partial match (AI assumption corrected via manual testing)
The first implementation of the `tag` query parameter did an **exact, case-insensitive match** against a task's tags. During manual browser testing, this produced a confusing experience: typing `doc` into the tag filter (intending to eventually type `docs`) showed "No matching tasks" instead of narrowing down as expected, because Search (which does partial matching) behaved differently from Tag filter (which didn't). We changed the tag filter to do the same case-insensitive **partial** match as Search, for UI consistency, and added `test_filter_tasks_by_tag_partial_match` to lock in the new behavior.

### 5. Search scope: title + description only
Search matches against `title` and `description` only — not `assignee` or `tags` (tag filtering has its own dedicated parameter). This keeps the two filters' responsibilities distinct rather than overlapping.

## Alternatives considered and rejected
- **Tags as a separate resource/endpoint** (e.g. `/tags`, `/tasks/{id}/tags`) — rejected as out of scope; the brief's "Tags/Labels" feature description treats tags as a field on the task, not a separate managed resource.
- **Multi-tag filtering** (e.g. `?tag=bug&tag=urgent` requiring both) — rejected for this pass; the current implementation supports filtering by a single tag at a time. This is called out in `user-stories.md` (Story 8) as a scoped-out extension, not a gap.
- **Debounced search on every keystroke sent to the server** — considered, but implemented client-side debouncing (300ms) instead of sending a request per keystroke, to avoid unnecessary load and match the pattern the frontend already uses.
