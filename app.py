import streamlit as st
import supabase
from typing import Dict
import pandas as pd

# Configuração da página com layout condicional
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Login'

# Configurar layout com base na página atual
layout_mode = "wide" if st.session_state.get('layout_wide', False) else "centered"

st.set_page_config(
    page_title="Sistema de Microbiologia",
    page_icon="🔬",
    layout=layout_mode
)

# Configurações de estilo
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        font-weight: bold;
        border-radius: 5px;
    }
    .login-container {
        border: 1px solid #f0f0f0;
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
        max-width: 450px;
        margin: 50px auto;
        background-color: white;
    }
    .centered-content {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    .form-header {
        text-align: center;
        margin-bottom: 25px;
    }
    .sidebar .sidebar-content {
        background-color: #f9f9f9;
    }
    </style>""", unsafe_allow_html=True)

# Função para inicializar conexão com Supabase
def init_connection():
    # Obter as credenciais do secrets.toml
    supabase_url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    supabase_key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    
    # Criar cliente do Supabase
    client = supabase.create_client(supabase_url, supabase_key)
    return client

# Função para autenticar usuário
def login_user(client, email: str, password: str) -> Dict:
    try:
        # Realizar autenticação no Supabase
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Função para buscar dados da tabela microbiologia
def fetch_microbiologia_data(client):
    try:
        response = client.table('microbiologia').select('*').execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Função para processar o login
def process_login(email, password):
    if not email or not password:
        st.error("Por favor, preencha todos os campos!")
        return False
    
    # Inicializar conexão com Supabase
    supabase_client = init_connection()
    
    # Tentar login
    result = login_user(supabase_client, email, password)
    
    if result["success"]:
        st.session_state['logged_in'] = True
        st.session_state['current_page'] = 'Dados'
        st.success("✅ Acesso autorizado!")
        st.balloons()  # Efeito visual de sucesso
        return True
    else:
        st.error(f"❌ Falha na autenticação: {result.get('error', 'Credenciais inválidas')}")
        return False

# Iniciar sessão para controlar estado de login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Iniciar sessão para controlar navegação
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Login'

# Controle de layout para alternar entre modo centralizado e wide
if 'layout_wide' not in st.session_state:
    st.session_state['layout_wide'] = False
    
# Se estiver na página de dados, garanta que o layout seja wide
if st.session_state['current_page'] == 'Dados':
    st.session_state['layout_wide'] = True

# Barra lateral para navegação
with st.sidebar:
    st.title("🔬 Microbiologia")
    st.divider()
    
    # Exibir menu de navegação com base no estado de login
    if st.session_state['logged_in']:
        # Mostrar informações do usuário
        st.success("✅ Autenticado")
        
        # Menu de navegação para usuário autenticado
        menu_options = ["Dados"]
        selected_menu = st.radio("Navegação", menu_options)
        
        # Atualizar página atual com base na seleção
        st.session_state['current_page'] = selected_menu
        
        # Botão de logout
        if st.button("Sair"):
            st.session_state['logged_in'] = False
            st.session_state['current_page'] = 'Login'
            st.session_state['layout_wide'] = False
            st.rerun()
    else:
        # Menu simplificado para usuário não autenticado
        st.info("🔒 Área restrita")
        st.session_state['current_page'] = 'Login'
    
    # Rodapé da barra lateral
    st.divider()
    st.caption("© 2025 Sistema de Microbiologia")

# Conteúdo principal baseado na página atual
if st.session_state['current_page'] == 'Login':
    # Página de Login
    if st.session_state['logged_in']:
        st.success("Você já está autenticado!")
        st.info("Use o menu lateral para navegar pelo sistema.")
    else:
        # Título simples
        st.title("Acesso ao Sistema")
        
        # Criar um formulário para capturar a tecla Enter
        with st.form(key="login_form"):
            # Campos de entrada
            email = st.text_input("Email", placeholder="Digite seu email")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            
            # Botão de login dentro do formulário (responde ao Enter)
            login_button = st.form_submit_button("Entrar")
            
            # Processar tentativa de login quando o botão for clicado ou Enter pressionado
            if login_button:
                success = process_login(email, password)
                if success:
                    # Após login bem-sucedido, mude para layout wide
                    st.session_state['layout_wide'] = True
                    st.rerun()  # Recarregar para atualizar a interface

elif st.session_state['current_page'] == 'Dados':
    # Verificar se o usuário está autenticado
    if not st.session_state['logged_in']:
        st.warning("Você precisa fazer login para acessar esta página.")
        st.session_state['current_page'] = 'Login'
        st.session_state['layout_wide'] = False
        st.rerun()
    
    # Página de Dados
    st.title("Dados de Microbiologia")
    st.write("Visualize e analise os dados da tabela de microbiologia.")
    
    # Exibir spinner durante o carregamento dos dados
    with st.spinner("Carregando dados..."):
        # Inicializar conexão Supabase
        supabase_client = init_connection()
        
        # Buscar dados da tabela microbiologia
        result = fetch_microbiologia_data(supabase_client)
        
        if result["success"]:
            if result["data"]:
                # Converter para DataFrame para melhor visualização
                df = pd.DataFrame(result["data"])
                
                # Criar colunas para layout
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Adicionar filtros e busca
                    st.text_input("Filtrar dados", key="filter_text", 
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
                if "filter_text" in st.session_state and st.session_state.filter_text:
                    filter_text = st.session_state.filter_text.lower()
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
                
            else:
                st.info("Nenhum dado encontrado na tabela de microbiologia.")
        else:
            st.error(f"Erro ao buscar dados: {result.get('error')}")