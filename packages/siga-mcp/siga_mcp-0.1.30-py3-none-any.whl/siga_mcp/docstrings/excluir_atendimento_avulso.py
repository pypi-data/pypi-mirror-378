from textwrap import dedent


def docs() -> str:
    return dedent("""\
            Exclui um atendimento avulso específico do sistema SIGA.

            Esta função remove permanentemente um atendimento avulso específico do sistema SIGA através da API do AVA, utilizando o código do atendimento e o código do analista como identificadores para garantir precisão na identificação do registro correto. A operação é irreversível e deve ser usada com cautela.

            Funcionalidades:
            - Exclui atendimento avulso pelo código e analista responsável
            - Garante precisão na identificação do registro correto (evita ambiguidade entre códigos duplicados)
            - Retorna informações estruturadas em formato XML com status da operação
            - Inclui tratamento de erros para diferentes cenários de falha
            - Utiliza autenticação via API Key do AVA

            Endpoint utilizado:
            - URL: https://ava3.uniube.br/ava/api/atendimentosAvulsos/excluiAtendimentoAvulsoSigaIA/
            - Método: POST
            - Autenticação: API Key (AVA_API_KEY)

            **Estrutura do XML retornado:**

            **Sucesso:**
            ```xml
            <exclusões_atendimento_avulso atendimento="123" analista="3214" sistema="SIGA">
                <exclusão sistema="SIGA">
                    <status>sucesso</status>
                    <mensagem>Atendimento avulso excluído com sucesso!</mensagem>
                </exclusão>
            </exclusões_atendimento_avulso>
            ```

            **Em caso de erro:**
            ```xml
            <exclusões_atendimento_avulso atendimento="123" analista="3214" sistema="SIGA">
                <exclusão sistema="SIGA">
                    <status>erro</status>
                    <mensagem>Não foi possível excluir o atendimento avulso. Verifique as informações digitadas.</mensagem>
                </exclusão>
            </exclusões_atendimento_avulso>
            ```

            Args:
                codigo_atendimento (int): Código único identificador do atendimento avulso. Obrigatório.
                    Deve ser um número inteiro válido correspondente a um atendimento existente no sistema SIGA.
                codigo_analista (str | Literal["CURRENT_USER"]): Matrícula do analista/usuário responsável pelo atendimento avulso. Obrigatório.
                    É necessário para garantir a identificação precisa do registro, evitando conflitos com códigos duplicados entre diferentes tipos de atendimento.

            Returns:
                str: XML bem formatado contendo o resultado da operação de exclusão.
                    - Em caso de sucesso: status "sucesso" com mensagem de confirmação
                    - Em caso de erro: status "erro" com mensagem explicativa
                    - Em caso de erro interno: mensagem de erro genérica

            Raises:
                Exception: Captura qualquer exceção durante a requisição HTTP ou processamento dos dados, retornando mensagem de erro amigável em formato XML.

            Example:
                >>> resultado = await excluir_atendimento_avulso(12345, "3214")
                >>> print(resultado)
                <?xml version="1.0" ?>
                <exclusões_atendimento_avulso atendimento="12345" analista="3214" sistema="SIGA">
                    <exclusão sistema="SIGA">
                        <status>sucesso</status>
                        <mensagem>Atendimento avulso excluído com sucesso!</mensagem>
                    </exclusão>
                </exclusões_atendimento_avulso>

                # Exemplo usando CURRENT_USER
                >>> resultado = await excluir_atendimento_avulso(12345, "CURRENT_USER")

                # Exemplo tratando erro
                >>> resultado = await excluir_atendimento_avulso(99999, "3214")
                >>> print(resultado)
                <?xml version="1.0" ?>
                <exclusões_atendimento_avulso atendimento="99999" analista="3214" sistema="SIGA">
                    <exclusão sistema="SIGA">
                        <status>erro</status>
                        <mensagem>Não foi possível excluir o atendimento avulso. Verifique as informações digitadas.</mensagem>
                    </exclusão>
                </exclusões_atendimento_avulso>

            Note:
                - **ATENÇÃO**: Esta operação é irreversível. Uma vez excluído, o atendimento não pode ser recuperado
                - Requer variável de ambiente AVA_API_KEY configurada
                - A função é assíncrona e deve ser chamada com await
                - Utiliza aiohttp para requisições HTTP assíncronas
                - O XML é formatado usando a classe XMLBuilder interna
                - Ambos os parâmetros (codigo_atendimento e codigo_analista) são obrigatórios para evitar conflitos com códigos duplicados em diferentes tabelas do sistema
                - Use com extrema cautela em ambientes de produção
            """)
