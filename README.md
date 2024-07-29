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
