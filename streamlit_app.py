# =============================================================================
# Atividade Prática - Aula 1 | Aplicações em Data Science (UNICAMP)
# Cadastro de Pacientes - VERSÃO STREAMLIT (local + Streamlit Community Cloud)
# Base: esqueleto do enunciado (PDF, seção 4.2), com ajustes indicados como
# "SUGESTÃO TÉCNICA" nos comentários.
# Executar:  streamlit run app.py   (no terminal - não funciona com F5 no IDLE)
# =============================================================================

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Configurações
# -----------------------------------------------------------------------------
# SUGESTÃO TÉCNICA: o CSV fica na mesma pasta deste app.py.
PASTA_APP = Path(__file__).resolve().parent
ARQUIVO_CSV = PASTA_APP / "pacientes.csv"

COLUNAS = ["timestamp", "nome", "idade", "convenio", "prioridade", "motivo"]
CONVENIOS = ["Particular", "Unimed", "Bradesco Saúde", "SulAmérica", "Outro"]
CODIFICACAO = "utf-8-sig"   # acentos corretos no Excel


# -----------------------------------------------------------------------------
# 2. Gravação no CSV - mesma lógica da versão Gradio (decisão da Etapa 2)
# -----------------------------------------------------------------------------
def gravar_linha(linha):
    """Acrescenta uma linha ao CSV; cria o arquivo com cabeçalho se não existir."""
    novo = pd.DataFrame([linha], columns=COLUNAS)
    if os.path.exists(ARQUIVO_CSV):
        novo.to_csv(ARQUIVO_CSV, mode="a", header=False, index=False,
                    encoding=CODIFICACAO)
    else:
        novo.to_csv(ARQUIVO_CSV, mode="w", header=True, index=False,
                    encoding=CODIFICACAO)


# -----------------------------------------------------------------------------
# 3. Página e memória da sessão (st.session_state)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Cadastro de Pacientes", page_icon="🏥",
                   layout="centered")
st.title("🏥 Cadastro de Pacientes")
st.caption("Recepção do consultório")

# O Streamlit reexecuta este script a cada interação. O session_state é a
# "memória" que sobrevive a essas reexecuções enquanto a aba estiver aberta.
if "pacientes" not in st.session_state:
    st.session_state.pacientes = pd.DataFrame(columns=COLUNAS)

# SUGESTÃO TÉCNICA: espaço reservado ACIMA do formulário para as mensagens,
# para que fiquem visíveis no celular sem precisar rolar a tela.
aviso = st.empty()


# -----------------------------------------------------------------------------
# 4. Formulário (st.form) - coluna única, adequada para celular
# -----------------------------------------------------------------------------
# Dentro de um st.form, digitar nos campos NÃO reexecuta o script;
# tudo é enviado de uma vez ao clicar em "Cadastrar".
with st.form("cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do paciente")
    # SUGESTÃO TÉCNICA: value=None deixa o campo vazio, obrigando a digitar.
    idade = st.number_input("Idade", min_value=0, max_value=120, step=1,
                            value=None, placeholder="Digite a idade")
    # SUGESTÃO TÉCNICA: index=None obriga a escolher um convênio.
    convenio = st.selectbox("Convênio", CONVENIOS, index=None,
                            placeholder="Selecione o convênio")
    prioridade = st.slider("Prioridade do atendimento", 1, 5, value=1,
                           help="1 = baixa · 5 = urgente")
    motivo = st.text_area("Motivo da consulta / observações")
    enviado = st.form_submit_button("Cadastrar", type="primary",
                                    width="stretch")


# -----------------------------------------------------------------------------
# 5. Tratamento do envio
# -----------------------------------------------------------------------------
if enviado:
    nome = nome.strip()
    # SUGESTÃO TÉCNICA: validação mínima (mesma da versão Gradio).
    if not nome:
        aviso.warning("⚠️ Informe o nome do paciente.")
    elif idade is None:
        aviso.warning("⚠️ Informe a idade.")
    elif not convenio:
        aviso.warning("⚠️ Selecione o convênio.")
    else:
        nova_linha = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome": nome,
            "idade": int(idade),
            "convenio": convenio,
            "prioridade": int(prioridade),
            "motivo": motivo.strip(),
        }
        # (a) grava no arquivo pacientes.csv
        gravar_linha(nova_linha)
        # (b) acumula na memória da sessão
        nova_df = pd.DataFrame([nova_linha], columns=COLUNAS)
        if st.session_state.pacientes.empty:
            st.session_state.pacientes = nova_df
        else:
            st.session_state.pacientes = pd.concat(
                [st.session_state.pacientes, nova_df], ignore_index=True)
        aviso.success(f"✅ Paciente {nome} cadastrado com sucesso em "
                   f"{nova_linha['timestamp']}.")


# -----------------------------------------------------------------------------
# 6. Tabela dos últimos cadastros e download do CSV
# -----------------------------------------------------------------------------
st.subheader("Últimos pacientes cadastrados (nesta sessão)")
st.dataframe(st.session_state.pacientes.tail(5), hide_index=True,
             width="stretch")

# O disco do Streamlit Community Cloud é efêmero: o download garante
# que a recepção possa exportar os dados cadastrados na sessão.
csv = st.session_state.pacientes.to_csv(index=False).encode(CODIFICACAO)
st.download_button("Baixar CSV", csv, "pacientes.csv", "text/csv",
                   width="stretch",
                   disabled=st.session_state.pacientes.empty)
