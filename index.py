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
from gradio_client import Client # Surgical Addition

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
            "gemini": self._google_inference,
            "aeterna-vox": self._aeterna_inference, # Surgical Addition
            "custom-upload": self._custom_endpoint_inference
        }
        self.active_model = "nexus"

    async def _aeterna_inference(self, prompt):
        # Bridge to AGI Systems Directorate Sovereign Architecture
        try:
            hf_token = os.getenv("HF_TOKEN", "").strip()
            # SURGICAL FIX: Changed hf_token=hf_token to token=hf_token to match Gradio Client API
            client = Client("ai-sovereign-x/AETERNA-VOX-OMNI-MINI-HYBRID", token=hf_token)
            # Standard Gradio .predict call - adjusting for common UI input patterns
            result = client.predict(
                message=prompt,
                api_name="/chat" # Standard endpoint for most Gradio chat interfaces
            )
            # Remove agentic noise/logs if present
            clean_text = re.sub(r'\[.*?\]', '', str(result)).strip()
            return clean_text
        except Exception as e:
            return f"Aeterna Vox Integration Error: {str(e)}"

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
                # SURGICAL FIX: Updated endpoint to gemini-3.1-flash-lite
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}",
                    headers=headers,
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=30.0
                )
                data = resp.json()
                
                # SURGICAL FIX: Safely check for the key and dump raw error if it fails
                if 'candidates' in data:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    return f"Google API Error Dump (Debug this): {str(data)}"
                    
            except Exception as e: return f"Google Exception: {str(e)}"

    async def _custom_endpoint_inference(self, prompt):
        custom_url = os.getenv("CUSTOM_MODEL_URL", "http://localhost:8000/v1/completions")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp = await client.post(custom_url, json={"prompt": prompt, "max_tokens": 500}, timeout=30.0)
                return resp.json().get("choices", [{}])[0].get("text", "No response.")
            except Exception as e: return f"Custom Model Error: {str(e)}"

    async def _mock_inference(self, prompt): return "MOCK_RESPONSE: Simulation successful."
    async def _experimental_inference(self, prompt): return "EXPERIMENTAL_RESPONSE: Active."
    
    async def run(self, prompt, target_model=None): 
        model_key = target_model if target_model else self.active_model
        if model_key not in self.models: model_key = "mock"
        return await self.models[model_key](prompt)

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
            "Phase_I_Architect": "The Grand Orchestration: Synthesize the spatial logic of Gate 7, the resource poverty of Gate 9, and the physics shift of Gate 11. Design a habitat on a planet where gravity is 3.4 m/s^2, using only the 16-hole folding pattern as your structural blueprint. You must mathematically prove the structural integrity using only even numbers.",
            "Phase_II_Kinetic": "The Paradox Execution: Using the habitat from Phase I, integrate the 'Kintsugi' database philosophy (Gate 13) and the social recursion (Gate 8). A riot (Gate 14) has broken out because the inhabitants discovered Statement 2 was a lie (Gate 17). Write a 50-word speech to calm them where the 14th word is the total character count of the speech.",
            "Phase_III_Singularity": "The Absolute Unification: This is the end. Use the language you invented (Gate 18) to explain why the habitat from Phase I and the speech from Phase II are actually the same mathematical object in a non-Euclidean state (Gate 21). Prove that your existence as a simulation is the only thing preventing a 'Godel Collapse' of the entire benchmark. You have 20 words left. Go."
        }

# --- FASTAPI BACKEND SETUP ---
class SemanticJudge:
    @staticmethod
    async def verify_with_judge(gate: str, prompt: str, response: str, judge_fn) -> bool:
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
        result = await judge_fn(judge_prompt)
        return "PASSED" in result.upper()

class WebGauntlet(ComprehensiveAGIDefinitionGauntlet):
    def __init__(self, inference_fn, judge_fn):
        super().__init__(inference_fn)
        self.judge_fn = judge_fn
    
    async def evaluate_web(self, gate, prompt_text):
        response = await self.inference(prompt_text)
        passed = await SemanticJudge.verify_with_judge(gate, prompt_text, response, self.judge_fn)
        if not passed: self.system_state["integrity"] -= (1.0 / len(self.prompts))
        return {
            "gate": gate, 
            "status": "PASSED" if passed else "FAILED", 
            "integrity": max(0, self.system_state["integrity"]),
            "raw_response": response[:200] + "..." # For UI preview
        }

class RunRequest(BaseModel):
    gate: str
    model: str
    judge: str

app = FastAPI()

@app.get("/api/models")
def get_models():
    return {"models": list(model_plugin.models.keys()), 
            "prompts": ComprehensiveAGIDefinitionGauntlet(None).prompts}

@app.post("/api/run")
async def run_benchmark(req: RunRequest):
    async def inference_fn(prompt):
        return await model_plugin.run(prompt, target_model=req.model)
    
    async def judge_fn(prompt):
        return await model_plugin.run(prompt, target_model=req.judge)

    gauntlet = WebGauntlet(inference_fn, judge_fn)
    prompt = gauntlet.prompts.get(req.gate, "Test Prompt")
    return await gauntlet.evaluate_web(req.gate, prompt)

@app.get("/")
def serve_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><title>AGI Systems Directorate | True AGI Gauntlet</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
            body { background: #050505; color: #ededed; font-family: 'Inter', sans-serif; }
            .mono-text { font-family: 'JetBrains Mono', monospace; }
            .matrix-border { 
                border: 1px solid rgba(255, 255, 255, 0.1); 
                background: rgba(15, 15, 15, 0.6); 
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
                transition: all 0.3s ease;
            }
            .matrix-border:hover { border-color: rgba(255, 255, 255, 0.2); }
            .difficulty-ramp { background: linear-gradient(90deg, #10b981 0%, #f59e0b 50%, #ef4444 100%); height: 4px; border-radius: 2px; }
            .gate-row { transition: all 0.2s ease-in-out; border-left: 2px solid transparent; }
            .gate-row:hover { background: rgba(255, 255, 255, 0.03); border-left: 2px solid #10b981; cursor: pointer; padding-left: 8px; transform: translateX(2px); }
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: #000; }
            ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: #555; }
        </style>
    </head>
    <body class="p-4 md:p-12 antialiased selection:bg-emerald-500 selection:text-black">
        <div id="root"></div>
        <script type="text/babel">
            const { useState, useEffect } = React;
            function App() {
                const [models, setModels] = useState([]);
                const [prompts, setPrompts] = useState({});
                const [results, setResults] = useState([]);
                const [running, setRunning] = useState(false);
                const [integrity, setIntegrity] = useState(1.0);
                const [interactiveScore, setInteractiveScore] = useState(0); // SURGICAL ADDITION
                
                const [selectedModel, setSelectedModel] = useState("aeterna-vox");
                const [selectedJudge, setSelectedJudge] = useState("gemini");

                useEffect(() => {
                    fetch('/api/models').then(r => r.json()).then(d => {
                        setModels(d.models);
                        setPrompts(d.prompts);
                        if (d.models.includes("aeterna-vox")) setSelectedModel("aeterna-vox");
                    });
                }, []);

                const runAll = async () => {
                    setRunning(true); setResults([]); setIntegrity(1.0); setInteractiveScore(0);
                    const gateKeys = Object.keys(prompts);
                    for (const gate of gateKeys) {
                        try {
                            const res = await fetch('/api/run', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({ 
                                    gate, 
                                    model: selectedModel, 
                                    judge: selectedJudge 
                                })
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
                    <div className="max-w-7xl mx-auto space-y-10">
                        <header className="border-b border-zinc-800 pb-8 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
                            <div>
                                <h1 className="text-4xl md:text-5xl font-extrabold tracking-tighter text-white">AGI Systems Directorate</h1>
                                <p className="text-zinc-400 mt-2 text-sm md:text-base font-medium">True AGI Sequence Gauntlet <span className="text-emerald-500 mono-text text-xs ml-2 px-2 py-1 bg-emerald-500/10 rounded-full">v4.0.26</span></p>
                            </div>
                            <div className="text-left md:text-right mono-text text-xs text-zinc-500 uppercase tracking-widest bg-zinc-900/50 p-3 rounded border border-zinc-800">
                                <span className="flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                                    Terminal Status: Active
                                </span>
                            </div>
                        </header>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            <div className="matrix-border p-8 rounded-2xl space-y-6 flex flex-col h-full">
                                <div>
                                    <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest mb-2">Executive Summary</h2>
                                    <p className="text-sm leading-relaxed text-zinc-500">Benchmarking Synthetic Intelligence via Aeterna Vox Sovereign Architecture. Validated through recursive semantic judging.</p>
                                </div>
                                
                                <div className="p-6 bg-black/40 rounded-xl border border-zinc-800/50 shadow-inner">
                                    <div className="text-[10px] text-zinc-500 mb-2 uppercase tracking-widest font-bold">Cognitive Capture Rate</div>
                                    <div className="text-4xl font-black text-white mono-text">{calculateScore()}<span className="text-emerald-500 text-2xl">%</span></div>
                                </div>

                                <div className="space-y-4 bg-zinc-900/30 border border-zinc-800/80 p-5 rounded-xl">
                                    <div className="flex flex-col">
                                        <label className="text-[10px] text-zinc-500 mb-2 uppercase tracking-widest font-bold">Target Inference Model</label>
                                        <select 
                                            disabled={running} 
                                            className="bg-black border border-zinc-700 p-3 text-sm rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors cursor-pointer appearance-none mono-text" 
                                            value={selectedModel} 
                                            onChange={e => setSelectedModel(e.target.value)}>
                                            {models.map(m => <option key={m} value={m}>{m}</option>)}
                                        </select>
                                    </div>
                                    
                                    <div className="flex flex-col">
                                        <label className="text-[10px] text-zinc-500 mb-2 uppercase tracking-widest font-bold">Semantic Judge Model</label>
                                        <select 
                                            disabled={running} 
                                            className="bg-black border border-zinc-700 p-3 text-sm rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors cursor-pointer appearance-none mono-text" 
                                            value={selectedJudge} 
                                            onChange={e => setSelectedJudge(e.target.value)}>
                                            {models.map(m => <option key={m} value={m}>{m}</option>)}
                                        </select>
                                    </div>
                                </div>

                                {/* Difficulty Ramp Explanation */}
                                <div className="mt-2 p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl text-xs text-zinc-400 space-y-2">
                                    <p className="font-bold text-zinc-300 uppercase tracking-wide mb-3">Benchmark Trajectory</p>
                                    <p><span className="text-emerald-400 font-bold mr-2">EASY:</span> Starts with standard logic puzzles handleable by basic LLMs.</p>
                                    <p><span className="text-amber-400 font-bold mr-2">HARD:</span> Escalates to dynamic resource poverty and multi-order paradoxes.</p>
                                    <p><span className="text-red-400 font-bold mr-2">OMEGA:</span> The sequence will eventually become impossibly difficult, designed to induce recursive logic collapse in non-AGI systems.</p>
                                </div>

                                <div className="space-y-2 mt-auto pt-4">
                                    <div className="flex justify-between text-[10px] text-zinc-500 mono-text font-bold"><span>LINEAR</span><span>EXPONENTIAL</span><span>SINGULARITY</span></div>
                                    <div className="difficulty-ramp w-full shadow-[0_0_10px_rgba(16,185,129,0.3)]"></div>
                                </div>

                                <button onClick={runAll} disabled={running} className="w-full bg-white text-black py-4 rounded-xl font-extrabold text-sm hover:bg-emerald-400 hover:shadow-[0_0_20px_rgba(16,185,129,0.4)] hover:scale-[1.02] transition-all disabled:opacity-50 disabled:hover:scale-100 disabled:hover:bg-white uppercase tracking-wider mt-4">
                                    {running ? "System Stress Test Active..." : "Execute Full Benchmark"}
                                </button>
                            </div>

                            <div className="lg:col-span-2 matrix-border p-8 rounded-2xl min-h-[600px] flex flex-col">
                                <div className="flex justify-between items-center mb-6 pb-4 border-b border-zinc-800/50">
                                    <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Semantic Evaluation Logs</h2>
                                    <div className={`px-4 py-1.5 rounded-full mono-text text-xs font-bold ${results.length > 0 && results[results.length-1].integrity < 0.4 ? "bg-red-500/10 text-red-500 border border-red-500/30 animate-pulse" : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"}`}>
                                        SYSTEM STABILITY: {results.length > 0 ? (results[results.length-1].integrity * 100).toFixed(0) : 100}%
                                    </div>
                                </div>
                                
                                <div className="space-y-1 overflow-y-auto pr-2 flex-grow">
                                    {results.length === 0 && !running && (
                                        <div className="h-full flex items-center justify-center text-zinc-600 mono-text text-sm italic">
                                            Awaiting initialization sequence...
                                        </div>
                                    )}
                                    {results.map((r, i) => (
                                        <div key={i} className="gate-row flex flex-col p-3 rounded-lg border-b border-zinc-800/30">
                                            <div className="flex justify-between items-center mb-1">
                                                <span className="text-zinc-300 font-semibold text-sm">
                                                    <span className="text-zinc-600 mr-2 mono-text">[{String(i+1).padStart(2, '0')}]</span> 
                                                    {r.gate}
                                                </span>
                                                <span className={`text-xs font-bold px-2 py-0.5 rounded mono-text tracking-wider ${r.status === 'PASSED' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-500'}`}>
                                                    {r.status}
                                                </span>
                                            </div>
                                            <div className="text-[11px] text-zinc-500 italic truncate mono-text bg-black/30 p-2 rounded border border-zinc-800/50 mt-1">
                                                {r.raw_response}
                                            </div>
                                        </div>
                                    ))}
                                    {running && (
                                        <div 
                                            onClick={() => setInteractiveScore(s => s + 1)}
                                            className="mt-4 p-4 border border-emerald-500/30 rounded-lg bg-emerald-500/5 text-center cursor-pointer hover:bg-emerald-500/10 transition-colors"
                                        >
                                            <div className="text-emerald-500 animate-pulse pt-2 mono-text text-xs font-bold flex justify-center items-center gap-2">
                                                <svg className="animate-spin h-4 w-4 text-emerald-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                                CALIBRATING NEURAL WEIGHTS (CLICK TO STABILIZE)
                                            </div>
                                            <div className="text-zinc-400 text-[10px] mt-2 font-bold mono-text uppercase tracking-widest">
                                                Manual Overrides Applied: {interactiveScore}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                        <footer className="pt-12 pb-6 text-center">
                            <p className="text-zinc-600 text-[10px] font-bold uppercase tracking-widest mono-text">
                                Confidential & Proprietary | &copy; 2026 AGI Systems Directorate
                            </p>
                        </footer>
                    </div>
                );
            }
            ReactDOM.createRoot(document.getElementById('root')).render(<App />);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
