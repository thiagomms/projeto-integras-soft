# Teste: Ordem de Compra externa → TOTVS RM (base de TESTE)

> **Para o Claude do programador:** este pacote é o contexto completo da tarefa. Objetivo: criar **uma** Ordem de Compra (tipo 1.1.04) no RM da Brasília Segurança, **somente na base de teste `Teste_BrasiliaSeg`**, chamando o WebService SOAP `wsDataServer` (método `SaveRecord`, DataServer `MovMovimentoTBCData`) pelo Postman ou SoapUI. A origem final dos dados será um formulário da SoftExpert, que ainda está sendo feito. Por isso o teste usa dados fixos, copiados de uma OC real da base de teste. Não grave nada direto nas tabelas por SQL.

## Arquivos do pacote

| Arquivo | Para que serve |
|---|---|
| `01_ReadRecord_OC_existente.xml` | Envelope SOAP que **lê** uma OC real (IDMOV 211266). Rodar primeiro: a resposta é o gabarito exato do XML nesta versão do RM. |
| `02_SaveRecord_OC_teste.xml` | Envelope SOAP que **cria** a OC de teste (1 item, R$ 10,00). |
| `03_conferencia_pos_teste.sql` | SELECTs para conferir cabeçalho, itens e rateio depois do envio, mais a consulta anti-duplicidade. |
| `04_listas_formulario_softexpert.sql` | Listas de valores (fornecedor, produto, centro de custo etc.) para o formulário da SoftExpert. Não é necessário no primeiro teste. |
| `05_postman_collection.json` | Coleção Postman com as duas chamadas prontas. Importar e preencher as variáveis. |
| `CAMPOS_FORMULARIO_SOFTEXPERT.md` | Campos que o formulário precisa ter e para onde vai cada um no RM. |

## Pré-requisitos (pedir à TI / ao administrador do RM)

1. **URL do RM.Host que aponta para a base de TESTE.** Atenção: se a URL for a de produção, a OC cai na `Corporerm_BrasiliaSeg`. Antes de enviar, confirme qual banco o Host usa (pelo alias no RM.Host ou com o administrador).
2. **WebService habilitado no Host.** Em geral fica em `http://<servidor>:8051/wsDataServer/IwsDataServer`; a porta pode mudar. O WSDL fica em `http://<servidor>:8051/wsDataServer/MEX?wsdl`. Se o WSDL abrir no navegador, o serviço está no ar.
3. **Usuário do RM para integração.** Ainda não existe nenhum (procurei por "integ", "ws" e "api" e não achei). Sugestão de nome: `integracao.softexpert`. Ele precisa de permissão para incluir movimentos do tipo **1.1.04** na coligada 1 / filial 1. Para o primeiro teste, pode ser o usuário do próprio programador.

## Passo a passo

1. Importar `05_postman_collection.json` no Postman e preencher as variáveis `rm_url`, `rm_user` e `rm_pass`. A autenticação é **Basic**.
2. Rodar **01 ReadRecord**:
   - Se der erro de autenticação ou permissão, resolva isso antes de seguir.
   - Compare o XML que o RM devolver com o `02`: nomes das tags, formato de data e **formato decimal** (vírgula ou ponto).
   - Ajuste o `02` para seguir esse formato.
3. Rodar **02 SaveRecord**:
   - **Sucesso:** o retorno é `1;<IDMOV>`.
   - **Erro:** o RM devolve o texto da exceção, que costuma apontar o campo ou a regra que falhou.
4. Rodar as consultas do `03_conferencia_pos_teste.sql` no banco `Teste_BrasiliaSeg`.
5. Abrir a OC no RM de teste (Compras → Movimentos → 1.1.04) e conferir na tela. Repare no **número gerado** e no **histórico**.
6. Para um novo envio, troque `IDINTEGRACAO` (por exemplo `SOFTEXPERT-TESTE-0002`). Cada OC precisa ter a sua.

## Detalhes da chamada SOAP

```
POST {rm_url}/wsDataServer/IwsDataServer
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://www.totvs.com/IwsDataServer/SaveRecord"
Authorization: Basic base64(usuario:senha)

Namespace: xmlns:tot="http://www.totvs.com/"
Parâmetros: DataServerName = MovMovimentoTBCData
            XML            = <MovMovimento>...</MovMovimento> (dentro de CDATA)
            Contexto       = CODCOLIGADA=1;CODFILIAL=1;CODSISTEMA=T;CODUSUARIO=<usuario>
```

- **SoapUI:** criar o projeto a partir do WSDL (`.../wsDataServer/MEX?wsdl`) e colar o corpo dos arquivos 01 e 02.
- **Data:** `AAAA-MM-DDT00:00:00`.
- **Numeração:** `IDMOV = -1` e `NUMEROMOV = -1` fazem o RM gerar o ID e o número da série **OR**.
- **Chaves-filhas:** `IDMOVRATCCU = -1` também é gerado pelo RM.

## Estrutura do XML (MovMovimento)

| Bloco | Tabela RM | Observação |
|---|---|---|
| `<TMOV>` | Cabeçalho da OC | 1 por OC. |
| `<TMOVHISTORICO>` | Histórico (texto longo) | Hoje Compras escreve aqui o nº da solicitação, a justificativa e o local de entrega. |
| `<TMOVRATCCU>` | Rateio por centro de custo do cabeçalho | **A soma dos valores precisa ser igual a VALORLIQUIDO.** 23% das OCs de 2026 têm mais de um centro de custo. |
| `<TITMMOV>` | Itens | `NSEQITMMOV` e `NUMEROSEQUENCIAL` 1, 2, 3… Média de 3,3 itens por OC. |
| `<TITMMOVRATCCU>` | Rateio do item | Mesma regra, por item. |

## Valores fixos do tipo 1.1.04 (tirados das OCs de 2026)

| Campo | Valor | Comentário |
|---|---|---|
| CODCOLIGADA | 1 | |
| CODFILIAL | 1 | |
| CODLOC | 01 | Local de estoque, igual em todas as OCs. |
| CODTMV | 1.1.04 | Ordem de Compra. |
| SERIE | OR | |
| TIPO / STATUS | A / A | O status inicial é "A" (em aberto). |
| CODMOEVALORLIQUIDO | R$ | |

## Campos variáveis (vêm do formulário da SoftExpert)

| Campo RM | Exemplo no teste | Origem / lista |
|---|---|---|
| CODCFO + CODCOLCFO | 878300 / 1 | Fornecedor, buscado pelo CNPJ na FCFO (lista 1 do arquivo 04). |
| CODCPG | 03 (30 DD após NF) | Lista 4. |
| CODCCUSTO | 52.2123 | Lista 3. Também vai no rateio. |
| CODDEPARTAMENTO | 0.04.03.06 (Seção de Transporte) | Lista 7. |
| CODTB1FLX | 0410 (Material de Limpeza) | Natureza da despesa, lista 5. Preenchido em 100% das OCs. |
| CODTB2FLX | 0001 (Custo Direto) | Tipo de custo, lista 6. |
| CODVEN1 | 55554 (Ana Paula – Compras) | Comprador, lista 8. |
| CODVEN2 | 06318 | Responsável/requisitante, lista 9. Preenchido em 100% das OCs. |
| FRETECIFOUFOB | 1 | Mais usados: 2 (962 OCs), 9 (606), 1 (193). Confirmar com Compras o que cada código significa na tela. |
| DATAEXTRA1 | 2026-10-15 | Usado em cerca de 20% das OCs; parece ser a previsão de entrega (confirmar com Compras). |
| CAMPOLIVRE1 | nome do centro de custo | Compras preenche com o nome do centro de custo/contrato. |
| SEGUNDONUMERO | SE-TESTE-0001 | Hoje recebe o nº da solicitação de origem (ex.: 19780, que também aparece como `#19780` no histórico). Até 20 caracteres. |
| **IDINTEGRACAO** | SOFTEXPERT-TESTE-0001 | **Chave da SoftExpert.** Hoje está vazio em todas as OCs, então fica livre para a integração. Até 100 caracteres. É a base do anti-duplicidade. |
| Item: IDPRD / CODUND | 19966 / TB200 | Produto e unidade de compra, lista 2. |
| Item: QUANTIDADE / PRECOUNITARIO | 1 / 10,00 | |
| Item: CAMPOLIVRE | TESTE | Hoje guarda a **placa** do veículo (ex.: SSI-1D63). Até 15 caracteres. |

## Regras de negócio para a versão final

- **Anti-duplicidade:** antes de cada `SaveRecord`, consultar `TMOV.IDINTEGRACAO` (consulta 4 do arquivo 03). Se a OC já existir, devolver o IDMOV existente em vez de criar outra.
- **Fechamento do rateio:** soma do rateio = valor líquido, no cabeçalho e em cada item. Arredondar em 2 casas e jogar a diferença de centavos na última linha.
- **Retorno para a SoftExpert:** devolver o `IDMOV` e o `NUMEROMOV` gerados (ex.: `048020`) para gravar no processo, ou o texto do erro.
- **Arquitetura:** a SoftExpert 3.1 tem "Fonte de dados SOAP", então pode chamar o `wsDataServer` direto de uma atividade de sistema do Workflow, logo após a aprovação. Uma alternativa é um serviço intermediário que lê a Web API REST da SoftExpert e grava no RM. O teste de hoje vale para os dois caminhos.

## Erros comuns

| Sintoma | Causa provável |
|---|---|
| 401 / "usuário ou senha inválidos" | Basic Auth errado, ou usuário sem acesso ao sistema T (Compras/Estoque). |
| Erro de conversão em valor numérico | Formato decimal: trocar vírgula por ponto, ou o contrário, conforme o ReadRecord. |
| "Rateio não confere" / diferença de valor | Soma de TMOVRATCCU ou TITMMOVRATCCU diferente do valor líquido. |
| Fornecedor/produto não encontrado | Código inexistente na coligada 1, ou cadastro inativo. Validar com as listas do arquivo 04. |
| OC criada na base errada | O Host aponta para produção. Cancelar a OC pela tela do RM e corrigir a URL. |

## Limpeza

Exclua as OCs de teste **pela tela do RM** (ação de excluir/cancelar movimento), nunca com DELETE no banco.
