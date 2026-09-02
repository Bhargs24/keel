# Security policy

## Reporting

Please report vulnerabilities privately via
[GitHub security advisories](https://github.com/Bhargs24/keel/security/advisories/new)
rather than a public issue. You will get an acknowledgement within a week.

## Scope notes

- `keel` writes only into the target folder you give it, runs no network
  code of its own, and never reads or transmits credentials.
- The cockpit and the board bind to `127.0.0.1` only; the board additionally
  refuses cross-origin writes.
- The bundled trespass copy analyzes SQL text; it never connects to a
  database. Report trespass findings upstream:
  https://github.com/Bhargs24/trespass/security
