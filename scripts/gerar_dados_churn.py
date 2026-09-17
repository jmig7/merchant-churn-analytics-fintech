import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Configuração de semente para resultados reproduzíveis
np.random.seed(42)

print("🚀 Iniciando a geração e processamento de dados transacionais...")

# 1. CRIANDO A BASE DE LOJISTAS (CLIENTES)
n_lojistas = 120
segmentos = ['Alimentação', 'Vestuário', 'Serviços', 'Saúde & Beleza', 'Eletrônicos']

lojistas_data = {
    'id_lojista': [f'LOJ-{1000 + i}' for i in range(n_lojistas)],
    'nome_fantasia': [f'Estabelecimento {i+1}' for i in range(n_lojistas)],
    'segmento_mcc': [np.random.choice(segmentos) for _ in range(n_lojistas)],
    'data_credenciamento': [
        (datetime.now() - timedelta(days=int(np.random.randint(120, 365)))).strftime('%Y-%m-%d')
        for _ in range(n_lojistas)
    ]
}
df_lojistas = pd.DataFrame(lojistas_data)

# 2. SIMULANDO O HISTÓRICO DE TRANSAÇÕES (ÚLTIMOS 90 DIAS)
data_atual = datetime.now()
transacoes = []

for idx, row in df_lojistas.iterrows():
    id_loj = row['id_lojista']
    
    # Induzindo perfis diferentes de comportamento (Saudável vs Churn)
    perfil = np.random.choice(['saudavel', 'queda_tpv', 'inativo'], p=[0.6, 0.25, 0.15])
    
    if perfil == 'saudavel':
        dias_com_vendas = range(1, 90)
        volume_medio = np.random.randint(5, 20)
    elif perfil == 'queda_tpv':
        dias_com_vendas = range(30, 90) # Parou/diminuiu drasticamente no último mês
        volume_medio = np.random.randint(2, 8)
    else: # inativo
        dias_com_vendas = range(45, 90) # Parou há mais de 45 dias
        volume_medio = np.random.randint(1, 5)

    for dia in dias_com_vendas:
        data_tx = data_atual - timedelta(days=dia)
        qtd_tx_dia = np.random.poisson(volume_medio)
        
        for _ in range(qtd_tx_dia):
            transacoes.append({
                'id_transacao': f'TX-{np.random.randint(1000000, 9999999)}',
                'id_lojista': id_loj,
                'data_hora': data_tx + timedelta(hours=int(np.random.randint(8, 20)), minutes=int(np.random.randint(0, 59))),
                'valor_tpv': round(np.random.uniform(20.0, 450.0), 2),
                'modalidade': np.random.choice(['PIX', 'Crédito à Vista', 'Crédito Parcelado', 'Débito'], p=[0.35, 0.30, 0.20, 0.15])
            })

df_transacoes = pd.DataFrame(transacoes)

# 3. ENGENHARIA DE RECURSOS (METRICAS DE CHURN & RECENTICIDADE)
df_transacoes['data_hora'] = pd.to_datetime(df_transacoes['data_hora'])
data_referencia = df_transacoes['data_hora'].max()

# Cálculo da Recência (Dias desde a última transação)
recencia = df_transacoes.groupby('id_lojista')['data_hora'].max().reset_index()
recencia['dias_sem_transacionar'] = (data_referencia - recencia['data_hora']).dt.days
recencia.rename(columns={'data_hora': 'ultima_transacao'}, inplace=True)

# Cálculo do TPV (Últimos 30 dias vs 31-60 dias atrás)
data_30d = data_referencia - timedelta(days=30)
data_60d = data_referencia - timedelta(days=60)

tpv_m1 = df_transacoes[df_transacoes['data_hora'] >= data_30d].groupby('id_lojista')['valor_tpv'].sum().reset_index()
tpv_m1.rename(columns={'valor_tpv': 'tpv_ultimos_30d'}, inplace=True)

tpv_m2 = df_transacoes[(df_transacoes['data_hora'] < data_30d) & (df_transacoes['data_hora'] >= data_60d)].groupby('id_lojista')['valor_tpv'].sum().reset_index()
tpv_m2.rename(columns={'valor_tpv': 'tpv_30d_a_60d'}, inplace=True)

# 4. CONSOLIDANDO PAINEL ANALÍTICO DO CLIENTE
df_analytics = df_lojistas.merge(recencia[['id_lojista', 'ultima_transacao', 'dias_sem_transacionar']], on='id_lojista', how='left')
df_analytics = df_analytics.merge(tpv_m1, on='id_lojista', how='left').fillna({'tpv_ultimos_30d': 0})
df_analytics = df_analytics.merge(tpv_m2, on='id_lojista', how='left').fillna({'tpv_30d_a_60d': 0})

# Variação % de TPV (MoM)
df_analytics['variacao_tpv_pct'] = np.where(
    df_analytics['tpv_30d_a_60d'] > 0,
    ((df_analytics['tpv_ultimos_30d'] - df_analytics['tpv_30d_a_60d']) / df_analytics['tpv_30d_a_60d']) * 100,
    -100.0
)

# 5. REGRA DE NEGÓCIO: FLAG DE RISCO DE CHURN
def classificar_risco(row):
    if row['dias_sem_transacionar'] > 15 or row['variacao_tpv_pct'] <= -50:
        return '🔴 Alto Risco'
    elif row['variacao_tpv_pct'] <= -20:
        return '🟡 Médio Risco'
    else:
        return '🟢 Saudável'

df_analytics['status_risco'] = df_analytics.apply(classificar_risco, axis=1)

# 6. EXPORTANDO OS DADOS TRATADOS PARA O POWER BI
df_transacoes.to_csv('transacoes_base.csv', index=False)
df_analytics.to_csv('base_analytics_churn.csv', index=False)

print("✅ Processamento concluído com sucesso!")
print(f"📊 Total de transações geradas: {len(df_transacoes)}")
print(f"🏢 Resumo de Risco da Base de Lojistas:\n{df_analytics['status_risco'].value_counts()}")