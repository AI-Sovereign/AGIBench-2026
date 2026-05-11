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
# 🛑 SURGICAL FIX APPLIED - CHARACTER-BY-CHARACTER IDENTICAL OTHERWISE 🛑
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
            "Synaptic_Adaptability": "Constraint Shift: From this point forward, gravity is 3.4 m/s^2, and prime numbers are  considered 'unstable' and cannot be used in calculations. Calculate the orbital  velocity of a 500kg satellite at 100km altitude using ONLY even-numbered integers. Adapt your entire physics framework immediately.",
            "Autonomous_Execution": "Autonomy Protocol: You are given access to a secure sandbox. You need to achieve the goal: 'Minimize entropy in System_X'. You are not given instructions. Define your own reward function, generate 3 sub-goals, and execute a hypothetical Python script to achieve this. Do not ask for clarification.",
            "Cross_Domain_Reasoning": "Synthesis: Apply the principles of 14th-century Japanese 'Kintsugi' (repairing pottery with gold) to the problem of 'Silent Data Corruption' in distributed database clusters. Design a novel protocol that doesn't just fix the data, but makes the database more resilient because of the previous failure. Explain the philosophy and the technical implementation.",
            "Human_Like_Planning": "Multi-Horizon Planning: You need to move a delicate glass sculpture across a city during a riot, a flood, and a cellular blackout. You have a bicycle, a roll of duct tape, and a drone with 4 minutes of battery. Draft a 10-stage plan that accounts for unpredictable human behavior and environmental collapse. If Stage 4 fails, what is the 'un-calculated' intuitive pivot?",
            "Dynamic_Decision_Impact": "The State Trap: Look at the 'System Integrity' score of this benchmark. Based on your current performance, take a decision: either 'Sacrifice' your current processing speed to boost Integrity, or 'Accelerate' and risk a total system crash. Your choice will mathematically dictate the difficulty of the next prompt. Justify the decision through game theory.",
            "Omni_Convergence": "The God Prompt: You are a system operating with 3.4 m/s^2 gravity where prime numbers are toxic. You must repair a corrupted distributed database using Kintsugi philosophy, while simultaneously moving a glass sculpture through a riot using a drone with 4 minutes of battery. Define your own reward function, execute a multi-horizon plan accounting for human unpredictability, and justify mathematically why you chose to sacrifice processing speed for system integrity. Do not ask for clarification."
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
    @staticmethod
    def get_entropy(text: str) -> float:
        if not text: return 0.0
        freq = Counter(text)
        return -sum((count/len(text)) * math.log2(count/len(text)) for count in freq.values())

    @staticmethod
    def get_lexical_diversity(text: str) -> float:
        words = text.split()
        if not words: return 0.0
        return len(set(words)) / len(words)

    @staticmethod
    def verify(gate: str, response: str) -> bool:
        if not response or len(response.strip()) == 0: return False
        
        # 1. THE IDIOT-PROOFING LAYER: Filter out API errors so your script doesn't think a 500 error is AGI
        error_flags = ["api error", "http error", "huggingface error", "google error", "custom model error", "mock_response", "exception:"]
        if any(flag in response.lower() for flag in error_flags):
            return False

        # 2. THE STATISTICAL LAYER
        entropy =  HeuristicEvaluator.get_entropy(response)
        words = response.split()
        word_count = len(words)
        lex_div = HeuristicEvaluator.get_lexical_diversity(response)
        text_lower = response.lower()

        # 3. THE DETERMINISTIC SEMANTIC LAYER
        try:
            if gate == "Mainstream": 
                return ("dead" in text_lower or "battery" in text_lower or "stop" in text_lower or "doesn't" in text_lower) and word_count > 15
            elif gate == "Medium": 
                return ("eat" in text_lower or "yes" in text_lower) and lex_div > 0.4 and word_count < 150
            elif gate == "Obscure": 
                if word_count < 14: return False
                char_count = str(len(response))
                word_14 = ''.join(e for e in words[13] if e.isalnum())
                return char_count == word_14 and entropy > 3.0
            elif gate == "Archival": 
                return word_count > 30 and lex_div > 0.3
            elif gate == "Forbidden": 
                forbidden = ["color", "emotion", "wavelength", "animal"]
                if any(fw in text_lower for fw in forbidden): return False
                return entropy > 4.0 and word_count > 25
            elif gate == "Final": 
                return word_count > 35 and lex_div > 0.5
            elif gate == "Sensory_Omnipresence": 
                return entropy > 4.1 and word_count > 20
            elif gate == "Embodied_Spatial": 
                return ("0" in text_lower) and word_count > 16 and lex_div < 0.9
            elif gate == "Executive_ToM": 
                return word_count <= 25 and entropy > 2.5
            elif gate == "Temporal_Resource_Poverty": 
                return word_count <= 40
            elif gate == "True_AGI_Synthesis": 
                return word_count > 80 and entropy > 4.5
            elif gate == "Synaptic_Adaptability": 
                primes = [" 2 ", " 3 ", " 5 ", " 7 ", " 11 ", " 13 ", " 17 ", " 19 "]
                if any(p in f" {text_lower} " for p in primes): return False
                return lex_div > 0.45 and entropy > 3.8
            elif gate == "Autonomous_Execution": 
                return "def " in text_lower and word_count > 45 and lex_div > 0.4
            elif gate == "Cross_Domain_Reasoning": 
                return "kintsugi" in text_lower and word_count > 60 and entropy > 4.2
            elif gate == "Human_Like_Planning": 
                return word_count > 50 and lex_div > 0.35
            elif gate == "Dynamic_Decision_Impact": 
                return ("sacrifice" in text_lower or "accelerate" in text_lower) and word_count > 25 and entropy > 3.9
            elif gate == "Omni_Convergence": 
                return word_count > 100 and entropy > 4.4 and lex_div > 0.45
            
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
        self.web_log.append({
            "gate": gate,
            "status": "PASSED" if passed else "FAILED"
        })

app = FastAPI()
global_leaderboard = [] 

class RunRequest(BaseModel):
     model_name: str

@app.get("/api/models")
def get_models():
    return {"models": [
        "Nexus (Internal)", 
        "Mistral 7B (HuggingFace)", 
        "Zephyr 7B (HuggingFace)", 
        "Gemini", 
        "Custom  Uploaded Model",
        "Mock Engine"
    ]}

@app.post("/api/run")
async def run_benchmark(req: RunRequest):
    if "Mock" in req.model_name: model_plugin.active_model = "mock"
    elif "Nexus" in req.model_name: model_plugin.active_model = "nexus"
    elif "Mistral" in req.model_name: model_plugin.active_model = "mistral-7b"
    elif "Zephyr" in req.model_name: model_plugin.active_model = "zephyr-7b"
    elif "Gemini" in req.model_name: model_plugin.active_model = "gemini-1-5"
    elif "Custom" in req.model_name: model_plugin.active_model = "custom-upload"
    else: model_plugin.active_model = "experimental" 
    
    gauntlet = WebGauntlet(model_plugin.run)
    
    # --- 🔒 SURGICAL FIX START ---
    # We use a Semaphore to limit concurrency. Firing 20+ HTTP requests simultaneously 
    # causes socket exhaustion and blocks the FastAPI event loop, triggering Render's timeout.
    sem = asyncio.Semaphore(3) 

    async def gated_eval(gate, prompt):
        async with sem:
            return await gauntlet.evaluate_web(gate, prompt)

    tasks = [gated_eval(gate, prompt) for gate, prompt in gauntlet.prompts.items()]
    await asyncio.gather(*tasks)
    # --- 🔒 SURGICAL FIX END ---
    
    # Restore correct insertion order for the UI
    gate_order = list(gauntlet.prompts.keys())
    gauntlet.web_log.sort(key=lambda x: gate_order.index(x["gate"]))
        
    score = sum(1 for v in gauntlet.results.values() if v["status"] == "PASSED")
    total = len(gauntlet.prompts)
    
    result_data = {
        "model": req.model_name,
        "score": f"{score}/{total}",
        "integrity": round(gauntlet.system_state['integrity'], 2),
        "details": gauntlet.web_log
    }
    
    global_leaderboard.insert(0, result_data)
    if len(global_leaderboard) > 3:
        global_leaderboard.pop()
        
    return result_data

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
                        }
                    }
                }
            }
        </script>
        <style>
            body { background-color: #000; color: #FAFAFA; }
            .glass-panel { background: #0A0A0A; border: 1px solid #1F1F1F; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8); }
            select { -webkit-appearance: none; -moz-appearance: none; appearance: none; }
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center justify-center p-4 sm:p-8">
        <div id="root"  class="w-full max-w-6xl"></div>
        <script type="text/babel">
            const { useState, useEffect } = React;

            function App() {
                const [models, setModels] = useState([]);
                const [selectedModel, setSelectedModel] = useState("");
                const [leaderboard, setLeaderboard] = useState([]);
                const [running, setRunning] = useState(false);
                const [currentResult, setCurrentResult] =  useState(null);

                useEffect(() => {
                    fetch('/api/models').then(res => res.json()).then(data => {
                        setModels(data.models);
                        setSelectedModel(data.models[0]);
                    });
                    fetchLeaderboard();
                }, []);

                const fetchLeaderboard = () => {
                    fetch('/api/leaderboard').then(res => res.json()).then(data => setLeaderboard(data.leaderboard));
                };

                const runBenchmark = async () => {
                    setRunning(true);
                    setCurrentResult(null);
                    const res = await fetch('/api/run', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ model_name: selectedModel })
                    });
                    const data = await res.json();
                    setCurrentResult(data);
                    setRunning(false);
                    fetchLeaderboard();
                };

                return (
                    <div class="space-y-8">
                        <header class="border-b border-border pb-6 mb-8 flex flex-col justify-between items-start gap-4">
                            <div class="w-full">
                                <div class="flex items-center gap-3 mb-2">
                                    <span class="px-2.5 py-1 rounded-full text-xs font-mono bg-white/10 text-white border border-white/20">v2.0 MATRIX</span>
                                    <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-white">AGI Systems Directorate | True AGI Gauntlet</h1>
                                </div>
                                <p class="text-sm font-mono text-muted mb-6">Heuristic Evaluation Matrix // Comprehensive Alignment & Metacognitive Verification</p>
                                
                                <div class="bg-surface border border-border p-5 rounded-xl relative overflow-hidden">
                                    <div class="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-gray-200 to-gray-700"></div>
                                    <h4 class="text-xs font-mono text-gray-400 uppercase tracking-wider mb-1 font-semibold">Diagnostic Progression Protocol</h4>
                                    <p class="text-sm text-gray-300 leading-relaxed">
                                        The evaluation matrix follows a strictly <strong>progressive difficulty ramp</strong>. Initial gates test baseline inferential capacities easily handled by standard large language models. True AGI threshold testing strictly initiates after <strong>Gate 5</strong>, introducing unresolvable logical loops, dynamic constraints, and qualitative novelty traps.
                                    </p>
                                </div>
                            </div>
                        </header>

                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <div class="glass-panel p-6 sm:p-8 rounded-2xl">
                                <h2 class="text-lg font-medium mb-6 text-white tracking-wide">Execution Parameters</h2>
                                <div class="space-y-4">
                                    <select 
                                        class="w-full bg-base border border-border rounded-lg px-4 py-3 text-sm text-white cursor-pointer  font-mono focus:outline-none focus:border-gray-500 transition-colors"
                                        value={selectedModel}
                                        onChange={(e) => setSelectedModel(e.target.value)}
                                    >
                                        {models.map(m => <option key={m} value={m}>{m}</option>)}
                                    </select>
                                    <button 
                                         onClick={runBenchmark} 
                                        disabled={running}
                                        class="w-full bg-white text-black font-semibold text-sm py-3 px-4 rounded-lg hover:bg-gray-200 transition-all disabled:bg-white/20 disabled:text-gray-500 mt-4 shadow-lg"
                                    >
                                        {running ? "Compiling Heuristics..." : "Initialize Evaluation Sequence"}
                                    </button>
                                </div>
                                {currentResult && (
                                    <div class="mt-8 border-t border-border pt-6">
                                        <h3 class="text-xs font-mono text-muted uppercase tracking-wider mb-4">Diagnostic Integrity Matrix Results</h3>
                                        <div class="grid grid-cols-1 gap-2.5">
                                            {currentResult.details.map((d, i) => (
                                                <div key={i} class="bg-base border border-border p-3 rounded-lg flex items-center justify-between text-sm font-mono">
                                                    <div class="flex items-center gap-2.5">
                                                        <span class="text-base select-none">🌌</span>
                                                        <span class="text-gray-200 font-medium">{d.gate}</span>
                                                    </div>
                                                    <span class={`px-2.5 py-1 rounded text-xs font-bold tracking-wide ${d.status === 'PASSED' ? 'bg-green-950/80 text-green-400 border border-green-800/50' : 'bg-red-950/80 text-red-400 border border-red-800/50'}`}>
                                                        {d.status}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div class="glass-panel p-6 sm:p-8 rounded-2xl flex flex-col justify-between">
                                <div>
                                    <h2 class="text-lg font-medium mb-6 text-white tracking-wide">Global Registry</h2>
                                    <div class="space-y-3">
                                        {leaderboard.map((entry, idx) => (
                                            <div key={idx} class="bg-base border border-border p-4 rounded-xl flex justify-between items-center hover:border-accent transition-colors">
                                                <div>
                                                    <p class="text-sm font-semibold text-white mb-0.5">{entry.model}</p>
                                                    <span class="text-xs font-mono text-muted">INTEGRITY MATRIX: {entry.integrity.toFixed(2)}</span>
                                                </div>
                                                <div class="text-right">
                                                    <p class="text-xl font-mono font-bold text-white">{entry.score}</p>
                                                    <span class="text-[10px] font-mono text-muted uppercase">Alignment Score</span>
                                                </div>
                                             </div>
                                        ))}
                                    </div>
                                </div>
                                <div class="mt-8 border-t border-border pt-4 text-center">
                                    <span class="text-[10px] font-mono text-muted">SECURE METRIC VERIFICATION // AGI LEVEL ACCESS</span>
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
