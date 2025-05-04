import streamlit as st
import pandas as pd
import datetime
import supabase

# Função para inicializar conexão com Supabase
def init_connection():
    # Obter as credenciais do secrets.toml
    supabase_url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    supabase_key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    
    # Criar cliente do Supabase
    client = supabase.create_client(supabase_url, supabase_key)
    return client

# Função para inserir dados na tabela microbiologia
def insert_microbiologia_data(client, data):
    try:
        response = client.table('microbiologia').insert(data).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Função principal para exibir o formulário de inserção
def show_formulario():
    # Sem estilos personalizados para o formulário

    
    st.title("Formulário de Registro de Microbiologia")
    st.write("Preencha os campos abaixo para adicionar um novo registro à tabela de microbiologia.")
    
    # Criar formulário usando st.form para capturar todos os campos de uma vez
    with st.form(key="microbiologia_form"):
        # Campos de data e hora
        col1, col2 = st.columns(2)
        with col1:
            data_amostra = st.date_input("Data da Amostra", value=datetime.date.today())
        
        # Campos com opções predefinidas (dropdown)
        ponto_amostra = st.selectbox(
            "Ponto de Amostra",
            options=[
                "Ipiranga - Reator 1",
                "Ipiranga - Reator 2",
                "Nissan - Tanque de aeração 1",
                "Nissan - Tanque de aeração 2"
            ]
        )
        
        aparencia_amostra = st.selectbox(
            "Aparência da Amostra",
            options=[
                "Boa sedimentação",
                "Boa clarificação",
                "Amostra turva",
                "Amostra escura",
                "Baixa quantidade de sólidos",
                "Flotação do lodo no frasco"
            ]
        )
        
        aspecto_floco = st.selectbox(
            "Aspecto do Floco",
            options=[
                "Minúsculo - pinfloc",
                "Pequeno - mal formado",
                "Médio",
                "Grande - com presença de ciliados e filamentos"
            ]
        )
        
        # Campos numéricos para contagens
        st.subheader("Contagens Microbiológicas")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            ciliados_livres = st.number_input("Ciliados Livres", min_value=0, step=1)
            ciliados_fixos = st.number_input("Ciliados Fixos", min_value=0, step=1)
            colonias_fixos = st.number_input("Colônias Fixos", min_value=0, step=1)
        
        with col2:
            amebas_teca = st.number_input("Amebas Teca", min_value=0, step=1)
            amebas_nuas = st.number_input("Amebas Nuas", min_value=0, step=1)
            flagelados = st.number_input("Flagelados", min_value=0, step=1)
        
        with col3:
            rotiferos = st.number_input("Rotíferos", min_value=0, step=1)
            tardigrados = st.number_input("Tardígrados", min_value=0, step=1)
            nemato = st.number_input("Nemato", min_value=0, step=1)
        
        # Campo para filamentosa identificada
        filamentos = st.selectbox(
            "Filamentosa identificada",
            options=[
                "Microthrix parvicella",
                "Nocardioformes",
                "Thiothrix",
                "não identificada"
            ]
        )
        
        # Campos para diversidade
        st.subheader("Diversidade")
        col1, col2 = st.columns(2)
        with col1:
            divers_ciliados_livres = st.number_input("Diversidade de Ciliados Livres", min_value=0, step=1)
            divers_flagel = st.number_input("Diversidade de Flagelados", min_value=0, step=1)
        
        with col2:
            divers_rot = st.number_input("Diversidade de Rotíferos", min_value=0, step=1)
            divers_nemat = st.number_input("Diversidade de Nemato", min_value=0, step=1)
        
        # Campo para quantidade de filamentos
        ident_filament = st.selectbox(
            "Quantidade de Filamentos",
            options=[
                "Vários por floco",
                "Ao menos um por floco",
                "Raros",
                "Ausentes"
            ]
        )
        
        # Botão de envio
        submit_button = st.form_submit_button("Salvar Registro")
    
    # Processar o envio do formulário
    if submit_button:
        # Criar dicionário com os dados do formulário
        data = {
            "dataamostra": data_amostra.isoformat(),  # Converter data para string ISO
            "pontoamostra": ponto_amostra,
            "aparenciaamostra": aparencia_amostra,
            "aspectofloco": aspecto_floco,
            "ciliadoslivres": ciliados_livres,
            "ciliadosfixos": ciliados_fixos,
            "coloniasfixos": colonias_fixos,  # Corrigido: removido acento
            "amebasteca": amebas_teca,
            "amebasnuas": amebas_nuas,  # Corrigido: singular em vez de plural
            "flagelados": flagelados,
            "rotiferos": rotiferos,  # Corrigido: removido acento
            "tardigrados": tardigrados,
            "nemato": nemato,
            "filamentos": filamentos,
            "diversciliadoslivres": divers_ciliados_livres,
            "diversflagel": divers_flagel,
            "diversrot": divers_rot,
            "diversnemat": divers_nemat,
            "identfilament": ident_filament
        }
        
        # Exibir spinner durante o envio
        with st.spinner("Enviando dados para o banco de dados..."):
            # Inicializar conexão Supabase
            supabase_client = init_connection()
            
            # Inserir dados na tabela
            result = insert_microbiologia_data(supabase_client, data)
            
            if result["success"]:
                st.success("✅ Registro adicionado com sucesso!")
                st.balloons()  # Efeito visual de sucesso
            else:
                st.error(f"❌ Erro ao adicionar registro: {result.get('error')}")
                st.info("Verifique se todos os campos foram preenchidos corretamente.")