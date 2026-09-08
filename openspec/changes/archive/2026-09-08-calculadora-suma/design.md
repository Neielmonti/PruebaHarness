# Design: calculadora-suma

## Technical Approach

Append one `@mcp.tool()`-decorated function to the existing single-file MCP server (`servidor_mcp.py`), following the exact pattern of the existing `consultar_estado_sistema` tool. `calcular_suma(a: float, b: float) -> float` returns `a + b`; the SDK (mcp 2.1.1) handles input schema generation, Pydantic validation, numeric-string coercion, error mapping (`isError`), and structured output `{result: number}` — no custom logic. The decorator must be invoked with parentheses (`@mcp.tool()`), annotations are mandatory for typed inputs, and the return annotation `-> float` drives the output schema. This maps to spec requirements 1–6 (Registration, Summation, Validation, Output Shape, Coexistence, Spanish Naming).

## Architecture Decisions

| Decision | Option chosen | Alternatives considered | Rationale |
|---|---|---|---|
| Placement | Append as a new method in `servidor_mcp.py` (after `consultar_estado_sistema`, before `if __name__`) | Separate `calculadora.py` module; second server file | Change is a single pure function; the file is only 13 lines; a seam adds structural cost the loose harness gains nothing from. Matches existing single-file convention. |
| Signature | `calcular_suma(a: float, b: float) -> float` | `numeros: list[float]`; `int` params; `-> str` message | Proposal locks scope to two operands with float (accepts ints, decimals, numeric strings). `int` truncates under Pydantic lax mode; human-string return buries the value. `float`/`-> float` is machine-friendly and produces `{result: number}`. |
| Validation | Rely on SDK/Pydantic `inputSchema`; no custom rules | `min_length`, manual type checks | No domain constraint exists for a two-operand sum; SDK validation is free and consistent with the existing tool's approach. |
| Naming | Spanish: function name `calcular_suma`, docstring "Calcula la suma de dos números." | English `sum`; `sumar` | Official codebase convention (Spanish identifiers/docstrings). SEP-986 accepts snake_case Spanish names. |
| Output shape | `-> float` (auto-published `outputSchema {result: number}` + `structured_content {"result": <sum>}`) | `-> dict[str, float]` (`{"suma": ...}`); `structured_output=False` | `-> float` gives a clean numeric structured result with zero explicit config; matches spec R5. |

## Data Flow

```
MCP client
   │  tools/call {name: "calcular_suma", args: {a: 2, b: 3}}
   ▼
mcp.tool() wrapper (SDK) ──► Pydantic validate_arguments ──► Tool.run
   │  invalid input → ValidationError → CallToolResult(isError=true)
   ▼
calcular_suma(a, b)  →  a + b  →  float  →  SDK post-process
   ▼
structured_content={"result": 5.0}  +  outputSchema {result: number}
   │
   ▼
MCP client
```

Numeric strings (e.g. `"5"`) are pre-parsed and coerced by Pydantic lax mode before reaching the function body.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `servidor_mcp.py` | Modify | Add ~7-line `calcular_suma` tool between `consultar_estado_sistema` and the `if __name__` block |

## Interfaces / Contracts

```python
@mcp.tool()
def calcular_suma(a: float, b: float) -> float:
    """Calcula la suma de dos números."""
    return a + b
```

- `inputSchema`: `{a: number (required), b: number (required)}` — auto-generated from annotations.
- `outputSchema`: `{result: number}` — auto-published from `-> float`.
- Error: invalid/missing args → SDK `CallToolResult(isError=true)`; no tool-level error text.

## Testing Strategy

No test runner exists (strict TDD false). Verify uses a stdio MCP smoke against the running server.

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Smoke (verify) | Tool registered + callable over stdio | `python -c` import + `mcp.client` session; `list_tools` shows 2 tools with schema `{a: number, b: number}`; call `calcular_suma(a=2, b=3)` → `5.0`, `structured_content={"result": 5.0}` |
| Coexistence | Existing `consultar_estado_sistema` still callable | Same smoke session: call existing tool, expect unchanged response |

Smoke exercises spec scenarios 1–6 (registration, sums, validation rejection, output shape, coexistence, Spanish docstring) by inspection of the SDK response.

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No migration required. Single-file, stateless addition; no data, config, or transport change. Rollback is deleting the added function.

## Open Questions

- None

## Review Budget

Change is ~7 authored lines (additions + deletions); 400-line budget risk is Low; single-pr delivery is appropriate.
