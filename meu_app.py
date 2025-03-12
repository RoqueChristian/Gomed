import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Go MED SAÚDE", page_icon=":bar_chart:", layout="wide")

with st.container():
    # Tratamento de Erros na Leitura do Arquivo
    try:
        df = pd.read_csv("df_vendas.csv")
    except FileNotFoundError:
        st.error("Arquivo 'df_vendas.csv' não encontrado. Certifique-se de que o arquivo existe e o caminho está correto.")
        st.stop()  # Impede a execução do restante do código
    except pd.errors.EmptyDataError:
        st.error("O arquivo 'df_vendas.csv' está vazio.")
        st.stop()
    except pd.errors.ParserError:
        st.error("Erro ao analisar o arquivo 'df_vendas.csv'. Verifique o formato do arquivo.")
        st.stop()
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar o arquivo: {e}")
        st.stop()

    # Funções de Formatação
    def formatar_moeda(valor, simbolo_moeda="R$"):
        """Formata um valor numérico como moeda."""
        return f"{simbolo_moeda} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Funções de Agregação e Cálculo
    def calcular_metricas(df):
        """Calcula e retorna métricas de vendas."""
        Total_NF = len(df['NF'].unique())
        Total_Qtd_Produto = df['Qtd_Produto'].sum()
        Valor_Total_item = df['Valor_Total_Item'].sum()
        Total_Custo_Compra = df['Total_Custo_Compra'].sum()
        Total_Lucro_Venda = df['Total_Lucro_Venda_Item'].sum()
        return Total_NF, Total_Qtd_Produto, Valor_Total_item, Total_Custo_Compra, Total_Lucro_Venda

    def agrupar_e_somar_linha(df):
        """Agrupa e soma vendas por linha de produto."""
        return df.groupby('Linha').agg(
            {'Valor_Total_Item': 'sum', 'Total_Custo_Compra': 'sum', 'Total_Lucro_Venda_Item': 'sum'}
        ).reset_index()

    def agrupar_e_somar_vendedor(df):
        """Agrupa e soma vendas por vendedor."""
        return df.groupby('Vendedor').agg(
            {'Valor_Total_Item': 'sum', 'Total_Custo_Compra': 'sum', 'Total_Lucro_Venda_Item': 'sum'}
        ).reset_index()

    def produtos_mais_vendidos(df, top_n=10, ordenar_por='Valor_Total_Item'):
        """Retorna os top N produtos mais vendidos."""
        df_agrupado = df.groupby('Descricao_produto')[ordenar_por].sum().reset_index()
        df_ordenado = df_agrupado.sort_values(by=ordenar_por, ascending=False)
        return df_ordenado.head(top_n)

    # Funções de Filtro
    def aplicar_filtros(df, vendedor, mes, ano, situacao, valor_min, valor_max):
        """Aplica filtros ao DataFrame."""
        df_filtrado = df.copy()
        if vendedor != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Vendedor'] == vendedor]
        if mes != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Mes'] == mes]
        if ano != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Ano'] == ano]
        if situacao != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['situacao'] == situacao]
        if valor_min is not None:
            df_filtrado = df_filtrado[df_filtrado['Valor_Total_Item'] >= valor_min]
        if valor_max is not None:
            df_filtrado = df_filtrado[df_filtrado['Valor_Total_Item'] <= valor_max]
        return df_filtrado

    # Funções de Gráficos
    def criar_grafico_barras(df, x, y, title, labels):
        """Cria e retorna um gráfico de barras."""
        return px.bar(df, x=x, y=y, title=title, labels=labels)

    # Renderiza a página de vendas com filtros, métricas e gráficos.
    vendedores = df['Vendedor'].unique().tolist()
    mes = df['Mes'].unique().tolist()
    ano = df['Ano'].unique().tolist()
    situacao = df['situacao'].unique().tolist()

    with st.expander("Filtros"):
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            vendedor_selecionado = st.selectbox("Selecionar Vendedor", options=['Todos'] + vendedores)
        with col2:
            mes_selecionado = st.selectbox("Selecionar Mes", options=['Todos'] + mes)
        with col3:
            ano_selecionado = st.selectbox("Selecionar Ano", options=['Todos'] + ano)
        with col4:
            situacao_selecionada = st.selectbox('Selecione a Situação', options=['Todos'] + situacao)
        with col5:
            valor_min = st.number_input("Valor Mínimo", value=None, placeholder="Opcional")
        with col6:
            valor_max = st.number_input("Valor Máximo", value=None, placeholder="Opcional")

    df_filtrado = aplicar_filtros(df, vendedor_selecionado, mes_selecionado, ano_selecionado, situacao_selecionada, valor_min, valor_max)

    # Métricas
    Total_NF, Total_Qtd_Produto, Valor_Total_item, Total_Custo_Compra, Total_Lucro_Venda = calcular_metricas(df_filtrado)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total de Notas", f"{Total_NF}")
    col2.metric("Total de Produtos", f"{Total_Qtd_Produto}")
    col3.metric("Faturamento Total", formatar_moeda(Valor_Total_item))
    col4.metric("Custo Total", formatar_moeda(Total_Custo_Compra))
    col5.metric("Lucro Total", formatar_moeda(Total_Lucro_Venda))

    # Gráficos
    st.subheader("Vendas por Linha de Produto")
    fig_linha = criar_grafico_barras(agrupar_e_somar_linha(df_filtrado), 'Linha', 'Valor_Total_Item',
                                    'Vendas por Linha de Produto', {'Valor_Total_Item': 'Valor Total de Venda'})
    st.plotly_chart(fig_linha)

    st.subheader("Vendas por Vendedor")
    fig_vendedor = criar_grafico_barras(agrupar_e_somar_vendedor(df_filtrado), 'Vendedor', 'Valor_Total_Item',
                                        'Vendas por Vendedor', {'Valor_Total_Item': 'Valor Total de Venda'})
    st.plotly_chart(fig_vendedor)

    st.subheader("Top 10 Produtos Mais Vendidos")
    fig_produtos = criar_grafico_barras(produtos_mais_vendidos(df_filtrado), 'Descricao_produto', 'Valor_Total_Item',
                                        'Top 10 Produtos Mais Vendidos',
                                        {'Descricao_produto': 'Produto', 'Valor_Total_Item': 'Valor Total de Venda'})
    st.plotly_chart(fig_produtos)