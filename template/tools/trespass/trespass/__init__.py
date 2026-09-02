"""trespass -- prove your tenants can't read each other's data.

A formal analyzer for Postgres / Supabase row-level security. It reads your
schema, models each policy in three-valued logic, and either *proves* that no
user can reach another user's rows or hands you the exact query that shows they
can.
"""

from __future__ import annotations

__version__ = "0.2.0"
