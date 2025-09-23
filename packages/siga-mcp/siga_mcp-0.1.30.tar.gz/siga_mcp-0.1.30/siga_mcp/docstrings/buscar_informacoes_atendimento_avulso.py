from textwrap import dedent


def docs() -> str:
    return dedent("""\
            Busca informações detalhadas de um atendimento avulso específico.

            Esta função realiza uma consulta ao sistema SIGA através da API do AVA para obter
            todas as informações relacionadas a um atendimento avulso específico. É especialmente
            útil para consultar dados antes de realizar edições no atendimento avulso.

            Funcionalidades:
            - Consulta dados completos de um atendimento avulso pelo código e analista responsável
            - Garante precisão na identificação do registro correto (evita ambiguidade entre códigos duplicados)
            - Retorna informações estruturadas em formato XML
            - Inclui tratamento de erros para requisições mal-sucedidas
            - Utiliza autenticação via API Key do AVA

            Endpoint utilizado:
            - URL: https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarInfoAtendimentoAvulsoSigaIA/
            - Método: POST
            - Autenticação: API Key (AVA_API_KEY)

            Estrutura do XML retornado:
            - Elemento raiz: <info_atendimentos_avulsos>
            - Atributos do elemento raiz: atendimento (código do atendimento) e analista (código do analista) 
            - Atributos customizados: sistema="SIGA"
            - Contém todos os dados do atendimento retornados pela API

            Args:
                codigo_atendimento (int): Código único identificador do atendimento avulso. Obrigatório. 
                    Deve ser um número inteiro válido correspondente a um atendimento existente no sistema SIGA.
                codigo_analista (str | Literal["CURRENT_USER"]): Matrícula do analista/usuário responsável pelo atendimento avulso. Obrigatório.
                    É necessário para garantir a identificação precisa do registro, evitando conflitos com códigos duplicados entre diferentes tipos de atendimento.

            Returns:
                str: XML bem formatado contendo as informações do atendimento avulso.
                    Em caso de erro na requisição ou processamento, retorna a mensagem:
                    "Erro ao buscar as informações do atendimento avulso."

            Raises:
                Exception: Captura qualquer exceção durante a requisição HTTP ou
                        processamento dos dados, retornando mensagem de erro amigável.

            Example:
                >>> resultado = await buscar_informacoes_atendimento_avulso(12345, "3214")
                >>> print(resultado)
                <?xml version="1.0" ?>
                <info_atendimentos_avulsos atendimento="12345" analista="3214" sistema="SIGA">
                    <campo1>valor1</campo1>
                    <campo2>valor2</campo2>
                    ...
                </info_atendimentos_avulsos>

                # Exemplo usando CURRENT_USER
                >>> resultado = await buscar_informacoes_atendimento_avulso(12345, "CURRENT_USER")

            Note:
                - Requer variável de ambiente AVA_API_KEY configurada
                - A função é assíncrona e deve ser chamada com await
                - Utiliza aiohttp para requisições HTTP assíncronas
                - O XML é formatado usando a classe XMLBuilder interna
                - Ambos os parâmetros (codigo_atendimento e codigo_analista) são obrigatórios para evitar conflitos com códigos duplicados em diferentes tabelas do sistema
            """)
