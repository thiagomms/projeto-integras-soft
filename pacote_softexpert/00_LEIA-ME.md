# Integração SoftExpert → TOTVS RM: configuração

Este pacote traz o necessário para a SoftExpert criar a Ordem de Compra (tipo **1.1.04**) no RM da Brasília Segurança. A OC é criada pelo WebService SOAP `wsDataServer`, depois da **aprovação final** do processo.

Faça todos os testes na **base de teste** do RM. Use somente a URL informada pela TI da Brasília Segurança.

## Arquivos

| Arquivo | Uso |
|---|---|
| `01_ReadView_antiduplicidade.xml` | Passo 1: verifica se a OC já existe. |
| `02_SaveRecord_OC.xml` | Passo 2: cria a OC. Modelo com marcadores `{{...}}` e o de-para dos campos do formulário. |
| `03_ReadRecord_OC.xml` | Passo 3: lê a OC criada para obter o número dela no RM. |
| `04_listas_formulario.sql` | SELECTs das listas do formulário: fornecedor, produto, centro de custo etc. |
| `05_postman_collection.json` | Os três passos prontos para teste manual no Postman. |

## Dados de conexão (a TI da Brasília Segurança envia)

| Item | Valor |
|---|---|
| URL do serviço | `{{rm_url}}/wsDataServer/IwsDataServer` |
| WSDL | `{{rm_url}}/wsDataServer/MEX?wsdl` |
| Autenticação | Basic, com o usuário de integração do RM (`{{rm_user}}` / `{{rm_pass}}`) |
| Banco para as listas | Servidor, banco e usuário **somente leitura** |

## Parâmetros fixos da chamada

```
Método HTTP:    POST
Content-Type:   text/xml; charset=utf-8
SOAPAction:     "http://www.totvs.com/IwsDataServer/<ReadView | SaveRecord | ReadRecord>"
Namespace:      xmlns:tot="http://www.totvs.com/"
DataServerName: MovMovimentoTBCData
Contexto:       CODCOLIGADA=1;CODFILIAL=1;CODSISTEMA=T;CODUSUARIO=<usuário de integração>
```

## Sequência no workflow (atividade de sistema após a aprovação final)

1. Chamar o **ReadView** filtrando pelo `IDINTEGRACAO` do processo.
   - Se a resposta tiver `<TMOV>`: a OC já existe. Grave `IDMOV` e `NUMEROMOV` no processo e encerre.
2. Chamar o **SaveRecord** com o XML da OC.
   - Retorno `1;<IDMOV>`: sucesso. Siga para o passo 3.
   - Qualquer outro retorno: erro. Grave o texto em "Mensagem de erro do RM" e marque a situação como **Erro**.
3. Chamar o **ReadRecord** com `PrimaryKey = 1;<IDMOV>`.
   - Grave `IDMOV` e `NUMEROMOV` no processo e marque a situação como **Enviada**.

Depois de um erro, o usuário corrige os dados e o processo é reenviado com o **mesmo** `IDINTEGRACAO`. A sequência recomeça no passo 1.

## Fonte de dados das listas

Cadastre o banco do RM como Fonte de Dados na SoftExpert, com usuário **somente leitura**. Use cada SELECT de `04_listas_formulario.sql` como conjunto de dados de um campo lista. A tela mostra o nome; o campo grava o código.

## Regras importantes

- Decimal com **ponto** (`10.0000`). Data no formato `AAAA-MM-DDT00:00:00`.
- `IDINTEGRACAO` é único por processo, com até 100 caracteres. Nunca reutilize o identificador de outro processo.
- A soma do rateio deve ser igual ao valor da OC. O mesmo vale para cada item.
- Não grave nada direto nas tabelas do RM por SQL. A gravação é sempre pelo WebService.
- Para excluir OCs de teste, use a tela do RM.

## Teste rápido no Postman

1. Importe `05_postman_collection.json`.
2. Preencha as variáveis `rm_url`, `rm_user` e `rm_pass`.
3. Rode o **1**. A resposta não deve ter `<TMOV>`.
4. Rode o **2**. O retorno deve ser `1;<IDMOV>`.
5. Copie o IDMOV para a variável `IDMOV` e rode o **3**.
6. Para criar outra OC, troque a variável `IDINTEGRACAO` (ex.: `SOFTEXPERT-TESTE-0003`).
