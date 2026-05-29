import os
import re
from collections import Counter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
        max_retries=5,
    )

def format_docs(docs):
    return "\n\n".join(docs)


def split_transcript(transcript: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    chunks = []
    start = 0
    while start < len(transcript):
        end = min(start + chunk_size, len(transcript))
        chunks.append(transcript[start:end])
        if end == len(transcript):
            break
        start = max(0, end - overlap)
    return chunks or [transcript]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def build_lightweight_retriever(transcript: str, k: int = 4):
    chunks = split_transcript(transcript)
    chunk_terms = [Counter(tokenize(chunk)) for chunk in chunks]

    def retrieve(question: str):
        query_terms = Counter(tokenize(question))
        if not query_terms:
            return chunks[:k]

        scored = []
        for index, terms in enumerate(chunk_terms):
            score = sum(min(count, terms.get(term, 0)) for term, count in query_terms.items())
            scored.append((score, index))

        scored.sort(key=lambda item: item[0], reverse=True)
        selected = [chunks[index] for score, index in scored[:k] if score > 0]
        return selected or chunks[:k]

    return retrieve

def build_rag_chain(transcript:str):

    retriever = build_lightweight_retriever(transcript, k=4)
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(

        [(
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ]
    )

    #full LCEL Rag pipeline 

    rag_chain = (

        {"context" : RunnableLambda(retriever) | RunnableLambda(format_docs),
         "question": RunnablePassthrough()
         }
         |prompt|llm|StrOutputParser()
    )

    return rag_chain


def load_rag_chain():
    raise RuntimeError("Persistent vector store loading is not used by the fast in-memory RAG engine.")

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context":  retriver| RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question:str) -> str:
    print(f"Question : {question}")
    answer = rag_chain.invoke(question)
    print(f"answer :{answer}")
    return answer
