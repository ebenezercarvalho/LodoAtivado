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
    st.title("Informações da Microbiologia de Lodos Ativados")
    st.write("Selecione abaixo o tipo de gráfico que deseja visualizar e filtre os dados conforme necessário.")
    
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
                        
                        # Criar colunas para os filtros
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        
                        with col1:
                            # Filtro por ponto de amostra
                            if 'pontoamostra' in df.columns:
                                pontos_amostra = df['pontoamostra'].unique().tolist()
                                ponto_selecionado = st.selectbox(
                                    "Filtrar por Ponto de Amostra",
                                    options=["Todos os Pontos"] + pontos_amostra
                                )
                        
                        with col2:
                            # Adicionar filtro de data
                            if 'dataamostra' in df.columns:
                                # Obter datas mínima e máxima
                                min_date = df['dataamostra'].min()
                                max_date = df['dataamostra'].max()
                                
                                # Calcular data de 6 meses atrás
                                six_months_ago = max_date - pd.DateOffset(months=6)
                                
                                # Criar filtro de data
                                start_date = st.date_input("Data Inicial", six_months_ago, key="grafico_start_date")
                        
                        with col3:
                            # Continuar o filtro de data
                            if 'dataamostra' in df.columns:
                                end_date = st.date_input("Data Final", max_date, key="grafico_end_date")
                        
                        with col4:
                            # Espaçamento para alinhar com os outros campos
                            st.write("")  # Adiciona um espaço vazio
                            st.write("")  # Adiciona outro espaço vazio
                            # Botão para resetar filtros dos gráficos
                            if st.button("Resetar Filtros", key="reset_grafico_filters"):
                                # Preservar o estado de login e layout
                                logged_in = st.session_state.get('logged_in', False)
                                current_page = st.session_state.get('current_page', 'Login')
                                
                                # Limpar apenas os estados relacionados aos filtros dos gráficos
                                for key in list(st.session_state.keys()):
                                    if key.startswith('grafico_'):
                                        del st.session_state[key]
                                
                                # Resetar o ponto de amostra para "Todos os Pontos"
                                st.session_state.grafico_ponto_amostra = "Todos os Pontos"
                                
                                # Restaurar o estado de login e layout
                                st.session_state['logged_in'] = logged_in
                                st.session_state['current_page'] = current_page
                                
                                st.rerun()
                        
                        # Permitir ao usuário selecionar colunas para o gráfico
                        selected_cols = st.multiselect(
                            "Selecione os microrganismos para visualizar",
                            options=numeric_cols,
                            default=['ciliadoslivres'] if 'ciliadoslivres' in numeric_cols else numeric_cols[:1] if numeric_cols else None
                        )
                        
                        if selected_cols:
                            # Aplicar filtro se um ponto específico for selecionado
                            if ponto_selecionado != "Todos os Pontos":
                                df_filtrado = df[df['pontoamostra'] == ponto_selecionado]
                            else:
                                df_filtrado = df
                            # Agrupar por data e somar os valores das colunas selecionadas
                            if 'dataamostra' in df_filtrado.columns:
                                df_agrupado = df_filtrado.groupby('dataamostra')[selected_cols].sum().reset_index()
                            else:
                                df_agrupado = df_filtrado
                            # Aplicar filtro de data
                            if 'dataamostra' in df_agrupado.columns:
                                if 'grafico_start_date' not in st.session_state:
                                    st.session_state.grafico_start_date = six_months_ago
                                if 'grafico_end_date' not in st.session_state:
                                    st.session_state.grafico_end_date = max_date
                                df_agrupado = df_agrupado[
                                    (df_agrupado['dataamostra'].dt.date >= st.session_state.grafico_start_date) &
                                    (df_agrupado['dataamostra'].dt.date <= st.session_state.grafico_end_date)
                                ]
                            # Criar gráfico de linha com data no eixo X
                            fig = px.line(df_agrupado, x='dataamostra', y=selected_cols, 
                                         title="Evolução ao longo do tempo" + 
                                         (f" - {ponto_selecionado}" if ponto_selecionado != "Todos os Pontos" else ""))
                            fig.update_xaxes(title="Data da Amostra")
                            fig.update_yaxes(title="Somatório")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Selecione pelo menos um microrganismo para visualizar o gráfico.")
                    else:
                        st.info("Não foram encontradas colunas numéricas para criar gráficos.")
                
                with tab2:
                    st.subheader("Gráficos de Barra")
                    # Verificar se há colunas categóricas e numéricas
                    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                    num_cols = df.select_dtypes(include=['number']).columns.tolist()
                    
                    if cat_cols and num_cols:
                        # Criar colunas para os filtros
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        
                        with col1:
                            # Filtro por ponto de amostra
                            if 'pontoamostra' in df.columns:
                                pontos_amostra = df['pontoamostra'].unique().tolist()
                                ponto_selecionado = st.selectbox(
                                    "Filtrar por Ponto de Amostra",
                                    options=["Todos os Pontos"] + pontos_amostra,
                                    key="grafico_barra_ponto_amostra"
                                )
                        
                        with col2:
                            # Adicionar filtro de data
                            if 'dataamostra' in df.columns:
                                # Obter datas mínima e máxima
                                min_date = df['dataamostra'].min()
                                max_date = df['dataamostra'].max()
                                
                                # Calcular data de 6 meses atrás
                                six_months_ago = max_date - pd.DateOffset(months=6)
                                
                                # Criar filtro de data
                                start_date = st.date_input("Data Inicial", six_months_ago, key="grafico_barra_start_date")
                        
                        with col3:
                            # Continuar o filtro de data
                            if 'dataamostra' in df.columns:
                                end_date = st.date_input("Data Final", max_date, key="grafico_barra_end_date")
                        
                        with col4:
                            # Espaçamento para alinhar com os outros campos
                            st.write("")  # Adiciona um espaço vazio
                            st.write("")  # Adiciona outro espaço vazio
                            # Botão para resetar filtros dos gráficos
                            if st.button("Resetar Filtros", key="reset_grafico_barra_filters"):
                                # Preservar o estado de login e layout
                                logged_in = st.session_state.get('logged_in', False)
                                current_page = st.session_state.get('current_page', 'Login')
                                
                                # Limpar apenas os estados relacionados aos filtros dos gráficos de barra
                                for key in list(st.session_state.keys()):
                                    if key.startswith('grafico_barra_'):
                                        del st.session_state[key]
                                
                                # Resetar o ponto de amostra para "Todos os Pontos"
                                st.session_state.grafico_barra_ponto_amostra = "Todos os Pontos"
                                
                                # Restaurar o estado de login e layout
                                st.session_state['logged_in'] = logged_in
                                st.session_state['current_page'] = current_page
                                
                                st.rerun()
                        
                        # Aplicar filtro se um ponto específico for selecionado
                        if ponto_selecionado != "Todos os Pontos":
                            df_filtrado = df[df['pontoamostra'] == ponto_selecionado]
                        else:
                            df_filtrado = df
                        
                        # Aplicar filtro de data
                        if 'dataamostra' in df_filtrado.columns:
                            # Se não houver data inicial no estado, usar 6 meses atrás
                            if 'grafico_barra_start_date' not in st.session_state:
                                st.session_state.grafico_barra_start_date = six_months_ago
                            # Se não houver data final no estado, usar a data mais recente
                            if 'grafico_barra_end_date' not in st.session_state:
                                st.session_state.grafico_barra_end_date = max_date
                            
                            # Aplicar filtro de data
                            df_filtrado = df_filtrado[
                                (df_filtrado['dataamostra'].dt.date >= st.session_state.grafico_barra_start_date) &
                                (df_filtrado['dataamostra'].dt.date <= st.session_state.grafico_barra_end_date)
                            ]
                        
                        # Agrupar por data e ponto de amostra e somar os valores numéricos
                        if 'dataamostra' in df_filtrado.columns and 'pontoamostra' in df_filtrado.columns:
                            y_col = st.selectbox("Selecione a coluna numérica (eixo Y)", 
                                               num_cols,
                                               index=num_cols.index('ciliadoslivres') if 'ciliadoslivres' in num_cols else 0)
                            df_agrupado = df_filtrado.groupby(['dataamostra', 'pontoamostra'])[y_col].sum().reset_index()
                            # Se um ponto específico foi selecionado, filtrar e usar apenas a data no eixo X
                            if ponto_selecionado != "Todos os Pontos":
                                df_agrupado = df_agrupado[df_agrupado['pontoamostra'] == ponto_selecionado]
                                x_axis = df_agrupado['dataamostra']
                            else:
                                # Combinar data e ponto para o eixo X
                                df_agrupado['data_ponto'] = df_agrupado['dataamostra'].dt.strftime('%d/%m/%Y') + ' - ' + df_agrupado['pontoamostra']
                                x_axis = df_agrupado['data_ponto']
                            fig = px.bar(df_agrupado, x=x_axis, y=y_col, 
                                        title=f"{y_col} por Data" + 
                                        (f" - {ponto_selecionado}" if ponto_selecionado != "Todos os Pontos" else ""))
                        else:
                            fig = px.bar(df_filtrado, x='dataamostra', y=y_col, 
                                        title=f"{y_col} por Data" + 
                                        (f" - {ponto_selecionado}" if ponto_selecionado != "Todos os Pontos" else ""))
                        
                        # Formatar as datas no eixo X
                        fig.update_xaxes(title="Data da Amostra")
                        fig.update_yaxes(title=y_col)
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("São necessárias colunas categóricas e numéricas para criar gráficos de barra.")
                
                # Gráfico de dispersão removido conforme solicitado
            else:
                st.info("Nenhum dado encontrado na tabela de microbiologia para gerar gráficos.")
        else:
            st.error(f"Erro ao buscar dados: {result.get('error')}")
    
    # Adicionar informações adicionais
    # st.subheader("Sobre os Gráficos")
    # st.write("""
    # Esta seção apresenta visualizações gráficas dos dados de microbiologia. 
    # Os gráficos são gerados dinamicamente com base nos dados disponíveis no banco de dados.
    
    # Para uma análise mais detalhada, você pode selecionar diferentes colunas e tipos de gráficos nas abas acima.
    # """)
    
    # Adicionar exibição da tabela de dados abaixo dos gráficos
    st.divider()
    st.subheader("Tabela de Dados")
    st.write("Visualize os dados completos da tabela de microbiologia.")
    
    if result["success"] and result["data"]:
        # Converter para DataFrame para visualização se ainda não foi feito
        df = pd.DataFrame(result["data"])
        
        # Criar colunas para layout
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            # Adicionar filtro de data
            if 'dataamostra' in df.columns:
                # Converter para datetime se necessário
                if df['dataamostra'].dtype != 'datetime64[ns]':
                    df['dataamostra'] = pd.to_datetime(df['dataamostra'])
                
                # Obter datas mínima e máxima
                min_date = df['dataamostra'].min()
                max_date = df['dataamostra'].max()
                
                # Criar filtro de data
                start_date = st.date_input("Data Inicial", min_date, key="tabela_start_date")
        
        with col2:
            # Continuar o filtro de data
            if 'dataamostra' in df.columns:
                end_date = st.date_input("Data Final", max_date, key="tabela_end_date")
        
        with col3:
            # Adicionar filtro por Ponto de Amostra
            if 'pontoamostra' in df.columns:
                pontos_amostra = ["Todos os Pontos"] + sorted(df['pontoamostra'].unique().tolist())
                ponto_selecionado = st.selectbox(
                    "Ponto de Amostra",
                    options=pontos_amostra,
                    key="tabela_ponto_amostra"
                )
        
        with col4:
            # Espaçamento para alinhar com os outros campos
            st.write("")  # Adiciona um espaço vazio
            st.write("")  # Adiciona outro espaço vazio
            # Botão para resetar filtros
            if st.button("Resetar Filtros", key="reset_filters"):
                # Preservar o estado de login e layout
                logged_in = st.session_state.get('logged_in', False)
                current_page = st.session_state.get('current_page', 'Login')
                
                # Limpar apenas os estados relacionados aos filtros
                for key in list(st.session_state.keys()):
                    if key.startswith('tabela_'):
                        del st.session_state[key]
                
                # Restaurar o estado de login e layout
                st.session_state['logged_in'] = logged_in
                st.session_state['current_page'] = current_page
                
                st.rerun()
        
        # Aplicar filtro de data
        if 'dataamostra' in df.columns:
            # Se não houver data inicial no estado, usar a data mais antiga
            if 'tabela_start_date' not in st.session_state:
                st.session_state.tabela_start_date = min_date
            # Se não houver data final no estado, usar a data mais recente
            if 'tabela_end_date' not in st.session_state:
                st.session_state.tabela_end_date = max_date
                
            df = df[
                (df['dataamostra'].dt.date >= st.session_state.tabela_start_date) &
                (df['dataamostra'].dt.date <= st.session_state.tabela_end_date)
            ]
        
        # Aplicar filtro de Ponto de Amostra
        if 'pontoamostra' in df.columns:
            # Se não houver ponto selecionado no estado, usar "Todos os Pontos"
            if 'tabela_ponto_amostra' not in st.session_state:
                st.session_state.tabela_ponto_amostra = "Todos os Pontos"
                
            if st.session_state.tabela_ponto_amostra != "Todos os Pontos":
                df = df[df['pontoamostra'] == st.session_state.tabela_ponto_amostra]
        
        # Exibir a tabela
        st.dataframe(df, use_container_width=True)
        
        # Mostrar estatísticas básicas
        st.subheader("Resumo dos Dados")
        st.info(f"Total de registros: {len(df)}")
        
        # Exibir estatísticas numéricas se houver colunas numéricas
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.write("Estatísticas das colunas numéricas:")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)