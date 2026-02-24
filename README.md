# YouTube AI Chat Assistant

A full-stack application designed to help users quickly understand YouTube videos and clear up their doubts. By extracting the video transcript and utilizing a local Retrieval-Augmented Generation (RAG) pipeline, this tool allows users to ask specific questions and receive answers based strictly on the video's actual content.

## Core Features

* **Automated Transcript Extraction:** Fetches and parses video captions directly from YouTube URLs, turning long videos into searchable text.
* **Context-Specific Q&A:** Enforces strict guardrails on the AI. The system answers user questions using only facts present in the specific video transcript, preventing hallucinations.
* **In-Memory Processing:** Utilizes FAISS to perform similarity searches entirely in the local server's RAM, keeping the application lightweight and fast without needing an external database.
* **Full-Stack Architecture:** A decoupled system featuring a clean React frontend and a Python FastAPI backend.

---

## Architecture & Tech Stack

This project is built with a decoupled architecture, isolating the user interface from the heavy natural language processing tasks.

| Category | Technology |
| --- | --- |
| **Frontend** |  |
| **Backend** |  |
| **AI / ML** |  |

---

## AI / ML Core

The application's intelligence is powered by a custom RAG pipeline to ensure accurate answers to user doubts.

### 1. Ingestion & Vectorization

* **Text Splitting:** Transcripts are processed into overlapping logical chunks to preserve context across sentences.
* **Embedding Model:** Google's `gemini-embedding-001` model translates text chunks into high-dimensional vector embeddings.
* **Storage:** Vectors are indexed using Facebook AI Similarity Search (FAISS). This index is stored ephemerally in RAM and scoped to individual video session IDs.

### 2. Retrieval & Generation

* **LLM Engine:** Powered by Google's `gemini-2.5-flash` model for high-speed inference.
* **Pipeline Integration:** Utilizes LangChain Expression Language (LCEL) and custom prompt templates to guarantee the AI only answers based on the retrieved transcript chunks.

---

## Running the Project Locally

Follow these instructions to configure and run the project environments on your local machine.

### Prerequisites

* Python 3.10+ and Conda
* Node.js and npm
* A Google AI Studio API Key

### 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/youtube-ai-chat.git
cd youtube-ai-chat

```

### 2. Backend Setup

1. **Navigate to the backend directory:**
```bash
cd backend

```


2. **Create and activate the conda environment:**
```bash
conda create -n youtube-chat python=3.10
conda activate youtube-chat

```


3. **Install Python dependencies:**
```bash
pip install -r requirements.txt

```


4. **Configure Environment Variables:**
Create a `.env` file inside the `backend` folder and add your Gemini API key:
```env
GEMINI_API_KEY="YOUR_GOOGLE_API_KEY"

```


5. **Start the server:**
```bash
uvicorn main:app --reload

```


The backend API will be accessible at `http://localhost:8000`.

### 3. Frontend Setup

1. **Open a secondary terminal window.**
2. **Navigate to the frontend directory:**
```bash
cd frontend

```


3. **Install Node.js dependencies:**
```bash
npm install

```


4. **Start the development server:**
```bash
npm run dev

```


The frontend interface will be available at `http://localhost:5173`.

---

## Challenges & Learnings

* **State Synchronization:** Handled the asynchronous flow of data between the React frontend and the FastAPI backend, ensuring the chat UI successfully mounts only after the backend has processed the video and generated the required vector indices.
* **Contextual Guardrails:** Designed system prompts to force the language model to rely exclusively on the retrieved FAISS vectors. This ensures that when a user asks a specific doubt, the AI does not hallucinate answers from outside knowledge, but strictly references the lecture or video material.
* **CORS Configuration:** Successfully configured Cross-Origin Resource Sharing (CORS) middleware to allow seamless local communication between the Vite development server and the Uvicorn backend.
