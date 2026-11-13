# Formulário de compra na SoftExpert: campos necessários

O levantamento foi feito em **1.800 Ordens de Compra (1.1.04) emitidas em 2026**, na base Teste_BrasiliaSeg.

**Princípio:** todo campo que vira código no RM deve ser uma **lista de valores vinda do próprio RM**. Para isso, cadastre o banco do RM como Fonte de Dados (DI003) e use os SELECTs do arquivo `04_listas_formulario_softexpert.sql` como Conjuntos de Dados. Se o usuário digitar texto livre onde o RM espera um código, a integração falha.

Legenda: **Obrigatório** = sem ele o RM recusa ou a OC fica errada. **Recomendado** = Compras usa hoje e convém manter.

## 1. Cabeçalho da compra

| # | Campo no formulário | Tipo | Grava no RM | Situação | Lista | Observação |
|---|---|---|---|---|---|---|
| 1 | Fornecedor | Lista com pesquisa por CNPJ ou nome | TMOV.CODCFO | **Obrigatório** | Lista 1 (~9.650 fornecedores ativos) | Gravar o **código** (ex.: 878300), não o nome. |
| 2 | Condição de pagamento | Lista | TMOV.CODCPG | **Obrigatório** | Lista 4 (~420) | Ex.: "30 DD – após emissão da NF". 102 condições diferentes foram usadas em 2026. |
| 3 | Centro de custo principal | Lista | TMOV.CODCCUSTO | **Obrigatório** | Lista 3 (~1.180) | |
| 4 | Departamento / Seção | Lista | TMOV.CODDEPARTAMENTO | **Obrigatório** | Lista 7 (~105) | Preenchido em 100% das OCs. Ex.: Seção de Transporte. |
| 5 | Natureza da despesa | Lista | TMOV.CODTB1FLX | **Obrigatório** | Lista 5 (~355) | Ex.: Material de Limpeza, Peças p/ Veículos. 100% das OCs. |
| 6 | Tipo de custo | Lista (6 opções) | TMOV.CODTB2FLX | **Obrigatório** | Lista 6 | Opções: Custo Direto, Custo Indireto, Despesa, Terceiros, Estoque, Investimento. |
| 7 | Comprador | Lista | TMOV.CODVEN1 | **Obrigatório** | Lista 8 (11 pessoas) | Pode vir automático do usuário de Compras que conduz o processo. |
| 8 | Responsável / requisitante | Lista | TMOV.CODVEN2 | **Obrigatório** | Lista 9 (~49) | 100% das OCs. Confirmar com Compras o nome deste campo na tela do RM. |
| 9 | Tipo de frete | Lista | TMOV.FRETECIFOUFOB | **Obrigatório** | Fixa | Códigos usados: 2, 9, 1, 4. Pedir a Compras o significado de cada um (CIF, FOB, sem frete…). |
| 10 | Data de emissão | Data | TMOV.DATAEMISSAO | **Obrigatório** | — | Pode ser a data da aprovação. |
| 11 | Previsão de entrega | Data | TMOV.DATAEXTRA1 | Recomendado | — | Usado em ~20% das OCs hoje. |
| 12 | Nº da solicitação / processo | Texto (até 20) | TMOV.SEGUNDONUMERO | Recomendado | — | Hoje Compras grava aqui o nº da solicitação (ex.: 19780). Pode ser o nº do processo da SoftExpert. |
| 13 | Descrição do contrato / CC | Texto (até 100) | TMOV.CAMPOLIVRE1 | Recomendado | — | Hoje recebe o nome do centro de custo (ex.: "CAESB – Veículos – Peças e Manutenção"). Pode ser preenchido automaticamente. |
| 14 | Justificativa / objeto da compra | Texto longo | TMOVHISTORICO | **Obrigatório** | — | Hoje traz o nº da solicitação, a justificativa e o contato. |
| 15 | Local e horário de entrega | Texto | TMOVHISTORICO (mesmo texto) | Recomendado | — | Hoje vai junto do histórico. |
| 16 | ID do processo SoftExpert | Automático, oculto | TMOV.IDINTEGRACAO | **Obrigatório (técnico)** | — | Identificador único que evita criar a mesma OC duas vezes. |

## 2. Itens (grade/tabela no formulário, 1 linha por item)

| # | Campo | Tipo | Grava no RM | Situação | Observação |
|---|---|---|---|---|---|
| 17 | Produto | Lista com pesquisa por código ou nome | TITMMOV.IDPRD | **Obrigatório** | Lista 2 (~7.545 produtos ativos). Não aceitar texto livre: se o produto não existir, ele precisa ser cadastrado no RM antes. |
| 18 | Unidade | Automática (vem com o produto) | TITMMOV.CODUND | **Obrigatório** | A lista 2 já traz a unidade de compra (ex.: UN, TB200). |
| 19 | Quantidade | Número (decimal) | TITMMOV.QUANTIDADE | **Obrigatório** | Maior que zero. |
| 20 | Preço unitário | Moeda | TITMMOV.PRECOUNITARIO | **Obrigatório** | |
| 21 | Valor total do item | Calculado | — | Automático | Quantidade × preço. |
| 22 | Placa / referência | Texto (até 15) | TITMMOV.CAMPOLIVRE | Recomendado | Usado em 2.900+ itens, quase sempre com a placa do veículo (ex.: SSI-1D63). |
| 23 | Centro de custo do item | Lista | TITMMOV.CODCCUSTO | Opcional | Se vazio, usa o do cabeçalho. |
| 24 | Desconto | Moeda ou % | TMOV.VALORDESC | Opcional | Usado em algumas OCs. |

## 3. Rateio por centro de custo (grade opcional)

| # | Campo | Grava no RM | Observação |
|---|---|---|---|
| 25 | Centro de custo | TMOVRATCCU.CODCCUSTO | **23% das OCs de 2026 (415 de 1.800) dividem o valor entre 2 ou mais centros de custo.** O formulário precisa permitir isso. |
| 26 | Valor ou % | TMOVRATCCU.VALOR | **A soma precisa fechar 100% do valor da OC**, senão o RM recusa. Validar no próprio formulário. |

## 4. Totais (calculados, só exibição)

Valor bruto, desconto e valor líquido. O RM recalcula esses valores, mas exibi-los ajuda o aprovador.

## 5. Campos de retorno (a integração preenche depois de criar a OC)

| Campo | Para que serve |
|---|---|
| Nº da OC no RM (NUMEROMOV, ex.: 048020) | Mostrar ao usuário e ao fornecedor. |
| IDMOV do RM | Referência técnica. |
| Status da integração / mensagem de erro | Se o RM recusar, o processo volta para correção com o motivo. |

## Validações que o formulário deve fazer antes de enviar

1. Todos os códigos escolhidos nas listas, sem texto livre em campos de código.
2. Pelo menos 1 item, com quantidade e preço maiores que zero.
3. Soma do rateio igual ao valor total da OC.
4. Fornecedor ativo. A lista já filtra os inativos, mas o cadastro pode mudar entre a criação e a aprovação.
5. Envio ao RM **somente após a aprovação final** do processo.

## Pontos para confirmar com Compras

- **Frete:** significado dos códigos de frete (1, 2, 4, 9).
- **CODVEN2 e DATAEXTRA1:** como esses dois campos aparecem na tela do RM.
- **Solicitações anteriores:** hoje 21% das OCs nascem de um Pedido (1.1.03) ou de uma Solicitação (1.1.01) no RM. Com a SoftExpert, a OC passa a ser criada direto, sem esse vínculo. Confirmar que Compras está de acordo.
