# My AI Playbook

## When I reach for AI first

- **Scaffolding a known, well-defined shape** — a Pydantic model, a CRUD route, a pytest test for a scenario I can describe precisely. AI is fast and usually gets the boilerplate right when I give it exact field names, types, and constraints.
- **Generating a first draft of documentation** — READMEs, ADRs, review logs — when I already know what happened and just need it organized and written up.
- **Diagnosing an error from evidence I already have** — pasting an exact stack trace, failing test output, or a specific HTTP response and asking "what's the likely cause" is much faster than reading through library internals myself.
- **Repetitive small edits across a file** — e.g. adding the same kind of field to three related models, once I've decided the shape.

## When I do not reach for AI first

- **When I don't yet know what "correct" looks like.** If I can't describe the expected behavior precisely (e.g. "should combined filters use AND or OR logic?"), I decide that myself first — otherwise I'm just accepting whatever the AI happens to default to, and won't know if it's wrong.
- **Environment and tooling problems on my own machine.** Today's session made this obvious — PowerShell execution policy, wrong working directories, missing Git — these needed me to actually read error messages and understand my own setup, not just paste errors and copy fixes blindly.
- **Anything touching validation rules that affect data integrity.** The null-title/status bug happened because a validator's edge case wasn't specified precisely enough in my original prompt. Security- and correctness-critical logic gets read line-by-line by me, not skimmed.

## My non-negotiables

- **Never paste real secrets, `.env` values, tokens, or personal/customer data into any AI tool.** Everything in this project used fictional data.
- **Every AI-generated code change gets run before I trust it** — `pytest`, a manual curl/`Invoke-RestMethod` check, or opening the app in a browser. A confident-sounding explanation is not verification.
- **I read the diff, not just the summary.** Several times today an AI-proposed change looked right at a glance but had one line that didn't do what the summary claimed.
- **I don't accept "it should work" as a substitute for "I confirmed it works."** Every claim in `docs/release-evidence.md` and `docs/final-ai-review.md` is backed by an actual command I ran and actual output I saw, not a description of what output I expected.

## My review rules

- Before accepting a generated diff, I check: does it touch only the files/functions I asked about, or did it drift into unrelated code?
- For anything involving validation, status codes, or filter/search logic, I check the *specific* edge case (empty input, `null` vs. omitted, case sensitivity, boundary values) rather than just the happy path.
- I grade AI review/security comments individually (Useful / Noise / Wrong, or Valid / False Positive / Noise) instead of accepting or dismissing a whole batch of feedback at once — some comments in the same response are worth acting on and others aren't.
- If a test passes on the first try, I treat that as inconclusive until I've either broken the underlying code on purpose to confirm the test catches it (a Break Test), or the logic is simple enough that I don't need to.

## What I am still figuring out

- How to balance "verify everything myself" against actually saving time — today's session took far longer than the code changes alone would suggest, partly because of legitimate environment friction, but I want a better sense of when double-checking is worth it versus when I'm just being overly cautious.
- What the right team norm would be for reviewing AI-suggested changes to validation/business-rule code specifically — I don't yet have a strong opinion on whether that always needs a second human reviewer, or whether a thorough Break Test is sufficient on a small team.
- How much of a security review (like the CORS/description-length findings in this project) is worth acting on immediately versus documenting and deferring, when the app isn't yet in a context where the risk is realized.

## Decision Card

| Situation | My one rule |
|---|---|
| New feature | Write the test cases (happy path + at least one edge case) before accepting generated implementation code. |
| Code review | Grade every AI comment individually — don't batch-accept or batch-dismiss. |
| Debugging | Give the AI the exact error/output, not a paraphrase — and don't let it "fix" a test to make a real bug disappear. |
| Infrastructure (CI/Docker) | Run it for real before calling it done — a green-looking config file is not the same as a green-looking Actions run or a container that actually responds on `/health`. |
| Never-paste | Real secrets, `.env` values, tokens, or personal/customer data — no exceptions, ever, even in throwaway test prompts. |
