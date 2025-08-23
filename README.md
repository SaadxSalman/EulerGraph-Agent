# OncoSense-A.I. 🧑‍⚕️🔬

An advanced, multi-modal diagnostic assistant that provides comprehensive cancer diagnoses. OncoSense-A.I. analyzes a combination of pathology slides, genomic data, and patient medical history to generate an integrated, accurate, and rapid diagnostic report. This system is a significant evolution of the previous OncoScope project.

## ✨ Features

  * **Multi-Modal Analysis:** Integrates and analyzes three distinct data types: high-resolution pathology images, genomic sequences, and patient medical history text.
  * **Intelligent Agentic Architecture:** Employs a team of specialized AI agents, including a **Triage Agent** for data organization, a **Pathology Agent** for slide analysis, a **Genomic Agent** for DNA sequence analysis, and a **Reporting Agent** for synthesizing findings.
  * **Vision-Powered Pathology:** Utilizes a state-of-the-art **vision transformer** to meticulously analyze and identify anomalies in high-resolution pathology images.
  * **Genomic Marker Discovery:** Develops specialized **genomic embeddings** to identify and interpret genetic markers linked to various cancer subtypes.
  * **Seamless Data Integration:** Leverages **GATv2** to analyze complex genomic networks and **BiomedCLIP** for accurate medical image-text alignment, ensuring cohesive and contextually-aware analysis.

## ⚙️ Tech Stack

  * **Front-end:** [Next.js](https://nextjs.org/) and [TanStack Query](https://tanstack.com/query/latest)
  * **Agent Orchestration:** Custom-built multi-agent system
  * **Vision Analysis:** Vision Transformer on tRPC
  * **Genomic Analysis:** [GATv2](https://www.google.com/search?q=https://github.com/tech-srl/GATv2-pytorch)
  * **Vector Search:** [Milvus](https://milvus.io/)
  * **Image-Text Alignment:** [BiomedCLIP](https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224)
  * **Genomic Embeddings:** [Sentence-Transformers](https://www.sbert.net/)

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

## 🤝 Contributing

Contributions are welcome\! If you're interested in improving OncoSense-A.I., please refer to our [CONTRIBUTING.md](https://www.google.com/search?q=https://github.com/saadsalmanakram/OncoSense-A.I./blob/main/CONTRIBUTING.md) for guidelines on submitting pull requests.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://www.google.com/search?q=https://github.com/saadsalmanakram/OncoSense-A.I./blob/main/LICENSE) file for more details.
