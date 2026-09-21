# Handoff prompt

> The brief given to a developer or an agent taking work from this repository.
> Fill in the task ids and paste it whole.
>
> It is a template because it is expected to change: every time somebody works
> from it and something goes wrong that this document could have prevented, fix
> it here. The paragraphs below each exist because a real run needed them —
> `docs/planning/tasks/reports/` holds the evidence.

---

```
Complete these tasks from the planning system in this repository:
<TASK IDS — e.g. T-002, T-007, T-009, T-012>

BEFORE YOU START
1. Read docs/planning/PROCESS.md in full. It defines the lifecycle, what a
   specification guarantees, and the re-scope rule. Follow it exactly.
2. Read docs/planning/tasks/reports/README.md. You will write a report.
3. Read each task file under docs/planning/tasks/, including its
   Preconditions section, before touching code.
4. Read CLAUDE.md for the codebase conventions.

SET UP
- Postgres 18 on port 5433 (docker compose up -d), database qori_testing.
- php artisan wayfinder:generate --with-form   (generated + gitignored; Vue
  imports from @/routes will not resolve without it)
- php artisan serve --port=8001 and npm run dev, if you can drive a browser.

RULES THAT MATTER
- Claim a task: set `status: doing` and `owner: <your name>` before starting.
- SCOPE IS THE CONTRACT. If an Acceptance line contradicts the Scope section,
  or promises a result the specified design cannot produce, that is a defect
  in the task: satisfy the Scope, record the defect under Notes, and report
  it. It is NOT a re-scope.
- Re-scope only when what must be BUILT changes — the approach cannot work,
  or a premise about the codebase is false in a way that changes the design.
  Then: write the Re-scope log, set `status: rescope`, and stop that task.
- Wrong lang key names, a differently-named test file, a helper the spec
  invented — all Notes, not re-scopes.
- Use the names the spec gives: columns, method signatures, lang keys, route
  names, test method names.
- Where a task changes the interface, look at it in a browser. If you cannot,
  say so — do not leave it unsaid.

DONE MEANS
- Every Acceptance box ticked.
- `composer ci:check` green from a clean working tree.
- `php artisan qori:tasks --check` passes (the board itself is rendered locally, not committed).
- A report written to docs/planning/tasks/reports/ from the right template.

WHEN YOU FINISH
- Commit nothing unless you were told to. Leave changes in the working tree.
- Reset the tasks you COMPLETED to `status: ready`, `owner: unassigned`,
  acceptance boxes un-ticked, ONLY if you were asked to — this is for
  comparison runs, not normal work. Keep the Notes either way.
- Never reset a task you re-scoped. It stays `rescope` — that status is the
  signal, and clearing it discards the only evidence anything was wrong.
- Regenerate the board again after any status change.
- Reply with: tasks completed, tasks re-scoped, final test count, what you
  could not verify and why, and every place a specification was wrong.
```

---

## Why each rule is here

| Rule                             | What happened without it                                                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Scope is the contract            | The same task was completed by three workers and re-scoped by two, all reacting to one wrong Acceptance line.                              |
| Never reset a `rescope`          | A worker correctly refused a blanket "reset the tasks" instruction, spotting that it contradicted the frozen-spec rule.                    |
| Say what you could not verify    | Two workers had no browser. The one defect that only shows on screen was found only by those who did.                                      |
| `wayfinder:generate` first       | Generated route helpers are gitignored, so a fresh clone analysing them reads an empty directory and reports success.                      |
| Notes, not re-scope, for wording | Four workers hit the same handful of wrong lang keys and test filenames; without the distinction, each of those could have stopped a task. |
