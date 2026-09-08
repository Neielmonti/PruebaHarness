from mcp.server.mcpserver import MCPServer

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

if __name__ == "__main__":
    mcp.run()