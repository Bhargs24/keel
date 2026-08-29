#!/usr/bin/env bash
CH=$(git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null)
echo "$CH" | grep -q '\.go$'    && (cd services/core-api 2>/dev/null && gofmt -w . && golangci-lint run --fix)
echo "$CH" | grep -q '\.py$'    && (ruff format . >/dev/null 2>&1; ruff check --fix . >/dev/null 2>&1)
echo "$CH" | grep -qE '\.tsx?$' && (cd apps/web 2>/dev/null && npx biome check --write .)
echo "$CH" | grep -q '\.dart$'  && (cd apps/student 2>/dev/null && dart format . && dart analyze --fatal-infos)
exit 0
