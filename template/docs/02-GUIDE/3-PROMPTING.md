# How to talk to it

*Class: **LIVING** · Last-updated: 2026-08-30 · Review-by: 2026-10-30 · Owner: <who>. How to hold the conversation with Keel so it builds the thing you meant. The shift that matters: you are not writing clever prompts, you are making decisions and pointing at where the truth is written. Most of the work happens before you type.*

---

## The conversation runs both ways

Keel talks the way a good mentor does: **one short question at a time, in plain words, and it waits for the answer** before the next one. It never hands you a numbered list of decisions or a wall of steps. That is a law it runs on every message, and it is there so a first-time builder never freezes.

You get the most out of it by answering in the same spirit. Take the questions one at a time. Keep your answers short and honest. Do not try to front-load ten decisions into your first message; the specialists surface the rest as they go, and a decision made too early, on too little, is a decision the whole plan then leans on wrongly.

---

## How to give it a good idea

The single best thing you can do at the start is hand it something specific.

- **Real beats abstract.** "A booking tool for pet groomers that stops double-booking" can be researched. "A SaaS app" cannot.
- **Say who it is for**, even loosely. "Solo groomers who run their books in a paper diary" points the research at a real person.
- **Say what makes it different, or say you are not sure.** "I think the wedge is same-day rebooking" is useful. So is "I do not know yet what makes it different", because that honestly shapes what the market-researcher goes looking for.

One or two sentences is plenty. `/keel` asks the couple of questions it still needs, one at a time, and starts the research.

---

## The anatomy of a good build prompt

Once you are past the pipeline and into the build, the highest-leverage habit is citing the spec. Six parts. Small tasks use the first three; anything above trivial uses all six.

| Part | Why | Example |
|---|---|---|
| **1. The spec pointer** | so nothing is guessed | "Implement `spec/02-Product/prd/M1.md`, the login flow." |
| **2. The task, in plain language** | intent, not implementation | "The user signs in with email and a one-time code." |
| **3. Constraints** | the rules it must not break | "A failed code never reveals whether the email exists." |
| **4. Out of scope** | bounds the exploration, which is where sessions die | "Do not touch billing. Do not add social login." |
| **5. Done when** | the external judge | "Done when the acceptance criteria in the spec pass." |
| **6. The output you want** | plan, diff, options | "Plan first. Do not write code until I approve." |

**The out-of-scope line is the most skipped and the most valuable.** An AI left unbounded explores, and exploration is what fills its context with noise until it goes dull.

---

## The templates

### Giving it the idea

```
/keel "<your idea in one or two sentences, with who it is for>"
```

Then answer its questions one at a time. That is the whole intake.

### Starting a build task

```
Read spec/<path>, the <section>.

Task: <one sentence in plain language>
Constraints: <the rule that bites here>
Out of scope: <what not to touch>
Done when: <the testable condition from the spec>

Plan first. Show me the files, the approach, and the tests.
Do not write code until I approve.
```

### Debugging

```
Symptom: <exactly what you saw, the error verbatim, no interpretation>
Expected: <what should happen, and which spec says so>
Already ruled out: <what you checked>

Find the root cause before proposing a fix. If you are not sure, say so
and tell me what would confirm it.
```

Note the shape: **do not hand it your diagnosis first.** An AI will tend to confirm your theory rather than test it, and you can lose an hour to a wrong hypothesis stated confidently.

### Correcting a document a specialist wrote

```
In <the document>, the <specific thing> is wrong: <what you expected instead,
and why>. Fix that section and anything downstream that depended on it.
```

### Ending a session

```
/wrap
```

It logs the honest state, writes the handoff, keeps the documents true, runs the checks, and commits. You do not compose this by hand.

### The confirmation, after any task

```
What changed, what did you skip, and what are you unsure about?
```

The third part is the one that pays. It will tell you what it guessed at, if you ask.

---

## When to push back

**Disagree with `/next`? Say why.** It ranks the candidates and shows its reasoning precisely so you can overrule it with information. It may know something you do not (a dependency, a blocked teammate); you may know something it does not (a demo on Friday). If you repeat your choice, it does it.

**When a specialist's document feels wrong, name the specific thing.** "The market size looks too high" gives it nothing to act on. "The market size assumes every groomer pays monthly, but half of them are seasonal" gives it the exact thread to pull. And remember the paired-honesty law cuts both ways: if it names a weakness with no fix, or a fix with no weakness, that is a bug in the answer, and you can ask for the missing half.

---

## How to correct it: re-plan, do not patch

If the direction is wrong, go back and re-plan rather than steering in the middle of an implementation. Mid-stream correction is how a clean session becomes a mess, because the failed attempt stays in its context and keeps influencing the next turn. `CHANGE-PROTOCOL.md` says which changes need plan mode first: anything above the smallest tier. Pour the effort into the plan so the build can be one shot.

---

## Rules for talking to it

- **Say what, not how.** "Validate the email per the spec" beats "write a regex". You hired the implementation; keep the intent.
- **One task per prompt.** Three tasks in one prompt produce three half-done things and a polluted context.
- **Give failing output verbatim.** Paste the error, the log line, the test output. The detail you drop is often the answer.
- **Name the file.** "The login handler" costs a search. The path costs nothing.
- **Ask for a plan when the task is bigger than a function.** Reading a plan takes a minute and saves an hour.
- **Ask for options when you do not know the answer.** "Give me two approaches with trade-offs" beats accepting the first idea in silence.
- **Tell it to stop when unsure.** "If the spec does not cover this, stop and ask rather than deciding." It complies with this readily, and it is the best defence against confident invention.

---

## Anti-patterns

| Do not | Because | Instead |
|---|---|---|
| "Make it better" | no definition of better; you get a random refactor | name the property: faster, fewer branches, testable |
| "Fix all the bugs" | unbounded, and it will invent bugs to fix | one symptom, one prompt |
| "You are wrong, redo it" | no new information, so you get a different wrong answer | say what specifically was wrong and what you expected |
| Describing the spec from memory | drift between what you said and what is written | point at the file, or run `/spec` |
| Rolling a stale session into the next task | context rot; the quality is already gone | `/wrap`, `/clear`, `/start` |
| Accepting a big diff unread because it looks done | it can look done and solve the wrong problem | check it against the spec, or run `/audit` |

---

## Before you type, check

- [ ] I gave it a real, specific idea, or I am citing a real spec section
- [ ] I said what is out of scope
- [ ] I know what "done" looks like, and it is testable
- [ ] The session is fresh, or still sharp
- [ ] For anything large, I am asking for a plan first
