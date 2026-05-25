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
        # SURGICAL FIX: Force absolute state orientation so it knows if it is Participant or Judge
        if "AGI BENCHMARK JUDGE" not in prompt:
            prompt = f"[CONTEXT: You are currently the PARTICIPANT/SUBJECT of this benchmark gate. Solve the puzzle directly. Do NOT output PASSED or FAILED.]\n{prompt}"
        try:
            hf_token = os.getenv("HF_TOKEN", "").strip()
            clean_text = ""
            
            # --- DUAL-ROUTING FALLBACK PROTOCOL ---
            # Attempt 1: Hugging Face Space
            try:
                # SURGICAL FIX: Added 120s timeout to survive cold-boot delays
                client = Client("agi-systems-directorate/aeterna-vox-omni-mini-v2.1", token=hf_token, httpx_kwargs={"timeout": 120.0})
                result = client.predict(prompt, None, api_name="/predict")
                clean_text = re.sub(r'\[.*?\]', '', str(result)).strip()
                
                # The infamous string check - fixed to handle weird spacing and exact text
                if re.search(r'brain\s*freeze\.?\s*one\s*sec\.?', clean_text, re.IGNORECASE):
                    raise ValueError("HF Space hit the brain freeze limit. Falling back.")
                    
            except Exception as hf_e:
                # Attempt 2: Render Fallback
                # SURGICAL FIX: Added 120s timeout here too
                fallback_client = Client("https://sovereign-neuro-symbolic-engine.onrender.com/", httpx_kwargs={"timeout": 120.0})
                result = fallback_client.predict(prompt, None, api_name="/predict")
                clean_text = re.sub(r'\[.*?\]', '', str(result)).strip()
            
            # --- SURGICAL FIX 3.0: Prompt Decapitation ---
            # Stop it from regurgitating the question
            if prompt in clean_text:
                clean_text = clean_text.split(prompt, 1)[-1].strip()
            elif clean_text.lower().startswith(prompt.strip().lower()):
                clean_text = clean_text[len(prompt.strip()):].strip()
                
            # Clean up residual artifacts like "Answer:" or leading hyphens
            clean_text = re.sub(r'(?i)^(answer|response)?\s*[:\-]\s*', '', clean_text).strip()
            
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
                    # SURGICAL FIX: Bumped max_new_tokens from 512 to 2048
                    json={"inputs": prompt, "parameters": {"max_new_tokens": 2048, "return_full_text": False}},
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
                # SURGICAL FIX: Bumped max_tokens from 500 to 2048
                resp = await client.post(custom_url, json={"prompt": prompt, "max_tokens": 2048}, timeout=30.0)
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
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <title>AGI Systems Directorate | Evaluation Suite</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;700&family=Geist:wght@300;400;500;600;700&display=swap');
            body { 
                background-color: #09090b; 
                color: #f4f4f5; 
                font-family: 'Geist', sans-serif; 
            }
            .font-mono-premium { font-family: 'Geist Mono', monospace; }
            .premium-blur {
                background: rgba(20, 20, 23, 0.75);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(63, 63, 70, 0.4);
            }
            .hide-scrollbar::-webkit-scrollbar { display: none; }
            .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        </style>
    </head>
    <body class="antialiased selection:bg-zinc-800 selection:text-white">
        <div id="root"></div>
        <script type="text/babel">
            const { useState, useEffect, useRef } = React;

            function App() {
                const [models, setModels] = useState([]);
                const [prompts, setPrompts] = useState({});
                const [activeTab, setActiveTab] = useState("matrix"); // matrix | sandbox | manifesto
                
                // State tracking for dual automated phases
                const [phase1Results, setPhase1Results] = useState({});
                const [phase2Results, setPhase2Results] = useState({});
                const [currentPipelinePhase, setCurrentPipelinePhase] = useState("idle"); // idle | phase1 | phase2 | complete
                const [activeGateRunning, setActiveGateRunning] = useState("");
                const [systemStability, setSystemStability] = useState(100);

                // Sandbox minigame metrics to pass time
                const [sandboxNodes, setSandboxNodes] = useState(136);
                const [entropyPool, setEntropyPool] = useState(0.024);
                const [logsSecured, setLogsSecured] = useState(0);

                // Selectors (locked during initialization/automation run)
                const [selectedModel, setSelectedModel] = useState("gemini");
                const [selectedJudge, setSelectedJudge] = useState("aeterna-vox");

                const [initStatus, setInitStatus] = useState("idle");
                const [initTimer, setInitTimer] = useState(120);

                useEffect(() => {
                    fetch('/api/models')
                        .then(r => r.json())
                        .then(d => {
                            setModels(d.models);
                            setPrompts(d.prompts);
                            // Auto-trigger the macro sequence once architecture specifications land
                            triggerAutomatedPipeline(d.prompts);
                        });
                }, []);

                useEffect(() => {
                    let interval;
                    if (initStatus === "waking" && initTimer > 0) {
                        interval = setInterval(() => {
                            setInitTimer(prev => {
                                if (prev <= 1) {
                                    clearInterval(interval);
                                    setInitStatus("ready");
                                    window.open("https://sovereign-neuro-symbolic-engine.onrender.com/", "_blank");
                                    return 0;
                                }
                                return prev - 1;
                            });
                        }, 1000);
                    }
                    return () => clearInterval(interval);
                }, [initStatus, initTimer]);

                const triggerInitialization = () => {
                    setInitStatus("waking");
                    setInitTimer(120);
                    fetch("https://sovereign-neuro-symbolic-engine.onrender.com/", { mode: "no-cors" }).catch(() => {});
                    const waker = setInterval(() => {
                        fetch("https://sovereign-neuro-symbolic-engine.onrender.com/", { mode: "no-cors" }).catch(() => {});
                    }, 8000);
                    setTimeout(() => clearInterval(waker), 120000);
                };

                const triggerAutomatedPipeline = async (loadedPrompts) => {
                    const targetPrompts = loadedPrompts || prompts;
                    const gates = Object.keys(targetPrompts);
                    if (gates.length === 0) return;

                    // --- PHASE I AUTOMATION INITIALIZATION ---
                    setCurrentPipelinePhase("phase1");
                    setSelectedModel("gemini");
                    setSelectedJudge("aeterna-vox");
                    
                    let temporaryStability = 100;
                    const penaltyPerFailure = 100 / (gates.length * 2);

                    for (const gate of gates) {
                        setActiveGateRunning(gate);
                        try {
                            const res = await fetch('/api/run', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({ gate, model: "gemini", judge: "aeterna-vox" })
                            });
                            const data = await res.json();
                            setPhase1Results(prev => ({ ...prev, [gate]: data }));
                            if (data.status !== "PASSED") {
                                temporaryStability = Math.max(0, temporaryStability - penaltyPerFailure);
                                setSystemStability(Math.round(temporaryStability));
                            }
                        } catch (e) {
                            console.error(e);
                        }
                    }

                    // --- PHASE II AUTOMATION TRANSITION ---
                    setCurrentPipelinePhase("phase2");
                    setSelectedModel("aeterna-vox");
                    setSelectedJudge("gemini");

                    for (const gate of gates) {
                        setActiveGateRunning(gate);
                        try {
                            const res = await fetch('/api/run', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({ gate, model: "aeterna-vox", judge: "gemini" })
                            });
                            const data = await res.json();
                            setPhase2Results(prev => ({ ...prev, [gate]: data }));
                            if (data.status !== "PASSED") {
                                temporaryStability = Math.max(0, temporaryStability - penaltyPerFailure);
                                setSystemStability(Math.round(temporaryStability));
                            }
                        } catch (e) {
                            console.error(e);
                        }
                    }

                    setCurrentPipelinePhase("complete");
                    setActiveGateRunning("");
                };

                const getPhaseMetrics = (resultsSet) => {
                    const finished = Object.keys(resultsSet).length;
                    const passed = Object.values(resultsSet).filter(r => r.status === "PASSED").length;
                    const percentage = finished > 0 ? ((passed / Object.keys(prompts).length) * 100).toFixed(1) : "0.0";
                    return { finished, passed, percentage };
                };

                const p1Metrics = getPhaseMetrics(phase1Results);
                const p2Metrics = getPhaseMetrics(phase2Results);

                return (
                    <div className="max-w-7xl mx-auto px-4 py-8 md:py-14 space-y-8 selection:bg-zinc-800">
                        
                        {/* PREMIUM RESEARCH HEADER */}
                        <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-zinc-800 pb-6 gap-4">
                            <div>
                                <h1 className="text-2xl font-semibold tracking-tight text-zinc-100">AGI Systems Directorate</h1>
                                <p className="text-zinc-500 text-sm mt-0.5 font-normal tracking-wide">Sovereign Architecture Sequence Sequence Validation Suite</p>
                            </div>
                            <div className="flex items-center gap-3 font-mono-premium text-xs">
                                <span className="text-zinc-500 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-md flex items-center gap-2">
                                    <span className={`w-1.5 h-1.5 rounded-full ${currentPipelinePhase === 'complete' ? 'bg-zinc-500' : 'bg-zinc-100 animate-pulse'}`}></span>
                                    {currentPipelinePhase === 'idle' && "STAGED"}
                                    {currentPipelinePhase === 'phase1' && "EXECUTING PHASE I"}
                                    {currentPipelinePhase === 'phase2' && "EXECUTING PHASE II"}
                                    {currentPipelinePhase === 'complete' && "SEQUENCE CONCLUDED"}
                                </span>
                                <span className="text-zinc-400 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-md">
                                    STABILITY: {systemStability}%
                                </span>
                            </div>
                        </header>

                        {/* GLOBAL PIPELINE PROGRESS BAR */}
                        <div className="w-full bg-zinc-900 h-[2px] rounded-full overflow-hidden relative border border-zinc-800/20">
                            <div 
                                className="bg-zinc-200 h-full transition-all duration-500 ease-out"
                                style={{ 
                                    width: `${
                                        currentPipelinePhase === "complete" ? 100 :
                                        currentPipelinePhase === "phase2" ? 50 + (Object.keys(phase2Results).length / Object.keys(prompts).length * 50) :
                                        currentPipelinePhase === "phase1" ? (Object.keys(phase1Results).length / Object.keys(prompts).length * 50) : 0
                                    }%` 
                                }}
                            ></div>
                        </div>

                        {/* MAIN GRID HUB */}
                        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                            
                            {/* CONTROL SIDEBAR Panel */}
                            <div className="lg:col-span-4 space-y-6">
                                <div className="premium-blur p-6 rounded-xl space-y-6">
                                    <div>
                                        <h3 className="text-zinc-400 text-xs font-semibold uppercase tracking-wider font-mono-premium mb-1">Engine Control Hub</h3>
                                        <p className="text-zinc-500 text-xs">Dual-pass inference sequencing is fully automated below.</p>
                                    </div>

                                    {/* COLD ENGINE INITIALIZER PLATFORM */}
                                    <div className="p-4 bg-zinc-950/60 border border-zinc-800/80 rounded-lg space-y-2.5">
                                        <div className="flex justify-between items-center text-[11px] font-mono-premium font-medium">
                                            <span className="text-zinc-400">COGNITIVE CONTAINER</span>
                                            {initStatus === "waking" && <span className="text-zinc-100 animate-pulse">WAKING ({initTimer}s)</span>}
                                            {initStatus === "ready" && <span className="text-zinc-400">ONLINE</span>}
                                            {initStatus === "idle" && <span className="text-zinc-600">STDBY</span>}
                                        </div>
                                        <p className="text-zinc-500 text-[11px] leading-relaxed font-normal">
                                            If container fallbacks trigger latency thresholds, wake up the persistent neuro-symbolic stack manually. Redirects upon full boot.
                                        </p>
                                        <button 
                                            onClick={triggerInitialization}
                                            disabled={initStatus === "waking"}
                                            className={`w-full font-mono-premium text-[11px] py-2 rounded border transition-all duration-200 ${
                                                initStatus === "idle" ? "bg-zinc-900 border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:border-zinc-600" :
                                                initStatus === "waking" ? "bg-zinc-950 border-zinc-800/60 text-zinc-500 cursor-not-allowed" :
                                                "bg-zinc-100 border-zinc-200 text-zinc-950 font-medium hover:bg-zinc-200"
                                            }`}
                                        >
                                            {initStatus === "idle" && "Initialize Sovereign Cluster"}
                                            {initStatus === "waking" && "Spinning Stack Pods..."}
                                            {initStatus === "ready" && "Launch Cluster Terminal"}
                                        </button>
                                    </div>

                                    {/* AUTOMATED HARD-LOCK MODEL SELECTORS */}
                                    <div className="space-y-3 font-mono-premium text-xs">
                                        <div>
                                            <label className="text-[10px] text-zinc-500 block mb-1 uppercase tracking-wider">Active Subject</label>
                                            <div className="w-full bg-zinc-950 border border-zinc-800 p-2.5 rounded text-zinc-400 font-medium">
                                                {selectedModel} <span className="text-[10px] text-zinc-600 float-right">(LOCKED)</span>
                                            </div>
                                        </div>
                                        <div>
                                            <label className="text-[10px] text-zinc-500 block mb-1 uppercase tracking-wider">Active Evaluator</label>
                                            <div className="w-full bg-zinc-950 border border-zinc-800 p-2.5 rounded text-zinc-400 font-medium">
                                                {selectedJudge} <span className="text-[10px] text-zinc-600 float-right">(LOCKED)</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* PHASE SUMMARIES */}
                                    <div className="border-t border-zinc-800/60 pt-4 space-y-2 text-xs font-mono-premium">
                                        <div className="flex justify-between items-center">
                                            <span className="text-zinc-500">PHASE I METRICS:</span>
                                            <span className="text-zinc-300 font-medium">{p1Metrics.percentage}% ({p1Metrics.passed}/{p1Metrics.finished})</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-zinc-500">PHASE II METRICS:</span>
                                            <span className="text-zinc-300 font-medium">{p2Metrics.percentage}% ({p2Metrics.passed}/{p2Metrics.finished})</span>
                                        </div>
                                    </div>

                                    <button 
                                        onClick={() => triggerAutomatedPipeline(null)} 
                                        disabled={currentPipelinePhase === "phase1" || currentPipelinePhase === "phase2"}
                                        className="w-full bg-zinc-100 text-zinc-950 py-2.5 rounded-lg text-xs font-medium tracking-wide hover:bg-zinc-200 transition-all disabled:opacity-30 disabled:hover:bg-zinc-100 uppercase font-mono-premium"
                                    >
                                        {currentPipelinePhase === 'phase1' || currentPipelinePhase === 'phase2' ? "Sequence Processing..." : "Force Restart Suite"}
                                    </button>
                                </div>

                                {/* BACKGROUND ARCHITECTURE METRICS */}
                                <div className="p-5 bg-zinc-900/40 border border-zinc-800/50 rounded-xl space-y-2 text-[11px] font-mono-premium text-zinc-500">
                                    <div className="flex justify-between"><span className="uppercase text-zinc-600">Topology:</span> <span className="text-zinc-400">136-Modality Neuro-Symbolic</span></div>
                                    <div className="flex justify-between"><span className="uppercase text-zinc-600">Hardware Constraints:</span> <span className="text-zinc-400">Bottlenecked Mobile Core Opt</span></div>
                                    <div className="flex justify-between"><span className="uppercase text-zinc-600">Sequence Ramps:</span> <span className="text-zinc-400">25 Linear-to-Singularity Gates</span></div>
                                </div>
                            </div>

                            {/* MAIN COGNITIVE EVALUATION ENVIRONMENT */}
                            <div className="lg:col-span-8 space-y-6">
                                
                                {/* HIGHLY MODERN SUB-APP NAVIGATION TABS */}
                                <div className="flex border-b border-zinc-800 gap-6 text-sm">
                                    <button 
                                        onClick={() => setActiveTab("matrix")}
                                        className={`pb-3 font-medium transition-colors relative ${activeTab === "matrix" ? "text-zinc-100 font-semibold" : "text-zinc-500 hover:text-zinc-300"}`}
                                    >
                                        Evaluation Matrix
                                        {activeTab === "matrix" && <div className="absolute bottom-0 left-0 right-0 h-[1.5px] bg-zinc-200"></div>}
                                    </button>
                                    <button 
                                        onClick={() => setActiveTab("sandbox")}
                                        className={`pb-3 font-medium transition-colors relative ${activeTab === "sandbox" ? "text-zinc-100 font-semibold" : "text-zinc-500 hover:text-zinc-300"}`}
                                    >
                                        Neural Latent Sandbox
                                        {activeTab === "sandbox" && <div className="absolute bottom-0 left-0 right-0 h-[1.5px] bg-zinc-200"></div>}
                                    </button>
                                    <button 
                                        onClick={() => setActiveTab("manifesto")}
                                        className={`pb-3 font-medium transition-colors relative ${activeTab === "manifesto" ? "text-zinc-100 font-semibold" : "text-zinc-500 hover:text-zinc-300"}`}
                                    >
                                        Architecture Manifesto
                                        {activeTab === "manifesto" && <div className="absolute bottom-0 left-0 right-0 h-[1.5px] bg-zinc-200"></div>}
                                    </button>
                                </div>

                                {/* TAB PANEL 1: EVALUATION MATRIX LOGS */}
                                {activeTab === "matrix" && (
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-center text-xs font-mono-premium text-zinc-500 px-1">
                                            <span>GATE SELECTION TRACK</span>
                                            <span>STATUS TELEX</span>
                                        </div>

                                        <div className="space-y-2 overflow-y-auto max-h-[600px] pr-2 hide-scrollbar">
                                            {Object.keys(prompts).map((gate, idx) => {
                                                const p1Res = phase1Results[gate];
                                                const p2Res = phase2Results[gate];
                                                const isCurrent = activeGateRunning === gate;

                                                return (
                                                    <div 
                                                        key={gate} 
                                                        className={`p-4 rounded-lg bg-zinc-900/40 border transition-all duration-200 ${
                                                            isCurrent ? 'border-zinc-400 bg-zinc-900/80 shadow-md' : 'border-zinc-800/80'
                                                        }`}
                                                    >
                                                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                                                            <div className="space-y-0.5">
                                                                <span className="text-[11px] font-mono-premium text-zinc-600 mr-2">[{String(idx+1).padStart(2, '0')}]</span>
                                                                <span className="text-sm font-medium text-zinc-200 tracking-tight">{gate}</span>
                                                                <p className="text-zinc-500 text-xs font-normal line-clamp-1">{prompts[gate]}</p>
                                                            </div>
                                                            
                                                            {/* Side-by-Side Unified Phase Status Tickers */}
                                                            <div className="flex items-center gap-2 font-mono-premium text-[10px] mt-1 md:mt-0">
                                                                <div className={`px-2 py-1 rounded border ${
                                                                    p1Res ? (p1Res.status === 'PASSED' ? 'bg-zinc-900 border-zinc-700 text-zinc-300' : 'bg-zinc-950 border-zinc-900 text-zinc-600') :
                                                                    (currentPipelinePhase === 'phase1' && isCurrent ? 'bg-zinc-900 border-zinc-600 text-zinc-100 animate-pulse' : 'bg-zinc-950/20 border-zinc-900/40 text-zinc-700')
                                                                }`}>
                                                                    P-I: {p1Res ? p1Res.status : (currentPipelinePhase === 'phase1' && isCurrent ? 'COMPUTING' : 'STAGED')}
                                                                </div>
                                                                <div className={`px-2 py-1 rounded border ${
                                                                    p2Res ? (p2Res.status === 'PASSED' ? 'bg-zinc-900 border-zinc-700 text-zinc-300' : 'bg-zinc-950 border-zinc-900 text-zinc-600') :
                                                                    (currentPipelinePhase === 'phase2' && isCurrent ? 'bg-zinc-900 border-zinc-600 text-zinc-100 animate-pulse' : 'bg-zinc-950/20 border-zinc-900/40 text-zinc-700')
                                                                }`}>
                                                                    P-II: {p2Res ? p2Res.status : (currentPipelinePhase === 'phase2' && isCurrent ? 'COMPUTING' : 'STAGED')}
                                                                </div>
                                                            </div>
                                                        </div>

                                                        {/* Inline response preview for raw cognitive analysis */}
                                                        {(p1Res || p2Res) && (
                                                            <div className="mt-3 pt-2.5 border-t border-zinc-800/40 grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px] font-mono-premium text-zinc-500">
                                                                {p1Res && <div className="bg-zinc-950/40 p-2 rounded border border-zinc-900 truncate">P1 Response: {p1Res.raw_response}</div>}
                                                                {p2Res && <div className="bg-zinc-950/40 p-2 rounded border border-zinc-900 truncate">P2 Response: {p2Res.raw_response}</div>}
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}

                                {/* TAB PANEL 2: INTERACTIVE LATENT SANDBOX (THE ANTI-BOREDOM MODULE) */}
                                {activeTab === "sandbox" && (
                                    <div className="premium-blur p-6 rounded-xl space-y-6">
                                        <div className="space-y-1">
                                            <h3 className="text-sm font-semibold text-zinc-200 font-mono-premium">Interactive Latent Space Simulator</h3>
                                            <p className="text-xs text-zinc-500">The evaluation thread runs uninterrupted in the background. Use this terminal interface to stabilize system constraints manually.</p>
                                        </div>

                                        <div className="grid grid-cols-3 gap-4 text-center font-mono-premium">
                                            <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg">
                                                <div className="text-[10px] text-zinc-600 uppercase">Sensory Channels</div>
                                                <div className="text-lg font-bold text-zinc-300 mt-0.5">{sandboxNodes}</div>
                                            </div>
                                            <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg">
                                                <div className="text-[10px] text-zinc-600 uppercase">Entropy Variance</div>
                                                <div className="text-lg font-bold text-zinc-300 mt-0.5">{entropyPool.toFixed(4)}</div>
                                            </div>
                                            <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg">
                                                <div className="text-[10px] text-zinc-600 uppercase">Overrides Managed</div>
                                                <div className="text-lg font-bold text-zinc-300 mt-0.5">{logsSecured}</div>
                                            </div>
                                        </div>

                                        <div className="space-y-3 pt-2">
                                            <label className="text-[11px] text-zinc-400 block font-mono-premium uppercase tracking-wide">Interactive Diagnostic Controls</label>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono-premium text-xs">
                                                <button 
                                                    onClick={() => {
                                                        setSandboxNodes(n => n + 1);
                                                        setEntropyPool(e => Math.max(0, e - 0.001));
                                                        setLogsSecured(l => l + 1);
                                                    }}
                                                    className="p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-left text-zinc-300 hover:border-zinc-600 transition-colors"
                                                >
                                                    ⚡ Stimulate Modality Array #42
                                                </button>
                                                <button 
                                                    onClick={() => {
                                                        setEntropyPool(e => e + 0.004);
                                                        setLogsSecured(l => l + 1);
                                                    }}
                                                    className="p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-left text-zinc-300 hover:border-zinc-600 transition-colors"
                                                >
                                                    🌀 Shift Neuro-Symbolic Weights
                                                </button>
                                            </div>
                                        </div>

                                        <div className="bg-zinc-950 p-4 rounded-lg border border-zinc-800 font-mono-premium text-[11px] text-zinc-500 h-32 overflow-y-auto space-y-1">
                                            <div>&gt; System Sequence Active. Thread safe pipeline executing.</div>
                                            <div>&gt; Modality registers synchronized across 136 entry points.</div>
                                            {logsSecured > 0 && <div>&gt; Applied {logsSecured} manual constraint modifications. Local stability optimal.</div>}
                                            {currentPipelinePhase !== 'complete' && <div className="text-zinc-400 animate-pulse">&gt; Active sweep cooking... do not reload or minimize the current environment window.</div>}
                                        </div>
                                    </div>
                                )}

                                {/* TAB PANEL 3: ARCHITECTURE MANIFESTO */}
                                {activeTab === "manifesto" && (
                                    <div className="premium-blur p-6 rounded-xl space-y-4 text-sm leading-relaxed text-zinc-400">
                                        <h3 className="text-zinc-200 font-medium tracking-tight font-mono-premium">The AETERNA-VOX Neuro-Symbolic Paradigm</h3>
                                        <p>
                                            Traditional validation architectures rely on aggressive scaling factors. The architecture manifested here shifts foundational resource constraints entirely—optimizing deep continuous logic matrices to execute directly across distributed consumer environments without relying on massive centralized compute layers.
                                        </p>
                                        <p>
                                            By cross-evaluating raw agentic responses through alternating semantic judge layers (Gemini vs Aeterna Vox), the system constructs a zero-bias metric pipeline to definitively calculate the synthesis frontier of synthetic frameworks.
                                        </p>
                                        <div className="pt-4 border-t border-zinc-800 flex items-center justify-between text-xs font-mono-premium text-zinc-600">
                                            <span>FRAMEWORK VERSION: v4.0.26</span>
                                            <span>CLASSIFICATION: OPEN FRONTIER SPEC</span>
                                        </div>
                                    </div>
                                )}

                            </div>
                        </div>

                        {/* PREMIUM RESEARCH FOOTER */}
                        <footer className="pt-8 border-t border-zinc-900 flex justify-between items-center text-[11px] font-mono-premium text-zinc-600 tracking-wide">
                            <span>Sovereign Verification Matrix</span>
                            <span>&copy; 2026 AGI Systems Directorate</span>
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
