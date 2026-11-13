/* =====================================================================
   Listas de valores para o formulario de compra na SoftExpert
   Ideia: cadastrar o banco do RM como Fonte de Dados na SoftExpert (DI003)
   e usar cada SELECT abaixo como "Conjunto de dados" de um campo lista.
   Assim o formulario so oferece codigos que existem no RM e a integracao
   nao quebra por de-para errado.
   Usar um usuario de banco SOMENTE LEITURA.
   Testado em Teste_BrasiliaSeg em 08/10/2026 (quantidade de linhas no fim de cada bloco).
   ===================================================================== */

/* 1) Fornecedores ativos (PAGREC 2 = fornecedor, 3 = cliente e fornecedor)  ~9.650 linhas
      Na tela, pesquisar por CNPJ ou nome; gravar CODCFO. */
SELECT
     FCFO.CODCFO
    ,FCFO.CODCOLIGADA AS CODCOLCFO
    ,FCFO.CGCCFO      AS CNPJ_CPF
    ,FCFO.NOMEFANTASIA
    ,FCFO.NOME        AS RAZAO_SOCIAL
FROM FCFO
WHERE FCFO.CODCOLIGADA = 1
  AND FCFO.ATIVO       = 1
  AND FCFO.PAGREC IN (2, 3)
ORDER BY FCFO.NOMEFANTASIA;

/* 2) Produtos ativos de ultimo nivel, com unidade de compra  ~7.545 linhas
      Gravar IDPRD (e mostrar CODIGOPRD + nome). A unidade vem junto. */
SELECT
     TPRODUTO.IDPRD
    ,TPRODUTO.CODIGOPRD
    ,TPRODUTO.NOMEFANTASIA
    ,TPRODUTODEF.CODUNDCOMPRA
FROM TPRODUTO
INNER JOIN TPRODUTODEF
        ON TPRODUTODEF.CODCOLIGADA = TPRODUTO.CODCOLPRD
       AND TPRODUTODEF.IDPRD       = TPRODUTO.IDPRD
WHERE TPRODUTO.CODCOLPRD   = 1
  AND TPRODUTO.ULTIMONIVEL = 1
  AND TPRODUTO.INATIVO     = 0
ORDER BY TPRODUTO.CODIGOPRD;

/* 3) Centros de custo que aceitam lancamento  ~1.180 linhas */
SELECT
     GCCUSTO.CODCCUSTO
    ,GCCUSTO.NOME
FROM GCCUSTO
WHERE GCCUSTO.CODCOLIGADA = 1
  AND GCCUSTO.ATIVO       = 'T'
  AND GCCUSTO.PERMITELANC = 'T'
ORDER BY GCCUSTO.CODCCUSTO;

/* 4) Condicoes de pagamento  ~420 linhas (INATIVO nulo conta como ativo) */
SELECT
     TCPG.CODCPG
    ,TCPG.NOME
FROM TCPG
WHERE TCPG.CODCOLIGADA = 1
  AND ISNULL(TCPG.INATIVO, 0) = 0
ORDER BY TCPG.NOME;

/* 5) Natureza da despesa (Tabela 1 do fluxo - CODTB1FLX)  ~355 linhas
      Ex.: 0410 Material de Limpeza e Higiene, 0131 Pecas e Acessorios p/Veiculos */
SELECT
     FTB1.CODTB1FLX
    ,FTB1.DESCRICAO
FROM FTB1
WHERE FTB1.CODCOLIGADA = 1
  AND FTB1.ATIVO       = 1
ORDER BY FTB1.DESCRICAO;

/* 6) Tipo de custo (Tabela 2 do fluxo - CODTB2FLX)  6 linhas
      0001 Custo Direto, 0002 Custo Indireto, 0003 Despesa, 0004 Terceiros, 0005 Estoque, 0006 Investimento */
SELECT
     FTB2.CODTB2FLX
    ,FTB2.DESCRICAO
FROM FTB2
WHERE FTB2.CODCOLIGADA = 1
  AND FTB2.ATIVO       = 1
ORDER BY FTB2.CODTB2FLX;

/* 7) Departamentos da filial 1  ~105 linhas */
SELECT
     GDEPTO.CODDEPARTAMENTO
    ,GDEPTO.NOME
FROM GDEPTO
WHERE GDEPTO.CODCOLIGADA = 1
  AND GDEPTO.CODFILIAL   = 1
  AND GDEPTO.ATIVO       = 'T'
ORDER BY GDEPTO.CODDEPARTAMENTO;

/* 8) Compradores (CODVEN1): quem emitiu OC nos ultimos 12 meses  ~11 linhas */
SELECT
     TVEN.CODVEN
    ,TVEN.NOME
FROM TVEN
WHERE TVEN.CODCOLIGADA = 1
  AND TVEN.INATIVO     = 0
  AND TVEN.CODVEN IN (SELECT TMOV.CODVEN1
                        FROM TMOV
                       WHERE TMOV.CODCOLIGADA = 1
                         AND TMOV.CODTMV      = '1.1.04'
                         AND TMOV.DATAEMISSAO >= DATEADD(MONTH, -12, GETDATE()))
ORDER BY TVEN.NOME;

/* 9) Responsavel / requisitante (CODVEN2) usados nos ultimos 12 meses  ~49 linhas
      Confirmar com Compras o rotulo deste campo na tela do RM. */
SELECT
     TVEN.CODVEN
    ,TVEN.NOME
FROM TVEN
WHERE TVEN.CODCOLIGADA = 1
  AND TVEN.INATIVO     = 0
  AND TVEN.CODVEN IN (SELECT TMOV.CODVEN2
                        FROM TMOV
                       WHERE TMOV.CODCOLIGADA = 1
                         AND TMOV.CODTMV      = '1.1.04'
                         AND TMOV.DATAEMISSAO >= DATEADD(MONTH, -12, GETDATE()))
ORDER BY TVEN.NOME;
