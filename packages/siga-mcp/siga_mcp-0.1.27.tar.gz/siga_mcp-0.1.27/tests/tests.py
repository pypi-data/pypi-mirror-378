import asyncio
from siga_mcp.tools import buscar_informacoes_atendimentos_os


async def main() -> str:
    return await buscar_informacoes_atendimentos_os(
        codigo_atendimento="409720", codigo_analista="24142"
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado)
