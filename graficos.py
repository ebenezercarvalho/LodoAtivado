import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import supabase

# Função para inicializar conexão com Supabase
def init_connection():
    # Obter as credenciais do secrets.toml
    supabase_url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    supabase_key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    
    # Criar cliente do Supabase
    client = supabase.create_client(supabase_url, supabase_key)
    return client

# Função para buscar dados da tabela microbiologia
def fetch_microbiologia_data(client):
    try:
        response = client.table('microbiologia').select('*').execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Função principal para exibir a página de gráficos
def show_graficos():
    st.title("Gráficos de Microbiologia")
    st.write("Visualize os dados de microbiologia em formato gráfico.")
    
    # Exibir spinner durante o carregamento dos dados
    with st.spinner("Carregando dados para gráficos..."):
        # Inicializar conexão Supabase
        supabase_client = init_connection()
        
        # Buscar dados da tabela microbiologia
        result = fetch_microbiologia_data(supabase_client)
        
        if result["success"]:
            if result["data"]:
                # Converter para DataFrame para visualização
                df = pd.DataFrame(result["data"])
                
                # Criar abas para diferentes tipos de gráficos (removido gráfico de dispersão)
                tab1, tab2 = st.tabs(["Gráficos de Linha", "Gráficos de Barra"])
                
                with tab1:
                    st.subheader("Gráficos de Linha")
                    # Verificar se há colunas numéricas para plotar
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    
                    if numeric_cols:
                        # Converter a coluna de data para datetime se não estiver
                        if 'dataamostra' in df.columns and df['dataamostra'].dtype != 'datetime64[ns]':
                            df['dataamostra'] = pd.to_datetime(df['dataamostra'])
                        
                        # Inicializar a variável ponto_selecionado com valor padrão
                        ponto_selecionado = "Todos os Pontos"
                        
                        # Filtro por ponto de amostra
                        if 'pontoamostra' in df.columns:
                            pontos_amostra = df['pontoamostra'].unique().tolist()
                            ponto_selecionado = st.selectbox(
                                "Filtrar por Ponto de Amostra",
                                options=["Todos os Pontos"] + pontos_amostra
                            )
                            
                            # Aplicar filtro se um ponto específico for selecionado
                            if ponto_selecionado != "Todos os Pontos":
                                df_filtrado = df[df['pontoamostra'] == ponto_selecionado]
                            else:
                                df_filtrado = df
                        else:
                            df_filtrado = df
                            st.warning("Coluna 'pontoamostra' não encontrada para filtrar.")
                        
                        # Permitir ao usuário selecionar colunas para o gráfico
                        selected_cols = st.multiselect(
                            "Selecione as colunas para visualizar",
                            options=numeric_cols,
                            default=numeric_cols[:1] if numeric_cols else None
                        )
                        
                        if selected_cols:
                            # Usar a coluna dataamostra como eixo X
                            if 'dataamostra' in df_filtrado.columns:
                                # Criar gráfico de linha com data no eixo X
                                fig = px.line(df_filtrado, x='dataamostra', y=selected_cols, 
                                             title="Evolução ao longo do tempo" + 
                                             (f" - {ponto_selecionado}" if ponto_selecionado != "Todos os Pontos" else ""))
                                fig.update_xaxes(title="Data da Amostra")
                            else:
                                st.warning("Coluna 'dataamostra' não encontrada. Usando índice como eixo X.")
                                fig = px.line(df_filtrado, y=selected_cols, 
                                             title="Evolução dos valores" + 
                                             (f" - {ponto_selecionado}" if ponto_selecionado != "Todos os Pontos" else ""))
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Selecione pelo menos uma coluna para visualizar o gráfico.")
                    else:
                        st.info("Não foram encontradas colunas numéricas para criar gráficos.")
                
                with tab2:
                    st.subheader("Gráficos de Barra")
                    # Verificar se há colunas categóricas e numéricas
                    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                    num_cols = df.select_dtypes(include=['number']).columns.tolist()
                    
                    if cat_cols and num_cols:
                        # Inicializar a variável ponto_selecionado com valor padrão
                        ponto_selecionado = "Todos os Pontos"
                        
                        # Filtro por ponto de amostra
                        if 'pontoamostra' in df.columns:
                            pontos_amostra = df['pontoamostra'].unique().tolist()
                            ponto_selecionado = st.selectbox(
                                "Filtrar por Ponto de Amostra",
                                options=["Todos os Pontos"] + pontos_amostra,
                                key="barra_ponto_amostra"  # Chave única para evitar conflito com o selectbox da aba anterior
                            )
                            
                            # Aplicar filtro se um ponto específico for selecionado
                            if ponto_selecionado != "Todos os Pontos":
                                df_filtrado = df[df['pontoamostra'] == ponto_selecionado]
                            else:
                                df_filtrado = df
                        else:
                            df_filtrado = df
                            st.warning("Coluna 'pontoamostra' não encontrada para filtrar.")
                        
                        # Permitir ao usuário selecionar colunas para o gráfico
                        x_col = st.selectbox("Selecione a coluna categórica (eixo X)", cat_cols)
                        y_col = st.selectbox("Selecione a coluna numérica (eixo Y)", num_cols)
                        
                        # Criar gráfico de barras
                        fig = px.bar(df_filtrado, x=x_col, y=y_col, 
                                    title=f"{y_col} por {x_col}" + 
                                    (f" - {ponto_selecionado}" if ponto_selecionado != "Todos os Pontos" else ""))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("São necessárias colunas categóricas e numéricas para criar gráficos de barra.")
                
                # Gráfico de dispersão removido conforme solicitado
            else:
                st.info("Nenhum dado encontrado na tabela de microbiologia para gerar gráficos.")
        else:
            st.error(f"Erro ao buscar dados: {result.get('error')}")
    
    # Adicionar informações adicionais
    st.subheader("Sobre os Gráficos")
    st.write("""
    Esta seção apresenta visualizações gráficas dos dados de microbiologia. 
    Os gráficos são gerados dinamicamente com base nos dados disponíveis no banco de dados.
    
    Para uma análise mais detalhada, você pode selecionar diferentes colunas e tipos de gráficos nas abas acima.
    """)
    
    # Adicionar exibição da tabela de dados abaixo dos gráficos
    st.divider()
    st.subheader("Tabela de Dados")
    st.write("Visualize os dados completos da tabela de microbiologia.")
    
    if result["success"] and result["data"]:
        # Converter para DataFrame para visualização se ainda não foi feito
        df = pd.DataFrame(result["data"])
        
        # Criar colunas para layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Adicionar filtros e busca
            st.text_input("Filtrar dados", key="filter_text_graficos", 
                         placeholder="Digite para filtrar...")
        
        with col2:
            # Adicionar opção de download
            if len(result["data"]) > 0:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="microbiologia_data.csv",
                    mime="text/csv",
                )
        
        # Aplicar filtro se houver texto de filtro
        if "filter_text_graficos" in st.session_state and st.session_state.filter_text_graficos:
            filter_text = st.session_state.filter_text_graficos.lower()
            filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(filter_text, case=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
        
        # Mostrar estatísticas básicas
        st.subheader("Resumo dos Dados")
        st.info(f"Total de registros: {len(df)}")
        
        # Exibir estatísticas numéricas se houver colunas numéricas
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.write("Estatísticas das colunas numéricas:")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)