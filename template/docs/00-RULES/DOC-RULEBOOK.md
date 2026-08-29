# The Document Rulebook

*Class: **LIVING** · Last-updated: · Owner: <who>. The laws for the front half - the business, product, and technical documents the specialists write. A hallucinated market size is as much a defect as an unhandled error.*

---

## 0 · The rigor standard (this is the bar the tool is judged on)

**Every document is a complete, deep, researched, cited, professional artifact - never a brief, a summary, or an outline of what a real one would contain.** If a person could not hand this document to an investor, an engineer, or a co-founder and have it stand on its own, it is not done.

Concretely, for every document:

- **Research the format first.** Before writing a PRD, a market analysis, a financial model, or a technical design, know what a genuinely good one of these contains, then write to *that*, in full. Do not invent a shape; use the professional standard for the artifact.
- **Write the whole thing, at real depth.** A master PRD is many pages of actual requirements, not a page of bullets. A market analysis shows the full sizing arithmetic and every competitor examined, not a paragraph. A financial model has the actual line items. "This section would cover X" is a failure; write X.
- **Cite as you go.** Every external fact carries its source **inline** - the name, the URL, and the date - and every document that makes factual claims ends with a **Sources** list. Use web search and real pages heavily; prefer primary sources. A claim with no citation and no `ASSUMPTION:` marker does not belong in the document.
- **Exhaustive, not indicative.** Every state, every edge case, every line item, every competitor, every risk. Completeness is the product; a gap is a defect the feasibility audit will find.
- **Standalone and cross-linked.** Each document reads on its own and cites the others as `[[DOC-NAME]]`. No document assumes the reader has the conversation you had.

This is what separates Keel's output from a chatbot's: not a summary of what you *should* write, but the actual, rigorous document, written religiously to standard and backed by research. Hold this bar on every file.

---

## 1 · Source-or-silence

**Every external claim is either sourced or not stated.** A market fact, a benchmark, a price, a competitor's behaviour, a cost - name the source, or don't write the number. A figure you cannot source is a figure you do not have; write "unknown, needs a data point" instead of inventing one.

Prefer primary sources - a company's own site, docs, and pricing page - over third-party summaries. Flag anything found only in an SEO article as unverified.

---

## 2 · Differentiate or don't ship

A positioning a competitor could copy word for word is not positioning. A product doc that lists features without tying each to a user need is a wish list. **Name the wedge - the thing true for you and false for them - or say plainly there isn't one yet.** An honest "no wedge here" is worth more than a confident me-too.

---

## 3 · Complete, not stub

The same rule as the code: a document that covers the easy 80% and stubs the hard 20% is not done. A PRD that specifies the happy path and skips the empty, error, and offline states has skipped the feature. A build roadmap with a step that depends on a later step is not a plan. **If a document can't be completed properly, say what's missing rather than papering over it.**

---

## 4 · Numbers are bottom-up and marked

- **Bottom-up, not top-down.** Build a number from units - a count, a price, a cost - never as a percentage of an analyst's headline.
- **Every assumption is marked** (`ASSUMPTION: …`) so the feasibility auditor can see exactly what rests on a guess and stress-test it.
- **No dates as inputs.** Size work in developer-weeks and dependency order; the calendar is an output of team size, never an input to scope.

---

## 5 · One source of truth

When two documents could disagree, one is authoritative and the other cites it. `THE-RULEBOOK.md` declares precedence when rules conflict; for product behaviour, the PRD module is authoritative over prose elsewhere; for the wire, the data model is authoritative. **Fix the loser in the same change** - a contradiction left in place is a trap for the next reader.

---

## 6 · Plain voice, honest headers

- **Plain voice.** No adjective doing the work of evidence. "Fast, powerful, revolutionary" says nothing; state what it does and let the reader conclude.
- **Every document carries an honest status header:** its class (LIVING or SNAPSHOT), the date, the owner, and - if LIVING - a review date. A document with no header is a document nobody owns.

---

## 7 · The two document classes

- **LIVING** - carries a review date and is expected to change. The rulebook, the PRD, the roadmap, the ownership map.
- **SNAPSHOT** - dated, and **never edited after that date**. Audits, decision records, the feasibility verdict. If a snapshot turns out wrong, it is *re-run* as a new dated document, never quietly corrected. An audit that gets edited after the fact is not a record of anything.

## Changelog

| Date | Change | Why | By |
|---|---|---|---|
| | created | | |
