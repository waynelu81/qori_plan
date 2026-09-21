---
id: T-002
title: The second fixture task
stream: fixture
status: doing
owner: someone
estimate: M
depends: T-001
blocks: none
---

# T-002 — The second fixture task

## Files

| Path                           | Change | Notes                                    |
| ------------------------------ | ------ | ---------------------------------------- |
| `app/Two.php`, `app/Three.php` | edit   | Two paths in one cell are both captured  |
| `app/dev/tasks/T-00*.md`       | edit   | A glob expands against the fixture root  |
| `Bare.php`                     | edit   | A bare basename, which the rules refuse  |
| `app/New/*.php`                | new    | A glob matching nothing stays as written |
