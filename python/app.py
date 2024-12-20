import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
import os
import shutil
import re

# Variável global para armazenar o diretório da pasta renomeados
pasta_renomeados = "renomeados"

# Função para selecionar o diretório principal


def selecionar_diretorio():
    pasta_selecionada = filedialog.askdirectory(
        title="Selecione o diretório contendo os PDFs")
    if pasta_selecionada:
        diretorio_label.config(text=pasta_selecionada)

# Função para limpar caracteres especiais do RA


def limpar_ra(ra):
    return re.sub(r"[^\w]", "", ra)

# Função para processar os PDFs no diretório selecionado


def processar_diretorio():
    global pasta_renomeados
    pasta_origem = diretorio_label.cget("text")

    if not pasta_origem:
        messagebox.showwarning(
            "Aviso", "Por favor, selecione um diretório contendo os PDFs.")
        return

    if not pasta_renomeados:
        messagebox.showwarning(
            "Aviso", "Por favor, selecione o diretório de saída.")
        return

    contagem_manual = 1

    # Renomeia a pasta de saída com base na pasta de origem
    nome_pasta_origem = os.path.basename(pasta_origem)
    pasta_destino_raiz = os.path.join(
        pasta_renomeados, f"{nome_pasta_origem}_renomeados")

    if not os.path.exists(pasta_destino_raiz):
        os.makedirs(pasta_destino_raiz)

    try:
        for root, _, files in os.walk(pasta_origem):
            for file in files:
                if file.endswith(".pdf"):
                    caminho_pdf = os.path.join(root, file)

                    with open(caminho_pdf, "rb") as arquivo:
                        leitor = PyPDF2.PdfReader(arquivo)

                        # Itera sobre todas as páginas do PDF
                        ra_encontrado = False
                        for pagina in leitor.pages:
                            texto = pagina.extract_text()

                            # Procura por informações após "RA:" no texto extraído
                            linhas = texto.splitlines()
                            for linha in linhas:
                                if "RA:" in linha:
                                    try:
                                        # Extrai o texto após "RA:"
                                        ra = linha.split("RA:")[1].strip()
                                        ra_limpo = limpar_ra(ra)

                                        # Verifica se o RA é válido
                                        if not ra_limpo:
                                            ra_limpo = f"termo_manual_{
                                                contagem_manual}"
                                            contagem_manual += 1

                                        # Define o caminho do novo arquivo com a estrutura preservada
                                        rel_path = os.path.relpath(
                                            root, pasta_origem)
                                        pasta_destino = os.path.join(
                                            pasta_destino_raiz, rel_path)

                                        if not os.path.exists(pasta_destino):
                                            os.makedirs(pasta_destino)

                                        novo_nome = os.path.join(
                                            pasta_destino, f"{ra_limpo}.pdf")
                                        shutil.copy(caminho_pdf, novo_nome)
                                        ra_encontrado = True
                                        break
                                    except IndexError:
                                        continue
                            if ra_encontrado:
                                break

        # Abre a pasta de destino automaticamente após o processamento
        abrir_pasta(pasta_destino_raiz)
        messagebox.showinfo(
            "Concluído", "Os arquivos foram renomeados com sucesso!")

    except Exception as e:
        messagebox.showerror(
            "Erro", f"Ocorreu um erro ao processar os arquivos PDF:\n{e}")

# Função para abrir a pasta renomeados automaticamente


def abrir_pasta(caminho):
    try:
        if os.name == 'nt':  # Windows
            os.startfile(caminho)
        elif os.name == 'posix':  # macOS ou Linux
            os.system(f'open "{caminho}"' if os.uname(
            ).sysname == 'Darwin' else f'xdg-open "{caminho}"')
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir a pasta:\n{e}")


# Criação da janela principal
janela = tk.Tk()
janela.title("Processador de PDFs e Renomeação de RAs")
janela.geometry("400x150")

# Layout da interface
tk.Label(janela, text="Selecione o diretório contendo os PDFs:").pack(pady=5)

# Label para exibir o diretório selecionado
diretorio_label = tk.Label(janela, text="", bg="white",
                           width=50, height=1, anchor="w", relief="sunken")
diretorio_label.pack(pady=5)

# Botão para selecionar o diretório
tk.Button(janela, text="Selecionar Diretório",
          command=selecionar_diretorio).pack(pady=5)

# Botão para processar os PDFs
tk.Button(janela, text="Processar PDFs",
          command=processar_diretorio).pack(pady=5)

# Executa a interface
janela.mainloop()
