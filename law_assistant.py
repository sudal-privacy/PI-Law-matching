import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def run_law_assistant(query):
    # 1. 문서 로드 (docs 폴더 내의 모든 PDF)
    loader = DirectoryLoader('./docs', glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    
    if not documents:
        return "학습된 결정문 데이터가 없습니다. docs 폴더에 PDF를 넣어주세요."

    # 2. 지식 베이스 생성 (Vector DB)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # 3. 답변을 위한 프롬프트 설정 (전문가 페르소나 부여)
    template = """당신은 개인정보보호위원회 결정문 전문 분석가입니다. 
    제공된 [결정문 자료]만을 바탕으로 사용자의 질문에 답하세요. 
    답변 시 해당 결정문의 '사건 번호'나 '피심인' 명칭을 반드시 언급하고 법적 근거를 명확히 하세요.
    모르는 내용은 지어내지 말고 자료에 없다고 답변하세요.

    [결정문 자료]
    {context}

    질문: {question}
    답변:"""
    
    QA_PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

    # 4. AI 모델 및 검색 체인 설정
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}), # 가장 관련있는 3개 문서 참조
        chain_type_kwargs={"prompt": QA_PROMPT}
    )
    
    # 5. 답변 실행
    response = qa_chain.invoke(query)
    return response["result"]

if __name__ == "__main__":
    # 테스트 질문 예시
    test_query = "영동군청의 개인정보 보호법 위반 행위와 이에 대한 시정 권고 내용은 무엇인가요?"
    print(f"\nQ: {test_query}")
    print(f"A: {run_law_assistant(test_query)}")
