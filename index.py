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
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>AGI Systems Directorate | Evaluation</title>
        
        <!-- THE ALL-SEEING DIAGNOSTIC PARASITE (CATCHES PROMISES & CONSOLE ERRORS) -->
        <script>
            (function() {
                function showErrorBox(msg) {
                    var errBox = document.getElementById('ui-error-gatekeeper');
                    if (!errBox) {
                        errBox = document.createElement('div');
                        errBox.id = 'ui-error-gatekeeper';
                        errBox.style = 'position:fixed; top:10px; left:10px; right:10px; background:#1A0505; border:1px solid #FF4444; color:#FF8888; padding:12px; border-radius:8px; z-index:99999; font-family:monospace; font-size:11px; white-space:pre-wrap; max-height:80vh; overflow-y:auto; word-break:break-all;';
                        
                        var appendToDOM = function() {
                            if (document.body) {
                                document.body.appendChild(errBox);
                            } else {
                                document.documentElement.appendChild(errBox);
                            }
                        };
                        
                        if (document.readyState === 'loading') {
                            document.addEventListener('DOMContentLoaded', appendToDOM);
                        } else {
                            appendToDOM();
                        }
                    }
                    errBox.innerText += "\\n\\n--- NEW DIAGNOSTIC ---\\n" + msg;
                }

                // Catch standard errors
                window.addEventListener('error', function(e) {
                    showErrorBox("🚨 WINDOW ERROR: " + e.message + "\\nLine: " + e.lineno + " in " + e.filename);
                });

                // Catch background fetch/async failures that skip window.onerror
                window.addEventListener('unhandledrejection', function(e) {
                    showErrorBox("🚨 PROMISE REJECTION (Fetch/Async failed): " + (e.reason && e.reason.stack ? e.reason.stack : e.reason));
                });

                // Hijack console.error to catch Babel compilation silent failures
                var originalConsoleError = console.error;
                console.error = function() {
                    originalConsoleError.apply(console, arguments);
                    var argsArray = Array.prototype.slice.call(arguments);
                    var msg = argsArray.map(function(a) { 
                        return (typeof a === 'object') ? JSON.stringify(a) : String(a); 
                    }).join(' ');
                    showErrorBox("🚨 CONSOLE.ERROR: " + msg);
                };
            })();
        </script>

        <!-- SECURED CDN DEPLOYMENTS WITH CROSS-ORIGIN AND DEVELOPMENT BUILDS FOR READABLE ERRORS -->
        <script src="https://cdn.tailwindcss.com" crossorigin="anonymous"></script>
        <script src="https://unpkg.com/react@18.2.0/umd/react.development.js" crossorigin="anonymous"></script>
        <script src="https://unpkg.com/react-dom@18.2.0/umd/react-dom.development.js" crossorigin="anonymous"></script>
        <script src="https://unpkg.com/@babel/standalone@7.23.12/babel.min.js" crossorigin="anonymous"></script>
        
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Geist+Mono:wght@400;500&display=swap');
            body { background: #0A0A0A; color: #EDEDED; font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }
            .mono-text { font-family: 'Geist Mono', monospace; }
            .glass-panel { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; }
            .btn-primary { background: #EDEDED; color: #0A0A0A; transition: all 0.2s ease; }
            .btn-primary:hover:not(:disabled) { background: #FFFFFF; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(255,255,255,0.1); }
            .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
            
            /* Clean Scrollbar */
            ::-webkit-scrollbar { width: 4px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
            ::-webkit-scrollbar-thumb:hover { background: #555; }
            
            .boredom-node { transition: all 0.1s ease; cursor: crosshair; }
            .boredom-node:active { transform: scale(0.9); }
        </style>
    </head>
    <body class="p-4 md:p-12 selection:bg-white/20 selection:text-white min-h-screen flex flex-col">
        <div id="root" class="flex-grow flex flex-col"></div>
        <script type="text/babel">
            const { useState, useEffect, useRef } = React;
            function App() {
                const [prompts, setPrompts] = useState({});
                const [phase, setPhase] = useState("idle"); // idle, p1, p2, done
                const [resultsP1, setResultsP1] = useState([]);
                const [resultsP2, setResultsP2] = useState([]);
                
                // Initialization States
                const [initStatus, setInitStatus] = useState("idle"); 
                const [initTimer, setInitTimer] = useState(120);
                
                // Interactive Mini-game state
                const [boredomScore, setBoredomScore] = useState(0);

                useEffect(() => {
                    fetch('/api/models').then(r => r.json()).then(d => {
                        setPrompts(d.prompts);
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
                    const wakeUpPinger = setInterval(() => {
                        fetch("https://sovereign-neuro-symbolic-engine.onrender.com/", { mode: "no-cors" }).catch(() => {});
                    }, 8000);
                    setTimeout(() => clearInterval(wakeUpPinger), 120000);
                };

                const runAutomatedSequence = async () => {
                    setPhase("p1");
                    setResultsP1([]); setResultsP2([]);
                    
                    // SURGICAL UX FIX: Keep screen alive for mobile users backgrounding the app
                    let wakeLock = null;
                    try {
                        if ('wakeLock' in navigator) {
                            wakeLock = await navigator.wakeLock.request('screen');
                        }
                    } catch (err) { console.log("WakeLock denied, relying on standard background execution."); }

                    const gateKeys = Object.keys(prompts);
                    
                    // PHASE 1: Gemini vs Aeterna (Judge)
                    let p1Data = [];
                    for (const gate of gateKeys) {
                        try {
                            const res = await fetch('/api/run', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({ gate, model: "gemini", judge: "aeterna-vox" })
                            });
                            const data = await res.json();
                            p1Data.push(data);
                            setResultsP1([...p1Data]);
                        } catch (e) { console.error(e); }
                    }

                    // PHASE 2: Aeterna vs Gemini (Judge)
                    setPhase("p2");
                    let p2Data = [];
                    for (const gate of gateKeys) {
                        try {
                            const res = await fetch('/api/run', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({ gate, model: "aeterna-vox", judge: "gemini" })
                            });
                            const data = await res.json();
                            p2Data.push(data);
                            setResultsP2([...p2Data]);
                        } catch (e) { console.error(e); }
                    }

                    if (wakeLock !== null) wakeLock.release();
                    setPhase("done");
                };

                const calcScore = (resultsArray) => {
                    if (resultsArray.length === 0) return "0.00";
                    const passed = resultsArray.filter(r => r.status === 'PASSED').length;
                    return ((passed / Object.keys(prompts).length) * 100).toFixed(2);
                };

                const totalGates = Object.keys(prompts).length;

                return (
                    <div className="max-w-5xl mx-auto w-full flex-grow flex flex-col space-y-8">
                        
                        {/* CLEAN HEADER */}
                        <header className="text-center pt-8 pb-4">
                            <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-[#EDEDED]">AGI Systems Directorate</h1>
                            <p className="text-[#888888] mt-2 text-sm">True AGI Gauntlet <span className="mono-text text-xs ml-2 px-2 py-0.5 bg-white/10 rounded text-white/80">v4.0.26</span></p>
                        </header>

                        {/* INITIALIZATION BLOCK (Hidden if already started) */}
                        {phase === "idle" && (
                            <div className="glass-panel p-8 md:p-12 text-center max-w-2xl mx-auto w-full space-y-6">
                                <div>
                                    <h2 className="text-lg font-medium mb-2">Engine Initialization Required</h2>
                                    <p className="text-[#888888] text-sm leading-relaxed">
                                        Prior to running the dual-phase AGI benchmark, the Sovereign Neuro-Symbolic Engine container must cold-boot. This takes approximately two minutes.
                                    </p>
                                </div>
                                
                                {initStatus === "waking" ? (
                                    <div className="p-4 rounded-lg bg-white/5 border border-white/10 mono-text text-sm">
                                        Container Spinning Up... Please wait <span className="text-white font-bold">{initTimer}s</span>
                                    </div>
                                ) : initStatus === "ready" ? (
                                    <div className="space-y-4">
                                        <div className="text-emerald-400 mono-text text-sm mb-4">SYSTEM ONLINE & READY</div>
                                        <div className="text-xs text-[#888888] mb-4 mono-text bg-white/5 p-3 rounded text-left">
                                            > PHASE 1: Participant [Gemini] | Judge [Aeterna]<br/>
                                            > PHASE 2: Participant [Aeterna] | Judge [Gemini]<br/>
                                            > BACKGROUND EXECUTION: Enabled via WakeLock. You may switch apps.
                                        </div>
                                        <button onClick={runAutomatedSequence} className="w-full btn-primary py-3 rounded-lg font-medium text-sm">
                                            Initiate Automated Sequence
                                        </button>
                                    </div>
                                ) : (
                                    <button onClick={triggerInitialization} className="w-full bg-white/10 hover:bg-white/20 text-white border border-white/10 py-3 rounded-lg font-medium text-sm transition-all">
                                        Boot Sovereign Engine
                                    </button>
                                )}
                            </div>
                        )}

                        {/* ACTIVE DASHBOARD */}
                        {phase !== "idle" && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-grow">
                                
                                {/* SCORE & STATUS PANEL */}
                                <div className="space-y-6 flex flex-col">
                                    <div className="glass-panel p-6 flex flex-col items-center justify-center space-y-4 flex-grow relative overflow-hidden">
                                        <div className="text-xs text-[#888888] font-medium tracking-wide uppercase">Phase 1 Score (Gemini)</div>
                                        <div className="text-5xl font-semibold mono-text">{calcScore(resultsP1)}<span className="text-2xl text-[#888888]">%</span></div>
                                        <div className="w-full bg-white/10 h-1 rounded-full mt-2 overflow-hidden">
                                            <div className="bg-white h-full transition-all duration-300" style={{width: `${(resultsP1.length/totalGates)*100}%`}}></div>
                                        </div>
                                    </div>
                                    
                                    <div className="glass-panel p-6 flex flex-col items-center justify-center space-y-4 flex-grow">
                                        <div className="text-xs text-[#888888] font-medium tracking-wide uppercase">Phase 2 Score (Aeterna)</div>
                                        <div className="text-5xl font-semibold mono-text">{calcScore(resultsP2)}<span className="text-2xl text-[#888888]">%</span></div>
                                        <div className="w-full bg-white/10 h-1 rounded-full mt-2 overflow-hidden">
                                            <div className="bg-white h-full transition-all duration-300" style={{width: `${(resultsP2.length/totalGates)*100}%`}}></div>
                                        </div>
                                    </div>

                                    {/* BOREDOM MITIGATION PROTOCOL */}
                                    {(phase === "p1" || phase === "p2") && (
                                        <div className="glass-panel p-4 text-center">
                                            <div className="text-[10px] text-[#888888] uppercase tracking-wider mb-3">Boredom Mitigation / Node Calibration</div>
                                            <div className="flex flex-wrap gap-2 justify-center mb-2">
                                                {[...Array(10)].map((_, i) => (
                                                    <div key={i} onClick={() => setBoredomScore(s => s + 1)} className="boredom-node w-6 h-6 rounded-md bg-white/10 hover:bg-white/30 border border-white/20"></div>
                                                ))}
                                            </div>
                                            <div className="mono-text text-xs text-[#888888]">Nodes Calibrated: {boredomScore}</div>
                                        </div>
                                    )}
                                </div>

                                {/* TERMINAL LOGS PANEL */}
                                <div className="glass-panel p-6 flex flex-col h-[600px]">
                                    <div className="flex justify-between items-center mb-4 pb-4 border-b border-white/10">
                                        <h3 className="text-sm font-medium">Evaluation Telemetry</h3>
                                        <span className="text-xs text-[#888888] mono-text">
                                            {phase === "p1" ? "Running Phase 1..." : phase === "p2" ? "Running Phase 2..." : "Sequence Complete"}
                                        </span>
                                    </div>
                                    
                                    <div className="flex-grow overflow-y-auto space-y-2 pr-2">
                                        {/* RENDER P1 */}
                                        {resultsP1.map((r, i) => (
                                            <div key={`p1-${i}`} className="p-3 rounded-lg bg-white/5 border border-white/5 text-sm">
                                                <div className="flex justify-between items-center mb-1">
                                                    <span className="text-white/80 font-medium text-xs">P1: {r.gate}</span>
                                                    <span className={`text-[10px] px-2 py-0.5 rounded mono-text ${r.status === 'PASSED' ? 'bg-white text-black' : 'bg-white/10 text-white/50'}`}>
                                                        {r.status}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                        
                                        {/* RENDER P2 */}
                                        {resultsP2.map((r, i) => (
                                            <div key={`p2-${i}`} className="p-3 rounded-lg bg-white/5 border border-white/5 text-sm">
                                                <div className="flex justify-between items-center mb-1">
                                                    <span className="text-white/80 font-medium text-xs">P2: {r.gate}</span>
                                                    <span className={`text-[10px] px-2 py-0.5 rounded mono-text ${r.status === 'PASSED' ? 'bg-white text-black' : 'bg-white/10 text-white/50'}`}>
                                                        {r.status}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                        
                                        {/* AUTOSCROLL ANCHOR */}
                                        <div style={{ float:"left", clear: "both" }}
                                             ref={(el) => { el && el.scrollIntoView({ behavior: "smooth" }) }}>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <footer className="pt-8 pb-4 text-center mt-auto border-t border-white/10">
                            <p className="text-[#555555] text-xs font-medium mono-text">
                                &copy; 2026 AGI Systems Directorate. All rights reserved.
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
