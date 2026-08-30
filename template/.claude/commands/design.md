---
description: Phase 2.5 - the design. Spawn the design lead to turn the product spec and brand into a distinctive design system and real screen mockups.
argument-hint: [optional focus, e.g. "just the dashboard screen"]
---

**Phase 2.5 · Design - what does it look like, and how does it feel to use?**

$ARGUMENTS

**Gate check first.** The PRD must exist (`spec/02-Product/PRD.md`) - you design
the screens the product spec names, not screens invented here. If it doesn't,
stop and run `/define`. The positioning (`spec/01-Company/POSITIONING.md`) should
exist too, since it carries the brand's personality; note it if it's missing and
proceed on what you have.

## Spawn the design lead

Use the **design-lead** subagent to produce, into `spec/06-Design/`:
- `DESIGN-BRIEF.md` - the art direction *and its reasoning*: the grounding (who
  the user is, their context, what the product is to them, the domain's visual
  language with real references), the two or three directions explored and the
  one committed to with why, the design thesis in a line, the palette as named
  hex values with each role justified, the type pairing and why, the layout and
  motion posture. Every choice traced to *this* product, so it could belong to
  no other.
- `DESIGN-SYSTEM.md` - the tokens (color roles, type scale, spacing, radius,
  elevation, motion) and the component inventory with their states. What the
  frontend stack must implement; the architect reads it when choosing the UI layer.
- `mockups/<screen>.html` - real, self-contained, *polished* HTML mockups of the
  key screens, with **real content (no lorem)**, covering **every state**
  (loading, empty, partial, error, offline), openable in a browser with a
  double-click.

**Hold the bar. This is the phase where AI ships a generic look by default, and a
generic look is worse than none.** The design lead must ground the direction in
the product's own world, explore real alternatives before committing, and pass
its own anti-generic self-critique (could this be mistaken for another product?
does it hit an AI-default pattern with no reason? is every choice justified?)
before anything is shown. If the result reads like the default AI theme, it goes
back.

## Preview, record, and gate

- Offer to open the mockups so the developer can see them, not just read about them.
- Update the doc register.
- Give a **short, plain recap** (2 to 4 lines, no jargon): the good news, the one thing to watch with its fix, and the single next step. The full detail is in the documents and the guide (`python tools/keel.py`) - point there, do not paste it. The recap covers: the design thesis in a sentence,
  the palette and type, and the screen or state the design lead flagged as hardest
  to build well.
- **The gate:** propose `/architect` next - the architect should know the design
  system (the component library, the theming needs) before choosing the frontend
  stack. Wait for the yes.

*Design and architecture inform each other; if the stack is already fixed, design
can also run in parallel with the build. Say which applies here.*
