# Archive Report: calculadora-suma

**Change**: calculadora-suma
**Archived**: 2026-09-08
**Mode**: openspec
**Cycle Status**: Complete

## Executive Summary

Added `calcular_suma(a: float, b: float) -> float` MCP tool to `servidor_mcp.py`. Single-file, stateless addition (+7 lines). All 6 requirements and 13/13 spec scenarios verified compliant via independent stdio MCP smoke. No blockers, no critical findings, no scope drift.

## Artifacts Produced (final state at close)

| Artifact | Path (archived) | Status |
|----------|----------------|--------|
| Proposal | `archive/2026-09-08-calculadora-suma/proposal.md` | ✅ Complete |
| Delta Spec | `archive/2026-09-08-calculadora-suma/specs/sum-calculator/spec.md` | ✅ Complete (6 reqs, 13 scenarios) |
| Design | `archive/2026-09-08-calculadora-suma/design.md` | ✅ Complete |
| Tasks | `archive/2026-09-08-calculadora-suma/tasks.md` | ✅ 7/7 tasks complete |
| Verify Report | `archive/2026-09-08-calculadora-suma/verify-report.md` | ✅ PASS, 13/13 compliant |

## Source of Truth Updated

| Domain | Action | Path |
|--------|--------|------|
| sum-calculator | Created (promoted from delta) | `openspec/specs/sum-calculator/spec.md` |

Delta spec promoted to main spec — `openspec/specs/` was empty prior to this archive; the delta IS the full capability spec.

## Task Completion Gate

All 7 implementation tasks marked `[x]` in `tasks.md`. Gate passes. No stale checkboxes.

## Verification Summary

- **Verdict**: PASS
- **Requirements**: 6/6 compliant
- **Scenarios**: 13/13 compliant
- **Blockers**: 0
- **Critical findings**: 0
- **Evidence revision**: sha256:d38fc3da2d6e6c7cf336d3457664a993ac6fb79b3793c9bd9b59d9e54a8da1b1
- **Fresh smoke**: Independently re-run by sdd-verify; all scenarios reproduced (not blindly trusted from apply evidence)

## File Changes (code)

| File | Lines | Description |
|------|-------|-------------|
| `servidor_mcp.py` | +7 (13 → 18) | Added `calcular_suma` tool: decorator + function + docstring + return |

No other files modified. No packaging, dependencies, test files, or config changes.

## Mechanical Copy Verification

### Spec Sync (delta → main)
- Source: `openspec/changes/calculadora-suma/specs/sum-calculator/spec.md`
- Destination: `openspec/specs/sum-calculator/spec.md`
- Method: `Copy-Item` (PowerShell)
- Readback: SHA256 match confirmed — source and destination byte-identical

### Archive Move
- Source: `openspec/changes/calculadora-suma/`
- Destination: `openspec/changes/archive/2026-09-08-calculadora-suma/`
- Pre-move snapshot created at OS temp directory; EXIT trap removed snapshot after verification
- Readback: All 7 files byte-identical between snapshot and archive destination
- Source directory confirmed absent after move

## Scope Drift Check

- ✅ Only `servidor_mcp.py` modified outside openspec/
- ✅ No scratch files, temp scripts, or test files remain
- ✅ No new dependencies, no packaging changes

## Risks

| Risk | Status | Notes |
|------|--------|-------|
| No test runner | Accepted | Verify used stdio MCP smoke; sufficient for 7-line change |
| Float display (4.0 vs 4) | Accepted tradeoff | Documented in spec scenarios; machine-friendly |

## Recommendations for Future Changes

- SDK v2 Python uses snake_case attributes (`input_schema`, `is_error`) on wire JSON uses camelCase (`inputSchema`, `isError`); future explore/verify scripts should use snake_case
- `ClientSession` requires `initialize()` before `list_tools` in mcp 2.x

## Key Learnings

1. MCP SDK 2.1.1 auto-generates inputSchema and outputSchema from Python type annotations without explicit config.
2. Pydantic lax mode coerces numeric strings to float before the tool body runs, enabling `"5" + 3 = 8.0`.
3. JSON cannot represent `inf`, so `1e308 + 1e308` fails client-side validation despite correct server-side computation.
4. MCP ClientSession must call `initialize()` before `list_tools` or the server returns "Invalid request parameters".
5. Single-file MCP servers with two tools remain within a 400-line review budget comfortably.
