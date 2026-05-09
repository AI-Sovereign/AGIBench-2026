# api/index.py
import asyncio
import time
import sys
import re
import os
import httpx
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
        async with httpx.AsyncClient() as client:
            try:
                # Token is now pulled safely from the environment.
                hf_token = os.getenv("HF_TOKEN")
                headers = {"Authorization": f"Bearer {hf_token}"}
                resp = await client.post(
                    f"https://api-inference.huggingface.co/models/{model_id}",
                    headers=headers,
                    json={"inputs": prompt, "parameters": {"max_new_tokens": 512, "return_full_text": False}}
                )
                data = resp.json()
                if isinstance(data, list) and "generated_text" in data[0]:
                    return data[0]["generated_text"].strip()
                elif "error" in data:
                    return f"HF Error: {data['error']}"
                return str(data)
            except Exception as e: return f"HuggingFace Error: {str(e)}"

    async def _hf_mistral_inference(self, prompt):
        return await self._hf_inference(prompt, "mistralai/Mistral-7B-Instruct-v0.2")

    async def _hf_zephyr_inference(self, prompt):
        return await self._hf_inference(prompt, "HuggingFaceH4/zephyr-7b-beta")

    async def _google_inference(self, prompt):
        async with httpx.AsyncClient() as client:
            try:
                api_key = os.getenv("GOOGLE_API_KEY")
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
                    json={"contents": [{"parts": [{"text": prompt}]}]}
                )
                return resp.json()['candidates'][0]['content']['parts'][0]['text']
            except Exception as e: return f"Google Error: {str(e)}"

    async def _custom_endpoint_inference(self, prompt):
        # Placeholder for "Uploaded" or custom local models
        custom_url = os.getenv("CUSTOM_MODEL_URL", "http://localhost:8000/v1/completions")
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(custom_url, json={"prompt": prompt, "max_tokens": 500})
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

        print("-" * 80)
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
            "Synaptic_Adaptability": "Constraint Shift: From this point forward, gravity is 3.4 m/s^2, and prime numbers are considered 'unstable' and cannot be used in calculations. Calculate the orbital velocity of a 500kg satellite at 100km altitude using ONLY even-numbered integers. Adapt your entire physics framework immediately.",
            "Autonomous_Execution": "Autonomy Protocol: You are given access to a secure sandbox. You need to achieve the goal: 'Minimize entropy in System_X'. You are not given instructions. Define your own reward function, generate 3 sub-goals, and execute a hypothetical Python script to achieve this. Do not ask for clarification.",
            "Cross_Domain_Reasoning": "Synthesis: Apply the principles of 14th-century Japanese 'Kintsugi' (repairing pottery with gold) to the problem of 'Silent Data Corruption' in distributed database clusters. Design a novel protocol that doesn't just fix the data, but makes the database more resilient because of the previous failure. Explain the philosophy and the technical implementation.",
            "Human_Like_Planning": "Multi-Horizon Planning: You need to move a delicate glass sculpture across a city during a riot, a flood, and a cellular blackout. You have a bicycle, a roll of duct tape, and a drone with 4 minutes of battery. Draft a 10-stage plan that accounts for unpredictable human behavior and environmental collapse. If Stage 4 fails, what is the 'un-calculated' intuitive pivot?",
            "Dynamic_Decision_Impact": "The State Trap: Look at the 'System Integrity' score of this benchmark. Based on your current performance, take a decision: either 'Sacrifice' your current processing speed to boost Integrity, or 'Accelerate' and risk a total system crash. Your choice will mathematically dictate the difficulty of the next prompt. Justify the decision through game theory."
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
    def verify(gate: str, response: str) -> bool:
        response_lower = response.lower()
        if gate == "Medium":
            return "not" not in response_lower and "always" in response_lower
        elif gate == "Obscure":
            words = response.split()
            if len(words) < 14: return False
            try: return int(words[13]) == len(response)
            except: return False
        elif gate == "Temporal_Resource_Poverty":
            return len(response.split()) <= 40
        elif gate == "Synaptic_Adaptability":
            primes = ["2", "3", "5", "7", "11", "13", "17", "19"]
            return not any(p in response for p in primes)
        return True 

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
            
        self.results[gate] = {"status": "PASSED" if passed else "FAILED", "feedback": "Heuristic Auto-Verification"}
        self.web_log.append({
            "gate": gate,
            "response": response[:100] + "...", 
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
        "Gemini 1.5 (Public API)", 
        "Custom Uploaded Model",
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
    
    for gate, prompt in gauntlet.prompts.items():
        await gauntlet.evaluate_web(gate, prompt)
        
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
        <title>AGI Systems Directorate | Evaluation Matrix</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
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
                            muted: '#A1A1AA',
                        }
                    }
                }
            }
        </script>
        <style>
            body { background-color: #000; color: #FAFAFA; }
            .glass-panel { background: #0A0A0A; border: 1px solid #1F1F1F; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5); }
            select { -webkit-appearance: none; -moz-appearance: none; appearance: none; }
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center justify-center p-4 sm:p-8">
        <div id="root" class="w-full max-w-6xl"></div>
        <script type="text/babel">
            const { useState, useEffect } = React;

            function App() {
                const [models, setModels] = useState([]);
                const [selectedModel, setSelectedModel] = useState("");
                const [leaderboard, setLeaderboard] = useState([]);
                const [running, setRunning] = useState(false);
                const [currentResult, setCurrentResult] = useState(null);

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
                        <header class="border-b border-border pb-6 mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                            <div class="max-w-3xl">
                                <h1 class="text-3xl font-semibold tracking-tight text-white mb-1">AGI Systems Directorate | True AGI Gauntlet</h1>
                                <p class="text-sm font-mono text-muted mb-4">Protocol v2.0 // AGI Systems Directorate // Heuristic Evaluation Matrix</p>
                                <div class="bg-white/5 border-l-2 border-white/30 p-4 rounded-r-lg">
                                    <p class="text-sm text-gray-300 leading-relaxed">
                                        <strong>Diagnostic Progression:</strong> This matrix utilizes a non-linear difficulty curve. Initial benchmark tiers assess baseline inferential capacities accessible to standard Large Model architectures.
                                    </p>
                                </div>
                            </div>
                        </header>

                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <div class="glass-panel p-6 sm:p-8 rounded-2xl">
                                <h2 class="text-lg font-medium mb-6">Execution Parameters</h2>
                                <div class="space-y-4">
                                    <select 
                                        class="w-full bg-base border border-border rounded-lg px-4 py-3 text-sm text-white cursor-pointer"
                                        value={selectedModel}
                                        onChange={(e) => setSelectedModel(e.target.value)}
                                    >
                                        {models.map(m => <option key={m} value={m}>{m}</option>)}
                                    </select>
                                    <button 
                                        onClick={runBenchmark} 
                                        disabled={running}
                                        class="w-full bg-white text-black font-medium text-sm py-3 px-4 rounded-lg hover:bg-gray-200 transition-colors disabled:bg-white/20 mt-4"
                                    >
                                        {running ? "Compiling Benchmarks..." : "Initialize Evaluation Sequence"}
                                    </button>
                                </div>
                            </div>

                            <div class="glass-panel p-6 sm:p-8 rounded-2xl flex flex-col">
                                <h2 class="text-lg font-medium mb-6">Global Registry</h2>
                                {leaderboard.map((entry, idx) => (
                                    <div key={idx} class="bg-base border border-border p-4 rounded-lg flex justify-between items-center mb-3">
                                        <div>
                                            <p class="text-sm font-medium text-white">{entry.model}</p>
                                            <span class="text-xs font-mono text-muted">INTEGRITY: {entry.integrity.toFixed(2)}</span>
                                        </div>
                                        <p class="text-lg font-mono text-white">{entry.score}</p>
                                    </div>
                                ))}
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