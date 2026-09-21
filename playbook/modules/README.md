# Modules

One file per capability. Each is written to the template below.

## The template

```markdown
# Module: <name>

**What it is.** One paragraph: what this capability does for the person using
the product, not how it is implemented.

**Done when.** The observable test. If you cannot walk it in a browser or call
it from a client, it is not done.

## Decide first

The questions that must be answered before any code, each with the answer
reached and the reason. A table: Question | Qori's answer | Why.

## Build order

Numbered steps, each one task-sized — a day or two, one reviewable change.
Each step names the shape of what it touches. Dependencies are explicit:
"needs 3" rather than left implied by order.

## Rules that bite

The non-obvious constraints. Every one of these cost somebody a day.

## Native contract

What an iOS or Android client needs from this module: the endpoints, what a
token carries, deep links, what must not be assumed. Marked **Not proven**
where nothing native has been built.

## Traps

What went wrong, and the symptom it presented as — because the symptom is what
the next person will search for, not the cause.

## Proven / Not proven

Two lists. What was exercised for real (a browser walk, a real vendor call, a
test against a live sandbox), and what is still design.

## Source

The tasks, reports and decisions behind this module.
```

## Why this shape

**Decide first** is the part that saves the week. Most of the cost in a module
like payouts or storage is not writing the code — it is discovering that the
vendor's account-creation API and its OAuth flow disagree about what an account
is, and then deciding what your product does about it. That discovery is
reusable; the code often is not.

**Traps are indexed by symptom** because that is how they are met. Nobody
searches for "the session keeps url.intended across regeneration"; they search
for "signed in and landed on someone else's page".

**Proven / Not proven** exists because a playbook that quietly mixes the two is
worse than no playbook. A build order you can execute straight away is only
valuable if you can trust which parts have been executed before.
