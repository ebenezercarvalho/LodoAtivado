# Sistema de Monitoramento de Lodos Ativados

Sistema web para monitoramento e análise de dados de microbiologia de lodos ativados, desenvolvido com Streamlit e Supabase.

## Funcionalidades

- Autenticação de usuários
- Registro de dados de microbiologia
- Visualização de gráficos
- Análise temporal dos dados
- Exportação de dados

## Requisitos

- Python 3.8 ou superior
- Conta no Supabase
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/lodos-ativados.git
cd lodos-ativados
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
   - Crie um arquivo `.streamlit/secrets.toml` na raiz do projeto
   - Adicione suas credenciais do Supabase:
```toml
[connections.supabase]
SUPABASE_URL = "sua-url-do-supabase"
SUPABASE_KEY = "sua-chave-do-supabase"
```

## Executando o Projeto

Para iniciar o servidor local:
```bash
streamlit run app.py
```

O aplicativo estará disponível em `http://localhost:8501`

## Estrutura do Projeto

```
lodos-ativados/
├── app.py              # Aplicação principal
├── formulario.py       # Módulo de formulários
├── graficos.py         # Módulo de visualização
├── requirements.txt    # Dependências
├── .gitignore         # Arquivos ignorados pelo Git
└── README.md          # Este arquivo
```

## Deploy

O projeto pode ser facilmente implantado em plataformas como:
- Streamlit Cloud
- Heroku
- AWS
- Google Cloud Platform

Para deploy, certifique-se de configurar as variáveis de ambiente necessárias na plataforma escolhida.

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. 