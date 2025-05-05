import streamlit as st
import supabase
from typing import Dict
import pandas as pd
# Importar os módulos
import graficos
import formulario

# Inicializar variáveis de estado se não existirem
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Login'

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Configurar a página - DEVE ser a primeira chamada do Streamlit
# IMPORTANTE: A página de login SEMPRE usa layout centered, outras páginas usam wide
st.set_page_config(
    page_title="Lodos Ativados - CAAN",
    page_icon="🔬",
    layout="centered" if st.session_state['current_page'] == 'Login' else "wide"
)

# Configurações básicas de estilo
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .centered-content {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    .login-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
        max-width: 450px;
        margin: 50px auto;
        background-color: #ffffff;
    }
    .form-header {
        text-align: center;
        margin-bottom: 25px;
    }
    
    /* Estilo para a página de login */
    div[data-testid="stAppViewContainer"] {
        background-image: url('https://raw.githubusercontent.com/ebenezercarvalho/LodoAtivado/main/assets/microscope-bg.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        filter: grayscale(0.0);
    }
    
    /* Overlay escuro para melhorar o contraste */
    div[data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.92);
        pointer-events: none;
    }
    
    /* Ajuste para o conteúdo principal */
    div[data-testid="stAppViewContainer"] > div {
        position: relative;
        z-index: 1;
    }
    
    /* Ajuste para o container de login */
    div[data-testid="stAppViewContainer"] .login-container {
        background-color: #ffffff;
        position: relative;
        z-index: 2;
    }
    /* Garantir que o controle de expandir/recolher da sidebar esteja visível */
    section[data-testid="stSidebar"] [data-testid="collapsedControl"],
    div[data-testid="stSidebar"] [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] {
        display: flex !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        visibility: visible !important;
        z-index: 9999 !important;
    }
    section[data-testid="stSidebar"],
    div[data-testid="stSidebar"] {
        overflow: visible !important;
        z-index: 999 !important;
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
        st.session_state['current_page'] = 'Formulário'
        st.success("✅ Acesso autorizado!")
        st.balloons()  # Efeito visual de sucesso
        return True
    else:
        st.error(f"❌ Falha na autenticação: {result.get('error', 'Credenciais inválidas')}")
        return False

# Barra lateral para navegação
with st.sidebar:
    st.markdown("<h1>🔬 Lodos Ativados</h1>", unsafe_allow_html=True)
    st.divider()
    
    # Exibir menu de navegação com base no estado de login
    if st.session_state['logged_in']:
        # Mostrar informações do usuário
        st.success("✅ Autenticado")
        
        # Menu de navegação para usuário autenticado
        st.markdown("<p style='font-weight:bold;'>Navegação</p>", unsafe_allow_html=True)
        menu_options = ["Formulário", "Gráficos"]
        selected_menu = st.radio("", menu_options, label_visibility="collapsed")
        
        # Atualizar página atual com base na seleção
        if st.session_state['current_page'] != selected_menu:
            st.session_state['current_page'] = selected_menu
            # Forçar recarregamento para atualizar o layout
            st.rerun()
        
                
        if st.button("Sair", key="logout_btn", help="Clique para sair", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['current_page'] = 'Login'
            # Forçar recarregamento para atualizar o layout
            st.rerun()
    else:
        # Menu simplificado para usuário não autenticado
        st.info("🔒 Área restrita")
        
        # Adicionar opção de Gráficos (acessível sem autenticação)
        menu_options = ["Login", "Gráficos"]
        selected_menu = st.radio("Navegação", menu_options)
        
        # Atualizar página atual com base na seleção
        if st.session_state['current_page'] != selected_menu:
            st.session_state['current_page'] = selected_menu
            # Forçar recarregamento para atualizar o layout
            st.rerun()
    
    # Rodapé da barra lateral
    st.divider()
    st.caption("© 2025 Ebenézer Carvalho")

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
                    # Recarregar para atualizar o layout e a interface
                    st.rerun()

elif st.session_state['current_page'] == 'Gráficos':
    # Página de Gráficos (acessível sem autenticação)
    # Chamar a função do módulo de gráficos para exibir o conteúdo
    graficos.show_graficos()

# A seção 'Dados' foi removida pois os dados já são exibidos na página de gráficos

elif st.session_state['current_page'] == 'Formulário':
    # Verificar se o usuário está autenticado
    if not st.session_state['logged_in']:
        st.warning("Você precisa fazer login para acessar esta página.")
        st.session_state['current_page'] = 'Login'
        # Recarregar para garantir que o layout seja atualizado para 'centered'
        st.rerun()
    
    # Exibir o formulário de inserção de dados
    formulario.show_formulario()