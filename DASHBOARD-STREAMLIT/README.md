# 📊 Dashboard: Mercado de Trabalho em Pernambuco (2015–2025)
## Equipe

Maria Luísa Albuquerque · Matheus Miranda · Jorge Augusto ·
Maria Júlia Germano · Bruno Oliveira · Heitor Santana

## Objetivo

Dashboard interativo de **data storytelling** sobre o mercado de trabalho de Pernambuco,
cobrindo emprego, informalidade e desocupação no período de 2015 a 2025.

A narrativa é organizada em **4 atos**, seguindo o roteiro de storytelling da equipe:

| Ato | Tema |
|-----|------|
| 1 | O Cenário — estabilidade aparente com informalidade estrutural |
| 2 | A Crise e o Pós-Pandemia — 2017 vs. 2022 |
| 3 | A Clivagem Estrutural de Gênero |
| 4 | A Recuperação Recente — real, mas não equitativa |

---

## Tecnologias utilizadas

| Tecnologia | Versão mín. | Uso |
|------------|-------------|-----|
| Python     | 3.9+        | Linguagem base |
| Streamlit  | 1.35+       | Interface web do dashboard |
| Pandas     | 2.0+        | Leitura e tratamento dos dados |
| Matplotlib | 3.7+        | Geração de todos os gráficos |

---

## Estrutura do projeto

```
dashboard/
├── app.py               # Aplicação principal do dashboard
├── emprego.csv          # Taxa de emprego trimestral (2012–2025)
├── informalidade.csv    # Taxa de informalidade trimestral (2015–2025)
├── desocupacao.csv      # Taxa de desocupação trimestral (2012–2025)
├── requirements.txt     # Dependências do projeto
└── README.md            # Este arquivo
```

---

## Como executar

### 1. Clone ou copie os arquivos do projeto

Certifique-se de que os arquivos `.csv` estejam dentro da pasta `dados/`.

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Execute o dashboard

```bash
streamlit run app.py
```
### ou 
```
streamlit run appStreamlit.py --server runOnSave true
```


O dashboard abrirá automaticamente em `http://localhost:8501`.

---

## Fonte dos dados

- PNAD Contínua — dados trimestrais de Pernambuco, 2015–2025.
- Indicadores: taxa de emprego, taxa de informalidade e taxa de desocupação,
  desagregados por sexo (total, homens e mulheres).

---

