# 📊 Preditivo de Churn & Inatividade Transacional em Fintechs

![Dashboard Overview](img/dashboard_churn.png)

## 🔎 Problema de Negócio
No mercado de meios de pagamento, adquirência e subadquirência, a evasão de clientes (churn) e a ociosidade de terminais/contas impactam diretamente o TPV e a margem de contribuição. A identificação precoce de contas em desaceleração transacional possibilita ações preventivas de retenção antes do cancelamento definitivo.

## 🛠️ Arquitetura e Tecnologias
- **Python (Pandas, NumPy):** Geração de base sintética transacional, limpeza, engenharia de recursos (recência e variação MoM) e regras lógicas de risco.
- **SQL / Modelagem:** Estruturação dos dados em esquema relacional (Dimensão Lojistas x Fato Transações).
- **Power BI (DAX):** Construção de KPIs executivos, análises temporais e painel de atuação operacional.

## 💡 Métricas e Regras de Negócio Implementadas
1. **Recência:** Medição diária do gap de transações por cliente (`dias_sem_transacionar`).
2. **Variação MoM (%):** Comparativo do TPV dos últimos 30 dias versus o período anterior de 31 a 60 dias.
3. **Classificação Dinâmica de Risco:**
   - 🔴 **Alto Risco:** >15 dias sem transacionar OU queda de TPV $\le$ -50%.
   - 🟡 **Médio Risco:** Queda de TPV entre -20% e -50%.
   - 🟢 **Saudável:** TPV estável ou em crescimento.
4. **Lojistas Ociosos:** Mapeamento de clientes com 100% de queda no volume comercializado.

## 📈 Insights e Resultados do Dashboard
- **Diagnóstico da Base:** Mapeamento de **R$ 2,39 Mi em TPV sob alto risco** de churn.
- **Volume Critico:** Identificação de **17 lojistas completamente ociosos** no último ciclo.
- **Plano de Ação:** Tabela operacional parametrizada por recência para atuação prioritária do time de Customer Success (CS).