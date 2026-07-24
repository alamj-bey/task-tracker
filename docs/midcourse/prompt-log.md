# Prompt Log

## Weak → Improved comparison (required)

**Weak prompt:**
> Add tags to my task model.

**Why this is weak:** doesn't specify the data shape (string vs list), validation rules, limits, or what happens with duplicate/blank tags — leaves the assistant free to invent any of these, likely inconsistently with the rest of the codebase's validation style.

**Improved prompt (T1, used in practice):**
> You are a senior Python backend engineer. Modify my existing FastAPI Task Tracker models to add tag support. Context files: @app/models.py. Changes to TaskCreate, TaskUpdate, TaskResponse: Add field tags: list[str] = []. Validation rules (add a field_validator for tags): each tag stripped of whitespace; blank tags rejected; max 5 tags; max 20 characters per tag; duplicate tags (case-insensitive) de-duplicated, not rejected. Constraints: keep Pydantic v2 syntax only, don't change any other field, don't add tags to any route or storage file in this step, preserve extra="forbid".

**What AI returned:** a `field_validator` implementing strip/reject-blank/max-count/max-length correctly, but the first draft **rejected** duplicate tags with a `ValueError` instead of de-duplicating them.

**What I accepted / edited / rejected:** accepted the overall validator structure and limits; **edited** the duplicate-handling branch to de-duplicate (keep first-seen casing, append to a `seen` set) instead of raising an error, since rejecting outright felt too strict for real usage. This correction is recorded in `mini-adr.md`, decision #2.

---

## T2 — Storage layer (tag filtering)
**Prompt used:** the T2 prompt from the implementation prompt set — asked for `get_all_tasks(status=None, priority=None, tag=None)` with case-insensitive tag matching, no error on zero matches.

**What AI returned:** correct signature and case-insensitive filtering logic, matching the spec exactly on the first pass.

**Accepted / edited / rejected:** accepted as-is. No edits needed at this stage — the exact-match behavior only became a problem later during Search integration (see the fix entry below).

---

## T3 — GET /tasks endpoint (tag query param)
**Prompt used:** T3, specifying the exact query param name, pass-through to storage, and explicit "no matches still returns 200 with []" constraint.

**What AI returned:** correct route update on the first pass.

**Accepted / edited / rejected:** accepted as-is.

---

## S1 — Search combined with existing filters (storage layer)
**Prompt used:** S1 from the implementation set — explicitly specified AND logic across all filters ("a task must satisfy every provided filter"), and required plain Python string matching (no external search library).

**What AI returned:** correct AND-combining logic using sequential list-comprehension narrowing (each filter narrows the previous result set further) — this pattern makes AND logic almost automatic, which is exactly why the prompt's explicit constraint mattered: a differently-structured implementation (e.g. computing separate per-filter match sets and unioning them) could easily have produced OR logic instead.

**Accepted / edited / rejected:** accepted as-is. Verified with `test_combined_filters_use_and_logic_not_or` and a deliberate Break Test (see `verification.md`) to confirm the test would actually catch an AND→OR regression.

---

## S4 — pytest tests for search + combined filters
**Prompt used:** S4, listing exact test names including `test_combined_filters_use_and_logic_not_or` and `test_invalid_status_filter_returns_422`.

**What AI returned:** all named tests generated correctly on the first pass, matching the existing fixture style (`client`, `created_task`, `_reset_storage`).

**Accepted / edited / rejected:** accepted as-is.

---

## Debugging entry: status-transition-on-edit bug (not from the prompt library — found via manual testing)
**What failed:** editing an existing task's assignee (without touching the Status dropdown) and clicking Save returned a 422 "Invalid status transition from InProgress to InProgress."

**Diagnosis:** the frontend's save handler always included the current `status` value in the PATCH payload, even when unchanged — this collided with the backend's "same → same is invalid" transition rule.

**Fix:** modified the modal save handler to only include `status` in the payload if it differs from the task's original status before the edit.

**Accepted / edited / rejected:** this was a self-diagnosed bug (not AI-generated in the first place — it was a gap in my own earlier prompt for the modal that didn't anticipate this interaction with the transition-validation rule from Module 2). Fix was written and verified manually in the browser before being applied to `frontend/index.html`.

---

## Debugging entry: tag filter exact-match vs. search partial-match
**What was observed:** typing `doc` into the tag filter (intending `docs`) showed "No matching tasks," while the same partial-word behavior worked fine in the Search box.

**Diagnosis:** the T2 storage prompt asked for tag matching without specifying exact vs. partial — the AI's default implementation (`tag_lower in [x.lower() for x in t.tags]`, an exact-match membership check) was reasonable given the prompt, but inconsistent with Search's partial-match behavior once both existed side by side.

**Fix:** changed the tag filter to `any(tag_lower in x.lower() for x in t.tags)` — a partial, case-insensitive substring check, matching Search's behavior. Added `test_filter_tasks_by_tag_partial_match` and proved it with a Break Test.

**Accepted / edited / rejected:** this is a case where the original AI output was technically correct against the prompt as written, but the prompt itself under-specified the desired behavior — corrected after manual testing revealed the inconsistency. Recorded in `mini-adr.md`, decision #4.
