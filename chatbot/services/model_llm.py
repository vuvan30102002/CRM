from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
pdf_path = BASE_DIR / "knowledge" / "knowledge_1.pdf"

loader = PyPDFLoader(str(pdf_path))
pages = loader.load()

clean_pages = []

for doc in pages:
    text = doc.page_content

    # Convert PHẦN -> H1
    text = re.sub(
        r"PHẦN\s+[IVX]+\.\s+(.+)",
        r"# \1",
        text
    )

    # Convert number heading -> H2
    text = re.sub(
        r"^(\d+)\.\s+(.+)$",
        r"## \2",
        text,
        flags=re.MULTILINE
    )

    # Kịch bản -> H2
    text = re.sub(
        r"(Kịch bản số \d+:.*)",
        r"## \1",
        text
    )

    # FAQ -> H2
    text = re.sub(
        r"(Câu hỏi \d+)",
        r"## \1",
        text
    )

    doc.page_content = text
    clean_pages.append(doc)

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "section"),
        ("##", "subsection"),
    ]
)

docs = []
for doc in clean_pages:
    chunks = splitter.split_text(doc.page_content)

    # giữ metadata từ PDF page nếu cần
    for c in chunks:
        c.metadata.update(doc.metadata)
        docs.append(c)

# vector_db = FAISS.from_documents(docs,embedding)

# vector_db.save_local("faiss_crm_index")
# print("save successfully")


embedding = None
vector_db = None

def load_db():
    global embedding, vector_db
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings

    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    vector_db = FAISS.load_local(
        "./chatbot/services/faiss_crm_index",
        embedding,
        allow_dangerous_deserialization=True
    )
    
# query = "CRM Pro có hỗ trợ điện thoại không?"

# results = vector_db.similarity_search(query, k=3)

# for i, doc in enumerate(results):
#     print("\n--- RESULT", i, "---")
#     print("METADATA:", doc.metadata)
#     print("CONTENT:", doc.page_content)

def search(query):
    results = vector_db.similarity_search(query, k=3)
    return results