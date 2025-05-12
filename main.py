import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
import pymsql
import uuid
import json
from dotenv import load_dotenv
load_dotenv()

blobConnectionString = os.getenv('BLOB_CONNECTION_STRING')
blobContainerName = os.getenv('BLOB_CONTAINER_NAME')
blobAccountName = os.getenv('BLOB_ACCOUNT_NAME')

SQL_SERVER = os.getenv('SQL_SERVER')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')

st.title('Cadastro de Produtos')

product_name = st.text_input('Nome do Produto')
product_price = st.number_input('Preço do Produto', min_value=0.0, format='%.2f')
product_description = st.text_area('Descrição do Produto')
product_image = st.file_uploader('Imagem do Produto', type=['jpg', 'png', 'jpeg'])

#Save image on blob storage
def upload_blob(file):
    blob_service_client = BlobServiceClient.from_connection_string(blobConnectionString)
    container_client = blob_service_client.get_container_client(blobContainerName)
    blob_name = str(uuid.uuid4()) + file.name
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.read(), overwrite=True)
    image_url = f"https://{blobaccountName}.blob.core.windows.net/{blobContainerName}/{blob_name}"
    return image_url

def insert_product_sql(product_data):
    try:
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO dbo.Produtos (nome, descricao, preco, imagem_url)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (product_data["nome"], product_data["descricao"], product_data["preco"], product_data["imagem_url"]))
        conn.commit()

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir no Azure SQL: {e}")
        return False


def list_products_sql():
    try:
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor(as_dict=True)
        query = "SELECT id, nome, descricao, preco, imagem_url FROM dbo.Produtos"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return []

def list_produtos_screen():
        products = list_products_sql()
        if products:
        # Define o número de cards por linha
            cards_por_linha = 3
            # Cria as colunas iniciais
            cols = st.columns(cards_por_linha)
            for i, product in enumerate(products):
                col = cols[i % cards_por_linha]
                with col:
                    st.markdown(f"### {product['nome']}")
                    st.write(f"**Descrição:** {product['descricao']}")
                    st.write(f"**Preço:** R$ {product['preco']:.2f}")
                    if product["imagem_url"]:
                        html_img = f'<img src="{product["imagem_url"]}" width="200" height="200" alt="Imagem do produto">'
                        st.markdown(html_img, unsafe_allow_html=True)
                    st.markdown("---")
                # A cada 'cards_por_linha' produtos, se ainda houver produtos, cria novas colunas
                if (i + 1) % cards_por_linha == 0 and (i + 1) < len(products):
                    cols = st.columns(cards_por_linha)
        else:
            st.info("Nenhum produto encontrado.")


if st.button("Cadastrar Produto"):
    if not product_name or not description or price is None:
        st.warning("Preencha todos os campos obrigatórios!")
    else:
        # Envia a imagem (se houver) para o Azure Storage
        image_url = ""
        if uploaded_file is not None:
            image_url = upload_image(uploaded_file)
        
        # Dados do produto
        product_data = {
            "nome": product_name,
            "descricao": description,
            "preco": price,
            "imagem_url": image_url
        }

        if insert_product_sql(product_data):
            st.success("Produto cadastrado com sucesso no Azure SQL!")
            list_produtos_screen()
        else:
            st.error("Houve um problema ao cadastrar o produto no Azure SQL.")

st.header("Listagem dos Produtos")

if st.button("Listar Produtos"):
    list_produtos_screen()