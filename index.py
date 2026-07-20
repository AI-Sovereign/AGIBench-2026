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

# =======================================================================
# 🌐 FRONTEND PLUMBING FIX - THE CDN JAILBREAK CACHE
# =======================================================================
_cdn_cache = {}

async def _fetch_and_cache(url: str):
    if url in _cdn_cache: return _cdn_cache[url]
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.get(url, timeout=15.0)
            _cdn_cache[url] = resp.text
            return resp.text
        except Exception: return ""

@app.get("/proxy/tailwind.js")
async def proxy_tailwind():
    from fastapi import Response
    content = await _fetch_and_cache("https://cdn.tailwindcss.com")
    return Response(content=content, media_type="application/javascript")

@app.get("/proxy/react.js")
async def proxy_react():
    from fastapi import Response
    content = await _fetch_and_cache("https://unpkg.com/react@18/umd/react.production.min.js")
    return Response(content=content, media_type="application/javascript")

@app.get("/proxy/react-dom.js")
async def proxy_react_dom():
    from fastapi import Response
    content = await _fetch_and_cache("https://unpkg.com/react-dom@18/umd/react-dom.production.min.js")
    return Response(content=content, media_type="application/javascript")

@app.get("/proxy/babel.js")
async def proxy_babel():
    from fastapi import Response
    content = await _fetch_and_cache("https://unpkg.com/@babel/standalone/babel.min.js")
    return Response(content=content, media_type="application/javascript")

# =======================================================================
# 🎨 2026 ENTERPRISE UI OVERHAUL 
# =======================================================================
@app.get("/")
def serve_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>AGI Systems Directorate | Workspace</title>
        
        <!-- THE LOCAL PROXY JAILBREAK -->
        <script src="/proxy/tailwind.js"></script>
        <script src="/proxy/react.js"></script>
        <script src="/proxy/react-dom.js"></script>
        <script src="/proxy/babel.js"></script>
        
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            brand: '#E5E5E5',
                            surface: '#0A0A0A',
                            surface2: '#141414',
                            border: '#262626'
                        },
                        fontFamily: {
                            sans: ['Inter', 'sans-serif'],
                            mono: ['Geist Mono', 'SFMono-Regular', 'monospace'],
                        }
                    }
                }
            }
        </script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Geist+Mono:wght@400;500&display=swap');
            
            body { 
                background-color: #030303;
                background-image: 
                    radial-gradient(circle at 15% 50%, rgba(255,255,255,0.03) 0%, transparent 50%),
                    radial-gradient(circle at 85% 30%, rgba(255,255,255,0.02) 0%, transparent 50%);
                color: #A3A3A3; 
                font-family: 'Inter', sans-serif; 
                -webkit-font-smoothing: antialiased;
                margin: 0;
                height: 100vh;
                overflow: hidden;
            }
            
            .mono-text { font-family: 'Geist Mono', monospace; }
            
            /* Modern 2026 App Layout */
            .app-container {
                display: grid;
                grid-template-rows: 64px 1fr;
                height: 100vh;
            }
            .main-content {
                display: grid;
                grid-template-columns: 320px 1fr;
                gap: 1px;
                background: #262626; /* borders between panels */
            }
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                    grid-template-rows: auto 1fr;
                    overflow-y: auto;
                }
                body { overflow: auto; }
                .app-container { height: auto; min-height: 100vh; }
            }

            .panel { background: #0A0A0A; overflow-y: auto; position: relative; }
            
            .btn-primary {
                background: #E5E5E5; color: #000;
                transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
                box-shadow: 0 1px 2px rgba(255,255,255,0.1);
            }
            .btn-primary:hover:not(:disabled) {
                background: #FFFFFF;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(255,255,255,0.15);
            }
            .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

            .btn-outline {
                background: transparent; color: #E5E5E5;
                border: 1px solid #262626;
                transition: all 0.2s ease;
            }
            .btn-outline:hover:not(:disabled) { background: #141414; border-color: #404040; }
            
            /* Custom Scrollbar for Terminal */
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: #262626; border-radius: 6px; }
            ::-webkit-scrollbar-thumb:hover { background: #404040; }

            .pulse-ring {
                animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: .3; }
            }

            .status-badge {
                display: inline-flex; items-center; padding: 2px 8px;
                border-radius: 9999px; font-size: 10px; font-weight: 500;
                letter-spacing: 0.05em; text-transform: uppercase;
            }
            .status-pass { background: rgba(16, 185, 129, 0.1); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.2); }
            .status-fail { background: rgba(239, 68, 68, 0.1); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.2); }

            .boredom-node { 
                transition: all 0.15s ease; cursor: crosshair; 
                background: #141414; border: 1px solid #262626;
            }
            .boredom-node:hover { background: #262626; border-color: #404040; }
            .boredom-node:active { transform: scale(0.85); background: #E5E5E5; }
        </style>
    </head>
    <body>
        <div id="root"></div>
        <script type="text/babel">
            const { useState, useEffect, useRef } = React;

            // --- SVG ICONS ---
            const IconLogo = () => (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            );
            const IconTerminal = () => (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line>
                </svg>
            );
            const IconPlay = () => (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
            );
            const IconPower = () => (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18.36 6.64a9 9 0 1 1-12.73 0"></path><line x1="12" y1="2" x2="12" y2="12"></line>
                </svg>
            );

            function App() {
                const [prompts, setPrompts] = useState({});
                const [phase, setPhase] = useState("idle"); 
                const [resultsP1, setResultsP1] = useState([]);
                const [resultsP2, setResultsP2] = useState([]);
                
                const [initStatus, setInitStatus] = useState("idle"); 
                const [initTimer, setInitTimer] = useState(120);
                
                const [boredomScore, setBoredomScore] = useState(0);
                const terminalEndRef = useRef(null);

                useEffect(() => {
                    fetch('/api/models').then(r => r.json()).then(d => setPrompts(d.prompts));
                }, []);

                useEffect(() => {
                    if (terminalEndRef.current) {
                        terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
                    }
                }, [resultsP1, resultsP2]);

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
                    
                    let wakeLock = null;
                    try {
                        if ('wakeLock' in navigator) {
                            wakeLock = await navigator.wakeLock.request('screen');
                        }
                    } catch (err) {}

                    const gateKeys = Object.keys(prompts);
                    
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
                        } catch (e) {}
                    }

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
                        } catch (e) {}
                    }

                    if (wakeLock !== null) wakeLock.release();
                    setPhase("done");
                };

                const calcScore = (resultsArray) => {
                    if (resultsArray.length === 0) return "0.0";
                    const passed = resultsArray.filter(r => r.status === 'PASSED').length;
                    return ((passed / Object.keys(prompts).length) * 100).toFixed(1);
                };

                const totalGates = Object.keys(prompts).length;

                return (
                    <div className="app-container">
                        {/* TOP NAVIGATION BAR */}
                        <header className="bg-surface border-b border-border flex items-center justify-between px-6 z-10 relative">
                            <div className="flex items-center space-x-3 text-brand">
                                <IconLogo />
                                <span className="font-semibold tracking-tight text-sm">AGI Directorate</span>
                                <span className="bg-surface2 border border-border px-2 py-0.5 rounded text-[10px] mono-text text-gray-400">v4.0.26</span>
                            </div>
                            <div className="flex items-center space-x-4 text-xs font-medium">
                                <span className="flex items-center space-x-1.5">
                                    <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
                                    <span>Telemetry API Online</span>
                                </span>
                            </div>
                        </header>

                        {/* MAIN WORKSPACE GRID */}
                        <main className="main-content">
                            
                            {/* SIDEBAR: CONTROLS & STATUS */}
                            <aside className="panel p-6 flex flex-col h-full border-r border-border md:border-none">
                                
                                <div className="mb-8">
                                    <h2 className="text-sm font-semibold text-brand mb-1">Execution Protocol</h2>
                                    <p className="text-xs text-gray-500 leading-relaxed">Initialize the Sovereign Engine prior to executing the dual-phase AGI benchmark gauntlet.</p>
                                </div>

                                {/* ACTION CENTER */}
                                <div className="space-y-4 mb-8">
                                    {phase === "idle" && (
                                        <div className="bg-surface2 border border-border rounded-lg p-4 space-y-4">
                                            {initStatus === "waking" ? (
                                                <div className="flex items-center justify-between">
                                                    <span className="text-xs text-gray-400 mono-text">Container Booting...</span>
                                                    <span className="text-brand font-medium mono-text pulse-ring">{initTimer}s</span>
                                                </div>
                                            ) : initStatus === "ready" ? (
                                                <div className="space-y-4">
                                                    <div className="flex items-center space-x-2 text-emerald-400 text-xs mono-text">
                                                        <IconPower /> <span>ENGINE ONLINE</span>
                                                    </div>
                                                    <button onClick={runAutomatedSequence} className="w-full btn-primary flex items-center justify-center space-x-2 py-2.5 rounded-md text-xs font-medium">
                                                        <IconPlay /> <span>Start Sequence</span>
                                                    </button>
                                                </div>
                                            ) : (
                                                <button onClick={triggerInitialization} className="w-full btn-outline flex items-center justify-center space-x-2 py-2.5 rounded-md text-xs font-medium">
                                                    <IconPower /> <span>Boot Engine</span>
                                                </button>
                                            )}
                                        </div>
                                    )}
                                    
                                    {phase !== "idle" && (
                                        <div className="bg-surface2 border border-border rounded-lg p-4 space-y-4">
                                            <div className="text-xs text-gray-400 mono-text uppercase tracking-wider mb-2">Live Sequence</div>
                                            <div className="flex items-center space-x-2 text-brand text-xs font-medium">
                                                <span className={`w-1.5 h-1.5 rounded-full ${phase !== 'done' ? 'bg-amber-400 pulse-ring' : 'bg-gray-600'}`}></span>
                                                <span>{phase === "p1" ? "Phase 1: Gemini vs Aeterna" : phase === "p2" ? "Phase 2: Aeterna vs Gemini" : "Sequence Terminated"}</span>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* LIVE METRICS */}
                                {phase !== "idle" && (
                                    <div className="space-y-4 mb-auto">
                                        <div className="bg-surface2 border border-border rounded-lg p-4">
                                            <div className="flex justify-between items-end mb-2">
                                                <span className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Gemini Score</span>
                                                <span className="text-2xl font-semibold text-brand mono-text">{calcScore(resultsP1)}%</span>
                                            </div>
                                            <div className="w-full bg-[#030303] h-1 rounded-full overflow-hidden">
                                                <div className="bg-white h-full transition-all duration-500" style={{width: `${(resultsP1.length/totalGates)*100}%`}}></div>
                                            </div>
                                        </div>
                                        <div className="bg-surface2 border border-border rounded-lg p-4">
                                            <div className="flex justify-between items-end mb-2">
                                                <span className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Aeterna Score</span>
                                                <span className="text-2xl font-semibold text-brand mono-text">{calcScore(resultsP2)}%</span>
                                            </div>
                                            <div className="w-full bg-[#030303] h-1 rounded-full overflow-hidden">
                                                <div className="bg-white h-full transition-all duration-500" style={{width: `${(resultsP2.length/totalGates)*100}%`}}></div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* BOREDOM MATRIX */}
                                {(phase === "p1" || phase === "p2") && (
                                    <div className="mt-8 pt-6 border-t border-border">
                                        <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-3">Calibration Matrix</div>
                                        <div className="grid grid-cols-5 gap-1.5 mb-3">
                                            {[...Array(15)].map((_, i) => (
                                                <div key={i} onClick={() => setBoredomScore(s => s + 1)} className="boredom-node w-full aspect-square rounded-sm"></div>
                                            ))}
                                        </div>
                                        <div className="mono-text text-[10px] text-gray-500">Nodes Aligned: {boredomScore}</div>
                                    </div>
                                )}
                            </aside>

                            {/* MAIN VIEW: TERMINAL / LOGS */}
                            <section className="panel flex flex-col h-full bg-[#030303]">
                                <div className="sticky top-0 bg-[#030303]/90 backdrop-blur-md border-b border-border px-6 py-4 flex justify-between items-center z-10">
                                    <div className="flex items-center space-x-2 text-brand text-xs font-medium">
                                        <IconTerminal /> <span>Execution Logs</span>
                                    </div>
                                    <span className="text-[10px] text-gray-500 mono-text">Output Stream</span>
                                </div>
                                
                                <div className="p-6 flex-grow overflow-y-auto space-y-3 font-mono text-xs">
                                    {phase === "idle" && (
                                        <div className="text-gray-600">Waiting for initialization command...</div>
                                    )}
                                    
                                    {resultsP1.map((r, i) => (
                                        <div key={`p1-${i}`} className="bg-surface border border-border p-3 rounded-md flex justify-between items-start group hover:border-gray-600 transition-colors">
                                            <div className="flex space-x-3">
                                                <span className="text-gray-500">[{`0${i+1}`.slice(-2)}]</span>
                                                <span className="text-gray-300 font-medium">Phase 1 :: {r.gate}</span>
                                            </div>
                                            <span className={`status-badge ${r.status === 'PASSED' ? 'status-pass' : 'status-fail'}`}>
                                                {r.status}
                                            </span>
                                        </div>
                                    ))}
                                    
                                    {resultsP2.map((r, i) => (
                                        <div key={`p2-${i}`} className="bg-surface border border-border p-3 rounded-md flex justify-between items-start group hover:border-gray-600 transition-colors">
                                            <div className="flex space-x-3">
                                                <span className="text-emerald-500/50">[{`0${i+1}`.slice(-2)}]</span>
                                                <span className="text-gray-300 font-medium">Phase 2 :: {r.gate}</span>
                                            </div>
                                            <span className={`status-badge ${r.status === 'PASSED' ? 'status-pass' : 'status-fail'}`}>
                                                {r.status}
                                            </span>
                                        </div>
                                    ))}
                                    
                                    <div ref={terminalEndRef} className="h-4"></div>
                                </div>
                            </section>
                        </main>
                    </div>
                );
            }
            
            const rootElement = document.getElementById('root');
            const root = ReactDOM.createRoot(rootElement);
            root.render(<App />);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
