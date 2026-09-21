# Lane: copy

**Asks.** Does the product say true things, in Qori's words, to somebody who is
mid-task and slightly annoyed?

**Needs.** `lang/en/*.php`, the terminology layer, and the screenshots to read
the words in place.

**Evidence.** Existing tests cover part of this: a test walks every lang line for
the article rule, and the terminology tests cover pluralisation. The rest is
read off the run.

## Checks

- **No inline user-facing string.** Every readable string is a lang key —
  errors in `errors.php`, everything else in its feature's file. `Log::`,
  `devMessage` and developer-facing console output are exempt.
- **Nouns come from the terminology layer.** Group, Series, Episode, Peer and
  the creator noun are configurable, so a screen that spells one out cannot be
  told otherwise. No `$noun.'s'`, no `a`/`an` immediately before a noun, no
  changed casing.
- **Sentences are authored whole**, with the noun interpolated. Not assembled
  from fragments.
- **Values are interpolated, not restated.** A line saying "expires in 15
  minutes" beside a constant that says 15 is two facts that will drift.
- **Button labels name the result.** "Add an Episode", not "Continue" or
  "Submit" or a bare "Start".
- **Errors say what happened and what to do.** A missing resolution is a
  deliberate statement that the path is final — so check that the ones without a
  resolution really are dead ends, and that the ones with a resolution offer
  something the reader can actually do.
- **No vendor names, status codes or jargon** in anything a customer reads.
- **Nothing promised that does not exist.** The archive promise outlived the
  archive feature once already.

## What it cannot see

- **Vue templates still hold inline English.** That is §13's unwired i18n and is
  tracked as its own work; this lane notes new ones and does not treat the
  existing ones as findings.
- **Tone at length.** Reading one screen says nothing about whether the whole
  product sounds like one voice, and nothing automated will tell you.
- **Whether a customer's own vocabulary reads well** in a sentence Qori wrote.
  The article rule catches the grammar, not the register.
