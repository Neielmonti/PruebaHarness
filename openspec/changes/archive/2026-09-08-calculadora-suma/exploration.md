# Exploration: calculadora-suma

Change: add a simple sum calculator to the existing Python MCP server.
Date: 2026-09-06
Phase: sdd-explore (artifact store: openspec)

## Current State

The workspace contains a single Python MCP server module, `servidor_mcp.py` (13 lines), with one registered
tool. Verified against the installed SDK (`mcp` **2.1.1**, `mcp-types` 2.1.1, Python 3.14.7):

```python
from mcp.server.mcpserver import MCPServer       # NEW v2 "MCPServer" API (not FastMCP)

mcp = MCPServer("MiServidorLocal")              # server name set; version defaults to ""

@mcp.tool()                                     # decorator MUST be called with parens
def consultar_estado_sistema() -> str:
    """Devuelve el estado operativo de los servicios locales."""
    return "Todos los servicios locales están funcionando al 100%."

if __name__ == "__main__":
    mcp.run()                                   # default transport: stdio
```

Verified SDK mechanics that constrain the design (read from installed `mcp` 2.1.1 source):

- **Tool registration**: `@mcp.tool()` / `mcp.add_tool(...)` build a Pydantic argument model from the
  function signature via `func_metadata`. The generated JSON Schema becomes the tool's `inputSchema`.
  Unannotated parameters are treated as **strings** in the schema — annotations are mandatory for typed inputs.
  Duplicate tool names warn and keep the first registration.
- **Input validation is free**: arguments are validated against the Pydantic model
  (`Tool.run` → `validate_arguments`). A `ValidationError` surfaces as a `ToolError` →
  `CallToolResult(isError=true)` with the message text. Numeric strings such as `"5"` are pre-parsed
  (`pre_parse_json`) and coerced by Pydantic lax mode.
- **Output shape is auto-detected from the return annotation** (`structured_output=None` default):
  - `-> str` (the existing tool today) publishes `outputSchema` `{result: string}` and returns both
    unstructured text AND `structured_content={"result": ...}` — the current tool is already "structured".
  - `-> float`/`-> int` publishes `outputSchema` `{result: number}` (+ wrap) and returns
    `structured_content={"result": <sum>}` plus text content with the JSON-dumped value.
  - `-> dict[str, float]` publishes the dict schema directly (RootModel) and returns
    `structured_content={"suma": <sum>}` plus JSON text — no wrap.
  - `structured_output=False` disables the output schema; only unstructured text content is returned.
- **Error handling**: uncaught exceptions in a tool body become `UnexpectedToolError` →
  `isError` result (message does not leak the exception text). Raised `ToolError` values pass through
  as `isError`.
- **Tool naming** (SEP-986): `[A-Za-z0-9._-]{1,128}`, case-sensitive; spaces/commas warn. Spanish snake_case
  names like `calcular_suma` or `sumar` are valid.
- **Transport**: `mcp.run()` defaults to **stdio**; SSE and streamable-HTTP are opt-in. No config change needed.

Project conventions (from `openspec/config.yaml` + init discovery):

- Tech stack: loose Python module; **no packaging** (no pyproject.toml/requirements.txt), **no tests**,
  **no test runner** (strict TDD: false, `test_command: ""`), no linter/formatter config.
- Code identifiers, docstrings, and responses are **Spanish** (`consultar_estado_sistema`,
  "Devuelve el estado operativo...").
- Workspace is NOT a git repo; delivery is single-pr; review budget 400 lines.

## Affected Areas

- `servidor_mcp.py` — the new summing tool is registered here; this is the only file that needs changing.
- `openspec/changes/calculadora-suma/` — SDD artifacts for this change (this file, later proposal/spec/design/tasks/verify).
- No new dependencies, no packaging metadata, no tests. Verify phase will need a non-`test_command` strategy
  (e.g., run a stdio JSON-RPC session via `mcp.client`, or `python -c` smoke import) since none is configured.

## Approaches

1. **Add a two-operand tool to `servidor_mcp.py` (recommended)**
   `@mcp.tool()` function, e.g. `calcular_suma(a: float, b: float) -> float`, returning the numeric sum.
   SDK auto-publishes `inputSchema` `{a: number, b: number}` (required) and `outputSchema` `{result: float}`,
   and returns `structured_content={"result": ...}`.
   - Pros: matches the existing file exactly (same decorator, same module, same Spanish convention);
     ~10–15 line diff; validation and error mapping come free from the SDK; zero new dependencies;
     trivial rollback (delete the function); far under the 400-line budget.
   - Cons: none of substance. The `2 + 2 = 4.0` float display is a cosmetic tradeoff (fix by using
     `int` params/return, or by returning a dict/string).
   - Effort: Low.

2. **N-operand (list) tool**
   `calcular_suma(numeros: list[float]) -> float` — accepts a variable number of numbers in one argument.
   - Pros: one call for any count; idiomatic for LLM callers (single list argument).
   - Cons: widens scope beyond the literal "sums two numbers" ask; slightly richer schema; optional
     length/count caps become a validation question (e.g., reject empty lists via `min_length=1`).
   - Effort: Low–Medium.

3. **Separate calculator module + binding**
   New `calculadora.py` with pure logic imported by `servidor_mcp.py`, or a second standalone server file.
   - Pros: separates pure math from MCP binding; unit-testable later without an MCP harness.
   - Cons: over-engineering for a single addition operation in a harness with no test runner to justify
     the seam; a second entry point complicates "which file do I run".
   - Effort: Medium.

4. **Human-string return style (`-> str`)**
   e.g. `"La suma de 2 y 3 es 5."` — matches the existing tool's human-readable style.
   - Pros: stylistically consistent with `consultar_estado_sistema`.
   - Cons: the numeric value is buried inside prose; `structured_content` still carries `{"result": "..."}`,
     but consumers must parse text for the number. Weaker for a calculator whose job is producing a value.
   - Effort: Low (can be combined with approach 1/2 as a return-shape option).

## Recommendation

**Approach 1** — add a two-operand sum tool to the existing `servidor_mcp.py`, keeping the file's Spanish
naming convention. Concretely, the shape to propose:

```python
@mcp.tool()
def calcular_suma(a: float, b: float) -> float:
    """Calcula la suma de dos números."""
    return a + b
```

Rationale: the change is a minimal, greenfield addition; the SDK v2 API already provides input schema
generation, validation, structured output, and error mapping — the tool is a pure function plus a decorator.
Approach 2 is the natural extension if N operands are wanted; approach 3 adds structural cost the harness
does not currently benefit from.

Design decisions to settle in the proposal phase (each has a recommendation):

- **Tool name**: `calcular_suma` (recommended, Spanish convention) vs `sumar` vs English `sum`.
- **Operands**: exactly two (`a`, `b`) — recommended default — vs N-number list (`numeros`).
- **Numeric type**: `float` (recommended: accepts integers, decimals, numeric strings) vs `int`
  (integer-only results; note Pydantic lax mode silently truncates float input like `2.5` → `2`).
- **Return shape**: numeric `-> float` (recommended, machine-friendly structured `{result}`) vs
  `-> dict[str, float]` (`{"suma": ...}`, explicit field name) vs `-> str` human message (matches
  existing tool style but buries the value).
- **Validation**: rely on SDK/Pydantic `inputSchema` validation (recommended — no domain constraints
  exist for a two-operand sum). Only the N-operand variant would add explicit rules (e.g.,
  `min_length=1` for the list).

## Risks

- **No test infrastructure**: there is no test command, so sdd-verify cannot run a runner-based check.
  Mitigation: define a smoke verification (import the module + call the tool through a stdio MCP session
  using `mcp.client`, or `python -m` import check) in proposal/verify. The change is small enough that a
  manual smoke is adequate.
- **Ambiguity of scope**: two operands vs N operands and integer vs float affect the spec scenarios;
  these must be locked in the proposal before specs are written.
- **SDK mechanics surprises**: `@mcp.tool` without parens raises `TypeError`; unannotated parameters are
  schema'd as strings; `-> str` auto-publishes structured output (existing tool already does). All verified
  against mcp 2.1.1 — no risk if the proposal follows the annotated-parameter pattern.
- **Cosmetic float display**: `2 + 2` yields `4.0` with float types; acceptable, or avoid via `int` typing.
- **Review budget**: change is ~10–25 lines; 400-line budget risk is Low; single-pr delivery is fine.

## Ready for Proposal

Yes. The proposal should:
1. Confirm the four open design decisions above (recommendations: `calcular_suma`, two operands, `float`,
   `-> float`).
2. Define scope as "add one tool to `servidor_mcp.py`; no packaging/test/dependency changes."
3. Include a trivial rollback plan (remove the added function).
4. Note the verify strategy gap (no test command; propose stdio smoke).