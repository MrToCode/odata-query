# OData Query Fork PR Migration Plan v1

**Date:** 2026-02-18  
**Target Fork:** `/Users/aturner/Development/Git/TcProjects/MrToCode/odata-query`  
**Upstream:** `gorilla-co/odata-query`  
**Scope:** Migrate only upstream PRs that benefit TC implementation

---

## 1. Objective

Adopt upstream changes that directly improve TC OData integration quality while avoiding unrelated dependency churn.

Recommended intake set:

1. PR #65: `feat: pass model to apply` -> **migrate now**
2. PR #60: `Fix UUID handling in OData queries` -> **migrate selectively now**
3. PR #67: parameterized SQL visitors -> **defer** (not needed for ORM-first service path)

---

## 2. AI Agent Operating Rules

1. Never force reset local branches.
2. Never auto-merge lockfile or dependency bumps unless explicitly approved.
3. Prefer file-level patching/cherry-pick over full PR merge.
4. Validate each migrated PR independently before stacking next PR.
5. Produce one commit per upstream PR migration for auditability.

---

## 3. Branch Strategy

Use one integration branch per upstream PR, then a final consolidation branch.

1. `ai/pr/parent/pr65-pass-model`
2. `ai/pr/parent/pr60-uuid-fix`

when complete the tasks then merge into `tc/master`
---

## 4. Pre-Flight Checklist (Agent)

Run in fork repo:

```bash
git -C /Users/aturner/Development/Git/TcProjects/MrToCode/odata-query fetch --all --prune
git -C /Users/aturner/Development/Git/TcProjects/MrToCode/odata-query checkout tc/master
git -C /Users/aturner/Development/Git/TcProjects/MrToCode/odata-query pull --ff-only origin tc/master
```

Validation baseline:

```bash
cd /Users/aturner/Development/Git/TcProjects/MrToCode/odata-query
poetry install --extras sqlalchemy --extras testing
pytest tests/integration/sqlalchemy -q
pytest tests/unit -q
```

If baseline fails, stop and log failures before migrating PRs.

---

## 5. PR #65 Migration Runbook (Adopt)

### 5.1 Why it helps TC

TC endpoints will frequently query from joins/relationship-heavy selects.  
Explicit model selection removes ambiguous root-model inference in shorthand usage.

### 5.2 Upstream files touched

- `odata_query/sqlalchemy/shorthand.py`
- `tests/integration/sqlalchemy/test_querying.py`

### 5.3 Step-by-step

1. Create branch:

```bash
git checkout -b codex/pr65-pass-model
```

2. Pull upstream patch for traceability:

```bash
curl -sL https://patch-diff.githubusercontent.com/raw/gorilla-co/odata-query/pull/65.patch -o /tmp/pr65.patch
```

3. Apply only intended files:

```bash
git apply --index --include=odata_query/sqlalchemy/shorthand.py --include=tests/integration/sqlalchemy/test_querying.py /tmp/pr65.patch
```

4. Manual review points:
- Ensure `apply_odata_query(..., model: Optional[Type[DeclarativeMeta]] = None)` exists.
- Ensure default behavior unchanged when `model` is omitted.
- Ensure existing SQLAlchemy 1.x compatibility path still works.

5. Test:

```bash
pytest tests/integration/sqlalchemy/test_querying.py -q
pytest tests/integration/sqlalchemy -q
pytest tests/unit -q
```

6. Commit:

```bash
git commit -m "feat(sqlalchemy): add explicit model override to apply_odata_query (upstream #65)"
```

### 5.4 Acceptance criteria

1. Existing tests pass.
2. New explicit-model test passes.
3. No dependency file changes in commit.

---

## 6. PR #60 Migration Runbook (Selective Adopt)

### 6.1 Why it helps TC

TC uses UUID-heavy schemas. Incorrect UUID literal typing can cause `uuid = varchar` failures on PostgreSQL.

### 6.2 Upstream files touched

- `odata_query/grammar.py`
- `odata_query/sqlalchemy/common.py`
- `tests/integration/sqlalchemy/test_odata_to_sqlalchemy_core.py`
- `tests/integration/sqlalchemy/test_odata_to_sqlalchemy_orm.py`
- `pyproject.toml` (upstream PR changes)
- `poetry.lock` (upstream PR changes)

### 6.3 Migration policy for this PR

Adopt logic changes only.  
Do **not** bring `poetry.lock` or dependency version churn unless required after validation.

### 6.4 Step-by-step

1. Create branch from latest `tc/master` (or cherry-pick on top of PR65 if stacking):

```bash
git checkout tc/master
git pull --ff-only origin tc/master
git checkout -b codex/pr60-uuid-fix
```

2. Pull upstream patch:

```bash
curl -sL https://patch-diff.githubusercontent.com/raw/gorilla-co/odata-query/pull/60.patch -o /tmp/pr60.patch
```

3. Apply only code/test files (exclude lock/dependency files):

```bash
git apply --index \
  --include=odata_query/grammar.py \
  --include=odata_query/sqlalchemy/common.py \
  --include=tests/integration/sqlalchemy/test_odata_to_sqlalchemy_core.py \
  --include=tests/integration/sqlalchemy/test_odata_to_sqlalchemy_orm.py \
  /tmp/pr60.patch
```

4. Compatibility hardening (required):
- Verify `Uuid` type import compatibility with fork support policy (`sqlalchemy ^1.4`).
- If `from sqlalchemy.types import Uuid` is unavailable in supported versions, add compatibility fallback:
  - preferred: feature-detect import and fallback to `literal(node.py_val)` with UUID object
  - avoid forcing global SQLAlchemy version bump.

5. Test matrix:

```bash
pytest tests/integration/sqlalchemy/test_odata_to_sqlalchemy_orm.py -q
pytest tests/integration/sqlalchemy/test_odata_to_sqlalchemy_core.py -q
pytest tests/integration/sqlalchemy -q
pytest tests/unit -q
```

6. Commit:

```bash
git commit -m "fix(sqlalchemy): preserve UUID typing in GUID literals (upstream #60 selective)"
```

### 6.5 Acceptance criteria

1. UUID equality filters compile with UUID-typed literals.
2. UUID `in (...)` filters compile and pass tests.
3. No `poetry.lock` or dependency changes included.

---

## 7. PR #67 Defer Plan (Not in current intake)

### Reason for defer

PR #67 targets SQL string visitors with parameterization.  
TC service path is SQLAlchemy ORM transpilation and execution, so immediate value is low.

### Re-evaluation trigger

Re-open #67 intake when any of these becomes true:

1. TC uses SQL visitor output in production path.
2. TC exposes raw SQL translation endpoint.
3. Security review requires parameterized SQL generation for non-ORM paths.

---

## 8. Validation and Handoff Checklist

After each PR migration branch:

1. `git show --name-only` confirms intended files only.
2. All targeted tests pass.
3. Document deltas in migration note file under fork (optional: `docs/changelog_tc.md`).
4. Open fork PR with title pattern:
   - `[TC intake] upstream #65 pass model`
   - `[TC intake] upstream #60 uuid handling`

Final rollup decision:

1. If both PRs pass independently, either:
   - merge both directly to `tc/master`, or
   - merge into `codex/pr-intake-rollup` and run full test suite once more.

---

## 9. Risks and Mitigations

1. **SQLAlchemy version drift risk** (PR #60):
   - Mitigation: no dependency bump by default; compatibility fallback for `Uuid`.
2. **Behavior change risk in model inference** (PR #65):
   - Mitigation: keep old inference path untouched, only add optional override.
3. **Patch context drift** if fork diverges:
   - Mitigation: apply by file and manually port hunks where needed.

---

## 10. Deliverables

1. Fork PR for upstream #65 migration.
2. Fork PR for upstream #60 selective migration.
3. Short migration report documenting:
   - what was imported
   - what was intentionally excluded
   - test evidence
   - any compatibility shims introduced
