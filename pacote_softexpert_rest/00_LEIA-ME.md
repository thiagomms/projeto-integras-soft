# Integração SoftExpert → TOTVS RM: configuração REST

Este pacote configura a integração que cria a Ordem de Compra (tipo **1.1.04**) no RM da Brasília Segurança depois da **aprovação final** do processo. A integração usa dois serviços do mesmo RM.Host:

| Passo | O que faz | Serviço | Situação |
|---|---|---|---|
| 1 | Verifica se a OC já existe (anti-duplicidade) | **REST** GET | Validado |
| 2 | Cria a OC | **SOAP** `SaveRecord` | Validado |
| 3 | Lê a OC criada para obter o número | **REST** GET | Validado |

Faça todos os testes na **base de teste** do RM. Use somente a URL informada pela TI da Brasília Segurança.

## Arquivos

| Arquivo | Uso |
|---|---|
| `02_SaveRecord_OC.xml` | Modelo SOAP da OC (passo 2), com marcadores `{{...}}` e o de-para dos campos do formulário. |
| `04_listas_formulario.sql` | SELECTs das listas do formulário: fornecedor, produto, centro de custo etc. |
| `05_postman_collection_rest.json` | Os três passos prontos para teste manual no Postman. |

## Dados de conexão (a TI da Brasília Segurança envia)

| Item | Valor |
|---|---|
| `{{rm_url}}` | `http://<servidor>:<porta>` do RM.Host de **teste** |
| Usuário / senha | Usuário de integração do RM, com autenticação **Basic** |
| Banco para as listas | Servidor, banco e usuário **somente leitura** |

O mesmo `{{rm_url}}`, o mesmo usuário e a mesma senha valem para o REST e para o SOAP.

## Passo 1: anti-duplicidade (REST GET)

Cadastro na SoftExpert (Fonte de dados REST):

| Etapa | Campo | Valor |
|---|---|---|
| Dados do serviço | URL | `{{rm_url}}/rmsrestdataserver/rest/MovMovimentoTBCData` |
| Dados do serviço | Autenticação | Basic, com o usuário de integração |
| Parâmetros de entrada | Método | `GET` |
| Parâmetros de entrada | Header `CODCOLIGADA` | Valor constante `1` |
| Parâmetros de entrada | Query `filter` | Texto montado com o IDINTEGRACAO do processo (abaixo) |
| Parâmetros de entrada | Corpo | Vazio |

O parâmetro `filter` precisa sair **exatamente** neste formato. É um array JSON com a condição SQL dentro:

```
["TMOV.CODCOLIGADA = 1 AND TMOV.CODTMV = '1.1.04' AND TMOV.IDINTEGRACAO = '<IDINTEGRACAO>'"]
```

- Mantenha o prefixo `TMOV.` nas colunas. Sem ele, o RM devolve "Ambiguous column name".
- O formato com `?` e valores separados (`["IDINTEGRACAO = ?", "..."]`) **não funciona** nesta versão do RM.
- O `IDINTEGRACAO` não pode conter aspas simples.
- Se o cadastro não permitir montar o texto, crie um campo calculado no processo com a string inteira e passe esse campo.

Resposta:

| Resposta | Significado | Ação |
|---|---|---|
| `length` = 0, com mensagem `0003 – Nenhum registro foi encontrado` | A OC não existe | Seguir para o passo 2 |
| `length` = 1 | A OC já existe | Gravar `IDMOV` e `NUMEROMOV` de `data` no processo e **não** chamar o passo 2 |

Exemplo de OC encontrada:
```json
{"messages":[],"length":1,"data":[{"id":"1$_$211266","IDMOV":211266,"NUMEROMOV":"048019","SERIE":"OR","CODTMV":"1.1.04","STATUS":"A", ...}]}
```

## Passo 2: criar a OC (SOAP SaveRecord)

| Item | Valor |
|---|---|
| URL | `{{rm_url}}/wsDataServer/IwsDataServer` (WSDL: `{{rm_url}}/wsDataServer/MEX?wsdl`, versão 1.1) |
| Método | `POST` |
| Headers | `Content-Type: text/xml; charset=utf-8`, `SOAPAction: "http://www.totvs.com/IwsDataServer/SaveRecord"` |
| Autenticação | Basic, com o mesmo usuário |
| Corpo | `02_SaveRecord_OC.xml`, com os marcadores preenchidos |

Resposta:
- `1;<IDMOV>`: sucesso. Siga para o passo 3 com o IDMOV.
- Qualquer outro texto: erro do RM. Grave em "Mensagem de erro do RM" e marque a situação como **Erro**.

## Passo 3: ler a OC criada (REST GET)

| Campo | Valor |
|---|---|
| URL | `{{rm_url}}/rmsrestdataserver/rest/MovMovimentoTBCData/1$_$<IDMOV>` |
| Método | `GET` |
| Header | `CODCOLIGADA: 1` |
| Autenticação | Basic |

A chave do registro é `coligada$_$idmov` (ex.: `1$_$211266`). Grave `data.IDMOV` e `data.NUMEROMOV` no processo e marque a situação como **Enviada**.

## Sequência no workflow (atividade de sistema após a aprovação final)

1. GET anti-duplicidade. Se `length` = 1, grave os números e encerre.
2. SOAP `SaveRecord`. Em caso de erro, grave a mensagem e encerre.
3. GET por IDMOV. Grave `NUMEROMOV` e `IDMOV`.

Depois de um erro, o usuário corrige os dados e o processo é reenviado com o **mesmo** `IDINTEGRACAO`. A sequência recomeça no passo 1.

## Regras importantes

- No XML do passo 2, decimal com **ponto** (`10.0000`) e data no formato `AAAA-MM-DDT00:00:00`.
- `IDINTEGRACAO` é único por processo, com até 100 caracteres. Nunca reutilize o identificador de outro processo.
- A soma do rateio deve ser igual ao valor da OC. O mesmo vale para cada item.
- As listas do formulário vêm do RM (`04_listas_formulario.sql`). A tela mostra o nome; o campo grava o código.
- Não grave nada direto nas tabelas do RM por SQL. Para excluir OCs de teste, use a tela do RM.

## Teste rápido no Postman

1. Importe `05_postman_collection_rest.json`.
2. Preencha as variáveis `rm_url`, `rm_user` e `rm_pass`.
3. Rode o **1**. O resultado deve ser `length` = 0.
4. Rode o **2**. O retorno deve ser `1;<IDMOV>`. Copie o IDMOV para a variável `IDMOV`.
5. Rode o **3**. A resposta traz o `NUMEROMOV`.
6. Rode o **1** de novo. Agora deve vir `length` = 1, o que mostra que o anti-duplicidade funciona.
7. Para criar outra OC, troque a variável `IDINTEGRACAO`.
