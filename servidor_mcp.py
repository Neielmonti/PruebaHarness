from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

# Inicializar el servidor MCP v2
mcp = MCPServer("MiServidorLocal")

# Definir la herramienta
@mcp.tool()
def consultar_estado_sistema() -> str:
    """Devuelve el estado operativo de los servicios locales."""
    return "Todos los servicios locales están funcionando al 100%."

@mcp.tool()
def calcular_suma(a: float, b: float) -> float:
    """Calcula la suma de dos números."""
    return a + b

@mcp.tool()
def calcular_division(a: float, b: float) -> float:
    """Divide a entre b."""
    if b == 0:
        raise ToolError("No se puede dividir por cero")
    return a / b

if __name__ == "__main__":
    mcp.run()