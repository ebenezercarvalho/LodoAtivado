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
                
                # Criar abas para diferentes tipos de gráficos
                tab1, tab2, tab3 = st.tabs(["Gráficos de Linha", "Gráficos de Barra", "Gráficos de Dispersão"])
                
                with tab1:
                    st.subheader("Gráficos de Linha")
                    # Verificar se há colunas numéricas para plotar
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    
                    if numeric_cols:
                        # Permitir ao usuário selecionar colunas para o gráfico
                        selected_cols = st.multiselect(
                            "Selecione as colunas para visualizar",
                            options=numeric_cols,
                            default=numeric_cols[:1] if numeric_cols else None
                        )
                        
                        if selected_cols:
                            # Verificar se há uma coluna de data para usar como eixo x
                            date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
                            if date_cols:
                                x_axis = st.selectbox("Selecione a coluna para o eixo X", date_cols)
                                # Criar gráfico de linha
                                fig = px.line(df, x=x_axis, y=selected_cols, title="Evolução ao longo do tempo")
                            else:
                                # Se não houver coluna de data, usar índice
                                fig = px.line(df, y=selected_cols, title="Evolução dos valores")
                            
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
                        # Permitir ao usuário selecionar colunas para o gráfico
                        x_col = st.selectbox("Selecione a coluna categórica (eixo X)", cat_cols)
                        y_col = st.selectbox("Selecione a coluna numérica (eixo Y)", num_cols)
                        
                        # Criar gráfico de barras
                        fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} por {x_col}")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("São necessárias colunas categóricas e numéricas para criar gráficos de barra.")
                
                with tab3:
                    st.subheader("Gráficos de Dispersão")
                    # Verificar se há pelo menos duas colunas numéricas
                    if len(num_cols) >= 2:
                        # Permitir ao usuário selecionar colunas para o gráfico
                        x_col = st.selectbox("Selecione a coluna para o eixo X", num_cols)
                        y_col = st.selectbox("Selecione a coluna para o eixo Y", 
                                             [col for col in num_cols if col != x_col] if len(num_cols) > 1 else num_cols)
                        
                        # Opção para adicionar uma terceira dimensão (tamanho)
                        size_col = st.selectbox("Selecione a coluna para o tamanho dos pontos (opcional)", 
                                               ["Nenhum"] + [col for col in num_cols if col != x_col and col != y_col])
                        
                        # Criar gráfico de dispersão
                        if size_col != "Nenhum":
                            fig = px.scatter(df, x=x_col, y=y_col, size=size_col, 
                                           title=f"Relação entre {x_col} e {y_col} (tamanho: {size_col})")
                        else:
                            fig = px.scatter(df, x=x_col, y=y_col, 
                                           title=f"Relação entre {x_col} e {y_col}")
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("São necessárias pelo menos duas colunas numéricas para criar gráficos de dispersão.")
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