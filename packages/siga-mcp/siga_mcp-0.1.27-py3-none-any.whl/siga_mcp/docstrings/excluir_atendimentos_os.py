def docs() -> str:
    return """
Exclui um atendimento de Ordem de Serviço (OS) do sistema SIGA.

Esta função remove permanentemente um atendimento específico do sistema,
utilizando o código do atendimento e o código do analista como identificadores
para garantir a autoria e permissão. A operação é irreversível e deve ser
usada com cautela.

**Endpoint utilizado:** `excluiAtendimentosOsSigaIA`

**Estrutura do XML retornado:**
```xml
<exclusões_atendimento_os atendimento="123" sistema="SIGA">
    <exclusão sistema="SIGA">
        <status>sucesso</status>
        <mensagem>Atendimento excluído com sucesso!</mensagem>
    </exclusão>
</exclusões_atendimento_os>
```

**Em caso de erro:**
```xml
<exclusões_atendimento_os atendimento="123" sistema="SIGA">
    <exclusão sistema="SIGA">
        <status>erro</status>
        <mensagem>Não foi possível excluir o atendimento. Verifique as informações digitadas.</mensagem>
    </exclusão>
</exclusões_atendimento_os>
```

Args:
    codigo_atendimento (int): Código único do atendimento a ser excluído.
        Este código deve corresponder a um atendimento existente no sistema.
    codigo_analista (str | Literal["CURRENT_USER"]): Matrícula do analista/usuário responsável pelo atendimento OS. É um critério obrigatório para a exclusão, garantindo que apenas o analista associado possa remover o atendimento.

Returns:
    str: XML formatado contendo:
        - Em caso de sucesso: confirmação da exclusão com status "sucesso"
        - Em caso de erro de validação: mensagem indicando problema com os dados
        - Em caso de erro de API: mensagem de erro específica
        - Em caso de erro interno: mensagem de erro genérica

        O XML sempre inclui o código do atendimento como atributo do elemento raiz.

Raises:
    Não levanta exceções diretamente. Todos os erros são capturados e retornados
    como XML formatado com informações detalhadas do erro.

Examples:
    >>> # Excluir atendimento específico
    >>> xml = await excluir_atendimentos_os(codigo_atendimento=12345, codigo_analista=3214)

    >>> # Exemplo de uso em contexto de limpeza
    >>> atendimentos_para_excluir = [123, 456, 789]
    >>> for codigo in atendimentos_para_excluir:
    ...     resultado = await excluir_atendimentos_os(codigo_atendimento=codigo)
    ...     print(f"Resultado para atendimento {codigo}: {resultado}")

Notes:
    - **ATENÇÃO**: Esta operação é irreversível. Uma vez excluído, o atendimento
        não pode ser recuperado através da API
    - A exclusão exige que o `codigo_atendimento` e o `codigo_analista` informados correspondam a um registro existente. O sistema valida que o atendimento existe **E que o analista fornecido é o responsável por ele.**
    - Não há validação de permissões - qualquer usuário com acesso à API pode excluir
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
    - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente

Warning:
    Use esta função com extrema cautela em ambientes de produção. Considere
    implementar validações adicionais ou logs de auditoria antes da exclusão.

"""
