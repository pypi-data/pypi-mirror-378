import asyncio
from siga_mcp.tools import excluir_atendimento_avulso


async def main() -> str:
    return await excluir_atendimento_avulso(
        **{"codigo_analista": "24142", "codigo_atendimento": 194972}
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado)
