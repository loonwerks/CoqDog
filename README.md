# CoqDog Copilot: a user-friendly AI- assistant for coq proof assistant - with a case study on Copland attestation protocols

we introduce CoqDog Copilot, which leverages the neuro-symbolic interplay between generative AI and the Coq theorem 
prover to form a productive "generate-and-test" loop, incrementally improving proofs based on failure information and 
human hints until valid proofs are achieved. 

Our Contributions for AISOLA2024:

1. Our research addresses critical challenges in developing a generative AI
   assistant for proof synthesis and repair:

– Introducing CoqDog Copilot, a web application for proof synthesis and
repair using the Coq theorem prover.

– Proposing an innovative approach to address the copilot’s context limitations; Figure 3 (AISOLA2024 paper).

– Developing a sound recommendation system supported by a ranking
mechanism to prevent logically unsound recommendations.

– Establishing effective metrics for measuring proof repair progress.

– Designing a statistically robust evaluation system for assessing conversational quality; Figure 5 (AISOLA2024 paper).

2. We present a comprehensive evaluation of CoqDog Copilot’s performance in
proof repair across multiple samples, as seen in Figure 4 (AISOLA2024). from the Copland
Coq proofbase, which consists of a total of 21,000 lines of Coq code.

## Installation

Follow these steps to set up the project:

### Prerequisites

Make sure you have the following installed:

- Python 3.9.7 for ubuntu 20.04 and 3.8 for ubuntu 18.04
- `pip` (Python package installer)

### Installation Steps

1. **Clone the Repository**:
   
   Clone the project from GitHub to your local machine.

  ```bash
   git clone https://github.com/loonwerks/CoqDog.git
   cd CoqDog
   
2. **Set Up a Virtual Environment**
  ```bash 
   python3.9 -m venv venv
   source venv/bin/activate
   
3. **Install Dependencies**
   ```bash
   pip3.9 install -r requirements.txt

4. **Set Up Environment Variables** 
   Open your `.env` file 
   ```bash
   gedit .env
   
   add the following line and save file after that. 
    
   OPENAI_API_KEY="your-openai-api-key"
    
   be sure to replace `your-openai-api-key` with your actual key.
      
   
5. **Run CoqDog Team Application**
   ```bash
     python3.9 CoqDog_Team.py
      
     
