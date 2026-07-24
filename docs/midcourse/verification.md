# Verification

## Baseline check (before adding Tags/Search)
Ran the existing test suite before making any feature changes:

```
================================================= test session starts =================================================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\PST\Downloads\task-tracker\task-tracker
plugins: anyio-4.14.2
collected 16 items
tests\test_tasks.py ................                                                                             [100%]
=========================================== 16 passed, 3 warnings in 0.19s ============================================
```

3 warnings noted (StarletteDeprecationWarning re: httpx/testclient usage and `HTTP_422_UNPROCESSABLE_ENTITY` naming) — reviewed and judged non-blocking, since they reflect newer-library naming changes rather than incorrect behavior. Not addressed, to stay within scope.

## Backend test results by stage

| Stage | Test count | Result |
|---|---|---|
| Baseline (Modules 1-3 equivalent) | 16 | 16 passed |
| + Tags backend (model/storage/endpoint/tests) | 24 | 24 passed |
| + Search backend (storage/endpoint/tests) | 31 | 31 passed |
| + Tag filter partial-match fix + test | 32 | 32 passed |

Final full run:
```
================================================= test session starts =================================================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 32 items
tests\test_tasks.py ................................                                                             [100%]
=========================================== 32 passed, 3 warnings in 0.30s ============================================
```

## Manual browser checks

### Drag-and-drop + business rule enforcement
Manually dragged a card from **In Progress → To Do**. Confirmed the move was rejected client-side with the exact server message surfaced in the UI:
> "Move rejected: Invalid status transition from InProgress to ToDo. Allowed transitions: ['Done->InProgress', 'InProgress->Done', 'ToDo->InProgress']"

The card correctly rolled back to its original column rather than staying in an invalid state. Confirmed the allowed reverse transition (**In Progress → Done**) succeeds without error.

### Tags — modal, chips, filter
- Created a task with tags `bug, urgent` via the modal — confirmed tag chips rendered on the card.
- Edited an existing task's tags via the modal — confirmed the chip list updated and other fields (title, priority) were unaffected.
- Typed a tag into the "Filter by tag..." box — confirmed the board narrowed to matching tasks only, with a short debounce delay.

### Search + combined filters — API level
Verified directly against the running backend with `Invoke-RestMethod`:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/tasks?search=login"
# returned both "Fix login bug" and "Write login docs"

Invoke-RestMethod -Uri "http://localhost:8000/tasks?search=login&priority=High"
# returned only "Fix login bug" -- confirms AND logic, not OR
```

### Search + combined filters — browser level
- Typed `login` into the Search box alone — board narrowed to the two matching tasks.
- Added `bug` into the tag filter box at the same time — board narrowed further to just the one task matching both conditions.
- Cleared both boxes — all tasks reappeared.

## Break Test evidence

**Test broken:** `test_combined_filters_use_and_logic_not_or`
**Change made:** temporarily changed the filter-combining logic in `storage.get_all_tasks` from sequential intersection (AND) to a union (OR) of per-filter matches.
**Result:** the test failed as expected — it asserted only the task matching *both* `priority=High` and `tag=bug` should be returned, but the broken OR version returned all three seeded tasks. This confirms the test is meaningful (it fails when the real bug it's designed to catch is introduced) and not a false-positive "always passes" test.
**Source code restored** to the AND version afterward; full suite re-run to confirm 32/32 passing again.

**Test broken (second check):** `test_filter_tasks_by_tag_partial_match`
**Change made:** temporarily reverted the tag filter back to exact match (`tag_lower in [x.lower() for x in t.tags]` instead of the `any(... in ...)` partial-match version).
**Result:** test failed as expected — searching `"doc"` no longer matched a task tagged `"docs"`. Confirms this regression test actually protects the fix. Source restored; full suite re-confirmed at 32/32.

## Bugs found and fixed during manual verification
See `prompt-log.md` and `mini-adr.md` for full detail on both:
1. **Status-transition-on-unrelated-edit bug** — editing a task's assignee/description without touching the Status dropdown always resent the current status, which tripped the "same → same is invalid" business rule and blocked unrelated edits. Fixed by only including `status` in the PATCH payload when it actually changed.
2. **Tag filter exact-match vs. Search partial-match inconsistency** — found via manual UI testing, documented as a decision in `mini-adr.md`, fixed with a regression test.
