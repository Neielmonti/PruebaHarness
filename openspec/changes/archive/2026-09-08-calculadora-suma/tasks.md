# Tasks: calculadora-suma

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~7 (+6 / -0) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Add `calcular_suma` tool | PR 1 | `python -c` import + call `calcular_suma(a=2, b=3)` | stdio MCP smoke session via `mcp.client` | Delete the added function; stateless single-file change |

## Phase 1: Core Implementation

- [x] 1.1 In `servidor_mcp.py`, append `@mcp.tool()`-decorated `calcular_suma(a: float, b: float) -> float` returning `a + b`, with Spanish docstring, placed after `consultar_estado_sistema` and before the `if __name__` block.

## Phase 2: Verification (stdio MCP smoke)

- [x] 2.1 Run a stdio MCP smoke: import `servidor_mcp.py` and confirm `list_tools` returns exactly 2 tools including `calcular_suma` with required schema `{a: number, b: number}` (spec R1; scenarios 1.1, 1.2).
- [x] 2.2 Call `calcular_suma(a=2, b=3)` over the smoke session: expect `5.0` with `structured_content={"result": 5.0}` and `outputSchema {result: number}` (spec R2/R4; scenarios 2.1, 5.1); also spot-check negative/zero paths (`a=-1.5,b=4.5` → 3.0; `a=0,b=0` → 0.0).
- [x] 2.3 Confirm SDK validation rejects non-numeric (`a="hello", b=3`) and missing args (`a=5`) with `isError=true`, and coerces numeric string `"5"` → `8.0` (spec R3; scenarios 3.1, 3.2, 3.3).
- [x] 2.4 Confirm `consultar_estado_sistema` still returns its unchanged response in the same session (spec R5; scenario 6.1) and the module imports cleanly.
- [x] 2.5 Confirm the `calcular_suma` docstring is Spanish (spec R6; scenario 7.1).

## Phase 3: Cleanup

- [x] 3.1 Remove any temporary smoke/scratch code and confirm `servidor_mcp.py` contains only the intended change; no packaging, deps, test, or config changes.
