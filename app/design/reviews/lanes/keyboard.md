# Lane: keyboard

**Asks.** Can the product be operated without a mouse, and can you see where you
are while doing it?

**Needs.** A **visible** browser that receives key events. Not a hidden pane, not
a headless run. This is the hard requirement in this whole directory and the
reason `T-022` is still blocked.

## Why it cannot be automated here

A hidden browser pane renders correctly, screenshots correctly, measures
correctly — and swallows every key event, because `document.hidden === true`
stops `Tab` reaching the document. `T-003` reported this after the fact; the
same class of failure has now cost this project three separate investigations.

So this lane has one precondition, and a pass that cannot meet it does not run
the lane and says so:

> `document.hidden === false`, in a browser window somebody can see.

## Checks

- **Everything reachable by Tab**, in an order that matches the visual one.
- **Visible focus, not clipped.** A ring cut off by a card's `overflow: hidden`
  or a drawer's edge is the same as no ring.
- **Focus moves into a dialog or sheet when it opens, and returns to the trigger
  when it closes.** Nothing behind an open dialog is reachable.
- **Escape closes what it should**, and only that. Reka handles some of this;
  what happens after it was half-observed once and is still unknown.
- **No traps.** Anything you can Tab into, you can Tab out of.
- **Skip to content**, or a reason there is none.
- **Icon-only buttons have accessible names**, labels are real labels, and an
  error is associated with the field that caused it. A placeholder is not a
  label.

## What it cannot see

- **Screen readers.** Nothing in this lane is a substitute for one. A page can
  pass every check here and still be unusable to somebody listening to it.
- **Voice control and switch access.**
- **Whether the tab order makes sense**, as opposed to merely existing. That
  needs a person who is trying to get something done.
