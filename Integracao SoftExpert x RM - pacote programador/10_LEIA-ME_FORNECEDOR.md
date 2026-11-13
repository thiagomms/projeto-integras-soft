# Cadastro de fornecedor: SoftExpert → TOTVS RM

> **Para o Claude do programador:** este é o segundo cenário da integração, no mesmo padrão da Ordem de Compra (arquivo `00_LEIA-ME_PROGRAMADOR.md`, nesta mesma pasta). Objetivo: criar **um** fornecedor na coligada 1, **somente na base de teste**, chamando o `wsDataServer` com o DataServer **`FinCFODataBR`**. A ordem é a mesma de antes: primeiro `ReadRecord`, depois `SaveRecord`, depois as consultas de conferência.
>
> **Ordem lógica no processo final:** quando a compra for para um fornecedor novo, ele precisa existir no RM **antes** da Ordem de Compra, que usa o CODCFO dele.

## Documentação oficial encontrada (TOTVS – TDN)

| Documento | O que tem |
|---|---|
| [Inclusão de Cliente/Fornecedor](https://tdn.totvs.com/pages/viewpage.action?pageId=450153132) | **Exemplo oficial de XML** do `FinCFODataBR` com `SaveRecord`, base do arquivo 12. |
| [TBC – Web Service DataServer](https://tdn.totvs.com/display/LRM/TBC+-+Web+Service+DataServer) | Métodos do wsDataServer (GetSchema, ReadRecord, ReadView, SaveRecord) e o formato da tag Contexto. |
| [Separadores decimais nos Web Services do RM](https://tdn.totvs.com/display/LRM/Separadores+decimais+nos+Web+Services+do+RM) | **Vírgula ou ponto nos números.** Também vale para a Ordem de Compra (ver o fim deste arquivo). |
| [Web Services do TBC](https://tdn.totvs.com/display/LRM/Web+Services+do+TBC) | Visão geral dos web services do RM. |
| [Cadastro Cliente/Fornecedor](https://tdn.totvs.com/pages/viewpage.action?pageId=425459224) | Manual da tela de cadastro. |
| [Usar o SoapUI para consumir DataServers RM](https://centraldeatendimento.totvs.com/hc/pt-br/articles/360007851192) | Passo a passo no SoapUI (Central de Atendimento TOTVS). |

Para o lado da SoftExpert (como o dado sai de lá), ver `20_LADO_SOFTEXPERT.md`.

## Regras da chamada (TDN)

- **Contexto sem espaços e sem aspas.** O certo é `CODCOLIGADA=1;CODSISTEMA=F;CODUSUARIO=usuario`. O exemplo da própria TDN usa `CODSISTEMA='F'`, com aspas, e a outra página da TDN diz que esse formato é **inválido**.
- **Sistema:** o cadastro de fornecedor fica no Financeiro, por isso `CODSISTEMA=F`. A Ordem de Compra usa `T`.
- **Endpoint:** o mesmo da OC, `.../wsDataServer/IwsDataServer`.
- **Estrutura do XML:** no exemplo da TDN, os blocos `FCFOCOMPL` e de contato aparecem **dentro** de `<FCFO>`, o que parece erro de formatação da página. No arquivo 12 eles estão lado a lado, dentro de `<FinCFOBR>`. Confirme pelo ReadRecord (arquivo 11).

## Como Compras cadastra hoje

Fonte: `Corporerm_BrasiliaSeg`, coligada 1, fornecedores criados de 01/10/2025 a 16/10/2026 (consulta de 16/10/2026).

- **Volume:** 356 fornecedores, cerca de 30 por mês. Quem cadastra: tatiana.macedo, kescia.oliveira, ainoa.santos, ana.almeida e lorrany.frota.
- **Código (CODCFO):** 6 dígitos, sequencial. Os últimos foram 009577 a 009587 em outubro de 2026. Teste primeiro com `-1` (numeração automática); se der erro, ver com a TI.
- **Tipo (PAGREC):** 84% recebem **3 = cliente e fornecedor**; 16% recebem **2 = só fornecedor**.
- **Pessoa:** 90% jurídica (J), 10% física (F). O CNPJ/CPF é gravado **com máscara** (`00.000.000/0000-00`).
- **Fornecedor por coligada:** o cadastro existe separado em cada coligada, e o mesmo código pode aparecer em várias. Os cadastros novos da Brasília Seg estão só na coligada 1.
- **Duplicidade:** já existem **260 CNPJs repetidos** na coligada 1. A integração precisa procurar o CNPJ antes de criar (consulta 1 do arquivo 13).
- **CEP:** gravado com e sem hífen (216 com, 141 sem). Padronize `00000-000`.
- **Nome e razão social:** em MAIÚSCULAS em 100% dos casos.

## Campos para o formulário da SoftExpert

| Campo no formulário | Grava no RM | Situação | Preenchimento hoje | Observação |
|---|---|---|---|---|
| CNPJ ou CPF | FCFO.CGCCFO | **Obrigatório** | 100% | Validar o dígito verificador; a máscara é aplicada na integração. Também é a chave de busca contra duplicidade. |
| Pessoa física ou jurídica | FCFO.PESSOAFISOUJUR | **Obrigatório** | 100% | Pode ser deduzido pelo tamanho do documento. |
| Razão social | FCFO.NOME | **Obrigatório** | 100% | Até 100 caracteres, maiúsculas. Ideal: preencher pela consulta de CNPJ. |
| Nome fantasia | FCFO.NOMEFANTASIA | **Obrigatório** | 100% | Até 100 caracteres. |
| Inscrição estadual | FCFO.INSCRESTADUAL | Recomendado | 36% | "ISENTO" quando não tiver. |
| Inscrição municipal | FCFO.INSCRMUNICIPAL | Opcional | 9% | Útil para prestador de serviço (ISS). |
| Tipo de logradouro | FCFO.TIPORUA | Recomendado | – | Lista 5 (RUA, QUADRA, SETOR…). |
| Logradouro, número, complemento | FCFO.RUA / NUMERO / COMPLEMENTO | **Obrigatório** | 100% | Tamanhos: RUA 100, NUMERO **8**, COMPLEMENTO 60. |
| Bairro | FCFO.BAIRRO (+ TIPOBAIRRO) | **Obrigatório** | 100% | Até 80 caracteres. |
| CEP | FCFO.CEP | **Obrigatório** | 100% | Formato `00000-000`. |
| UF e município | FCFO.CODETD + CODMUNICIPIO + CIDADE | **Obrigatório** | 100% | Lista 4 (código IBGE sem o prefixo da UF; DF = 00108). O código do município é obrigatório para nota fiscal. |
| E-mail | FCFO.EMAIL | **Obrigatório** | 80% | Até 250 caracteres. |
| Telefone | FCFO.TELEFONE | Recomendado | 53% | **Até 15 caracteres.** |
| Contato (nome) | FCFO.CONTATO | Recomendado | 38% | Até 40 caracteres. |
| Categoria do fornecedor | FCFO.CODTCF (+ CODCOLTCF = 1) | **Obrigatório** | 85% | Lista 3 (125 categorias). |
| Tipo de cadastro | FCFO.PAGREC | **Obrigatório** | 100% | 3 = cliente e fornecedor (padrão de Compras); 2 = só fornecedor. |
| Optante pelo Simples | FCFO.OPTANTEPELOSIMPLES | Recomendado | – | Hoje ninguém marca, mas afeta retenção de impostos. **Validar com o Fiscal.** |
| Nível do fornecedor | FCFOCOMPL.NIVELFORN | Recomendado | 42% | Valores "Nível A", "Nível B", "Nível C". Combina com a avaliação ou homologação feita na SoftExpert. |
| Dados bancários | FDADOSPGTO | Opcional | 7% | Quase ninguém cadastra hoje. Se o Financeiro quiser, é **outro DataServer** e fica para uma segunda fase. |
| ID do processo SoftExpert | FCFO.IDINTEGRACAO | **Obrigatório (técnico)** | 0% | Campo livre hoje, até 100 caracteres. |

**Valores fixos** (iguais em todos os cadastros recentes, a integração preenche sozinha):

| Campo | Valor |
|---|---|
| CODCOLIGADA | 1 |
| ATIVO | 1 |
| IDPAIS | 1 |
| CONTRIBUINTE | 0 |
| CODRECEITA | 1708 |
| REGIMEISS | N |
| CONTRIBUINTEISS, RETENCAOISS, ORGAOPUBLICO, PORTE, RAMOATIV, NACIONALIDADE, TIPOCONTRIBUINTEINSS, CALCULAAVP, ENTIDADEEXECUTORAPAA, APOSENTADOOUPENSIONISTA, SOCIOCOOPERADO, CONTRIBUINTE_IBS_CBS | 0 |

Alguns desses campos são obrigatórios no banco e ficam zerados nos cadastros de Compras.

## Passo a passo do teste

1. Na coleção do Postman (`05_postman_collection.json`, atualizada), rodar **11 ReadRecord – fornecedor 009586**.
2. No arquivo 12, trocar CNPJ e nome por dados de teste, com um CNPJ **válido** (o RM costuma checar o dígito).
3. Rodar a consulta 1 do arquivo 13 com o CNPJ de teste. Ela não pode voltar linha.
4. Rodar **12 SaveRecord – criar fornecedor**. Sucesso: `1;<CODCFO>`.
5. Rodar a consulta 2 do arquivo 13 e abrir o fornecedor na tela do RM de teste.
6. Usar o CODCFO gerado no XML da Ordem de Compra (arquivo 02) e testar os dois juntos.

## Pontos para confirmar

- **Compras:**
  - o padrão é mesmo PAGREC 3 (cliente e fornecedor)?
  - quem define o "Nível do fornecedor"?
- **Fiscal:** Simples Nacional, CODRECEITA 1708 e retenção de ISS: alguma regra por categoria?
- **Financeiro:** os dados bancários entram já na primeira fase?
- **TI:** a numeração automática de Cli/For está ligada (CODCFO = -1)? Qual a cultura (`WebServiceCulture`) do RM.Host?

## Correção para o pacote da Ordem de Compra (separador decimal)

A TDN avisa que o `ReadRecord` pode devolver números com separador **diferente** do que o `SaveRecord` espera. Por isso, **não copie o formato de número do ReadRecord**, ao contrário do que dizia o primeiro LEIA-ME. A regra:

| `WebServiceCulture` no RM.Host | Separador que o SaveRecord espera (sem schema) |
|---|---|
| Não configurada (padrão) | **Vírgula**: `10,0000`, como já está no arquivo 02 |
| `Invariant` (a TOTVS recomenda para integrações novas) | **Ponto**: `10.0000` |

Pergunte à TI se a tag `WebServiceCulture` existe no `RM.Host.exe.config` (ou `RM.Host.Service.exe.config`).
