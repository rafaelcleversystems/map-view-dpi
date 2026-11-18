# MapView · DPI e Inteligência Artificial

Aplicação HTML/CSS/JavaScript para o Tema 2 · Diagnóstico Comparativo Internacional. Usa exclusivamente a planilha `data/Tema2_DPI_IA_Base_Global_MapView.xlsx`. Não calcula índices sintéticos nem altera métricas.

## Executar offline

Abra **index.html** no Chrome, Edge ou Firefox. Nenhuma instalação, conexão, Excel, Python ou servidor · necessário. `start.bat` abre o arquivo no Windows; Linux/macOS: `sh start.sh`. Todos os dados, fronteiras e bibliotecas estão neste diretório. Links de referência abrem páginas externas apenas quando acionados.

Opcionalmente, com Python 3 instalado, execute `start.bat 8080` ou `sh start.sh 8080` para servir em `http://127.0.0.1:8080`. A porta · configurável pelo argumento. O servidor atende somente a interface local; Ctrl+C encerra.

## Explorar

Escolha fonte e indicador. A cor representa um indicador original por vez. Alterar filtros ou indicador preserva a posição e zoom. Escalas fixas: GTMI agregado e componentes 0–1, Oxford 0–100, DGI/OURdata agregados 0–1. Para contagens DPI, códigos GTMI e parcelas ponderadas OCDE, a base não fornece limites fixos autoritativos: a interface informa o intervalo observado. A escala observada considera o recorte atual. O indicador e sua unidade aparecem na legenda e no tooltip.

Passe o cursor para a síntese das quatro fontes; clique para todos os campos agrupados por fonte, precisão completa, unidade, descrição, disponibilidade, referência e ano. Exporte o país como CSV UTF-8 (separador ponto e vírgula; ausências vazias e zeros preservados). A busca aceita nomes com ou sem acento e ISO3/ISO2. Países fora dos filtros ficam esmaecidos; a busca respeita os mesmos filtros. O destaque dourado identifica o estudo e não muda cores ou valores. Brasil tem acesso direto no painel inicial. A tela cheia depende do suporte do navegador.

## Dados e validação

214 registros nacionais/territoriais, 64 colunas, 13 prioritários, 45 indicadores numéricos e 9.281 registros na aba longa. Os 12 sistemas regionais permanecem separados, disponíveis em “Sobre os dados”. A aba LEIA_ME completa · preservada nos metadados e exibida na interface.

Correspondência cartográfica estritamente por ISO3. Sete registros não possuem geometria exata: BES, GLP, GUF, KSV, MTQ, WBG e XKX. Continuam pesquisáveis e exportáveis; não são associados por nomes ou códigos presumidos. Kosovo está originalmente representado como KSV e XKX: isso foi registrado sem deduplicar. Consulte `validation/validation_report.json`, inclusive a lista de geometrias sem dados. Formas sem observação ficam cinza; zero permanece numérico.

Os seis casos requeridos estão no relatório. Há zero duplicidades ISO3, zero divergências entre tabela longa e consolidada, zero indicadores sem dicionário e zero valores fora das escalas fixas verificadas. 754 zeros e 2.413 ausências numéricas foram preservados. Datas e referências refletem a planilha, não uma atualização das fontes. Fronteiras não expressam posição sobre disputas territoriais.

## Atualizar a planilha

Somente o pré-processamento requer Python 3.9+; não há pacotes obrigatórios:

```sh
python scripts/prepare_data.py
# Ou outro arquivo:
python scripts/prepare_data.py caminho/arquivo.xlsx
```

O conversor usa ZIP/XML da biblioteca padrão, lê as abas por seus nomes e relações reais, preserva células nulas e zero e confronta todos os registros da aba longa. Gera `countries.json`, `indicators.json`, `indicators_long.json`, `metadata.json`, `bundle.js` e o relatório. Não modifica o XLSX. O bundle contém os mesmos dados e fronteiras dos JSON, permitindo abertura direta sem fetch. Após atualizar dados, execute os testes e revise o relatório antes de usar na pesquisa.

## Organização

- `js/data.js`: estado, unidades, seleção e formatação.
- `js/map.js`: Leaflet, geometria e cores.
- `js/filters.js`: controles e busca.
- `js/tooltip.js`: resumo, detalhe e CSV.
- `js/app.js`: inicialização e notas metodológicas.
- `scripts/prepare_data.py`: importação e validação reproduzíveis.
- `validation/browser_report.json`: resultados dos testes de navegador.

## Licenças e origem cartográfica

Leaflet 1.9.4, licença BSD-2-Clause em `vendor/leaflet/LICENSE`, obtido de https://leafletjs.com/. Fronteiras Natural Earth (domínio público), distribuídas por https://github.com/datasets/geo-countries sob ODC PDDL. Cópia local em `data/world.geojson`. Bibliotecas e fronteiras foram obtidas durante o desenvolvimento; nenhuma · baixada em execução. As métricas e links das quatro fontes são fornecidos no dicionário e nos metadados originais.

## Popup dos países

O resumo usa duas colunas em telas maiores. Clique no país para fixá-lo e ler com calma; o painel detalhado também é atualizado. Clique fora do popup para liberar o mouse over, ou em outro país para fixar o novo resumo. Use o ícone Copiar para enviar o conteúdo à área de transferência. Em telas pequenas, a janela fica limitada à área visível e permite rolagem quando necessário.
