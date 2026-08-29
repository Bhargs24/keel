#!/usr/bin/env bash
# Blocks a write that looks like it carries a secret.
if git diff -U0 2>/dev/null | grep -nEi \
  '^\+.*(api[_-]?key|secret|passwd|password|token|BEGIN [A-Z ]*PRIVATE KEY)[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"']{12,}' ; then
  echo "BLOCKED: this looks like a secret. Use the secret manager."
  echo "See 00-RULES/CODE-RULEBOOK.md section 5."
  exit 1
fi
exit 0
