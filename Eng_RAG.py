# Engineering_Insight_Generator.py  ― 5 May 2025
# Completely replaces Credit_Card_Optimizer.py

# 1. ── install / import
!p ip install openai azure-cosmos langchain pymongo beautifulsoup4 requests tiktoken streamlit streamlit_jupyter nest_asyncio

import os, uuid, hashlib
import streamlit as st
from streamlit_jupyter import StreamlitPatcher, tqdm
import nest_asyncio
import openai, tiktoken
from pymongo import MongoClient
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch

nest_asyncio.apply()
StreamlitPatcher().jupyter()

# 2. ── keys & DB endpoints  (👉 EDIT THESE!)
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
cosmos_mongo_uri       = "your-cosmos-mongo-uri"
cosmos_db              = "EngKnowledgeDB"
cosmos_container       = "EngDocs"

# 3. ── helper utilities
def estimate_tokens(text, model="gpt-4o"):
    return len(tiktoken.encoding_for_model(model).encode(text))

def sha_cache(s: str) -> str:
    return hashlib.sha256(s.encode("utf‑8")).hexdigest()

def quick_subject(question: str, model="gpt-3.5-turbo-0125") -> str:
    msgs = [{"role":"system","content":"Summarize this engineering request in ≤5 words."},
            {"role":"user","content":question}]
    return openai.ChatCompletion.create(model=model,messages=msgs,
                                        temperature=0,max_tokens=20).choices[0].message.content.strip()

def peer_review(question:str, answer:str, model="gpt-3.5-turbo-0125") -> str:
    msgs=[{"role":"system","content":
           "You are a senior peer reviewer. Does this engineering answer fully address the question? "
           "Check clarity, traceability to data, mention of relevant standards, and give bullet feedback."},
          {"role":"user","content":f"Question:\n{question}\n\nAnswer:\n{answer}"}]
    return openai.ChatCompletion.create(model=model,messages=msgs,
                                        temperature=0.2,max_tokens=400).choices[0].message.content

# 4. ── core generator ---------------------------------------------------------
client         = MongoClient(cosmos_mongo_uri)
collection     = client[cosmos_db][cosmos_container]
embedding_model= OpenAIEmbeddings()
vector_store   = MongoDBAtlasVectorSearch(collection=collection,
                                          embedding=embedding_model)

cache_store = {}

def generate_engineering_insight(question:str, k:int=4, force_gpt35:bool=False)->dict:
    ck=sha_cache(question)
    if ck in cache_store:  # serve from cache
        st.success("🔂 Cached result delivered")
        return cache_store[ck]

    subject = quick_subject(question)
    st.write(f"**Detected subject:** *{subject}*")

    docs    = vector_store.similarity_search(question, k=k)
    context = "\n\n".join([d.page_content[:800] for d in docs])

    model   = "gpt-3.5-turbo-0125" if force_gpt35 else "gpt-4o"
    role_prompt = (
        f"You are a lead systems engineer specialising in {subject}. "
        "Using ONLY the dataset context provided, craft a detailed, step‑by‑step technical response.  "
        "Reference MIL‑STD‑882 and other standards where appropriate.  "
        "Present the answer in structured **Markdown** with clear section headings, numbered lists, "
        "and a concise conclusion.  Cite the provided context snippets inline in (Ctx‑#) form."
    )

    messages=[{"role":"system","content":role_prompt},
              {"role":"user","content":f"Context snippets:\n{context}\n\n---\n\nQuestion:\n{question}"}]

    cost_tokens=sum(estimate_tokens(m["content"],model) for m in messages)
    st.write(f"ℹ️  Prompt tokens: {cost_tokens}")

    answer=openai.ChatCompletion.create(model=model,messages=messages,
                                        temperature=0.25,max_tokens=1100).choices[0].message.content

    review=peer_review(question,answer)
    cache_store[ck]={"answer":answer,"review":review}
    return cache_store[ck]

# 5. ── Streamlit UI -----------------------------------------------------------
st.title("🛠️  Engineering Insight Generator")
st.markdown("Ask a systems‑engineering question and receive a dataset‑grounded, standard‑referenced answer.")

question = st.text_area("Engineering question", height=120,
                        placeholder="e.g. What hazard controls are recommended for lithium battery integration in UUVs?")
use_gpt35= st.checkbox("Economy mode (GPT‑3.5)")

if st.button("Generate answer") and question.strip():
    result = generate_engineering_insight(question, force_gpt35=use_gpt35)
    st.subheader("🔎 Detailed Engineering Answer")
    st.markdown(result["answer"])
    st.subheader("📝 Automated Peer Review")
    st.write(result["review"])