# OmniBrain

## Overview
OmniBrain is an Agentic Multi-Modal Retrieval Augmented Generation (RAG) system designed to analyze complex documents containing text, tables, and images.

The system aims to provide accurate, context-aware responses by combining document retrieval, AI agents, and multimodal understanding.

## Problem Statement
Traditional RAG systems mainly focus on text retrieval and struggle with:
- Financial tables
- Charts and images
- Multi-step reasoning across different data sources

## Tech Stack

- Python
- LangGraph
- LangChain
- Qdrant / FAISS
- FastAPI
- Streamlit
- LLMs & Vision Language Models

## Dataset

Initial dataset:
- Microsoft Annual Reports (Financial Documents)

## Supported Functions

OmniBrain provides the following capabilities:

- User authentication with JWT-protected API routes
- Register new user accounts
- Login and receive access tokens
- Retrieve authenticated user profile
- Upload documents for ingestion
- Ingest supported file types:
  - PDF documents
  - Word documents (.doc/.docx)
  - Plain text (.txt)
  - Images (.png, .jpg, .jpeg)
  - Tabular files (.csv, .xlsx, .xls)
- Create and manage persistent user conversations
- Persist chat history in PostgreSQL across logins
- Perform natural-language queries over multimodal content
- Route queries to search, vision, or SQL agents
- Use LangGraph orchestration for multi-step reasoning
- Apply server-side input/output guardrails for safety
- Prevent destructive SQL operations in SQL agent queries
- Frontend Streamlit interface for dashboard, chat, upload, and auth

## API Endpoints

### Authentication

- `POST /auth/register`: register a new user with username, email, and password
- `POST /auth/login`: authenticate and receive a JWT access token
- `GET /auth/me`: return the current authenticated user profile

### Conversations

- `GET /conversations/`: list conversations for the current user
- `POST /conversations/`: create a new conversation
- `GET /conversations/{conversation_id}`: retrieve a conversation and its messages
- `POST /conversations/{conversation_id}/messages`: append a message to an existing conversation
- `POST /conversations/ensure`: create or return an existing conversation for a user

### Query and Retrieval

- `POST /query`: send a natural-language query through the RAG graph, persist chat history, and receive assistant answer, sources, documents, image paths, and conversation ID
- `POST /upload`: upload a document for ingestion into the backend

## How Conversation Works

The conversation system is user-scoped and persisted in PostgreSQL.

1. A user registers or logs in through `/auth/register` or `/auth/login`.
   - The API returns a JWT token.
   - The frontend stores this token and sends it in the `Authorization: Bearer ...` header for protected requests.

2. When the user opens chat or sends a message, the frontend either:
   - creates a new conversation via `/conversations/ensure`, or
   - reuses an existing conversation id.

3. The backend uses `create_or_get_for_user()` from `backend/chat/service.py` to:
   - fetch the user's current conversation by `conversation_id`,
   - or create a new `Conversation` row tied to the authenticated `user_id`.

4. When a query is sent to `/query`:
   - the backend loads the current user from JWT,
   - writes the user message into `messages` via `add_message(...)`,
   - builds the LangGraph input state,
   - invokes the agent workflow (`router -> search/vision/sql -> synthesis -> guardrails`),
   - and then stores the assistant response back into the same conversation.

5. Each conversation stores:
   - `id`
   - `user_id`
   - `title`
   - `created_at`
   - `updated_at`
   - message rows (`role`, `content`, `created_at`)

6. Conversation history can be fetched with:
   - `GET /conversations/` to list all chats for the logged-in user
   - `GET /conversations/{conversation_id}` to retrieve the full conversation
   - `GET /conversations/{conversation_id}/messages` to list message history

This means each user sees only their own chat history, while the system can continue a thread across multiple queries without losing context.

## Frontend Features

- Login and registration pages
- Dashboard for uploading and monitoring ingested content
- Chat page with saved conversations and history
- Upload page for document ingestion
- Client-side token storage and authenticated API interaction

## Running the Project

1. Install dependencies:
   - `python -m pip install -r requirements.txt`
2. Start the backend:
   - `uvicorn app:app --reload`
3. Start the frontend:
   - `cd frontend/streamlit`
   - `streamlit run app.py`
4. Use the Streamlit UI to register, login, upload documents, and ask questions.

## Notes

- PostgreSQL is required for auth and persistent conversation storage.
- JWT tokens are required for protected routes and are passed in the Authorization header.
- Guardrails validate unsafe inputs and outputs on the server.
- The system currently supports multimodal ingestion, semantic search, SQL queries, and image reasoning.
