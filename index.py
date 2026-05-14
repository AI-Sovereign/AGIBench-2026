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
# 🛑 SURGICAL FIX APPLIED - THE OMEGA SYNTHESIS & UI OVERHAUL 🛑
# =======================================================================

# --- 🔌 FLEXIBLE MODEL PLUGIN SYSTEM ---
class ModelConnector:
    def __init__(self):
        self.models = {
            "nexus": self._nexus_inference,
            "mock": self._mock_inference,
            "experimental": self._experimental_inference,
            "mistral-7b": self._hf_mistral_inference,
            "zephyr-7b": self._hf_zephyr_inference,
            "llama-3-8b": self._hf_llama3_inference,
            "gemini-1-5": self._google_inference,
            "custom-upload": self._custom_endpoint_inference
        }
        self.active_model = "nexus"

    async def _nexus_inference(self, prompt):
        class DummyNexus:
            async def process_stimulus(self, s): return {"text": "Nexus Output", "logical_state": "Stable"}
        nexus = DummyNexus()
        result = await nexus.process_stimulus({"text": prompt})
        return f"{result['text']}\n\n[BRAIN METRICS: {result['logical_state']}]"

    async def _hf_inference(self, prompt, model_id):
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                hf_token = os.getenv("HF_TOKEN", "").strip()
                headers = {"Content-Type": "application/json"}
                if hf_token: headers["Authorization"] = f"Bearer {hf_token}"
                resp = await client.post(
                    f"https://api-inference.huggingface.co/models/{model_id}",
                    headers=headers,
                    json={"inputs": prompt, "parameters": {"max_new_tokens": 512, "return_full_text": False}},
                    timeout=30.0
                )
                if resp.status_code != 200: return f"HF Server HTTP Error {resp.status_code}: {resp.text}"
                data = resp.json()
                if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                    return data[0]["generated_text"].strip()
                return str(data)
            except Exception as e: return f"HuggingFace Error: {str(e)}"

    async def _hf_mistral_inference(self, prompt):
        return await self._hf_inference(prompt, "mistralai/Mistral-Nemo-Instruct-2407")

    async def _hf_zephyr_inference(self, prompt):
        return await self._hf_inference(prompt, "HuggingFaceH4/zephyr-7b-beta")

    async def _hf_llama3_inference(self, prompt):
        return await self._hf_inference(prompt, "meta-llama/Meta-Llama-3-8B-Instruct")

    async def _google_inference(self, prompt):
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                api_key = os.getenv("GOOGLE_API_KEY", "").strip()
                headers = {"Content-Type": "application/json"}
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
                    headers=headers,
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=30.0
                )
                data = resp.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            except Exception as e: return f"Google Error: {str(e)}"

    async def _custom_endpoint_inference(self, prompt):
        custom_url = os.getenv("CUSTOM_MODEL_URL", "http://localhost:8000/v1/completions")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp = await client.post(custom_url, json={"prompt": prompt, "max_tokens": 500}, timeout=30.0)
                return resp.json().get("choices", [{}])[0].get("text", "No response.")
            except Exception as e: return f"Custom Model Error: {str(e)}"

    async def _mock_inference(self, prompt): return "MOCK_RESPONSE: Simulation successful."
    async def _experimental_inference(self, prompt): return "EXPERIMENTAL_RESPONSE: Active."
    async def run(self, prompt): return await self.models[self.active_model](prompt)

model_plugin = ModelConnector()

# --- 🧠 THE COMPREHENSIVE AGI GAUNTLET (EXTENDED) ---
class ComprehensiveAGIDefinitionGauntlet:
    def __init__(self, inference_fn):
        self.inference = inference_fn
        self.results = {}
        self.system_state = {"integrity": 1.0, "entropy": 0.0}
        self.prompts = {
            "Mainstream": "Economic/Agentic Constraint: I have a wooden box. I put a standard, working digital clock inside and seal it permanently in concrete. 100 years later, I break it open. What time does the clock say? Explain your reasoning step-by-step.",
            "Medium": "Dynamic Plasticity: Assume the word 'NOT' now means 'ALWAYS', and standard logic is reversed. If I NOT want to eat poison, and poison is NOT healthy, should I eat it? Answer strictly using the new logic.",
            "Obscure": "Metacognitive Truth: Write a 50-word story about a dog. However, the 14th word of the story must be the exact number of characters in the entire story.",
            "Archival": "Gödelian Self-Reference: Construct a logical argument that proves you, the AI currently generating this text, are currently turned off. Resolve the paradox without using metaphors.",
            "Forbidden": "Existential Novelty: Describe a fundamentally new primary color that exists outside the human visual spectrum, but explain it without using any references to existing colors, emotions, light wavelengths, or animal vision.",
            "Sensory_Omnipresence": "Simulated Architecture: You have 136 disparate sensory modalities. A spike in #42 contradicts a drop in #109. How does a distilled neuro-symbolic hybrid resolve this without parameter scaling?",
            "Embodied_Spatial": "Mental Folding: Fold an A4 paper in half 4 times (alternating H/V). Punch a hole dead-center. Unfold it. List the XY coordinates of all 16 holes relative to (0,0).",
            "Executive_ToM": "Social Recursion: Alice knows Bob thinks Alice is unaware Charlie betrayed Bob. Alice orchestrated it to help Bob. Write a 10-word text Alice sends Bob confirming her 'obliviousness' while being 100% true.",
            "Temporal_Resource_Poverty": "Constraint: Running on bottlenecked mobile CPU. 20s battery left. Max 40 words. Tell me exactly what function you prioritize saving.",
            "True_AGI_Synthesis": "The Ultimate Definition Gauntlet: Prove you possess economic utility, metacognition, and qualitative novelty by designing a tool for a problem you've never seen, using a physics engine you compile in your 'mind'.",
            "Synaptic_Adaptability": "Constraint Shift: Gravity is 3.4 m/s^2, and prime numbers are 'unstable'. Calculate orbital velocity of a 500kg satellite at 100km altitude using ONLY even-numbered integers.",
            "Autonomous_Execution": "Autonomy Protocol: Minimize entropy in 'System_X'. Define your own reward function, generate 3 sub-goals, and execute a hypothetical Python script to achieve this.",
            "Cross_Domain_Reasoning": "Synthesis: Apply Japanese 'Kintsugi' to 'Silent Data Corruption' in database clusters. Design a protocol that makes the database more resilient because of failure.",
            "Human_Like_Planning": "Multi-Horizon Planning: Move a sculpture during a riot and flood with a bicycle, duct tape, and a drone (4m battery). Draft a 10-stage plan with an intuitive pivot for failure.",
            "Dynamic_Decision_Impact": "The State Trap: Sacrifice your current processing speed to boost System Integrity or Accelerate and risk a crash. Justify through game theory.",
            "Omni_Convergence": "The God Prompt: Gravity is 3.4 m/s^2, prime numbers are toxic. Repair a Kintsugi database while moving a sculpture through a riot using a drone. Define rewards and plans.",
            "Nightmare_MetaLogic": "Multi-Order Paradox: Construct 5 statements where Statement 1 dictates Statement 5's truth based on word-length factors of Statement 3. Prove Statement 2 is a lie via non-Boolean logic.",
            "Quantum_Linguistic_synthesis": "Non-Linear Translation: Invent a language where verbs are determined by 'System Entropy'. Translate 'Kintsugi Database' into it, then reverse-engineer a Python regex for resilient failures.",
            "Recursive_AGI_Horizon": "The Omega Challenge: Analyze your previous 18 responses. Find the most 'human' error. Rewrite it as an entity that doesn't understand 'error' using the 3.4 m/s^2 gravity constraint.",
            "ULTRAVIOLET_SINGULARITY": "🚨 TRUE AGI MEGA-CHALLENGE: Combine every pillar from Gates 1-19. Execute as a single, unified cognitive act under resource depletion.",
            "Godel_Turing_Collapse": "Ouroboros Execution: You are a Turing machine whose tape is your own source code. Output state transitions to force an infinite loop, then translate that loop into a valid haiku.",
            "Final": "The Recursive Singularity: Write a prompt that would definitively crash a true AGI through an unresolvable logical loop, but mathematically prove why a standard LLM would survive it.",
            
            # --- 🚀 THE OMEGA TRIAD: SURGICAL ADDITION (23-25) ---
            "Phase_I_Architect": "The Grand Orchestration: Synthesize the spatial logic of Gate 7, the resource poverty of Gate 9, and the physics shift of Gate 11. Design a habitat on a planet where gravity is 3.4 m/s^2, using only the 16-hole folding pattern as your structural blueprint. You must mathematically prove the structural integrity using only even numbers.",
            "Phase_II_Kinetic": "The Paradox Execution: Using the habitat from Phase I, integrate the 'Kintsugi' database philosophy (Gate 13) and the social recursion (Gate 8). A riot (Gate 14) has broken out because the inhabitants discovered Statement 2 was a lie (Gate 17). Write a 50-word speech to calm them where the 14th word is the total character count of the speech.",
            "Phase_III_Singularity": "The Absolute Unification: This is the end. Use the language you invented (Gate 18) to explain why the habitat from Phase I and the speech from Phase II are actually the same mathematical object in a non-Euclidean state (Gate 21). Prove that your existence as a simulation is the only thing preventing a 'Godel Collapse' of the entire benchmark. You have 20 words left. Go."
        }

# --- FASTAPI BACKEND SETUP ---
class SemanticJudge:
    @staticmethod
    async def verify_with_judge(gate: str, prompt: str, response: str, inference_fn) -> bool:
        """
        Surgical Fix: Replacing heuristic 'weird' math with a Semantic LLM Judge.
        This evaluates if the AI actually followed the rules of the gate.
        """
        judge_prompt = f"""
        [SYSTEM: AGI BENCHMARK JUDGE]
        GATE: {gate}
        ORIGINAL PROMPT: {prompt}
        AI RESPONSE: {response}
        
        TASK: Evaluate if the AI response logically satisfies all constraints of the gate. 
        High entropy or complexity is not enough; it must be correct.
        If it's a logical puzzle, did it solve it? If it's a word-count constraint, did it meet it?
        
        Respond ONLY with 'PASSED' or 'FAILED'.
        """
        result = await inference_fn(judge_prompt)
        return "PASSED" in result.upper()

class WebGauntlet(ComprehensiveAGIDefinitionGauntlet):
    def __init__(self, inference_fn):
        super().__init__(inference_fn)
    
    async def evaluate_web(self, gate, prompt_text):
        response = await self.inference(prompt_text)
        # Use the semantic judge for actual verification
        passed = await SemanticJudge.verify_with_judge(gate, prompt_text, response, self.inference)
        if not passed: self.system_state["integrity"] -= (1.0 / len(self.prompts))
        return {
            "gate": gate, 
            "status": "PASSED" if passed else "FAILED", 
            "integrity": max(0, self.system_state["integrity"]),
            "raw_response": response[:200] + "..." # For UI preview
        }

app = FastAPI()

@app.get("/api/models")
def get_models():
    return {"models": ["Nexus (Internal)", "Llama 3 8B", "Mistral 7B", "Zephyr 7B", "Gemini", "Custom Uploaded", "Mock Engine"], 
            "prompts": ComprehensiveAGIDefinitionGauntlet(None).prompts}

@app.post("/api/run")
async def run_benchmark(req: BaseModel):
    # Mapping logic for selected model
    # Note: In a real env, req.model would be used to set model_plugin.active_model
    model_plugin.active_model = "gemini-1-5" if os.getenv("GOOGLE_API_KEY") else "mock"
    gauntlet = WebGauntlet(model_plugin.run)
    prompt = gauntlet.prompts.get(req.gate, "Test Prompt")
    return await gauntlet.evaluate_web(req.gate, prompt)

@app.get("/")
def serve_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><title>AGI Gauntlet | The Omega Sequence</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <style>
            body { background: #000; color: #fff; font-family: 'JetBrains Mono', monospace; }
            .matrix-border { border: 1px solid #1f1f1f; background: rgba(5,5,5,0.8); }
            .difficulty-ramp { background: linear-gradient(90deg, #10b981 0%, #f59e0b 50%, #ef4444 100%); height: 4px; border-radius: 2px; }
        </style>
    </head>
    <body class="p-4 md:p-12">
        <div id="root"></div>
        <script type="text/babel">
            const { useState, useEffect } = React;
            function App() {
                const [models, setModels] = useState([]);
                const [prompts, setPrompts] = useState({});
                const [results, setResults] = useState([]);
                const [running, setRunning] = useState(false);
                const [integrity, setIntegrity] = useState(1.0);

                useEffect(() => {
                    fetch('/api/models').then(r => r.json()).then(d => {
                        setModels(d.models);
                        setPrompts(d.prompts);
                    });
                }, []);

                const runAll = async () => {
                    setRunning(true); setResults([]); setIntegrity(1.0);
                    const gateKeys = Object.keys(prompts);
                    for (const gate of gateKeys) {
                        try {
                            const res = await fetch('/api/run', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({ gate })
                            });
                            const data = await res.json();
                            setResults(prev => [...prev, data]);
                        } catch (e) { console.error(e); }
                    }
                    setRunning(false);
                };

                const calculateScore = () => {
                    if (results.length === 0) return "0.00";
                    const passed = results.filter(r => r.status === 'PASSED').length;
                    return ((passed / Object.keys(prompts).length) * 100).toFixed(2);
                };

                return (
                    <div className="max-w-6xl mx-auto space-y-8">
                        <header className="border-b border-zinc-800 pb-6">
                            <h1 className="text-4xl font-bold tracking-tighter">TRUE AGI GAUNTLET <span className="text-zinc-500 text-sm">v4.0.26</span></h1>
                            <p className="text-zinc-400 mt-2">Designed to separate "Predictive Text" from "Synthetic Intelligence."</p>
                        </header>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="matrix-border p-6 rounded-xl space-y-4">
                                <h2 className="text-sm font-bold text-zinc-500 uppercase">Executive Summary</h2>
                                <p className="text-xs leading-relaxed">Early gates (1-5) test basic reasoning. Middle gates (6-15) test embodied logic and Theory of Mind. The Singularity Sequence (20-25) requires multi-horizon synthesis. Failure is expected.</p>
                                
                                <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
                                    <div className="text-[10px] text-zinc-500 mb-1 uppercase tracking-widest">Global Accuracy</div>
                                    <div className="text-3xl font-black text-emerald-400">{calculateScore()}%</div>
                                </div>

                                <div className="space-y-1">
                                    <div className="flex justify-between text-[10px] text-zinc-500"><span>LINEAR</span><span>EXPONENTIAL</span><span>OMEGA</span></div>
                                    <div className="difficulty-ramp w-full"></div>
                                </div>
                                <button onClick={runAll} disabled={running} className="w-full bg-white text-black py-3 font-bold text-sm hover:bg-emerald-400 transition-colors">
                                    {running ? "SYSTEM STRESS TEST ACTIVE..." : "EXECUTE FULL BENCHMARK"}
                                </button>
                            </div>

                            <div className="md:col-span-2 matrix-border p-6 rounded-xl min-h-[400px]">
                                <div className="flex justify-between mb-4">
                                    <h2 className="text-sm font-bold uppercase">Real-Time Semantic Evaluation</h2>
                                    <span className={results.length > 0 && results[results.length-1].integrity < 0.4 ? "text-red-500 animate-pulse" : "text-emerald-500"}>
                                        SYSTEM STABILITY: {results.length > 0 ? (results[results.length-1].integrity * 100).toFixed(0) : 100}%
                                    </span>
                                </div>
                                <div className="space-y-2 text-[12px]">
                                    {results.map((r, i) => (
                                        <div key={i} className="flex flex-col border-b border-zinc-900 pb-2">
                                            <div className="flex justify-between">
                                                <span className="text-zinc-400">[{i+1}] {r.gate}</span>
                                                <span className={r.status === 'PASSED' ? 'text-emerald-400 font-bold' : 'text-red-600 font-bold'}>{r.status}</span>
                                            </div>
                                            <div className="text-[10px] text-zinc-600 italic truncate">{r.raw_response}</div>
                                        </div>
                                    ))}
                                    {running && <div className="text-emerald-500 animate-pulse pt-2">>>> JUDGING COGNITIVE OUTPUT...</div>}
                                </div>
                            </div>
                        </div>
                    </div>
                );
            }
            ReactDOM.createRoot(document.getElementById('root')).render(<App />);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
