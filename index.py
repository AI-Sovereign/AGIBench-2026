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
from gradio_client import Client

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
            "aeterna-vox": self._aeterna_inference, 
            "custom-upload": self._custom_endpoint_inference
        }
        self.active_model = "nexus"

    async def _aeterna_inference(self, prompt):
        # Bridge to AGI Systems Directorate Sovereign Architecture
        is_judge = "AGI BENCHMARK JUDGE" in prompt
        original_prompt = prompt # STORE ORIGINAL TO FIX THE 0% DECAPITATION BUG
        
        # Force absolute state orientation so it knows if it is Participant or Judge
        if not is_judge:
            prompt = f"[CONTEXT: You are currently the PARTICIPANT/SUBJECT of this benchmark gate. Solve the puzzle directly. Do NOT output PASSED or FAILED.]\n{prompt}"
            
        try:
            hf_token = os.getenv("HF_TOKEN", "").strip()
            clean_text = ""
            raw_result = ""
            
            # --- DUAL-ROUTING FALLBACK PROTOCOL ---
            try:
                client = Client("agi-systems-directorate/aeterna-vox-omni-mini-v2.1", token=hf_token, httpx_kwargs={"timeout": 120.0})
                result = client.predict(prompt, None, api_name="/predict")
                raw_result = str(result)
                
                if re.search(r'brain\s*freeze\.?\s*one\s*sec\.?', raw_result, re.IGNORECASE):
                    raise ValueError("HF Space hit the brain freeze limit. Falling back.")
                    
            except Exception as hf_e:
                fallback_client = Client("https://sovereign-neuro-symbolic-engine.onrender.com/", httpx_kwargs={"timeout": 120.0})
                result = fallback_client.predict(prompt, None, api_name="/predict")
                raw_result = str(result)
            
            # --- THE 0% BUG FIX ---
            # If it's the judge, DO NOT strip brackets, because it might output [PASSED]
            if is_judge:
                clean_text = raw_result.strip()
            else:
                clean_text = re.sub(r'\[.*?\]', '', raw_result).strip()
            
            # --- SURGICAL FIX 3.0: Prompt Decapitation ---
            # Now checking against BOTH the original prompt and the modified one
            if original_prompt in clean_text:
                clean_text = clean_text.split(original_prompt, 1)[-1].strip()
            elif prompt in clean_text:
                clean_text = clean_text.split(prompt, 1)[-1].strip()
            elif clean_text.lower().startswith(original_prompt.strip().lower()):
                clean_text = clean_text[len(original_prompt.strip()):].strip()
                
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
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}",
                    headers=headers,
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=30.0
                )
                data = resp.json()
                
                if 'candidates' in data:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    return f"Google API Error Dump (Debug this): {str(data)}"
                    
            except Exception as e: return f"Google Exception: {str(e)}"

    async def _custom_endpoint_inference(self, prompt):
        custom_url = os.getenv("CUSTOM_MODEL_URL", "http://localhost:8000/v1/completions")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
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
# 🎨 ENTERPRISE TIER UI - SaaS PRODUCT AESTHETIC
# =======================================================================
@app.get("/")
def serve_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>AGI Directorate | Console</title>
        
        <script src="/proxy/tailwind.js"></script>
        <script src="/proxy/react.js"></script>
        <script src="/proxy/react-dom.js"></script>
        <script src="/proxy/babel.js"></script>
        
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            background: '#F9FAFB',
                            surface: '#FFFFFF',
                            border: '#E5E7EB',
                            textPrimary: '#111827',
                            textSecondary: '#6B7280',
                            brand: '#4F46E5',
                            brandHover: '#4338CA'
                        },
                        fontFamily: {
                            sans: ['Inter', '-apple-system', 'sans-serif'],
                        },
                        boxShadow: {
                            'soft': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
                        }
                    }
                }
            }
        </script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            body { 
                background-color: #F9FAFB;
                color: #111827; 
                font-family: 'Inter', sans-serif; 
                -webkit-font-smoothing: antialiased;
                margin: 0;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            .btn-primary {
                background: #4F46E5; color: #FFFFFF;
                font-weight: 500;
                transition: all 0.2s ease;
                border-radius: 8px;
            }
            .btn-primary:hover:not(:disabled) {
                background: #4338CA;
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
            }
            .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

            .btn-secondary {
                background: #FFFFFF; color: #374151;
                border: 1px solid #D1D5DB;
                font-weight: 500;
                transition: all 0.2s ease;
                border-radius: 8px;
            }
            .btn-secondary:hover:not(:disabled) { background: #F3F4F6; }

            /* Refined Scrollbar */
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 6px; }
            ::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }

            .badge {
                padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; 
            }
            .badge-pass { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
            .badge-fail { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
            
            .card-hover { transition: all 0.2s ease; }
            .card-hover:hover { transform: translateY(-1px); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border-color: #D1D5DB; }
            
            .shimmer {
                background: linear-gradient(90deg, #F3F4F6 0px, #FFFFFF 50%, #F3F4F6 100%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite linear;
            }
            @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
        </style>
    </head>
    <body>
        <div id="root" class="h-full flex flex-col"></div>
        <script type="text/babel">
            const { useState, useEffect, useRef } = React;

            const LogoSVG = () => (
                <svg width="28" height="28" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="40" height="40" rx="10" fill="#4F46E5"/>
                    <path d="M12 20L20 12L28 20L20 28L12 20Z" stroke="white" strokeWidth="2.5" strokeLinejoin="round"/>
                    <circle cx="20" cy="20" r="3" fill="white"/>
                </svg>
            );

            function App() {
                const [prompts, setPrompts] = useState({});
                const [phase, setPhase] = useState("idle"); 
                const [resultsP1, setResultsP1] = useState([]);
                const [resultsP2, setResultsP2] = useState([]);
                
                const [initStatus, setInitStatus] = useState("idle"); 
                const [initTimer, setInitTimer] = useState(120);
                
                const scrollRef = useRef(null);

                useEffect(() => {
                    fetch('/api/models').then(r => r.json()).then(d => setPrompts(d.prompts));
                }, []);

                useEffect(() => {
                    if (scrollRef.current) {
                        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
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

                    setPhase("done");
                };

                const calcScore = (resultsArray) => {
                    if (resultsArray.length === 0) return "0.0";
                    const passed = resultsArray.filter(r => r.status === 'PASSED').length;
                    return ((passed / Object.keys(prompts).length) * 100).toFixed(1);
                };

                const totalGates = Object.keys(prompts).length;

                return (
                    <div className="flex flex-col h-full overflow-hidden">
                        {/* ENTERPRISE TOP NAVIGATION */}
                        <header className="bg-surface border-b border-border px-6 py-4 flex items-center justify-between shrink-0">
                            <div className="flex items-center space-x-3">
                                <LogoSVG />
                                <div>
                                    <h1 className="font-bold text-base text-textPrimary leading-tight">AGI Systems Directorate</h1>
                                    <p className="text-xs text-textSecondary font-medium">Evaluation Workspace</p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-4">
                                <div className="flex items-center space-x-2 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-200">
                                    <span className="w-2 h-2 rounded-full bg-green-500"></span>
                                    <span className="text-xs text-gray-700 font-semibold">System Online</span>
                                </div>
                            </div>
                        </header>

                        {/* MAIN LAYOUT */}
                        <main className="flex-grow flex flex-col md:flex-row overflow-hidden max-w-7xl w-full mx-auto">
                            
                            {/* LEFT CONTROL PANEL */}
                            <aside className="w-full md:w-80 p-6 flex flex-col shrink-0 overflow-y-auto border-r border-border bg-gray-50/50">
                                
                                {/* ABOUT SECTION - HIDES WHEN BOOTED/RUNNING */}
                                {(initStatus === "idle" || initStatus === "waking") && (
                                    <div className="bg-white border border-indigo-100 rounded-xl p-5 mb-6 shadow-sm">
                                        <h3 className="text-indigo-900 font-bold text-sm mb-2 flex items-center gap-2">
                                            <svg className="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            About Benchmark
                                        </h3>
                                        <p className="text-gray-600 text-xs leading-relaxed">
                                            The initial constraints (Gates 1-10) are relatively trivial; most standard LLMs can navigate them successfully regardless of reasoning quality. However, progressing past the 10th gate introduces compounding, dynamic difficulty spikes designed specifically to stress-test true neuro-symbolic reasoning.
                                        </p>
                                    </div>
                                )}

                                {/* ACTION CENTER */}
                                <div className="mb-8">
                                    <h2 className="text-sm font-bold text-gray-900 mb-4 uppercase tracking-wider">Execution Controls</h2>
                                    {phase === "idle" ? (
                                        <div className="space-y-3">
                                            {initStatus === "waking" ? (
                                                <div className="btn-secondary w-full py-3 flex justify-center items-center rounded-lg opacity-70 cursor-wait shimmer border-transparent">
                                                    <span className="text-sm font-semibold text-gray-600">Booting Architecture ({initTimer}s)</span>
                                                </div>
                                            ) : initStatus === "ready" ? (
                                                <button onClick={runAutomatedSequence} className="w-full btn-primary py-3 flex items-center justify-center space-x-2">
                                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                                    <span className="text-sm">Execute Benchmark</span>
                                                </button>
                                            ) : (
                                                <button onClick={triggerInitialization} className="w-full btn-secondary py-3 flex items-center justify-center space-x-2">
                                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                                                    <span className="text-sm">Initialize Engine</span>
                                                </button>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                                            <div className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Current Status</div>
                                            <div className="flex items-center space-x-3 text-sm font-bold text-gray-900">
                                                <span className={`w-2.5 h-2.5 rounded-full ${phase !== 'done' ? 'bg-indigo-500 animate-pulse' : 'bg-green-500'}`}></span>
                                                <span>{phase === "p1" ? "Phase 1: Evaluating Gemini" : phase === "p2" ? "Phase 2: Evaluating Aeterna" : "Evaluation Complete"}</span>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* ENTERPRISE METRICS */}
                                {phase !== "idle" && (
                                    <div className="space-y-6 mt-auto bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                                        <div>
                                            <div className="flex justify-between items-baseline mb-2">
                                                <span className="text-sm text-gray-600 font-semibold">Gemini Performance</span>
                                                <span className="text-xl font-bold text-gray-900">{calcScore(resultsP1)}%</span>
                                            </div>
                                            <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                                                <div className="bg-indigo-500 h-full transition-all duration-700 ease-out" style={{width: `${(resultsP1.length/totalGates)*100}%`}}></div>
                                            </div>
                                        </div>
                                        <div className="pt-2">
                                            <div className="flex justify-between items-baseline mb-2">
                                                <span className="text-sm text-gray-600 font-semibold">Aeterna Performance</span>
                                                <span className="text-xl font-bold text-gray-900">{calcScore(resultsP2)}%</span>
                                            </div>
                                            <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                                                <div className="bg-indigo-500 h-full transition-all duration-700 ease-out" style={{width: `${(resultsP2.length/totalGates)*100}%`}}></div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </aside>

                            {/* RIGHT RESULTS AREA */}
                            <div className="flex-grow p-6 overflow-y-auto bg-background" ref={scrollRef}>
                                {phase === "idle" ? (
                                    <div className="h-full flex flex-col items-center justify-center text-gray-400 space-y-4">
                                        <svg className="w-12 h-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                        </svg>
                                        <p className="text-sm font-medium">Awaiting execution command to populate telemetry.</p>
                                    </div>
                                ) : (
                                    <div className="space-y-3 max-w-3xl mx-auto pb-10">
                                        {resultsP1.map((r, i) => (
                                            <div key={`p1-${i}`} className="bg-surface border border-border p-4 rounded-xl flex justify-between items-center card-hover">
                                                <div className="flex items-center space-x-4">
                                                    <span className="text-gray-400 font-mono text-sm w-6">{(i+1).toString().padStart(2, '0')}</span>
                                                    <div className="flex flex-col">
                                                        <span className="text-xs text-indigo-500 font-bold tracking-wide uppercase mb-0.5">Phase 1 / {r.gate}</span>
                                                    </div>
                                                </div>
                                                <span className={`badge ${r.status === 'PASSED' ? 'badge-pass' : 'badge-fail'}`}>
                                                    {r.status}
                                                </span>
                                            </div>
                                        ))}
                                        
                                        {resultsP2.length > 0 && <div className="py-4 flex items-center justify-center"><span className="h-px w-full bg-gray-200"></span><span className="px-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Phase 2 Transition</span><span className="h-px w-full bg-gray-200"></span></div>}

                                        {resultsP2.map((r, i) => (
                                            <div key={`p2-${i}`} className="bg-surface border border-border p-4 rounded-xl flex justify-between items-center card-hover">
                                                <div className="flex items-center space-x-4">
                                                    <span className="text-gray-400 font-mono text-sm w-6">{(i+1).toString().padStart(2, '0')}</span>
                                                    <div className="flex flex-col">
                                                        <span className="text-xs text-emerald-500 font-bold tracking-wide uppercase mb-0.5">Phase 2 / {r.gate}</span>
                                                    </div>
                                                </div>
                                                <span className={`badge ${r.status === 'PASSED' ? 'badge-pass' : 'badge-fail'}`}>
                                                    {r.status}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
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
