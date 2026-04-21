import streamlit as st
from fpdf import FPDF
import urllib.parse

# --- configuração da página ---
st.set_page_config(page_title="Vidro Van - Orçamentos", layout="centered")

# --- memória ---
if 'meus_servicos' not in st.session_state:
    st.session_state.meus_servicos = []

# --- funções de lógica ---
def adicionar_e_limpar():
    """Adiciona o serviço à lista e limpa os campos de entrada"""
    nome_item = st.session_state.nome_servico_input
    preco_item = st.session_state.preco_servico_input
    
    if nome_item:
        st.session_state.meus_servicos.append({
            "nome": nome_item, 
            "preco": preco_item
        })
        st.session_state.nome_servico_input = ""
        st.session_state.preco_servico_input = 0.0
    else:
        st.toast("⚠️ Escreva a descrição do serviço que sera feito!")


def gerar_pdf(nome_cliente, modelo_van, ano_van, lista_servicos, total):
    pdf = FPDF()
    pdf.add_page()
    
    
    try:
        largura_logo = 60 
        posicao_x = (210 - largura_logo) / 2 
        
        pdf.image("logo.png", x=posicao_x, y=10, w=largura_logo)
        
        pdf.ln(45) 
    except:
        pdf.ln(10)
    
    # Título
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(200, 20, "VIDRO VAN - RJ", ln=True, align='C')
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(200, 10, "Orçamento de Transformação", ln=True, align='C')
    pdf.ln(10)
    
    # Dados do Cliente
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(200, 10, f"Cliente: {nome_cliente}", ln=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(200, 10, f"Veículo: {modelo_van} ({ano_van})", ln=True)
    pdf.ln(5)
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(140, 10, " Descrição do Serviço", border=1, fill=True)
    pdf.cell(50, 10, " Preço (R$)", border=1, ln=True, align='C', fill=True)
    
    # Itens da Tabela
    pdf.set_font("helvetica", "", 12)
    for s in lista_servicos:
        pdf.cell(140, 10, f" {s['nome']}", border=1)
        pdf.cell(50, 10, f"R$ {s['preco']:,.2f}", border=1, ln=True, align='R')
    
    # Total
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(140, 10, "TOTAL GERAL:", align='R')
    pdf.cell(50, 10, f"R$ {total:,.2f}", ln=True, align='R')
    
    # Rodapé 
    pdf.set_y(-30)
    pdf.set_font("helvetica", "I", 8)
    pdf.cell(0, 10, "Este orçamento tem validade de 15 dias.", align='C')
    
    return bytes(pdf.output())

# --- interface ---

col1, col2, col3 = st.columns([1, 2, 1]) 

with col2:
    try:
        
        st.image("logo.png", width=300, use_container_width=False) 
    except:
        st.warning("⚠️ Logo não encontrada")

st.markdown("<h1 style='text-align: center;'>Vidro Van - Gerenciador</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Sistema de Orçamentos Profissionais</p>", unsafe_allow_html=True)

# dados do cliente
with st.container(border=True):
    col_cli, col_tel = st.columns(2) 
    nome = col_cli.text_input("Nome do Cliente", placeholder="Paulo vinicius")
    telefone = col_tel.text_input("WhatsApp do Cliente", placeholder="21999999999")
    col_van, col_ano = st.columns([3, 1])
    modelo = col_van.text_input("Modelo da Van", placeholder="Sprinter 415")
    ano = col_ano.number_input("Ano", 1990, 2027, 2024)

st.divider()

# adicionar os serviços 
st.subheader("🛠️ Adicionar Serviços")
c1, c2 = st.columns([3, 1])

with c1:
    st.text_input("Descrição do Serviço", 
                 placeholder="Ex: Instalar 4 bancos reclináveis", 
                 key="nome_servico_input")

with c2:
    st.number_input("Preço unitário (R$)", 
                   min_value=0.0, 
                   step=50.0, 
                   key="preco_servico_input")

# Botão que usa o CALLBACK para limpar os campos
st.button("➕ Incluir no Orçamento", on_click=adicionar_e_limpar, use_container_width=True)

st.divider()

# Seção do Resumo
st.subheader("📋 Resumo do Orçamento")

if not st.session_state.meus_servicos:
    st.info("Nenhum serviço adicionado ainda.")
    valor_total = 0.0
else:
    valor_total = 0.0
    for i, item in enumerate(st.session_state.meus_servicos):
        col_txt, col_btn = st.columns([0.8, 0.2])
        col_txt.write(f"**{item['nome']}** - R$ {item['preco']:,.2f}")
        
        # Botão para remover um item específico
        if col_btn.button("Remover", key=f"del_{i}", type="secondary"):
            st.session_state.meus_servicos.pop(i)
            st.rerun()
            
        valor_total += item['preco']

    st.write(f"### **Total: R$ {valor_total:,.2f}**")

    col_pdf, col_clear = st.columns(2)
    
    with col_pdf:
        # Geração do PDF
        pdf_data = gerar_pdf(nome, modelo, ano, st.session_state.meus_servicos, valor_total)
        st.download_button(
            label="📄 Baixar Orçamento em PDF",
            data=pdf_data,
            file_name=f"Orcamento_{nome.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col_clear:
        if st.button("🗑️ Limpar Tudo", use_container_width=True):
            st.session_state.meus_servicos = []
            st.rerun()

#-- Logica do whatsapp pra mandar pro cliente --            
if st.session_state.meus_servicos:
    telefone_limpo = "".join(filter(str.isdigit, telefone))
    if len(telefone_limpo) == 11:
        telefone_limpo ="55" + telefone_limpo

    texto_zap = f"Olá *{nome}*! \n\n" 
    texto_zap += f"Segue o Orçamento para a sua *{modelo}* ({ano}):\n\n"

    for s in st.session_state.meus_servicos:
        texto_zap += f"{s['nome']}: R$ {s['preco']:,.2f}\n"

    texto_zap +=f"\n*Total Geral: R$ {valor_total:,.2f}*\n\n"
    texto_zap += "Enviaremos o orçamento en PDF abaixo. Qualquer dúvida, estamos à disposição!"  

    texto_url = urllib.parse.quote(texto_zap.encode('utf-8'))
    link_whatsapp = f"https://wa.me/{telefone_limpo}?text={texto_url}"

    #botão do zap pro streamlit
    st.markdown(f"""
        <a href="{link_whatsapp}" target="_blank">
            <button style="
                width: 100%;
                background-color: #25D366;
                color: white;
                border: none;
                padding: 10px 20px;
                order-radius: 5px;
                cursor: pointer;
                font-weigth: bold;
                font-size: 16px;
                margin-top: 10px;">
                📱 enviar Orçamento via Whatsapp
                </button>
               </a>
             """, unsafe_allow_html=True)   



