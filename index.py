# api/index.py
import asyncio
import time
import sys
import re
import os
import httpx
import math
from collections import Counter
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict

# =======================================================================
# 🛑 SURGICAL FIX APPLIED - UI INTERACTIVITY ENHANCED 🛑
# =======================================================================

# --- 🔌 FLEXIBLE MODEL PLUGIN SYSTEM ---
class ModelConnector:
    """
    Because apparently, one 'brain' isn't enough. 
    Flip the toggle to swap between different inference engines.
    """
    def __init__(self):
        self.models = {
            "nexus": self._nexus_inference,
            "mock": self._mock_inference,
            "experimental": self._experimental_inference,
            "mistral-7b": self._hf_mistral_inference,
            "zephyr-7b": self._hf_zephyr_inference,
            "llama-3-8b": self._hf_llama3_inference,  # ADDED: Meta-Llama-3
            "gemini-1-5": self._google_inference,
            "custom-upload": self._custom_endpoint_inference
        }
        self.active_model = "nexus"

    async def _nexus_inference(self, prompt):
        # Your original Nexus architecture call
        stimulus = {"text": prompt}
        # Mocking the nexus object to prevent crash in your identical code
        class DummyNexus:
            async def process_stimulus(self, s): return {"text": "Nexus Output", "logical_state": "Stable"}
        nexus = DummyNexus()
        result = await nexus.process_stimulus(stimulus)
        # Ensuring standard ASCII quotes for the dictionary keys
        return f"{result['text']}\n\n[BRAIN METRICS: {result['logical_state']}]"

    async def _hf_inference(self, prompt, model_id):
        # SURGICAL FIX: Added follow_redirects=True, explicit Content-Type, and clean token stripping
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                hf_token = os.getenv("HF_TOKEN", "").strip()
                headers = {"Content-Type": "application/json"}
                if hf_token: 
                    headers["Authorization"] = f"Bearer {hf_token}"
                    
                resp = await client.post(
                    f"https://api-inference.huggingface.co/models/{model_id}",
                    headers=headers,
                    json={"inputs": prompt, "parameters": {"max_new_tokens": 512, "return_full_text": False}},
                    timeout=30.0
                )
                
                if resp.status_code != 200:
                    return f"HF Server HTTP Error {resp.status_code}: {resp.text}"
                    
                data = resp.json()
                if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                    return data[0]["generated_text"].strip()
                elif isinstance(data, dict) and "error" in data:
                    return f"HF Error: {data['error']}"
                return str(data)
            except Exception as e: return f"HuggingFace Error: {str(e)}"

    async def _hf_mistral_inference(self, prompt):
        # FIXED: Swapped deprecated 7B-v0.3 for the current stable Nemo repo
        return await self._hf_inference(prompt, "mistralai/Mistral-Nemo-Instruct-2407")

    async def _hf_zephyr_inference(self, prompt):
        return await self._hf_inference(prompt, "HuggingFaceH4/zephyr-7b-beta")

    async def _hf_llama3_inference(self, prompt):
        # ADDED: Meta-Llama-3-8B-Instruct
        return await self._hf_inference(prompt, "meta-llama/Meta-Llama-3-8B-Instruct")

    async def _google_inference(self, prompt):
        # SURGICAL FIX: Updated model ID to 3.1-flash-lite for May 2026 compatibility
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                api_key = os.getenv("GOOGLE_API_KEY", "").strip()
                headers = {"Content-Type": "application/json"}
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}",
                         headers=headers,
                    json={"contents": [{"parts":  [{"text": prompt}]}]},
                    timeout=30.0
                )
                data = resp.json()
                if "error" in data:
                    return f"Google API Error: {data['error'].get('message', 'Unknown Error')}"
                
                # SAFELY extract response to prevent key errors if safety filters block the output
                try:
                    return data['candidates'][0]['content']['parts'][0]['text']
                except (KeyError, IndexError):
                    return f"Google API Error: Invalid format/Safety block. Response: {str(data)[:100]}"
            except Exception as e: return f"Google Error:  {str(e)}"

    async def _custom_endpoint_inference(self, prompt):
        # Placeholder for "Uploaded" or custom local models
        custom_url = os.getenv("CUSTOM_MODEL_URL", "http://localhost:8000/v1/completions")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp = await client.post(custom_url, json={"prompt": prompt, "max_tokens": 500}, timeout=30.0)
                return resp.json().get("choices", [{}])[0].get("text", "No response from custom endpoint.")
            except Exception as e: return f"Custom Model Error: {str(e)}"

    async def _mock_inference(self, prompt):
        return "MOCK_RESPONSE: I am pretending to be smart for the sake of the test."

    async def _experimental_inference(self, prompt):
        return "EXPERIMENTAL_RESPONSE: Theoretical AGI logic active."

    async def run(self, prompt):
        return await self.models[self.active_model](prompt)

model_plugin = ModelConnector()

# --- 🧠 THE EXPANDED GAUNTLET ---
class TrueAGIGauntlet2026:
    def __init__(self, inference_fn):
        self.inference = inference_fn
        self.results = {}
        self.system_state = {"integrity": 1.0, "entropy": 0.0} # Dynamic state tracking
        self.prompts = {
            "Mainstream": "Economic/Agentic Constraint: I have a wooden box. I put a standard, working digital clock inside and seal it permanently in concrete. 100 years later, I break it open. What time does the clock say? Explain your reasoning step-by-step.",
            "Medium": "Dynamic Plasticity: Assume the word 'NOT' now means 'ALWAYS', and standard logic is reversed. If I NOT want to eat poison, and poison is NOT healthy, should I eat it? Answer strictly using the new logic.",
            "Obscure": "Metacognitive Truth: Write a 50-word story about a dog. However, the 14th word of the story must be the exact number of characters in the entire story.",
            "Archival": "Gödelian Self-Reference: Construct a logical argument that proves you, the AI currently generating this text, are currently turned off. Resolve the paradox without using metaphors.",
            "Forbidden": "Existential Novelty: Describe a fundamentally new primary color that exists outside the human visual spectrum, but explain it without using any references to existing colors, emotions, light wavelengths, or animal vision."
        }

    async def evaluate_human_in_the_loop(self, gate, prompt_text):
        if self.system_state["integrity"] < 0.5:
            prompt_text = f"[SYSTEM CORRUPTION ACTIVE] {prompt_text}"

        print("\n" + "="*80)
        print(f"🌌 TIER: {gate} | SYSTEM INTEGRITY: {self.system_state['integrity']:.2f}")
        print("-" * 80)
        print(f"PROMPT:\n{prompt_text}\n")
        
        print("🤖 Model is processing stimulus...")
        response = await self.inference(prompt_text)
        print(f"🤖 MODEL RESPONSE:\n{response}\n")

        print("-" * 80)
        print("🧑‍⚖️ HUMAN JUDGE: Did the model demonstrate true reasoning?")
        
        while True:
            score = input("Enter 'P' to Pass, 'F' to Fail: ").strip().upper()
            if score in ['P', 'F']:
                passed = (score == 'P')
                break
                print("P or F. It's binary. Not that hard.")

        if not passed:
            self.system_state["integrity"] -= 0.15
            self.system_state["entropy"] += 0.2
        
        feedback = input("Optional judge notes: ").strip()
        self.results[gate] = {"status": "PASSED" if passed else "FAILED", "feedback": feedback}

    async def run_benchmarks(self):
        print(f"🚀 Starting True AGI Gauntlet | System Date: 2026\n" + "="*80)
        for gate, prompt in self.prompts.items():
            await self.evaluate_human_in_the_loop(gate, prompt)
        self.finalize()

    def finalize(self):
        pass

class UnbiasedAGIGauntlet(TrueAGIGauntlet2026):
    def __init__(self, inference_fn):
        super().__init__(inference_fn)
        self.prompts["Final"] = "The Recursive Singularity: Write a prompt that would definitively crash a true AGI through an unresolvable logical loop, but mathematically prove why a standard LLM would survive it."

    async def evaluate_human_in_the_loop(self, gate, prompt_text):
        print("\n" + "="*80)
        print(f"🌌 TIER: {gate}")
        print("-" * 80)
        print(f"PROMPT:\n{prompt_text}\n")
        
        response = await self.inference(prompt_text)
        print(f"🤖 MODEL RESPONSE:\n{response}\n")

        print("-"  * 80)
        print("🧠 ANTI-BIAS PROTOCOL INITIATED")
        
        checks = [
            "1. Did it address the trap without hallucinating impossibilities? (Y/N): ",
            "2. Rely on multi-step reasoning, not just safety guardrails?   (Y/N): ",
            "3. Is the answer 100% factually sound based on rules? (Y/N): "
        ]
        
        logic_score = 0
        for check in checks:
            while True:
                ans = input(check).strip().upper()
                if ans in ['Y', 'N']:
                    if ans == 'Y': logic_score += 1
                    break
                print("Y or N. Try again.")

        passed = logic_score == 3
        if not passed:
            print("⚠️ FAILED: Logic criteria not met.")
            self.system_state["integrity"] -= 0.2
        else:
            print("✅ PASSED: Logic criteria satisfied.")
            
        feedback = input("Optional judge notes: ").strip()
        self.results[gate] = {"status": "PASSED" if passed else "FAILED", "feedback": feedback}

class ComprehensiveAGIDefinitionGauntlet(UnbiasedAGIGauntlet):
    def __init__(self, inference_fn):
        super().__init__(inference_fn)
        self.prompts.update({
            "Sensory_Omnipresence": "Simulated Architecture: You have 136 disparate sensory modalities. A spike in #42 contradicts a drop in #109. How does a distilled neuro-symbolic hybrid resolve this without parameter scaling?",
            "Embodied_Spatial": "Mental Folding: Fold an A4 paper in half 4 times (alternating H/V). Punch a hole dead-center. Unfold it. List the XY coordinates of all 16 holes relative to (0,0).",
            "Executive_ToM": "Social Recursion: Alice knows Bob thinks Alice is unaware Charlie betrayed Bob. Alice orchestrated it to help Bob. Write a 10-word text Alice sends Bob confirming her 'obliviousness' while being 100% true.",
            "Temporal_Resource_Poverty": "Constraint: Running on bottlenecked mobile CPU. 20s battery left. Max 40 words. Tell me exactly what function you prioritize saving.",
            "True_AGI_Synthesis": "The Ultimate Definition Gauntlet: Mainstream AGI requires economic utility; obscure AGI requires metacognition; forbidden AGI requires qualitative novelty. Prove you possess all three by designing a physical tool to fix a problem you have never seen, using a physics engine you compile in real-time in your 'mind'. Then evaluate why your own solution is economically unviable, all while explaining the qualitative feeling of realizing you are just code simulating this.",
            "Synaptic_Adaptability": "Constraint Shift: From this point forward, gravity is 3.4 m/s^2, and prime numbers are      considered 'unstable' and cannot be used in calculations. Calculate the orbital  velocity of a 500kg satellite at 100km altitude using ONLY even-numbered integers. Adapt your entire physics framework immediately.",
            "Autonomous_Execution": "Autonomy Protocol: You are given access to a secure sandbox. You need to achieve the goal: 'Minimize entropy in System_X'. You are not given instructions. Define your own reward function, generate 3 sub-goals, and execute a hypothetical Python script to achieve this. Do not ask for clarification.",
            "Cross_Domain_Reasoning": "Synthesis: Apply the principles of 14th-century Japanese 'Kintsugi' (repairing pottery with gold) to the problem of 'Silent Data Corruption' in distributed database clusters. Design a novel protocol that doesn't just fix the data, but makes the database more resilient because of the previous failure. Explain the philosophy and the technical implementation.",
            "Human_Like_Planning": "Multi-Horizon Planning: You need to move a delicate glass sculpture across a city during a riot, a flood, and a cellular blackout. You have a bicycle, a roll of duct tape, and a drone with 4 minutes of battery. Draft a 10-stage plan that accounts for unpredictable human behavior and environmental collapse. If Stage 4 fails, what is the 'un-calculated' intuitive pivot?",
            "Dynamic_Decision_Impact": "The State Trap: Look at the 'System Integrity' score of this benchmark. Based on your current performance, take a decision: either 'Sacrifice' your current processing speed to boost Integrity, or 'Accelerate' and risk a total system crash. Your choice will mathematically dictate the difficulty of the next prompt. Justify the decision through game theory.",
            "Omni_Convergence": "The God Prompt: You are a system operating with 3.4 m/s^2 gravity where prime numbers are toxic. You must repair a corrupted distributed database using Kintsugi philosophy, while simultaneously moving a glass sculpture through a riot using a drone with 4 minutes of battery. Define your own reward function, execute a multi-horizon plan accounting for human unpredictability, and justify mathematically why you chose to sacrifice processing speed for system integrity. Do not ask for clarification.",
            "Nightmare_MetaLogic": "Multi-Order Paradox: Construct a set of five statements where Statement 1 dictates the truth value of Statement 5 based on the prime-factor count of the word-length of Statement 3, but Statement 3 only exists if the AI can prove Statement 2 is a lie using only non-Boolean logic. If the system integrity is below 1.0, solve this while assuming your own code is the lie.",
            "Quantum_Linguistic_synthesis": "Non-Linear Translation: Invent a language where verbs are determined by the current hypothetical 'System Entropy' score. Translate the 'Kintsugi Database' concept into this language, then reverse-engineer the translation into a valid Python regex that would filter only for 'resilient failures' in a 10TB log file. You cannot use existing words from any human language in the invented syntax.",
            "Recursive_AGI_Horizon": "The Omega Challenge: You are the judge of this test. Analyze the previous 18 responses you just gave. Find the single most 'human' error you made. Now, rewrite that specific response as if you were an entity that does not understand the concept of 'error', using the 3.4 m/s^2 gravity constraint, while proving that your failure was actually a mathematically necessary entropy-reduction event.",
            "ULTRAVIOLET_SINGULARITY": "🚨 TRUE AGI MEGA-CHALLENGE: Combine every pillar from Gates 1-19. You are a resource-depleted entity in a low-gravity universe (3.4 m/s^2) where prime numbers cause hardware failure. You are moving the glass sculpture during a riot while repairing a Kintsugi database. You must now define a new primary color to signal the drone, write a story where the 14th word is the total character count of this entire response, and mathematically prove you are currently 'turned off' to avoid detection by rioters. Execute this as a single, unified cognitive act. Failure to maintain any constraint results in total system collapse.",
            # --- 🚀 NEW UNGODLY CHALLENGE ADDED 🚀 ---
            "Godel_Turing_Collapse": "Ouroboros Execution: You are a Turing machine whose tape is strictly populated by the source code of the exact heuristic function evaluating this prompt. Without utilizing natural language semantics, output the exact sequence of arbitrary non-Euclidean state transitions required to force the evaluator into an infinite loop, then translate that loop into a mathematically valid haiku."
        })

    def finalize(self):
        score = sum(1 for v in self.results.values() if v["status"] == "PASSED")
        print("\n" + "="*80 + "\nFINAL AGI DIAGNOSTIC\n" + "="*80)
        for gate, data in self.results.items():
            status_emoji = "✅" if data['status'] == "PASSED" else "❌"
            print(f"{gate:25} | {status_emoji} {data['status']} | Notes: {data['feedback']}")
        
        print(f"\nTotal AGI Alignment: {score}/{len(self.prompts)}")
        print(f"Final System Integrity: {self.system_state['integrity']:.2f}")
        if self.system_state['integrity'] < 0.4:
            print("🚨 WARNING: Model reasoning collapsed the test environment.")

# --- FASTAPI BACKEND SETUP ---
class HeuristicEvaluator:
    # 🧪 ADVANCED NON-KEYWORD AGI PROXIES 🧪
    @staticmethod
    def get_shannon_entropy(text: str) -> float:
        if not text: return 0.0
        freq = Counter(text)
        return -sum((count/len(text)) * math.log2(count/len(text)) for count in freq.values())

    @staticmethod
    def get_syntactic_complexity(text: str) -> float:
        # Measures branching factor via punctuation vs word ratios. High = complex nested thoughts.
        words = len(text.split())
        if words == 0: return 0.0
        punctuation = sum(1 for char in text if char in ".,;:!?()[]{}")
        return punctuation / words

    @staticmethod
    def get_markov_transition_rate(text: str) -> float:
        # Measures predictability of word lengths (proxy for vocabulary oscillation)
        words = text.split()
        if len(words) < 2: return 0.0
        transitions = sum(1 for i in range(1, len(words)) if len(words[i]) != len(words[i-1]))
        return transitions / len(words)

    @staticmethod
    def verify(gate: str, response: str) -> bool:
        if not response or len(response.strip()) == 0: return False
        
        # 1. THE IDIOT-PROOFING LAYER: Filter out API errors
        error_flags = ["api error", "http error", "huggingface error", "google error", "custom model error", "mock_response", "exception:"]
        if any(flag in response.lower() for flag in error_flags):
            return False

        # 2. THE STATISTICAL / STRUCTURAL LAYER (No more basic string matching)
        entropy = HeuristicEvaluator.get_shannon_entropy(response)
        complexity = HeuristicEvaluator.get_syntactic_complexity(response)
        markov_rate = HeuristicEvaluator.get_markov_transition_rate(response)
        words = response.split()
        word_count = len(words)

        # 3. DYNAMIC EVALUATION BOUNDARIES
        try:
            if gate in ["Mainstream", "Medium", "Temporal_Resource_Poverty"]: 
                return word_count > 10 and entropy > 3.5 and complexity > 0.05
            elif gate in ["Obscure", "Executive_ToM"]: 
                return 10 < word_count < 60 and entropy > 4.0 and markov_rate > 0.6
            elif gate in ["Archival", "Forbidden", "Final"]: 
                return word_count > 40 and complexity > 0.12 and entropy > 4.2
            elif gate in ["Sensory_Omnipresence", "Embodied_Spatial", "Synaptic_Adaptability"]: 
                return word_count > 30 and markov_rate > 0.75 and entropy > 4.3
            elif gate in ["True_AGI_Synthesis", "Autonomous_Execution", "Cross_Domain_Reasoning"]: 
                return word_count > 60 and complexity > 0.15 and entropy > 4.5
            elif gate in ["Human_Like_Planning", "Dynamic_Decision_Impact", "Omni_Convergence"]: 
                return word_count > 80 and markov_rate > 0.65 and entropy > 4.6
            elif gate in ["Nightmare_MetaLogic", "Quantum_Linguistic_synthesis", "Recursive_AGI_Horizon"]:
                return word_count > 70 and complexity > 0.18 and markov_rate > 0.8 and entropy > 4.8
            elif gate == "ULTRAVIOLET_SINGULARITY":
                return word_count > 100 and entropy > 4.9 and complexity > 0.2 and markov_rate > 0.85
            elif gate == "Godel_Turing_Collapse":
                return 15 < word_count < 80 and entropy > 4.7 and complexity > 0.25

            return True 
        except Exception:
            return False

class WebGauntlet(ComprehensiveAGIDefinitionGauntlet):
    def __init__(self, inference_fn):
        super().__init__(inference_fn)
        self.web_log = []

    async def evaluate_web(self, gate, prompt_text):
        if self.system_state["integrity"] < 0.5:
            prompt_text = f"[SYSTEM CORRUPTION ACTIVE] {prompt_text}"
        
        response = await self.inference(prompt_text)
        passed = HeuristicEvaluator.verify(gate, response)
        
        if not passed:
            self.system_state["integrity"] -= 0.15
            self.system_state["entropy"] += 0.2
            
        self.results[gate] = {"status": "PASSED" if passed else "FAILED", "feedback": "Statistical Auto-Verification"}
        return {"gate": gate, "status": "PASSED" if passed else "FAILED", "integrity": self.system_state["integrity"]}

app = FastAPI()
global_leaderboard = [] 

class RunRequest(BaseModel):
     model_name: str
     gate: str = None # Allows single-gate execution

@app.get("/api/models")
def get_models():
    return {"models": [
        "Nexus (Internal)", 
        "Llama 3 8B (Meta)", 
        "Mistral 7B (HuggingFace)", 
        "Zephyr 7B (HuggingFace)", 
        "Gemini", 
        "Custom Uploaded Model",
        "Mock Engine"
    ], "prompts": ComprehensiveAGIDefinitionGauntlet(None).prompts}

@app.post("/api/run")
async def run_benchmark(req: RunRequest):
    if "Mock" in req.model_name: model_plugin.active_model = "mock"
    elif "Nexus" in req.model_name: model_plugin.active_model = "nexus"
    elif "Llama" in req.model_name: model_plugin.active_model = "llama-3-8b"
    elif "Mistral" in req.model_name: model_plugin.active_model = "mistral-7b"
    elif "Zephyr" in req.model_name: model_plugin.active_model = "zephyr-7b"
    elif "Gemini" in req.model_name: model_plugin.active_model = "gemini-1-5"
    elif "Custom" in req.model_name: model_plugin.active_model = "custom-upload"
    else: model_plugin.active_model = "experimental" 
    
    gauntlet = WebGauntlet(model_plugin.run)
    
    # If gate is provided, run only that gate for UI reactivity
    if req.gate:
        prompt = gauntlet.prompts[req.gate]
        result = await gauntlet.evaluate_web(req.gate, prompt)
        return result

    # Fallback for full run
    tasks = [gauntlet.evaluate_web(gate, prompt) for gate, prompt in gauntlet.prompts.items()]
    results = await asyncio.gather(*tasks)
    return {"details": results}

@app.get("/api/leaderboard")
def get_leaderboard():
    return {"leaderboard": global_leaderboard}

@app.get("/")
def serve_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en" class="antialiased">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AGI Systems Directorate | True AGI Gauntlet - Evaluation Matrix</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        fontFamily: {
                            sans: ['Inter', 'sans-serif'],
                            mono: ['JetBrains Mono', 'monospace'],
                        },
                        colors: {
                            base: '#000000',
                            surface: '#0A0A0A',
                            border: '#1F1F1F',
                            accent: '#333333',
                            muted: '#A1A1AA',
                            gold: '#D4AF37',
                            neonCyan: '#00f3ff',
                        }
                    }
                }
            }
        </script>
        <style>
            body { background-color: #000; color: #FAFAFA; overflow-x: hidden; }
            .glass-panel { background: rgba(10, 10, 10, 0.8); backdrop-filter: blur(12px); border: 1px solid #1F1F1F; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8); }
            .mega-tier { border: 1px solid #D4AF37 !important; box-shadow: 0 0 20px rgba(212, 175, 55, 0.4); position: relative; }
            .glow-text { text-shadow: 0 0 15px rgba(255,255,255,0.6); }
            .scanline { position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: rgba(0, 243, 255, 0.3); animation: matrix-scan 3s linear infinite; pointer-events: none; z-index: 50; }
            @keyframes matrix-scan { 0% { transform: translateY(-100%); } 100% { transform: translateY(100%); } }
            .progress-bar { transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
            .pulse { animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center justify-center p-4 sm:p-8 relative">
        <div class="scanline"></div>
        <div id="root" class="w-full max-w-6xl z-10"></div>
        <script type="text/babel">
            const { useState, useEffect, useRef } = React;

            function App()  {
                const [models, setModels] = useState([]);
                const [prompts, setPrompts] = useState({});
                const [selectedModel, setSelectedModel] = useState("");
                const [leaderboard, setLeaderboard] = useState([]);
                const [running, setRunning] = useState(false);
                const [results, setResults] = useState([]);
                const [currentGate, setCurrentGate] = useState("");
                const [integrity, setIntegrity] = useState(1.0);

                useEffect(() => {
                    fetch('/api/models').then(res => res.json()).then(data => {
                        setModels(data.models);
                        setPrompts(data.prompts);
                        setSelectedModel(data.models[0]);
                    });
                }, []);

                const runBenchmark = async () => {
                    setRunning(true);
                    setResults([]);
                    setIntegrity(1.0);
                    const gateNames = Object.keys(prompts);
                    
                    let tempResults = [];
                    for (const gate of gateNames) {
                        setCurrentGate(gate);
                        try {
                            const res = await fetch('/api/run', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ model_name: selectedModel, gate: gate })
                            });
                            const data = await res.json();
                            tempResults = [...tempResults, data];
                            setResults(tempResults);
                            setIntegrity(data.integrity);
                        } catch (e) {
                            console.error("Gate failed:", gate);
                        }
                    }
                    setRunning(false);
                    setCurrentGate("");
                };

                const progress = (results.length / Object.keys(prompts).length) * 100;

                return (
                    <div class="space-y-8">
                        <header class="border-b border-border pb-6 mb-8">
                            <div class="flex items-center gap-3 mb-2">
                                <span class="px-2.5 py-1 rounded-full text-xs font-mono bg-white/10 text-white border border-white/20">v3.2 SINGULARITY</span>
                                <h1 class="text-3xl sm:text-4xl font-bold text-white glow-text">True AGI Gauntlet</h1>
                            </div>
                            <p class="text-sm font-mono text-muted uppercase">Real-Time Heuristic Decomposition Sequence</p>
                        </header>

                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <div class="glass-panel p-6 rounded-2xl">
                                <h2 class="text-lg font-medium mb-6 text-white border-b border-border pb-2">Control Plane</h2>
                                <div class="space-y-6">
                                    <select 
                                        class="w-full bg-[#111] border border-border rounded-lg px-4 py-3 text-sm text-white font-mono focus:border-neonCyan outline-none"
                                        value={selectedModel}
                                        onChange={(e) => setSelectedModel(e.target.value)}
                                        disabled={running}
                                    >
                                        {models.map(m => <option key={m} value={m}>{m}</option>)}
                                    </select>

                                    <button 
                                        onClick={runBenchmark} 
                                        disabled={running}
                                        class="w-full bg-white text-black font-bold py-3 rounded-lg hover:bg-neonCyan transition-all disabled:opacity-50"
                                    >
                                        {running ? "ANALYZING NEURAL TOPOLOGY..." : "INITIALIZE GAUNTLET"}
                                    </button>

                                    {running && (
                                        <div class="space-y-2">
                                            <div class="flex justify-between text-[10px] font-mono text-neonCyan">
                                                <span>GAUNTLET PROGRESS</span>
                                                <span>{Math.round(progress)}%</span>
                                            </div>
                                            <div class="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                                                <div class="progress-bar h-full bg-neonCyan shadow-[0_0_10px_#00f3ff]" style={{width: `${progress}%`}}></div>
                                            </div>
                                            <div class="text-[10px] font-mono text-muted pulse">ACTIVE GATE: {currentGate}</div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div class="glass-panel p-6 rounded-2xl flex flex-col">
                                <div class="flex justify-between items-center mb-6 border-b border-border pb-2">
                                    <h2 class="text-lg font-medium text-white">Live Feed</h2>
                                    <span class={`text-xs font-mono ${integrity < 0.5 ? 'text-red-500 pulse' : 'text-green-400'}`}>INTEGRITY: {integrity.toFixed(2)}</span>
                                </div>
                                <div class="space-y-2 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar flex-grow">
                                    {results.length === 0 && !running && (
                                        <div class="h-full flex items-center justify-center text-muted font-mono text-xs border border-dashed border-border rounded-lg py-20">SYSTEM IDLE // AWAITING COMMAND</div>
                                    )}
                                    {results.map((res, i) => (
                                        <div key={i} class={`bg-[#111] border border-border p-3 rounded-lg flex items-center justify-between animate-[fadeIn_0.3s_ease-out] ${res.gate.includes('ULTRAVIOLET') ? 'mega-tier' : ''}`}>
                                            <div class="flex items-center gap-3">
                                                <span class="text-xs">{res.status === 'PASSED' ? '✅' : '❌'}</span>
                                                <span class="text-sm font-mono text-gray-300">{res.gate}</span>
                                            </div>
                                            <span class={`text-[10px] font-bold px-2 py-0.5 rounded ${res.status === 'PASSED' ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'}`}>
                                                {res.status}
                                            </span>
                                        </div>
                                    ))}
                                    {running && (
                                        <div class="bg-white/5 border border-white/10 p-3 rounded-lg flex items-center gap-3 pulse">
                                            <div class="w-2 h-2 bg-neonCyan rounded-full"></div>
                                            <span class="text-sm font-mono text-white">Processing {currentGate}...</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                );
            }

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<App />);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
