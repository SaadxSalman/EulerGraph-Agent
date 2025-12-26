# OncoSense-A.I. 🧑‍⚕️🔬

An advanced, multi-modal diagnostic assistant that provides comprehensive cancer diagnoses. OncoSense-A.I. analyzes a combination of pathology slides, genomic data, and patient medical history to generate an integrated, accurate, and rapid diagnostic report. This system is a significant evolution of the previous OncoScope project.

## ✨ Features

  * **Multi-Modal Analysis:** Integrates and analyzes three distinct data types: high-resolution pathology images, genomic sequences, and patient medical history text.
  * **Intelligent Agentic Architecture:** Employs a team of specialized AI agents, including a **Triage Agent** for data organization, a **Pathology Agent** for slide analysis, a **Genomic Agent** for DNA sequence analysis, and a **Reporting Agent** for synthesizing findings.
  * **Vision-Powered Pathology:** Utilizes a state-of-the-art **vision transformer** to meticulously analyze and identify anomalies in high-resolution pathology images.
  * **Genomic Marker Discovery:** Develops specialized **genomic embeddings** to identify and interpret genetic markers linked to various cancer subtypes.
  * **Seamless Data Integration:** Leverages **GATv2** to analyze complex genomic networks and **BiomedCLIP** for accurate medical image-text alignment, ensuring cohesive and contextually-aware analysis.

## ⚙️ Tech Stack

* **Frontend:** [Next.js 14+](https://nextjs.org/) (App Router) with [TypeScript](https://www.typescriptlang.org/) for type-safe UI components.
* **Styling:** [Tailwind CSS](https://tailwindcss.com/) & [Shadcn/UI](https://ui.shadcn.com/) for a clean, clinical dashboard aesthetic.
* **State Management & Data Fetching:** [TanStack Query v5](https://tanstack.com/query/latest) for caching diagnostic results and [tRPC](https://trpc.io/) for end-to-end typesafe API calls.
* **API Orchestration:** [Node.js](https://nodejs.org/) with [Express.js](https://expressjs.com/) to manage user sessions and clinical records.
* **Primary Database:** [MongoDB](https://www.mongodb.com/) (MERN stack core) for storing structured patient metadata and report history.

---

### 🧠 Multi-Modal AI Engine (Python 3.10+)

The heart of the system is built on **FastAPI**, chosen for its high-concurrency capabilities and native support for asynchronous tasks.

#### **1. Pathology & Vision Analysis**

* **Architecture:** [Vision Transformer (ViT)](https://huggingface.co/docs/transformers/model_doc/vit) for global context analysis of high-resolution biopsy slides.
* **Alignment:** [BiomedCLIP](https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224) for zero-shot medical image-text retrieval and cross-modal alignment.
* **Framework:** [PyTorch](https://pytorch.org/) & [Hugging Face Transformers](https://huggingface.co/docs/transformers/index).

#### **2. Genomic Deep Learning**

* **Graph Analysis:** [GATv2 (Graph Attention Networks v2)](https://www.google.com/search?q=https://docs.dgl.ai/en/0.8.x/generated/dgl.nn.pytorch.conv.GATv2Conv.html) implemented via **DGL (Deep Graph Library)** to model complex gene-interaction networks.
* **Vector Search:** [Milvus](https://milvus.io/) (Standalone) for high-performance similarity searching of genomic embeddings.
* **Embeddings:** [Sentence-Transformers](https://www.sbert.net/) for converting raw DNA sequences and medical notes into dense vectors.

#### **3. Agentic Orchestration**

* **Logic:** Custom Python classes utilizing **Asynchronous Task Queues** to allow specialized agents (Triage, Path, Gen, Report) to work in parallel.
* **Synthesis:** [OpenAI GPT-4o](https://openai.com/index/hello-gpt-4o/) or local [Llama 3 (via Ollama)](https://ollama.com/) for medical narrative generation.

---

### 🛠️ DevOps & Infrastructure

* **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) for managing the 5+ microservices.
* **Vector Storage:** [MinIO](https://min.io/) (as a back-end storage for Milvus metadata).
* **Reporting:** [FPDF2](https://pyfpdf.github.io/fpdf2/) for programmatic generation of PDF clinical reports.
* **Version Control:** Git (Hosted on GitHub under `saadsalmanakram/OncoSense-A.I.`).

### 📊 Tech Stack Summary Table

| Layer | Technology | Key Usage |
| --- | --- | --- |
| **UI/UX** | Next.js, Tailwind, Lucide Icons | Diagnostic dashboard & Slide viewer |
| **Communication** | tRPC, Axios, WebSockets | Real-time agent status updates |
| **Vision AI** | ViT, BiomedCLIP, OpenCV | Anomaly detection in pathology slides |
| **Genomic AI** | GATv2, DGL, PyTorch | Gene interaction & mutation analysis |
| **Vector DB** | Milvus | Searching genomic "fingerprints" |
| **Orchestration** | FastAPI, Node.js | Multi-agent coordination |
| **Storage** | MongoDB, MinIO | Patient data & Vector metadata |

## 🚀 Getting Started

### Prerequisites

  * Node.js (for Next.js)
  * Python 3.10+
  * Docker (for Milvus)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/saadsalmanakram/OncoSense-A.I.git
    cd OncoSense-A.I.
    ```
2.  **Set up the front-end:**
    ```bash
    cd frontend
    npm install
    ```
3.  **Set up the backend services:**
    Follow the instructions in the `backend/` directory to set up the Python environment and Milvus.

### Configuration

Create a `.env` file in the `frontend` directory for any necessary API keys or environment variables.

### Usage

1.  **Start the front-end server:**
    ```bash
    npm run dev
    ```
2.  **Start the backend services:**
    Run the necessary Python scripts and services to handle data processing and agentic operations.

---

