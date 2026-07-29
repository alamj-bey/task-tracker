# Final AI Review and Ownership Evidence

## AGENTS.md guardrails
- Repo-specific stack and commands included: yes
- Docs-first/read-first guardrail included: yes
- Unexpected app/frontend edits rule included: yes

## AI code review mini-log

Reviewed diff: the `TaskUpdate` fix in `app/models.py` that rejects an explicit `null` for `title` and `status` (previously both were silently accepted and could wipe a required field). Full context in `docs/midcourse/mini-adr.md`, decision #6.

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| "The new `validate_status` check correctly distinguishes an omitted field from an explicit `null`, because Pydantic only invokes a field's validator when the field is actually present in the request body." | Useful | Correctly identifies *why* the fix is safe (it doesn't accidentally also reject the legitimate "leave status unchanged" case). This was the exact risk worth checking before accepting the change. | Confirmed with `test_patch_omitted_title_leaves_it_unchanged`, which passes — omission still works. |
| "Consider raising a more specific error class than a generic `ValueError` so the API can distinguish this failure mode from other validation errors." | Noise | Technically true in the abstract, but out of scope here — Pydantic's `field_validator` is expected to raise `ValueError`/`TypeError`/`AssertionError`, which FastAPI already converts into a structured 422 response with a field-level detail message. Adding a custom exception class would be unnecessary complexity for no behavioral gain in this project. | Not applied. |
| "This change could break existing clients that rely on being able to clear a task's title by sending `null`." | Wrong | No such usage existed anywhere in this codebase — the frontend never sends `null` for these fields (confirmed by reading `frontend/index.html`'s save handler), and no test asserted that behavior. The AI flagged a hypothetical regression without checking whether the behavior was ever real. | Checked frontend code and existing test suite before dismissing; no regression risk found. |

## AI security mini-review

| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| CORS middleware allows all origins (`allow_origins=["*"]`) while also allowing credentials (`allow_credentials=True`) | `app/main.py`, `CORSMiddleware` config | Valid | A wildcard origin combined with credentials is a recognized misconfiguration pattern — if this app ever added cookie-based auth, any site could make credentialed requests to it. Currently low actual risk since there is no authentication or cookie usage anywhere in the app, but the configuration itself is the kind of thing that should not silently make it into a more production-like setup later. | Documented here rather than changed now — changing it requires knowing the real frontend origin(s) at deploy time, which isn't yet defined for this course project, and the brief restricts `app/` changes to genuine bug/security fixes with justification. Flagging for whoever deploys this beyond local/course use. |
| `description` field on `TaskCreate`/`TaskUpdate` has no maximum length, unlike `title` (200 chars) and each tag (20 chars) | `app/models.py` | Valid | An unbounded string field accepted from client input is a minor but real inconsistency — every other free-text field in the model has an explicit size limit for exactly this reason. | Not changed — flagged rather than fixed, since adding a new validation constraint changes accepted input shape and falls closer to a scope change than a strict bug fix under this project's "no new product features" rule. Documented here for future work instead. |
| No rate limiting or request-size limiting at the application level | `app/main.py` | False Positive (for current scope) | This is a standard generic finding any AI security scanner produces for nearly any API, regardless of context. This project is an in-memory, no-auth, course/demo backend with no persistent storage and no public deployment target — rate limiting protects against abuse scenarios that don't apply here. Would become a real finding only if this were deployed publicly. | No action — noted as context-dependent, not acted on. |

## Manual security check

I manually tested `PATCH /tasks/{id}` by sending `{"title": null}` and `{"status": null}` directly via `Invoke-RestMethod`, rather than relying on the AI's own review of the validator code. This was not something the AI flagged on its own when the tag/search features were first built — it surfaced only from directly exercising the API with an input the existing test suite hadn't covered. Before the fix, both requests returned HTTP 200 and silently overwrote the field with `None`, despite `title` and `status` being declared as required, non-nullable fields on `TaskResponse`. This confirmed a real gap between what the model *declared* and what the update path actually *enforced*, which static code reading alone had not caught.

## One AI output I rejected or corrected

Early in the mid-course project, `requirements.txt` was generated with exact version pins (e.g. `pydantic==2.9.2`) following the same pattern shown in the course's Module 2 prompt examples. On this machine (Python 3.14, very recently released), that exact pydantic version had no pre-built wheel available, so `pip install` fell back to compiling `pydantic-core` from Rust source — a process that hung for many minutes and risked failing outright without a local Rust toolchain. I corrected this by switching `requirements.txt` to minimum-version constraints (`pydantic>=2.10`, etc.) instead of exact pins, which let pip resolve to a newer release with a pre-built wheel for this Python version. I did not accept the original pinned-version output as-is once it became clear it didn't actually work in this environment.

## Three AI usage rules

1. **Never paste:** real credentials, `.env` contents, API tokens, production logs, or any real personal/customer data into an AI tool or into this repo — test data only, always fictional.
2. **Always verify:** run the actual test suite (and, where relevant, a manual request against the running app) before accepting any AI-suggested code change — a suggestion that reads correctly is not the same as one that behaves correctly, as the null-title bug proved.
3. **Record AI contributions by:** logging real prompts and their outcomes (accepted / edited / rejected, and why) in `docs/midcourse/prompt-log.md` and this file, rather than a generic "AI helped with X" note — specific enough that someone else could see exactly what was generated, what was kept, and what was changed.

## Ownership statement

I'm comfortable submitting this repository as my own work because every feature, bug fix, and test in it was verified by actually running it — not just accepted because AI-generated code looked plausible. Three real bugs surfaced during this project (a frontend status-transition edge case, a tag-filter matching inconsistency, and the null-title/status validation gap), and none of them were caught by reading code alone; each was found by exercising the app directly through the browser or the API and then traced back to its root cause before fixing it. I made and can explain specific design decisions that AI's first draft didn't make on its own, including how duplicate tags are handled, that combined filters use AND rather than OR logic, and why the null-value validation gap needed closing. I also know where I chose *not* to act on an AI suggestion (the CORS and description-length findings above) and why. The commands, configuration, and test results throughout this repository's `docs/` folder reflect what I actually ran on my own machine, not fabricated output.
