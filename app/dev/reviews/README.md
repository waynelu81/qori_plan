# Reviews

**A review is a second pair of eyes on a stream or a design, before it is
built.** It is not a code review of a pull request, and it is not a task: no
`T-###`, no board entry, nothing claimed. A review exists because a stream
was specified largely by one person and somebody wanted it read by someone
who did not write it.

**Only the brief stays here.** It is named `<stream>-YYYY-MM-DD.md`, and it
is the whole instruction to a reviewer: point them at its path and nothing
else needs saying, because it names its own reading order, what to aim at,
what is out of scope and what to deliver.

**Findings are transferred into the plan and then removed.** A reviewer
writes `<stream>-YYYY-MM-DD-findings-<who>.md` beside the brief; each
finding is then carried into the task, stream or reference document it
concerns — under a dated heading in that task's "Before this can be ready",
as an in-place correction where the review found the document simply wrong,
or into `vendor-accounts.md` where it is durable reference — and the findings
file is then deleted. Two copies of a finding drift apart, and the one in the
task is the one a developer will read.

**Commit the findings file before deleting it, in a commit of its own.** The
deletion is then one `git show` away from being undone, and the transfer can
be read against what it came from. Deleting a file git has never seen
destroys it, which is how the first of these was lost on 20 September 2026.

**The one that was lost is `storage-2026-09-20-findings-codex.md`**, the
twelve findings on the storage stream. It is named here because a dozen task
files quote it, cite it, or say "the storage review" without a path, and a
reader who goes looking will not find it and should not have to work out why.
It cannot be recovered: `git log --diff-filter=A -- docs/planning/reviews/`
shows only this README and the briefs, so there is no commit to restore it
from. **What the tasks carry is therefore the review itself, not a summary of
it** — those bullets are the primary source, and `storage-2026-09-20.md`, the
brief that commissioned it, is still here for context. The rule above exists
because of this file, and it is the whole of the cost of breaking it.

**A finding is not a change.** Nothing a review says rewrites a task's
specification, a stream's order or `decisions.md` on its own. Acting on one
is the stream owner's: it becomes a line under "Before this can be ready", a
re-scope, a new task, or a proposed decision record — and a proposal stays a
proposal until the owner takes it.

The brief, like every other planning document, is history once written and is
never rewritten.
