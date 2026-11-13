# Campos do formulário SoftExpert → Ordem de Compra no RM (1.1.04)

Este documento lista os campos que o fluxo de compra na SoftExpert **precisa ter** para que a Ordem de Compra (OC) seja enviada ao TOTVS RM. Também diz para onde vai cada campo no RM.

## Pontos de atenção ao montar o fluxo

1. **Listas do RM, nunca texto livre.** Todo campo que vira código no RM deve ser uma lista de valores puxada do próprio RM. Os SQLs dessas listas estão no arquivo `04_listas_formulario_softexpert.sql`. A ideia é cadastrar o banco do RM como Fonte de Dados na SoftExpert (com um usuário **somente leitura**) e usar cada SELECT como conjunto de dados de um campo lista. Na tela aparece o nome; no campo fica gravado o código.
2. **Envio só depois da aprovação.** O fluxo só pode mandar a OC ao RM depois da **aprovação final**. Nenhuma etapa anterior deve chamar o RM.
3. **Campos de retorno.** O formulário precisa ter campos para gravar o nº da OC gerada no RM e a mensagem de erro, caso o RM recuse o envio (ver a seção "Campos de retorno").

## Cabeçalho da OC

| Campo no formulário | Tipo | Obrigatório | Campo RM | Lista (arquivo 04) | Observação |
|---|---|---|---|---|---|
| Fornecedor | Lista | Sim | `CODCFO` + `CODCOLCFO` | 1 | Pesquisar por CNPJ ou nome. Gravar `CODCFO` e `CODCOLCFO`. |
| Condição de pagamento | Lista | Sim | `CODCPG` | 4 | Ex.: 03 = 30 DD após NF. |
| Centro de custo principal | Lista | Sim | `CODCCUSTO` | 3 | O **nome** do centro de custo também vai para `CAMPOLIVRE1`. |
| Departamento | Lista | Sim | `CODDEPARTAMENTO` | 7 | Departamentos da filial 1. |
| Natureza da despesa | Lista | Sim | `CODTB1FLX` | 5 | Preenchido em 100% das OCs hoje. |
| Tipo de custo | Lista | Sim | `CODTB2FLX` | 6 | 6 opções (Custo Direto, Indireto, Despesa…). |
| Comprador | Lista | Sim | `CODVEN1` | 8 | Quem emite a OC em Compras. |
| Responsável / requisitante | Lista | Sim | `CODVEN2` | 9 | Preenchido em 100% das OCs hoje. Confirmar com Compras o rótulo deste campo no RM. |
| Tipo de frete | Lista fixa | Sim | `FRETECIFOUFOB` | — | Códigos mais usados: 1, 2 e 9. **Compras precisa confirmar o significado de cada código** antes de montar a lista. |
| Previsão de entrega | Data | Não | `DATAEXTRA1` | — | Usado em cerca de 20% das OCs. Confirmar com Compras se é mesmo a previsão de entrega. |
| Nº da solicitação | Texto (até 20) | Sim | `SEGUNDONUMERO` | — | Nº do processo/solicitação de origem. |
| Justificativa | Texto longo | Sim | `TMOVHISTORICO` | — | Vai para o histórico da OC. |
| Local de entrega | Texto longo | Sim | `TMOVHISTORICO` | — | Vai para o histórico, junto com a justificativa. |

**Não precisam aparecer no formulário** (são preenchidos pela integração):

| Campo RM | Valor | Origem |
|---|---|---|
| `IDINTEGRACAO` | Identificador único do processo na SoftExpert (até 100 caracteres) | Gerado pelo fluxo. Evita que a mesma OC seja criada duas vezes. **Não pode se repetir.** |
| `DATAEMISSAO` | Data do envio ao RM | Data da aprovação final. |
| `VALORBRUTO` / `VALORLIQUIDO` | Soma dos itens | Calculado. |
| `CODCOLIGADA`, `CODFILIAL`, `CODLOC`, `CODTMV`, `SERIE`, `TIPO`, `STATUS`, `CODMOEVALORLIQUIDO` | 1, 1, 01, 1.1.04, OR, A, A, R$ | Fixos. |

## Itens da OC (tabela/grid, 1 ou mais linhas)

As OCs de hoje têm, em média, 3,3 itens.

| Campo no formulário | Tipo | Obrigatório | Campo RM | Lista (arquivo 04) | Observação |
|---|---|---|---|---|---|
| Produto | Lista | Sim | `IDPRD` | 2 | Mostrar código + nome. Gravar `IDPRD`. |
| Unidade de compra | Automático | Sim | `CODUND` | 2 | Vem junto com o produto (`CODUNDCOMPRA`). Não deixar o usuário digitar. |
| Quantidade | Número (4 casas) | Sim | `QUANTIDADE` | — | Maior que zero. |
| Preço unitário | Moeda (até 4 casas) | Sim | `PRECOUNITARIO` | — | Maior que zero. |
| Centro de custo do item | Lista | Sim | `CODCCUSTO` | 3 | Sugerir o centro de custo do cabeçalho. |
| Placa / observação do item | Texto (até 15) | Não | `CAMPOLIVRE` | — | Hoje Compras usa para a placa do veículo (ex.: SSI-1D63). |

## Rateio por centro de custo

23% das OCs de 2026 têm mais de um centro de custo. O formulário precisa permitir isso.

| Campo no formulário | Tipo | Campo RM | Observação |
|---|---|---|---|
| Centro de custo | Lista (lista 3) | `CODCCUSTO` | Uma linha por centro de custo. |
| Valor ou percentual | Moeda / % | `VALOR` | **A soma precisa ser igual ao valor total da OC** (e de cada item). Se o rateio for por percentual, a integração arredonda em 2 casas e joga a diferença de centavos na última linha. |

Se houver um só centro de custo, o rateio pode ser montado automaticamente com 100% no centro de custo principal.

## Campos de retorno (gravados pela integração)

| Campo no formulário | Tipo | Preenchido quando | Conteúdo |
|---|---|---|---|
| Nº da OC no RM | Texto | Sucesso | `NUMEROMOV` gerado (ex.: 048020). |
| ID do movimento no RM | Número | Sucesso | `IDMOV` gerado. |
| Situação da integração | Lista fixa | Sempre | Pendente / Enviada / Erro. |
| Mensagem de erro do RM | Texto longo | Erro | Texto que o RM devolve (costuma indicar o campo ou a regra que falhou). |
| Data/hora do envio | Data/hora | Sempre | Momento da tentativa. |

Em caso de erro, o fluxo deve permitir corrigir os dados e reenviar **com o mesmo** identificador do processo (`IDINTEGRACAO`). Antes de cada envio, a integração confere se a OC já existe e, se existir, devolve o nº que já foi gerado em vez de criar outra.
