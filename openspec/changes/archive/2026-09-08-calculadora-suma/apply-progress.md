# Apply Progress: calculadora-suma

**Phase**: sdd-apply
**Date**: 2026-09-07
**Batch**: 1 (first and only batch)
**Mode**: Standard (strict_tdd false; no test runner)
**Delivery strategy**: single-pr (~7 lines; 400-line budget risk Low)
**Attempt lease**: token sha256:90867cfd17c7883ca34f9decbd9af9c370dffa298cf07b82cb8bec2e03b7613b

## Task Status (cumulative)

### Phase 1: Core Implementation

- [x] 1.1 In `servidor_mcp.py`, append `@mcp.tool()`-decorated `calcular_suma(a: float, b: float) -> float` returning `a + b`, with Spanish docstring, placed after `consultar_estado_sistema` and before the `if __name__` block.

### Phase 2: Verification (stdio MCP smoke)

- [x] 2.1 Run a stdio MCP smoke: import `servidor_mcp.py` and confirm `list_tools` returns exactly 2 tools including `calcular_suma` with required schema `{a: number, b: number}`. — **PASS**
- [x] 2.2 Call `calcular_suma(a=2, b=3)` over the smoke session: `5.0` with `structured_content={"result": 5.0}` and `outputSchema {result: number}`; negative/zero paths verified. — **PASS**
- [x] 2.3 SDK validation rejects non-numeric (`a="hello", b=3`) and missing args (`a=5`) with `isError=true`; numeric string `"5"` coerced → `8.0`. — **PASS**
- [x] 2.4 Existing `consultar_estado_sistema` returns unchanged response in same session; module imports cleanly. — **PASS**
- [x] 2.5 `calcular_suma` docstring is Spanish. — **PASS**

### Phase 3: Cleanup

- [x] 3.1 Removed all temporary smoke/scratch code; `servidor_mcp.py` contains only the intended change; no packaging, deps, test, or config changes. — **PASS**

## Work Unit Evidence (Hard Gate — all modes)

| Evidence | Required value |
|---|---|
| Focused test command and exact result | `python -c "from servidor_mcp import mcp, calcular_suma"` + in-process smoke (temp `_smoke_mcp.py`): import OK; `list_tools` count=2 (`consultar_estado_sistema`, `calcular_suma`); `calcular_suma(a=2,b=3)` → `content='5.0'`, `structured_content={'result': 5.0}`, `is_error=False`; `(a=-1.5,b=4.5)` → 3.0; `(0,0)` → 0.0; `(-10,3)` → -7.0; non-numeric/missing → SDK `ToolError` (Pydantic ValidationError: `float_parsing` / `missing`); `("5",3)` → 8.0; existing tool text unchanged; docstring `'Calcula la suma de dos números.'` — ALL PASS, exit 0 |
| Runtime harness command/scenario and exact result | True stdio MCP session over subprocess (temp `_smoke_stdio.py`): `python servidor_mcp.py` launched via `mcp.client.stdio`; `session.initialize()` → `server_info=name='MiServidorLocal'`; `list_tools` → count=2; wire calls: (2,3)→5.0, (-1.5,4.5)→3.0, (0,0)→0.0 all `isError=False` + `structured_content.result` matches; non-numeric and missing-b → `isError=True` with Pydantic error text; "5"+3 → 8.0 `isError=False`; `consultar_estado_sistema` → `'Todos los servicios locales están funcionando al 100%.'` `isError=False` — ALL PASS, exit 0 |
| Rollback boundary | Delete added function block (lines 12–16 of `servidor_mcp.py`): the `@mcp.tool()` decorator + `calcular_suma` definition + blank-line separator. Stateless, single-file addition; no other files touched. |

## Deviations from Design

None — implementation matches design.md exactly (placement, signature, `@mcp.tool()`, Spanish docstring, no custom validation).

## Issues / Discoveries

1. **Validation error surfaces as exception in-process, `isError=true` on the wire**: direct `mcp.call_tool()` on the server object raises `ToolError` wrapping Pydantic `ValidationError`; over a real stdio transport the framework serializes this into `CallToolResult(isError=true)` with the Pydantic message as text content. Spec R3 (scenarios 3.1/3.2) verified at the transport layer, which is what clients observe.
2. **SDK v2 attribute names are snake_case in Python** (`input_schema`, `output_schema`, `is_error`, `structured_content`); wire JSON uses camelCase (`inputSchema`, `isError`, `structuredContent`) via the client SDK models. Documented to save future verify/explore iterations.
3. **Infinity cannot cross the wire**: `1e308 + 1e308 → inf` computes fine server-side but the client SDK rejects `structured_content` validation (`None is not of type 'number'`) because JSON has no `inf`. Not a spec scenario; spec 2.5 (`2e15`) passes.
4. **`ClientSession` must call `initialize()` before `list_tools`** in mcp 2.x; otherwise `Invalid request parameters`.

## Smoke Evidence (exact commands + observed results)

### Command 1 — in-process smoke (temp script `_smoke_mcp.py`, removed after run)

```
[2.1] Import OK
[2.1] list_tools -> count=2, names=['consultar_estado_sistema', 'calcular_suma']
[2.1] calcular_suma input_schema = {"properties": {"a": {"title": "A", "type": "number"}, "b": {"title": "B", "type": "number"}}, "required": ["a", "b"], "title": "calcular_sumaArguments", "type": "object"}
[2.1] calcular_suma output_schema = {"properties": {"result": {"title": "Result", "type": "number"}}, "required": ["result"], "title": "calcular_sumaOutput", "type": "object"}
[2.2] calcular_suma(a=2, b=3) -> content='5.0', structured_content={'result': 5.0}, is_error=False
[2.2] calcular_suma(a=-1.5, b=4.5) -> content='3.0', structured_content={'result': 3.0}, is_error=False
[2.2] calcular_suma(a=0, b=0) -> content='0.0', structured_content={'result': 0.0}, is_error=False
[2.2] calcular_suma(a=-10, b=3) -> content='-7.0', structured_content={'result': -7.0}, is_error=False
[2.3] calcular_suma(a='hello', b=3) -> EXCEPTION: ToolError: ... 1 validation error ... a ... Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='hello', input_type=str]
[2.3] OK: Non-numeric input rejected by SDK/Pydantic validation
[2.3] calcular_suma(a=5) -> EXCEPTION: ToolError: ... 1 validation error ... b ... Field required [type=missing, input_value={'a': 5}, input_type=dict]
[2.3] OK: Missing required arg rejected by SDK (missing-parameter error)
[2.3] calcular_suma(a='5', b=3) -> structured_content={'result': 8.0}, is_error=False
[2.4] consultar_estado_sistema -> text='Todos los servicios locales están funcionando al 100%.', is_error=False
[2.5] calcular_suma.__doc__ = 'Calcula la suma de dos números.'
==================================================
ALL SMOKE CHECKS PASSED (2.1-2.5)
```

### Command 2 — true stdio MCP session over subprocess (temp script `_smoke_stdio.py`, removed after run)

```
> python _smoke_stdio.py
[init] server_info=name='MiServidorLocal' title=None version='' description=None website_url=None icons=None
[2.1] list_tools -> count=2
[2.1]   * consultar_estado_sistema => input_schema={"properties": {}, "type": "object", "title": "consultar_estado_sistemaArguments"}
[2.1]   * calcular_suma => input_schema={"properties": {"a": {"title": "A", "type": "number"}, "b": {"title": "B", "type": "number"}}, "required": ["a", "b"], "type": "object", "title": "calcular_sumaArguments"}
[2.1] OK: 2 tools; calcular_suma schema a=number,b=number, both required
[2.1] outputSchema = {"properties": {"result": {"title": "Result", "type": "number"}}, "required": ["result"], "type": "object", "title": "calcular_sumaOutput"}
[2.2] call_tool({'a': 2, 'b': 3}) -> text='5.0', structured_content.result=5.0, isError=False   PASS
[2.2] call_tool({'a': -1.5, 'b': 4.5}) -> text='3.0', structured_content.result=3.0, isError=False   PASS
[2.2] call_tool({'a': 0, 'b': 0}) -> text='0.0', structured_content.result=0.0, isError=False   PASS
[2.3] non-numeric a='hello' -> isError=True, content="Error executing tool calcular_suma: 1 validation error ... [type=float_parsing, input_value='hello', input_type=str] ..."   PASS
[2.3] missing b -> isError=True, content="Error executing tool calcular_suma: 1 validation error ... b ... Field required [type=missing, input_value={'a': 5}, input_type=dict] ..."   PASS
[2.3] numeric string a='5',b=3 -> isError=False, structured_content.result=8.0, text='8.0'   PASS
[2.4] consultar_estado_sistema -> text='Todos los servicios locales están funcionando al 100%.', isError=False   PASS
>>> FULL STDIO SESSION COMPLETE
```

### Command 3 — extra spec scenarios over stdio (temp script `_smoke_extra.py`, removed after run)

```
[extra] spec 2.4 negative result: args={'a': -10, 'b': 3} -> result=-7.0, isError=False  PASS
[extra] spec 2.5 large magnitude: args={'a': 1e15, 'b': 1e15} -> result=2e15, isError=False  PASS
```

## Final File State (after cleanup)

`servidor_mcp.py` (18 lines, +7 from original 13) — only change is the added `calcular_suma` tool:

```python
@mcp.tool()
def calcular_suma(a: float, b: float) -> float:
    """Calcula la suma de dos números."""
    return a + b
```

No packaging, deps, test, or config changes. No scratch files remain. Rollback: delete lines 12–16.

## Status

7/7 tasks complete. Ready for verify.