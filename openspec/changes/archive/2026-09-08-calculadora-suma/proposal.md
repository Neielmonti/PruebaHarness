# Proposal: calculadora-suma

## Intent

The workspace is a single-file MCP v2 server (`servidor_mcp.py`) exposing one local tool. The user wants a sum-calculator tool that MCP clients can call to add two numbers. This is a greenfield, minimal addition: one new tool on the existing server, relying on the SDK's free input validation and structured output.

## Scope

### In Scope
- Add `calcular_suma(a: float, b: float) -> float` to `servidor_mcp.py` via `@mcp.tool()`.
- Rely on SDK/Pydantic `inputSchema` validation for the two operands; no custom domain constraints.
- Spanish docstring/identifier, matching the file's convention.
- Verify via stdio MCP smoke (e.g., `mcp.client` session or `python -c` import+call) since no test runner exists.

### Out of Scope
- N-operand/list variant (`numeros: list[float]`), packaging metadata, new dependencies, test files, config or other file changes.
- Custom validation rules beyond SDK defaults; `int`/`str`/`dict` return variants.

## Capabilities

### New Capabilities
- `sum-calculator`: the `calcular_suma` MCP tool — two required float operands (`a`, `b`), numeric float result returned as structured content `{result: <sum>}`, SDK/Pydantic validated inputs, Spanish naming consistent with the module.

### Modified Capabilities
None — `openspec/specs/` is empty; no existing spec-level behavior changes.

## Approach

Adopt exploration Approach 1. Append to `servidor_mcp.py`:

```python
@mcp.tool()
def calcular_suma(a: float, b: float) -> float:
    """Calcula la suma de dos números."""
    return a + b
```

SDK 2.1.1 mechanics (verified in exploration): annotations generate `inputSchema` (`a: number`, `b: number`, both required); Pydantic validates arguments and pre-parses numeric strings (`"5"` -> 5.0); `-> float` auto-publishes `outputSchema` `{result: number}` and returns `structured_content={"result": ...}`. Pattern mirrors the existing tool's decorator usage; no transport or config change.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `servidor_mcp.py` | Modified | Add `calcular_suma` tool (~7 lines) |
| `openspec/changes/calculadora-suma/` | New | SDD artifacts (proposal, later spec/design/tasks/verify) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| No test runner for verify | Med | Verify uses stdio MCP smoke; change is ~7 lines |
| Float display cosmetic (`2+2` -> `4.0`) | Low | Accepted tradeoff; noted in spec scenarios |
| SDK misuse (missing parens, missing annotations) | Low | Pattern copied from verified existing tool |

## Rollback Plan

Delete the `calcular_suma` function from `servidor_mcp.py`. Single-file, stateless change — no migration, data, or config to revert.

## Dependencies

- `mcp` 2.1.1 + `mcp-types` 2.1.1 (installed), Python 3.14.7.

## Success Criteria

- [ ] `calcular_suma` registered; `list_tools` shows 2 tools with required schema `{a: number, b: number}`
- [ ] Stdio smoke call `calcular_suma(a=2, b=3)` returns `5.0` with `structured_content={"result": 5.0}`
- [ ] `consultar_estado_sistema` still works and the module imports cleanly