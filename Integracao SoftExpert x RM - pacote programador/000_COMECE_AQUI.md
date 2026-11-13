# Integração SoftExpert → TOTVS RM: pacote para o programador

> Se você usa o Claude, entregue esta pasta inteira a ele e comece por este arquivo.

**Objetivo:** dados aprovados na SoftExpert (v3.1) entram no RM da Brasília Segurança como **fornecedor** (quando novo) e como **Ordem de Compra** (TMV 1.1.04).

**Agora:** teste de fora para dentro **somente na base de teste `Teste_BrasiliaSeg`**, via Postman ou SoapUI.

## Ordem de leitura

| # | Arquivo | Para quê |
|---|---|---|
| 1 | `00_LEIA-ME_PROGRAMADOR.md` | Guia da **Ordem de Compra**: pré-requisitos, passo a passo, campos, erros comuns. |
| 2 | `05_postman_collection.json` | Importar no Postman: 4 chamadas (ler e criar OC; ler e criar fornecedor). |
| 3 | `01` e `02` (.xml) | Envelopes SOAP da OC (ler uma existente / criar a de teste). |
| 4 | `03_conferencia_pos_teste.sql` | Conferir a OC criada e evitar duplicidade. |
| 5 | `10_LEIA-ME_FORNECEDOR.md` | Guia do **fornecedor** (DataServer FinCFODataBR) com a documentação da TOTVS. |
| 6 | `11` e `12` (.xml) e `13` (.sql) | Envelopes e SQL do fornecedor. |
| 7 | `20_LADO_SOFTEXPERT.md` | Como a SoftExpert vai chamar o RM na versão final. |
| 8 | `CAMPOS_FORMULARIO_SOFTEXPERT.md` e `04_listas_formulario_softexpert.sql` | Campos e listas de valores do formulário de compra. |

## Antes de começar (TI do RM)

1. **URL do RM.Host da base de TESTE.** Confirme que **não** é a de produção.
2. **Usuário do RM para integração.** Ainda não existe; para o 1º teste pode ser o seu.
3. **Separador decimal:** saber se o `RM.Host.exe.config` tem a tag `WebServiceCulture`. Sem a tag, use vírgula; com `Invariant`, ponto.

## Regras gerais

- **Nada de INSERT/UPDATE direto** nas tabelas do RM: só `wsDataServer` (`SaveRecord`).
- **Comentários SQL:** só `/* */`, nunca `--` (o RM quebra a sentença).
- **`IDINTEGRACAO`** recebe o ID do processo SoftExpert. Consulte-o antes de gravar, para não duplicar.
- **Limpeza:** apague os registros de teste pela tela do RM, nunca com DELETE.
