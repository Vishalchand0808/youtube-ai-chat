from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import os

from fastapi.middleware.cors import CORSMiddleware

# Imports for AI Memeory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load the secret keys from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

app = FastAPI()

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins (good for local testing)
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],
)
# ------------------

# THIS IS OUR RAM DATABASE! 
# When the server sleeps, this dictionary is wiped clean.
memory_db = {} 

# We define the shape of the data we expect from the frontend
class VideoRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    video_id: str
    question: str

def get_video_id(url):
    """A helper function to slice the YouTube URL and grab the ID."""
    if "v=" in url:
        # Handles standard youtube.com/watch?v=ID&...
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        # Handles youtu.be/ID?si=...
        # Split by '/', get the last part, then split by '?' to remove tracking junk
        return url.split("/")[-1].split("?")[0]
    return None

@app.get("/")
def home():
    return {"message": "API is running and ready to process videos."}

@app.post("/process")
def process_video(request: VideoRequest):
    try:
        video_id = get_video_id(request.url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        # 1. Fetch the Transcript
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id)
        full_text = " ".join([item.text for item in transcript_list])

        # 2. Chop the text into small chunks
        # chunk_overlap ensures sentences aren't awkwardly cut in half
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.create_documents([full_text])

        # 3. Convert text to Vectors using Google's free embedding model
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )

        # 4. Store the vectors in our RAM database (FAISS)
        # We save it under the 'video_id' so we can find it later!
        vector_store = FAISS.from_documents(docs, embeddings)
        memory_db[video_id] = vector_store

        return {
            "status": "success", 
            "message": f"Video {video_id} processed and stored in RAM!",
            "chunks_created": len(docs),
            "video_id": video_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat_with_video(request: ChatRequest):
    try:
        # 1. Check if the video memory exists
        if request.video_id not in memory_db:
            raise HTTPException(
                status_code=404, 
                detail="Memory not found. Please process the video again."
            )

        # 2. Retrieve the specific vector database
        vector_store = memory_db[request.video_id]
        retriever = vector_store.as_retriever()

        # 3. Initialize the AI Model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=api_key
        )

        # 4. Create the Prompt Template
        template = """Answer the question based ONLY on the following context:
        {context}

        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)

        # Helper function to format the chunks of text
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # 5. Build the Modern LCEL Chain using the pipe | operator
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # 6. Ask the question!
        response = rag_chain.invoke(request.question)

        return {"answer": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))