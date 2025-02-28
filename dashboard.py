import streamlit as st
import pandas as pd
from datetime import date
from utils import carregar_dados  # Importa a função de carregar dados
import asyncio
import matplotlib.pyplot as plt
import io

# Configuração da página
st.set_page_config(page_title="Painel de Licenças", layout="wide")

# Carregar os dados (executando a função assíncrona)
df = asyncio.run(carregar_dados())

# Certificar-se de que a coluna 'validade' é do tipo datetime.date
if 'validade' in df.columns:
    df['validade'] = pd.to_datetime(df['validade']).dt.date

# Título do painel
st.title("📊 Painel de Licenças Ambientais")

# Métrica 1: Quantidade de Registros
total_registros = len(df)
st.metric("Total de Registros", total_registros)

# Data atual
hoje = date.today()

# Métrica 2: Próximos Vencimentos
proximos_vencimentos = df[df['validade'] > hoje].sort_values(by='validade')

# Adicionar coluna de dias restantes
proximos_vencimentos['Dias Restantes'] = proximos_vencimentos['validade'].apply(lambda x: (x - hoje).days)

# Selecionar apenas as colunas desejadas
colunas_exibir = ['numero_licenca', 'atividade', 'razao_social', 'tipo_licenca', 'data_emissao', 'validade', 'status', 'Dias Restantes']
proximos_vencimentos_filtrados = proximos_vencimentos[colunas_exibir]
    
st.subheader("📅 Próximos Vencimentos")
st.dataframe(proximos_vencimentos_filtrados.head(10))  # Exibe apenas as colunas selecionadas

# Botão para exportar próximos vencimentos como CSV
if not proximos_vencimentos_filtrados.empty:
    csv_data = proximos_vencimentos_filtrados.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Exportar Próximos Vencimentos (CSV)",
        data=csv_data,
        file_name="proximos_vencimentos.csv",
        mime="text/csv",
    )
else:
    st.warning("Não há próximos vencimentos para exportar.")

# Função para criar uma imagem da tabela usando Matplotlib
def salvar_tabela_como_imagem(df):
    fig, ax = plt.subplots(figsize=(12, 4))  # Ajuste o tamanho conforme necessário
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)  # Ajuste o tamanho da fonte
    table.scale(1.2, 1.2)  # Ajuste a escala da tabela
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')  # Salva a imagem em memória
    buf.seek(0)
    return buf.getvalue()

# Botão para exportar próximos vencimentos como imagem
if not proximos_vencimentos_filtrados.empty:
    image_data = salvar_tabela_como_imagem(proximos_vencimentos_filtrados.head(10))  # Limita a 10 linhas
    st.download_button(
        label="Exportar Próximos Vencimentos como Imagem (PNG)",
        data=image_data,
        file_name="proximos_vencimentos.png",
        mime="image/png",
    )
else:
    st.warning("Não há próximos vencimentos para exportar.")

# Métrica 3: Licenças Vencidas
licencas_vencidas = df[df['validade'] <= hoje].sort_values(by='validade')

# Adicionar coluna de dias vencidos
licencas_vencidas['Dias Vencidos'] = licencas_vencidas['validade'].apply(lambda x: (hoje - x).days)

# Selecionar apenas as colunas desejadas
licencas_vencidas_filtradas = licencas_vencidas[colunas_exibir[:-1] + ['Dias Vencidos']]  # Substitui 'Dias Restantes' por 'Dias Vencidos'

st.subheader("❌ Licenças Vencidas")
st.dataframe(licencas_vencidas_filtradas.head(10))  # Exibe apenas as colunas selecionadas

# Botão para exportar licenças vencidas como CSV
if not licencas_vencidas_filtradas.empty:
    csv_data = licencas_vencidas_filtradas.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Exportar Licenças Vencidas (CSV)",
        data=csv_data,
        file_name="licencas_vencidas.csv",
        mime="text/csv",
    )
else:
    st.warning("Não há licenças vencidas para exportar.")

# Botão para exportar licenças vencidas como imagem
if not licencas_vencidas_filtradas.empty:
    image_data = salvar_tabela_como_imagem(licencas_vencidas_filtradas.head(10))  # Limita a 10 linhas
    st.download_button(
        label="Exportar Licenças Vencidas como Imagem (PNG)",
        data=image_data,
        file_name="licencas_vencidas.png",
        mime="image/png",
    )
else:
    st.warning("Não há licenças vencidas para exportar.")

# Métrica 4: Tipos de Licenças
tipos_licencas = df['tipo_licenca'].value_counts()

# Criar um gráfico Plotly com barras mais estreitas
import plotly.express as px
df_tipos_licencas = tipos_licencas.reset_index()
df_tipos_licencas.columns = ['Tipo de Licença', 'Quantidade']
fig = px.bar(
    df_tipos_licencas,
    x='Tipo de Licença',
    y='Quantidade',
    labels={'Tipo de Licença': 'Tipos', 'Quantidade': 'Total'},
    text='Quantidade',  # Exibir os valores nas barras
)
# Ajustar a largura das barras
fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')), width=0.4)  # Largura menor
# Melhorar o layout
fig.update_layout(
    xaxis_title="Tipos de Licença",
    yaxis_title="Quantidade",
    showlegend=False,  # Ocultar legenda se não for necessária
    height=400,  # Altura do gráfico
)
st.subheader("📋 Tipos de Licenças")
st.plotly_chart(fig, use_container_width=True)

# Filtros Interativos
st.sidebar.header("Filtros")
filtro_tipo = st.sidebar.multiselect(
    "Filtrar por Tipo de Licença",
    options=df['tipo_licenca'].unique(),
    default=df['tipo_licenca'].unique()
)
filtro_status = st.sidebar.multiselect(
    "Filtrar por Status",
    options=df['status'].unique(),
    default=df['status'].unique()
)
# Aplicar filtros
df_filtrado = df[df['tipo_licenca'].isin(filtro_tipo) & df['status'].isin(filtro_status)]
st.subheader("Licenças Filtradas")
st.dataframe(df_filtrado)