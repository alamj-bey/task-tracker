# User Stories — Mid-Course Project

## Feature 1: Tags / Labels

**Story 1 — Add tags when creating a task**
As a team member, I want to add tags to a task when I create it, so that I can categorize work by topic.
- Tags are optional; a task with no tags is valid.
- Each tag is trimmed of whitespace; blank tags are rejected.
- A reasonable max tag count (e.g. 5) and max tag length (e.g. 20 chars) is enforced; exceeding either returns HTTP 422.

**Story 2 — Edit a task's tags**
As a team member, I want to update a task's tags after creation, so that I can re-categorize it as work evolves.
- PATCH accepts a new tag list and replaces the existing one.
- Updating tags does not change other fields (title, status, etc.).

**Story 3 — See tags on the board**
As a team member, I want to see tag chips on each card, so that I can quickly identify a task's category without opening it.
- Tag chips render on the card in the Kanban view.
- A task with no tags shows no chip row (no empty placeholder clutter).

**Story 4 — Filter tasks by tag**
As a team member, I want to filter the board by a tag, so that I can focus on a specific category of work.
- Filtering by a tag that matches no tasks returns an empty (but valid) result — not an error.
- Filtering is case-insensitive.

**Story 5 — Reject invalid tag input**
As a team member, I want the system to reject blank or oversized tags, so that the tag list stays clean and usable.
- Empty string tag → 422.
- Whitespace-only tag → 422.
- Duplicate tags in the same request are silently de-duplicated (not rejected) — *[AI assumption to verify: some AIs will instead reject duplicates with a 422; pick one behavior and document it in the ADR].*

---

## Feature 2: Search + Combined Filters

**Story 6 — Search tasks by keyword**
As a team member, I want to search tasks by a text keyword, so that I can find a task without scrolling the whole board.
- Search matches against title and description (case-insensitive, partial match).
- A search with no matches returns HTTP 200 with an empty list, not 404.

**Story 7 — Combine search with status/priority filters**
As a team member, I want to combine a text search with status and/or priority filters, so that I can narrow results precisely.
- All provided filters are applied with AND logic (not OR).
- Omitted filters are ignored (no default status/priority assumed).

**Story 8 — Combine search with tag filter**
As a team member, I want to combine search/filters with a tag filter, so that I can find, e.g., "high priority tasks tagged 'bug' containing 'login'."
- Requires Tags feature to exist first.
- *[AI assumption to verify: confirm whether tag filtering is single-tag or multi-tag AND/OR — pick one and document it.]*

**Story 9 — Invalid filter values are rejected clearly**
As a team member, I want invalid filter values (e.g. an unrecognized status) to return a clear error, so that I know my query was malformed rather than silently getting wrong results.
- Invalid status/priority enum value → HTTP 422.
- Unrecognized query param name is ignored, not rejected (documented choice).

**Story 10 — Search bar stays usable with empty state**
As a team member, I want the board to clearly show "no results" when my search/filter combination matches nothing, so that I don't think the app is broken.
- Columns remain visible with 0 counts.
- A clear "no matching tasks" indicator appears (not just blank columns).
