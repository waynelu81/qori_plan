# Qori brand and interface guide

Version 1.0 - 8 September 2026

## Brand idea

Qori is a private classroom for people a teacher already knows. The identity should feel warm, clear, capable and human. It should never feel like a public social feed, a finance dashboard or an untouched software starter kit.

The open-circle Q represents knowledge moving between people. The opening matters: sharing is an invitation, not a closed system. The short tail keeps the mark recognisable as Q at favicon size.

"sharing is caring" is a brand line, not the product explanation. Pair it with a concrete subline such as "A private classroom for people you already teach" anywhere a visitor does not already know Qori.

## Logo files

- `logos/qori-logo-primary.svg`: default transparent lockup on paper or other light backgrounds.
- `logos/qori-logo-reverse.svg`: lockup prepared on an ink panel.
- `logos/qori-logo-mono-ink.svg`: one-colour use when colour is unavailable.
- `logos/qori-mark.svg`: standalone open-circle mark.
- `logos/qori-app-icon.svg`: gold rounded-square app icon.
- PNG exports are provided for systems that cannot use SVG.

### Logo rules

- Keep clear space equal to the stroke width of the Q mark on every side of the lockup.
- Minimum digital sizes: mark 24px; horizontal logo 96px wide.
- Use only paper, ink or Qori gold versions.
- Do not close the ring, rotate the mark, recolour individual letters, add a shadow, stretch the lockup or place it over a busy image.
- The SVG logo uses vector geometry and does not depend on a font file.

## Colour

| Token             |       Hex | Purpose                            |
| ----------------- | --------: | ---------------------------------- |
| Paper             | `#FAF8F5` | Main background                    |
| Card              | `#FFFDF8` | Raised content surface             |
| Ink               | `#231F1A` | Primary text and dark fields       |
| Qori Gold         | `#98661B` | Primary actions and brand identity |
| Gold Hover        | `#7F5113` | Hover/pressed action state         |
| Muted Text        | `#6E665E` | Secondary copy on paper            |
| Soft Surface      | `#F1ECE5` | Muted panels and inactive regions  |
| Decorative Border | `#DED6CB` | Non-essential panel separation     |
| Input Boundary    | `#8A7F73` | Essential control outline          |
| Success           | `#286B49` | Positive semantic state            |
| Warning           | `#8A5A10` | Warning semantic state             |
| Destructive       | `#B42318` | Destructive/error semantic state   |

Qori Gold (`#98661B`) with Paper (`#FAF8F5`) is approximately 4.66:1 and is suitable for normal button text. Gold is not the only status signal: status always includes a label or icon. Decorative borders may be subtle; essential input boundaries and focus rings must remain perceivable at 3:1.

Dark mode uses warm charcoal, not blue-black or zinc. Use `#211E19` for the page, `#2B2721` for cards, `#F8F2E8` for primary text and `#F0B85A` for actions. If dark mode is exposed, test every component in it; otherwise ship the light theme alone.

## Typography

Use Instrument Sans for product UI and marketing. Recommended fallback: Inter, then the system sans-serif. Use only 400, 500, 600 and 700.

| Role       | Desktop | Mobile |  Weight | Line height |
| ---------- | ------: | -----: | ------: | ----------: |
| Display    |    56px |   40px |     700 |        1.05 |
| Page H1    |    32px |   28px | 650-700 |        1.15 |
| Section H2 |    22px |   20px |     650 |        1.25 |
| Card title |    18px |   18px |     600 |         1.3 |
| Body       |    16px |   16px |     400 |        1.55 |
| UI/label   |    14px |   14px | 500-600 |         1.4 |
| Caption    |    12px |   12px |     500 |         1.4 |

Do not introduce a decorative second font in the first design pass. Warmth comes from colour, spacing, course objects and language.

## Layout and shape

- Base spacing unit: 8px. Use 4px only for tight icon/text relationships.
- Control radius: 10px. Panel radius: 12px. Feature/cover radius: 20px.
- Keep one aligned page header: H1, one-line context, one ranked primary action.
- Use a comfortable desktop content width; do not stretch forms to fill a wide panel.
- At 360px the sidebar becomes the existing drawer. No page-level horizontal scrolling.
- Primary mobile targets are at least 44px high.
- Shadows are quiet and rare. Borders and space define the hierarchy.

## Course identity

`CourseCover` is the shared identity primitive. Generate its wash from an immutable course id, not the mutable title. Stay in the paper/gold range; avoid random rainbow covers and empty grey rectangles.

Use separate compositions for separate jobs:

- Studio course card: status, lesson count, price and edit/open action.
- Learning course card: classroom/teacher, progress, next lesson and Continue/Start.
- Public course hero: teacher/classroom, summary, real contents, known duration, price and enrolment state.

Do not make the public page a studio card enlarged. Do not add internal draft language to learner/public surfaces. A progress bar includes text such as "3 of 8 lessons" and an accessible value.

## Voice

Qori sounds like a calm, capable teaching partner. Use plain verbs and name the result.

| Prefer                                                            | Avoid                       |
| ----------------------------------------------------------------- | --------------------------- |
| Create course                                                     | Submit                      |
| Publish course                                                    | Continue                    |
| Invite student                                                    | Add contact                 |
| Your classroom                                                    | Workspace (customer-facing) |
| 3 of 8 lessons complete                                           | 38% (on its own)            |
| We could not publish this course. Add one lesson, then try again. | Something went wrong        |

Do not use jokes to fill empty states, invent activity, or promise unavailable features. "sharing is caring" should never stand alone as the value proposition.

## UX rules

1. Objects before metrics: show the course before aggregate counts.
2. One next action: use `TeachDigest.nextAction` and land at the completing control.
3. Blocking and permission states outrank encouragement.
4. Success changes the visible object and offers the next useful action; it is not only a toast.
5. Empty states occupy the future object's space and show only actions the role/plan permits.
6. Every changed surface covers loading, empty, populated, failure, success, permission and locked states.
7. One logical H1, visible focus, keyboard operation, associated form errors, 200% zoom and 360px review are part of done.

## Banner files

- `banners/qori-banner-hero-1600x640.*`: light product/website hero treatment.
- `banners/qori-banner-social-1500x500.*`: dark social/profile cover treatment.

Both use course geometry and the open circle rather than stock photos. Replace copy for a specific campaign, but preserve the logo safe area, warm palette and single-message hierarchy.
