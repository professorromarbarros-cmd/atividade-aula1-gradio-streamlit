# =============================================================================
# Atividade Prática - Aula 1 | Aplicações em Data Science (UNICAMP)
# Cadastro de Pacientes - VERSÃO GRADIO (execução local)
# Base: esqueleto do enunciado (PDF, seção 3.2), com ajustes indicados como
# "SUGESTÃO TÉCNICA" nos comentários.
# =============================================================================

import os
from datetime import datetime
from pathlib import Path

import gradio as gr
import pandas as pd

# -----------------------------------------------------------------------------
# 1. Configurações
# -----------------------------------------------------------------------------
# SUGESTÃO TÉCNICA: o CSV fica na mesma pasta deste app.py, não importa de
# onde o programa seja executado (terminal ou F5 no IDLE).
PASTA_APP = Path(__file__).resolve().parent
ARQUIVO_CSV = PASTA_APP / "pacientes.csv"

COLUNAS = ["timestamp", "nome", "idade", "convenio", "prioridade", "motivo"]
CONVENIOS = ["Particular", "Unimed", "Bradesco Saúde", "SulAmérica", "Outro"]

# SUGESTÃO TÉCNICA: "utf-8-sig" faz o Excel exibir os acentos corretamente.
CODIFICACAO = "utf-8-sig"


# -----------------------------------------------------------------------------
# 2. Funções de dados (leitura e gravação do CSV)
# -----------------------------------------------------------------------------
def ler_ultimos(qtd=5):
    """Retorna os últimos `qtd` cadastros (ou uma tabela vazia)."""
    if ARQUIVO_CSV.exists():
        return pd.read_csv(ARQUIVO_CSV, encoding=CODIFICACAO).tail(qtd)
    return pd.DataFrame(columns=COLUNAS)


def gravar_linha(linha):
    """Acrescenta uma linha ao CSV; cria o arquivo com cabeçalho se não existir."""
    novo = pd.DataFrame([linha], columns=COLUNAS)
    if os.path.exists(ARQUIVO_CSV):
        # Arquivo já existe: acrescenta ("a" = append), sem repetir o cabeçalho
        novo.to_csv(ARQUIVO_CSV, mode="a", header=False, index=False,
                    encoding=CODIFICACAO)
    else:
        # Primeira execução: cria o arquivo ("w" = write) com cabeçalho
        novo.to_csv(ARQUIVO_CSV, mode="w", header=True, index=False,
                    encoding=CODIFICACAO)


# -----------------------------------------------------------------------------
# 3. Função chamada pelo botão "Cadastrar"
# -----------------------------------------------------------------------------
def cadastrar_paciente(nome, idade, convenio, prioridade, motivo):
    nome = (nome or "").strip()
    motivo = (motivo or "").strip()

    # SUGESTÃO TÉCNICA: validação mínima para não gravar linhas incompletas.
    # gr.update() = "não altere este campo" (mantém o que o usuário digitou).
    manter = [gr.update()] * 5
    if not nome:
        return ["⚠️ Informe o nome do paciente.", ler_ultimos()] + manter
    if idade is None:
        return ["⚠️ Informe a idade.", ler_ultimos()] + manter
    if not convenio:
        return ["⚠️ Selecione o convênio.", ler_ultimos()] + manter

    linha = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nome": nome,
        "idade": int(idade),
        "convenio": convenio,
        "prioridade": int(prioridade),
        "motivo": motivo,
    }
    gravar_linha(linha)

    mensagem = f"✅ Paciente {nome} cadastrado com sucesso em {linha['timestamp']}."
    # SUGESTÃO TÉCNICA: limpa o formulário para o próximo paciente
    # (mesmo comportamento do clear_on_submit=True da versão Streamlit).
    limpar = ["", None, None, 1, ""]
    return [mensagem, ler_ultimos()] + limpar


# -----------------------------------------------------------------------------
# 4. Interface (gr.Blocks) - coluna única, adequada para celular
# -----------------------------------------------------------------------------
with gr.Blocks(title="Cadastro de Pacientes") as demo:
    gr.Markdown("## 🏥 Cadastro de Pacientes\nRecepção do consultório")

    nome = gr.Textbox(label="Nome do paciente")
    idade = gr.Number(label="Idade", precision=0, minimum=0, maximum=120)
    convenio = gr.Dropdown(CONVENIOS, label="Convênio")
    prioridade = gr.Slider(1, 5, value=1, step=1,
                           label="Prioridade do atendimento",
                           info="1 = baixa · 5 = urgente")
    motivo = gr.Textbox(label="Motivo da consulta / observações", lines=3)

    botao = gr.Button("Cadastrar", variant="primary")

    saida_msg = gr.Textbox(label="Status", interactive=False)
    tabela = gr.Dataframe(label="Últimos pacientes cadastrados",
                          headers=COLUNAS, interactive=False, wrap=True)

    # Evento: clique no botão -> função -> atualiza saídas (e limpa o formulário)
    botao.click(
        cadastrar_paciente,
        inputs=[nome, idade, convenio, prioridade, motivo],
        outputs=[saida_msg, tabela, nome, idade, convenio, prioridade, motivo],
    )

    # SUGESTÃO TÉCNICA: ao abrir a página, já mostra os cadastros existentes.
    demo.load(ler_ultimos, inputs=None, outputs=tabela)


# -----------------------------------------------------------------------------
# 5. Inicialização
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    demo.launch()
