# Lado SoftExpert (v3.1): como o dado sai da SoftExpert e chega ao RM

> Fontes: documentação oficial da SoftExpert (developer.softexpert.com e documents.softexpert.com), lida em 16/10/2026. A versão do SoftExpert Suite usada pela empresa precisa ser confirmada; a documentação abaixo é da 3.1.

## Três caminhos possíveis

| # | Caminho | Como funciona | Quando escolher |
|---|---|---|---|
| **A** | **Fonte de dados SOAP (DI002) apontando para o RM** | Cadastra-se o WSDL do `wsDataServer` do RM na SoftExpert. A própria SoftExpert chama o `SaveRecord` com os dados do formulário. | Sem servidor intermediário. Bom para começar, se o WSDL do RM for aceito (ver os riscos abaixo). |
| **B** | **Atividade de sistema do Workflow + aplicação externa (PM042)** | Depois da aprovação, uma atividade de sistema chama uma aplicação externa (URL ou script). A seção **Envio de dados** manda os atributos do processo; a seção **Retorno de dados** grava a resposta em atributos, por exemplo o nº da OC gerada no RM. | Quando for preciso tratar regras: anti-duplicidade, montar o rateio, devolver o erro ao processo. **Recomendado para a versão final.** |
| **C** | **Serviço intermediário que consulta a SoftExpert** | Um serviço agendado lê os processos aprovados pela Web API REST da SoftExpert e grava no RM. | Quando a TI preferir controlar tudo fora da SoftExpert. Tem atraso, porque depende do agendamento. |

O teste de hoje (Postman → RM) vale para os três caminhos: o XML enviado ao RM é o mesmo.

## A) Fonte de dados SOAP (DI002)

- **Onde:** Gerenciamento de fontes de dados > Fonte de dados > SOAP (DI002).
- **Cadastro:** dá para importar a partir do arquivo WSDL (botão "Incluir fonte de dados Web Service a partir de arquivo WSDL"). O WSDL do RM fica em `http://<RM.Host>:8051/wsDataServer/MEX?wsdl`; salve-o como arquivo antes de importar.
- **Autenticação:** escolha **Autenticação básica** (usuário e senha do RM), que é o que o wsDataServer usa. A opção "API key" é só para WSDL da própria SoftExpert.
- **Endpoint:** em **Avançado > URL de conexão**, informe `http://<RM.Host>:8051/wsDataServer/IwsDataServer`. Se o WSDL tiver mais de um binding, a SoftExpert usa o primeiro que encontrar.
- **Teste:** a etapa **Resumo > Teste de consumo** permite chamar o `SaveRecord` na hora, com os parâmetros DataServerName, XML e Contexto, e mostra o retorno em JSON.
- **Riscos para conferir no primeiro teste:** a SoftExpert **não suporta** WSDL com arrays (`soap-enc:Array` ou `element[]`), tag `<any>` aninhada, herança com `<extension>` nem retornos de estrutura dinâmica. O WSDL do RM é gerado pelo WCF. Se a importação falhar, siga pelo caminho B.

## B) Atividade de sistema + aplicação externa

1. **Cadastrar a aplicação externa** em Processo > Cadastro > Automação: Aplicação externa (**PM042**). Informe um Identificador, um Nome e o **Caminho da aplicação** (a URL do script ou serviço). Na aba **Parâmetro**, declare os parâmetros recebidos.
2. **Montar o processo:** no desenho, incluir uma **atividade de sistema** logo depois da aprovação final.
3. **Configurar a atividade:**
   - **Envio de dados:** para cada parâmetro, escolha Constante ou Variável. Variável = um atributo do formulário, como fornecedor, centro de custo ou itens.
   - **Retorno de dados:** escolha o atributo que vai receber o retorno. Exemplos: "Nº OC RM", "IDMOV RM", "Mensagem de erro".
   - **Alvo e expressão condicional:** desviar para uma atividade de correção quando o RM devolver erro.
4. **SDK PHP do Workflow:** se a aplicação externa rodar dentro do SoftExpert (pasta `customization/web/wwwroot/workflow/wf_app`), ela pode usar o SDK oficial (`getAttributeValue`, `setAttributeValue`, `getEntityAttributeValue`…) para ler e gravar dados do processo. A SoftExpert proíbe usar funções fora desse SDK.

## C) Web API REST da SoftExpert

- **API Gateway:** `https://<seu-dominio>/apigateway/`
- **Autenticação:** **API Key** (token JWT) do usuário, pego na tela "Conta do usuário", seção API Gateway. HTTPS obrigatório desde a 2.2.
- **Endpoints úteis:**
  - Consultar dados do workflow: `GET /apigateway/se/exp/chatbot/api/instance-attribute.php`
  - Consultar instância: `GET` da seção Workflow > Process / Instance
  - Tabelas do formulário (entidades dinâmicas): seção Form > Table
- **Documentação:** https://developer.softexpert.com/docs/category/openapi/rest/workflow

## Usuário de integração (recomendação oficial da SoftExpert)

Crie um usuário **exclusivo** para integrações na SoftExpert:

- com **um único grupo de acesso** e **uma licença MANAGER**;
- **sem sincronizar com o AD**;
- sem uso no dia a dia.

Assim o histórico do que foi integrado fica rastreável. As credenciais do RM podem ser guardadas na tela **Credenciais (DI004)** e referenciadas pela fonte de dados, em vez de digitadas em cada lugar.

## Fornecedor na SoftExpert

A SoftExpert tem um componente próprio de **Fornecedor** (tabelas `ADCOMPANY` / `GNSUPPLIER`, com categoria e nível de qualidade). A API REST tem um endpoint para gravar o **nível de qualidade** do fornecedor.

- **Se a empresa usar esse componente:** a homologação do fornecedor pode acontecer nele, e o "Nível do fornecedor" vai para o RM em `FCFOCOMPL.NIVELFORN`.
- **Se não usar:** o cadastro fica num formulário do Workflow, como descrito em `10_LEIA-ME_FORNECEDOR.md`.

## Links

- [Integrar com o SoftExpert Suite](https://developer.softexpert.com/docs/data-integration/getting-started/integrate-with-softexpert-suite)
- [Autenticação e segurança (API Key, usuário de integração, DI004)](https://developer.softexpert.com/docs/data-integration/authentication-guides)
- [Fonte de dados SOAP (DI002)](https://developer.softexpert.com/docs/data-integration/menu-data-source/soap-data-source)
- [Configurar uma fonte de dados SOAP](https://documents.softexpert.com/pt_BR/manage_data_source/di_002)
- [Fonte SOAP a partir de WSDL](https://documents.softexpert.com/pt_BR/manage_data_source/di_0021)
- [Cadastro de aplicação externa (PM042)](https://developer.softexpert.com/docs/data-integration/tutorials-and-articles/external-applications/external-application-menu)
- [SDK PHP do Workflow](https://developer.softexpert.com/docs/data-integration/tutorials-and-articles/external-applications/sdk-workflow-guide)
- [Configurações da atividade (Envio/Retorno de dados)](https://documents.softexpert.com/pt_BR/process_advanced_resources/pm_02227)
- [Consultar dados do workflow (REST)](https://developer.softexpert.com/docs/openapi/rest/workflow/get-instance-attribute)
- [Modelo de dados – Fornecedor](https://developer.softexpert.com/docs/database-docs/data-template/supplier/su001)
