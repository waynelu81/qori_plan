# qori-plan

Planning, design and brand for Qori. **The code is in the `qori` repository**,
checked out beside this one as `../qori`.

The two were one repository until 21 September 2026. Planning was about a
third of the tracked files and changed several times a day, so every plan edit
showed up as a commit against the application and tripped the frontend dev
server into a reload. Splitting them leaves the code repository to the code.

| Where                          | What is in it                                        |
| ------------------------------ | ---------------------------------------------------- |
| [`app/`](app/)                 | The Qori web app: the plan, the process, the design   |
| [`app/PLAN.md`](app/PLAN.md)   | **Start here** — intent, build status, release gates  |
| [`app/dev/`](app/dev/)         | Process, streams, tasks, decisions, product specs     |
| [`app/design/`](app/design/)   | Brand, UI documents, design reviews                   |
| [`playbook/`](playbook/)       | Reusable modules distilled from what Qori actually built |
| [`ios/`](ios/)                 | Planning for the iOS app                              |
| [`android/`](android/)         | Planning for the Android app                          |

```bash
bin/tasks           # render app/dev/BOARD.md locally (it is not committed)
bin/tasks --check   # parse every task file and apply the rules
bin/tasks --new <stream> <slug>   # a draft stub with the next free id
composer check      # bin/tasks --check, then the rule tests
```

`bin/tasks` was `php artisan qori:tasks` in the code repository. It is the same
reader and the same rules, with Laravel taken out of it, so the plan and the
tool that checks the plan live together.

## What stayed in the code repository

Documents that describe the code rather than the plan, because they are read
and edited alongside it and go stale the moment they are somewhere else:

- `docs/architecture/` — how the built system is shaped, in the code's names
- `docs/flows/` — what the code actually does today, as real call chains
- `docs/tinker/` — how to drive each flow by hand
- `docs/pptcs/` — the privacy policy and terms the app renders
- `CLAUDE.md` — the coding conventions

Task files name paths in the code repository (`app/Services/…`,
`docs/flows/…`). Those are relative to `../qori`, and the board's rules read
them that way.
