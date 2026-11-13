# Integração SoftExpert → TOTVS RM

Integração que leva os dados aprovados num processo de compras da **SoftExpert** para o **TOTVS RM**:

- cadastra o **fornecedor**, quando ele ainda não existe (DataServer `FinCFODataBR`);
- cria a **Ordem de Compra**, tipo de movimento `1.1.04` (DataServer `MovMovimentoTBCData`).

A gravação é feita só pelos WebServices oficiais do RM.Host: SOAP `wsDataServer` (`SaveRecord` / `ReadRecord`) e REST `rmsrestdataserver`. **Não há INSERT nem UPDATE direto nas tabelas.**

## Fluxo

| Passo | O que faz | Serviço |
|---|---|---|
| 1 | Verifica se a OC já existe pelo `IDINTEGRACAO` (anti-duplicidade) | REST GET |
| 2 | Cria a OC | SOAP `SaveRecord` |
| 3 | Lê a OC criada para obter o número gerado | REST GET / SOAP `ReadRecord` |

## Estrutura

| Pasta / arquivo | Conteúdo |
|---|---|
| `Integracao SoftExpert x RM - pacote programador/` | Pacote completo para o programador. **Comece pelo `000_COMECE_AQUI.md`.** |
| `pacote_softexpert/` | Versão final em SOAP, com marcadores `{{...}}` para a SoftExpert preencher. |
| `pacote_softexpert_rest/` | Versão final com REST (consulta) + SOAP (gravação). |
| `CAMPOS_FORMULARIO_SOFTEXPERT.md` | Campos do formulário e para qual campo do RM vai cada um. |
| `01`–`05` (raiz) | Envelopes SOAP, SQLs de conferência e de listas, e a coleção Postman. |
| `tools/` | Scripts Python de teste (leitura do banco, chamadas SOAP/REST, envio de OC). |
| `*.wsdl` | Contrato do `wsDataServer`. |

## Configuração

1. Copie o `.env.example` para `.env` e preencha os dados da **base de teste**:
   - `DB_*`: SQL Server do RM, com usuário **somente leitura**;
   - `RM_URL`, `RM_USER` e `RM_PASS`: RM.Host e usuário de integração (autenticação Basic).
2. Instale as dependências dos scripts:
   ```
   pip install pyodbc python-dotenv requests
   ```
3. Teste a conexão: `python tools/check_db.py`

> O `.env` não é versionado. Nunca coloque usuário, senha ou endereço de servidor nos arquivos do repositório.

## Regras importantes

- Teste sempre na **base de teste** e confirme para qual banco o RM.Host aponta antes de usar o `SaveRecord`.
- Comentários em SQL enviado ao RM: use só `/* */`, nunca `--`.
- `IDINTEGRACAO` recebe o ID do processo SoftExpert e deve ser consultado antes de gravar, para não duplicar a OC.
- Filtro do REST: array JSON com a expressão SQL literal e colunas com o prefixo `TMOV.` (por exemplo `["TMOV.IDMOV = 123"]`).
- Registros de teste são apagados pela tela do RM, nunca com `DELETE`.
