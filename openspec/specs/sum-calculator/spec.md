# Sum Calculator Specification

## Purpose

Defines the `sum-calculator` capability: an MCP tool (`calcular_suma`) that accepts two numeric operands and returns their sum as structured content. The tool coexists with the existing `consultar_estado_sistema` tool on the same MCP v2 server (`servidor_mcp.py`).

## Requirements

### Requirement: Tool Registration

The system MUST register `calcular_suma` as an MCP tool via `@mcp.tool()` on the `MCPServer` instance in `servidor_mcp.py`.

#### Scenario: Tool appears in server listing

- GIVEN the MCP server is started
- WHEN a client calls `list_tools`
- THEN the response includes `calcular_suma` alongside the existing `consultar_estado_sistema`
- AND the tool count is exactly 2

#### Scenario: Tool metadata matches declared schema

- GIVEN the MCP server is started
- WHEN a client inspects `calcular_suma` metadata
- THEN the `inputSchema` declares `a` and `b` as `number` type
- AND both `a` and `b` are required

### Requirement: Summation Behavior

The tool SHALL accept two required float parameters (`a`, `b`) and return the arithmetic sum as a float.

#### Scenario: Sum of two positive integers

- GIVEN the tool is called with `a=2, b=3`
- WHEN the tool executes
- THEN the result is `5.0`

#### Scenario: Sum of negative and positive values

- GIVEN the tool is called with `a=-1.5, b=4.5`
- WHEN the tool executes
- THEN the result is `3.0`

#### Scenario: Sum of two zero operands

- GIVEN the tool is called with `a=0, b=0`
- WHEN the tool executes
- THEN the result is `0.0`

#### Scenario: Sum producing a negative result

- GIVEN the tool is called with `a=-10, b=3`
- WHEN the tool executes
- THEN the result is `-7.0`

#### Scenario: Large-magnitude operands

- GIVEN the tool is called with `a=1e15, b=1e15`
- WHEN the tool executes
- THEN the result is `2e15` (float precision rules apply)

### Requirement: Input Validation via SDK

The system MUST rely on SDK/Pydantic `inputSchema` validation for the two operands. The tool MUST NOT implement custom validation logic.

#### Scenario: Non-numeric input rejected

- GIVEN the tool is called with `a="hello", b=3`
- WHEN SDK validation evaluates the arguments
- THEN the call is rejected with a type error
- AND no custom error message is produced by the tool itself

#### Scenario: Missing required parameter rejected

- GIVEN the tool is called with `a=5` and `b` omitted
- WHEN SDK validation evaluates the arguments
- THEN the call is rejected with a missing-parameter error

#### Scenario: Numeric string coerced by SDK

- GIVEN the tool is called with `a="5", b=3`
- WHEN SDK validation evaluates the arguments
- THEN Pydantic coerces `"5"` to `5.0` and the tool receives valid floats
- AND the result is `8.0`

### Requirement: Structured Output Shape

The tool MUST return a float, which the SDK auto-publishes as `outputSchema` with `{result: number}` and delivers in `structured_content`.

#### Scenario: Structured content contains result key

- GIVEN the tool is called with `a=2, b=3`
- WHEN the tool returns `5.0`
- THEN the response `structured_content` contains `{"result": 5.0}`
- AND the `outputSchema` declares `result` as `number`

### Requirement: Coexistence with Existing Tool

Adding `calcular_suma` MUST NOT alter the behavior, registration, or availability of the existing `consultar_estado_sistema` tool.

#### Scenario: Existing tool still callable

- GIVEN the MCP server is started with both tools registered
- WHEN a client calls `consultar_estado_sistema`
- THEN the response is `"Todos los servicios locales están funcionando al 100%."`
- AND no error or behavioral change occurs

### Requirement: Spanish Naming Convention

The tool function name, docstring, and any identifiers MUST use Spanish, consistent with the existing convention in `servidor_mcp.py`.

#### Scenario: Docstring is in Spanish

- GIVEN the tool definition in `servidor_mcp.py`
- WHEN the function docstring is inspected
- THEN the docstring text is in Spanish (e.g., "Calcula la suma de dos números.")
