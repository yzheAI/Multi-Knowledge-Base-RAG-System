## v1_basic.md
```mermaid
graph TD
A[user] --> B[Chunk + Embedding]
B --> C[FAISS]
C --> D[Search]
D --> E[LLM]
E --> F[Answer]

