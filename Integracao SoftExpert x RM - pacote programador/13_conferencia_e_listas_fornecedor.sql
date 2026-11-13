/* =====================================================================
   Fornecedor (FCFO) - anti-duplicidade, conferencia e listas de valores
   Testado em 16/10/2026. Comentarios so em bloco: o RM nao aceita comentario de linha.
   ===================================================================== */

/* 1) ANTI-DUPLICIDADE - rodar ANTES de cada SaveRecord.
      Compara o CNPJ/CPF so pelos numeros (o RM tem CEP e CNPJ gravados com e sem mascara).
      Se voltar linha, o fornecedor ja existe: usar o CODCFO devolvido, nao criar outro.
      Hoje ja existem 260 CNPJs repetidos na coligada 1 - a integracao nao deve aumentar isso. */
SELECT
     FCFO.CODCFO
    ,FCFO.NOMEFANTASIA
    ,FCFO.CGCCFO
    ,FCFO.ATIVO
    ,FCFO.PAGREC
FROM FCFO
WHERE FCFO.CODCOLIGADA = 1
  AND REPLACE(REPLACE(REPLACE(FCFO.CGCCFO, '.', ''), '/', ''), '-', '') = '00000000000000';  /* CNPJ so numeros */

/* 2) Conferencia do fornecedor criado pelo teste */
SELECT
     FCFO.CODCFO
    ,FCFO.IDCFO
    ,FCFO.NOME
    ,FCFO.NOMEFANTASIA
    ,FCFO.CGCCFO
    ,FCFO.PAGREC
    ,FCFO.CODTCF
    ,FCFO.CODMUNICIPIO
    ,FCFO.CODETD
    ,FCFO.ATIVO
    ,FCFO.IDINTEGRACAO
    ,FCFO.USUARIOCRIACAO
    ,FCFO.DATACRIACAO
    ,FCFOCOMPL.NIVELFORN
FROM FCFO
LEFT JOIN FCFOCOMPL
       ON FCFOCOMPL.CODCOLIGADA = FCFO.CODCOLIGADA
      AND FCFOCOMPL.CODCFO      = FCFO.CODCFO
WHERE FCFO.CODCOLIGADA = 1
  AND FCFO.IDINTEGRACAO LIKE 'SOFTEXPERT-FORN-TESTE-%';

/* ---------------- Listas de valores para o formulario ---------------- */

/* 3) Tipo de fornecedor / categoria (CODTCF)  ~125 linhas
      Mais usados no ultimo ano: 109 Servicos prestados PJ, 77 Material aplicado,
      35 Equipamentos eletronicos, 69 Lanches e refeicoes, 110 Suprimentos de informatica */
SELECT
     FTCF.CODTCF
    ,FTCF.DESCRICAO
FROM FTCF
WHERE FTCF.CODCOLIGADA = 1
ORDER BY FTCF.DESCRICAO;

/* 4) Municipios (CODMUNICIPIO = codigo IBGE sem o prefixo da UF; ex.: DF 00108 = Brasilia)  ~5.574 linhas
      No formulario: escolher UF e depois municipio. */
SELECT
     GMUNICIPIO.CODETDMUNICIPIO AS UF
    ,GMUNICIPIO.CODMUNICIPIO
    ,GMUNICIPIO.NOMEMUNICIPIO
FROM GMUNICIPIO
ORDER BY GMUNICIPIO.CODETDMUNICIPIO, GMUNICIPIO.NOMEMUNICIPIO;

/* 5) Tipo de logradouro (TIPORUA)  48 linhas - ex.: 1 RUA, 38 QUADRA, 47 SETOR */
SELECT
     DTIPORUA.CODIGO
    ,DTIPORUA.DESCRICAO
FROM DTIPORUA
ORDER BY DTIPORUA.DESCRICAO;

/* 6) Tipo de bairro (TIPOBAIRRO)  19 linhas - ex.: 1 BAIRRO */
SELECT
     DTIPOBAIRRO.CODIGO
    ,DTIPOBAIRRO.DESCRICAO
FROM DTIPOBAIRRO
ORDER BY DTIPOBAIRRO.DESCRICAO;
