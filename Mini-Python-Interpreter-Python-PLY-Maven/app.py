import streamlit as st
import pandas as pd
import io
import sys
import os
import json
from datetime import datetime

st.set_page_config(
    page_title="Mini-Python Compiler Visualizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark background */
.stApp { background: #0a0d14; color: #e2e8f0; }

/* Hide default header */
header[data-testid="stHeader"] { background: transparent; }

/* Hero */
.hero-section {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at center, rgba(139,92,246,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.4rem; font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #06b6d4, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0 0 8px 0;
}
.hero-sub {
    font-size: 1rem; color: #94a3b8; margin: 0;
    letter-spacing: 0.02em;
}

/* Sidebar */
section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    border-right: 1px solid rgba(139,92,246,0.2);
}
.sidebar-brand {
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: #6366f1; margin-bottom: 16px;
}
.sidebar-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 14px; margin-bottom: 12px;
}
.sidebar-label {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #7c3aed; margin-bottom: 8px;
}

/* Stat cards */
.stats-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 16px; }
.stat-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(6,182,212,0.08));
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 10px; padding: 12px 10px; text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99,102,241,0.2);
}
.stat-value { font-size: 1.5rem; font-weight: 700; color: #a78bfa; line-height: 1; }
.stat-label { font-size: 0.65rem; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.08em; }

/* Pipeline progress */
.pipeline-wrap { display: flex; align-items: center; gap: 0; margin: 16px 0; flex-wrap: wrap; }
.phase-badge {
    display: flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 600;
    white-space: nowrap;
}
.phase-ok { background: rgba(52,211,153,0.15); border: 1px solid rgba(52,211,153,0.4); color: #34d399; }
.phase-err { background: rgba(248,113,113,0.15); border: 1px solid rgba(248,113,113,0.4); color: #f87171; }
.phase-skip { background: rgba(100,116,139,0.15); border: 1px solid rgba(100,116,139,0.3); color: #64748b; }
.phase-arrow { color: #4b5563; margin: 0 4px; font-size: 0.8rem; }

/* Code editor area */
.stTextArea textarea {
    font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    font-size: 14px !important;
    background: #0d1117 !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    line-height: 1.7 !important;
    caret-color: #a78bfa;
}
.stTextArea textarea:focus {
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.1) !important;
}

/* Run button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6d28d9, #0891b2) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 12px 24px !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(109,40,217,0.35) !important;
    letter-spacing: 0.03em !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(109,40,217,0.55) !important;
    background: linear-gradient(135deg, #7c3aed, #0e7490) !important;
}

/* Secondary buttons */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.04) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #a78bfa !important;
}

/* Dataframe */
.stDataFrame { border-radius: 10px; overflow: hidden; }
[data-testid="stDataFrame"] { border: 1px solid rgba(99,102,241,0.2); border-radius: 10px; }

/* Code blocks */
.stCodeBlock { border-radius: 10px !important; }
code { font-family: 'JetBrains Mono', monospace !important; }

/* Terminal output */
.terminal-box {
    background: #020617;
    border: 1px solid rgba(52,211,153,0.3);
    border-radius: 10px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    line-height: 1.8;
    color: #34d399;
    white-space: pre-wrap;
    word-break: break-word;
}
.terminal-prompt { color: #6366f1; }
.terminal-out { color: #e2e8f0; }
.terminal-done { color: #34d399; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    gap: 4px; padding: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #64748b !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(109,40,217,0.4), rgba(8,145,178,0.3)) !important;
    color: #e2e8f0 !important;
}

/* Alerts */
.stAlert { border-radius: 10px !important; }

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Section headers */
.section-header {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: #6366f1;
    display: flex; align-items: center; gap: 6px;
    margin-bottom: 12px; padding-bottom: 8px;
    border-bottom: 1px solid rgba(99,102,241,0.2);
}

/* Fade-in animation */
@keyframes fadeInUp {
    from { opacity:0; transform: translateY(12px); }
    to   { opacity:1; transform: translateY(0); }
}
.fade-in { animation: fadeInUp 0.4s ease forwards; }

/* Glow pulse on run */
@keyframes glowPulse {
    0%,100% { box-shadow: 0 0 12px rgba(139,92,246,0.4); }
    50%      { box-shadow: 0 0 28px rgba(139,92,246,0.8); }
}
.glow { animation: glowPulse 1.5s infinite; }

/* Complexity cards */
.complexity-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0;
}
.complexity-card {
    background: linear-gradient(135deg, rgba(30,41,59,0.5), rgba(15,23,42,0.8));
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 12px; padding: 20px;
    position: relative; overflow: hidden;
}
.complexity-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
}
.card-time::before { background: linear-gradient(to bottom, #3b82f6, #8b5cf6); }
.card-space::before { background: linear-gradient(to bottom, #10b981, #059669); }

.complexity-header { font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;}
.complexity-value { font-size: 2.2rem; font-weight: 800; margin-bottom: 4px; }
.time-val { background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.space-val { background: linear-gradient(to right, #34d399, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.complexity-desc { font-size: 0.85rem; color: #cbd5e1; line-height: 1.4; }
.complexity-detail { font-size: 0.75rem; color: #64748b; margin-top: 12px; padding-top: 12px; border-top: 1px dashed rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

# ── Imports ──────────────────────────────────────────────────────────────────
try:
    from src.lexer import tokenize
    from src.myparser import parser
    from src.semantic_analyzer import semantic_analysis
    from src.icg_generator import generate_icg
    from src.interpreter import Interpreter
    from src.utils import ASTVisualizer
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# ── Complexity Analyzer ───────────────────────────────────────────────────────
def analyze_complexity(tokens):
    """Estimate Big-O Time and Space complexity from token stream."""
    loop_kws   = {"FOR", "WHILE"}
    types      = [t['type'] for t in tokens]
    
    # Time Complexity calculation
    max_depth  = 0
    depth      = 0
    has_recur  = False
    func_names = []

    for i, t in enumerate(tokens):
        if t['type'] == 'DEF' and i+1 < len(tokens):
            func_names.append(tokens[i+1]['value'])

    for i, t in enumerate(tokens):
        if t['type'] in loop_kws:
            depth += 1
            max_depth = max(max_depth, depth)
        elif t['type'] == 'DEDENT':
            depth = max(0, depth - 1)
        if t['type'] == 'IDENTIFIER' and t['value'] in func_names:
            if i+1 < len(tokens) and tokens[i+1]['type'] == 'LPAREN':
                has_recur = True

    if has_recur and max_depth == 0:
        time_o = "O(n)"   ; time_d = "Recursive — depends on call stack depth"
    elif max_depth == 0:
        time_o = "O(1)"   ; time_d = "Constant time — no loops detected"
    elif max_depth == 1:
        time_o = "O(n)"   ; time_d = "Linear time — single loop level"
    elif max_depth == 2:
        time_o = "O(n²)"  ; time_d = "Quadratic time — 2 nested loops"
    elif max_depth == 3:
        time_o = "O(n³)"  ; time_d = "Cubic time — 3 nested loops"
    else:
        time_o = f"O(n^{max_depth})"; time_d = f"{max_depth} nested loops — high complexity"

    # Space Complexity calculation
    has_lists = 'LBRACKET' in types
    
    if has_recur:
        space_o = "O(n)"
        space_d = "Linear space — recursion uses call stack memory"
    elif has_lists:
        space_o = "O(n)"
        space_d = "Linear space — lists consume memory proportional to elements"
    else:
        space_o = "O(1)"
        space_d = "Constant space — only scalar variables used"

    return {
        "time_o": time_o, "time_desc": time_d, "depth": max_depth, "recursive": has_recur,
        "space_o": space_o, "space_desc": space_d, "has_lists": has_lists
    }

# ── Compiler pipeline ─────────────────────────────────────────────────────────
def run_compiler_pipeline(code):
    results = {}
    try:
        results['tokens'] = tokenize(code)
        results['lexer_error'] = None
    except Exception as e:
        results['tokens'] = []
        results['lexer_error'] = str(e)
        return results

    try:
        ast = parser.parse(code)
        results['ast'] = ast
        results['parser_error'] = None
    except Exception as e:
        results['ast'] = None
        results['parser_error'] = str(e)
        return results

    if not results.get('ast'):
        return results

    try:
        is_valid, sem_out = semantic_analysis(results['ast'])
        results['semantic_valid'] = is_valid
        results['semantic_output'] = sem_out
        results['semantic_error'] = None
    except Exception as e:
        results['semantic_error'] = str(e)

    try:
        results['icg_output'] = generate_icg(results['ast'])
        results['icg_error'] = None
    except Exception as e:
        results['icg_error'] = str(e)

    try:
        buf = io.StringIO()
        interp = Interpreter(output_buffer=buf)
        interp.execute(code)
        results['exec_output'] = buf.getvalue()
        results['exec_error'] = None
    except Exception as e:
        results['exec_output'] = ""
        results['exec_error'] = str(e)

    return results

# ── Token stats helper ────────────────────────────────────────────────────────
KEYWORDS = {"IF","ELSE","WHILE","FOR","IN","DEF","RETURN","BREAK","CONTINUE",
            "TRY","EXCEPT","PRINT","LEN","RANGE","AND","OR","NOT","TRUE","FALSE"}
OPERATORS = {"PLUS","MINUS","TIMES","DIVIDE","MODULO","EQUALS","GT","LT","GE","LE","EQ","NE"}

def compute_stats(tokens, code):
    types = [t['type'] for t in tokens]
    return {
        "total":       len(tokens),
        "keywords":    sum(1 for t in types if t in KEYWORDS),
        "identifiers": sum(1 for t in types if t == "IDENTIFIER"),
        "operators":   sum(1 for t in types if t in OPERATORS),
        "literals":    sum(1 for t in types if t in ("NUMBER","STRING")),
        "lines":       len([l for l in code.splitlines() if l.strip()]),
    }

# ── Pipeline badge HTML ───────────────────────────────────────────────────────
def pipeline_html(results):
    phases = [
        ("Lexer",    not results.get('lexer_error')    and bool(results.get('tokens'))),
        ("Parser",   not results.get('parser_error')   and bool(results.get('ast'))),
        ("Semantic", 'semantic_valid' in results),
        ("ICG",      not results.get('icg_error')      and bool(results.get('icg_output'))),
        ("Output",   not results.get('exec_error')     and 'exec_output' in results),
    ]
    parts = []
    for i, (name, ok) in enumerate(phases):
        cls = "phase-ok" if ok else "phase-err"
        icon = "✔" if ok else "✘"
        parts.append(f'<span class="phase-badge {cls}">{icon} {name}</span>')
        if i < len(phases)-1:
            parts.append('<span class="phase-arrow">→</span>')
    return f'<div class="pipeline-wrap fade-in">{"".join(parts)}</div>'

# ── EXAMPLES ──────────────────────────────────────────────────────────────────
EXAMPLES = {
    "── Select Example ──": "",
    "👋 Hello World":        'print("Hello Mini-Python!")',
    "🔢 Variables & Math":   'x = 10\ny = 5\nz = x + y * 2\nprint(z)',
    "🔀 Conditionals":       'x = 42\nif x > 50:\n    print("Big")\nelse:\n    print("Small")',
    "🔁 For Loop":           'print("Counting:")\nfor i in range(5):\n    print(i)',
    "🔄 While Loop":         'n = 1\nwhile n < 6:\n    print(n)\n    n = n + 1',
    "🧩 Functions":          'def greet(name):\n    print("Hello " + name)\n\ngreet("User")',
    "📋 Lists":              'nums = [1, 2, 3]\nprint(len(nums))\nprint(nums[0])',
    "⚠️ Try / Except":       'try:\n    x = 1\n    print(x)\nexcept:\n    print("error")',
}

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    # ── Session state init ────────────────────────────────────────────────────
    if 'code' not in st.session_state:
        st.session_state['code'] = ""
    if 'results' not in st.session_state:
        st.session_state['results'] = None
    if 'theme' not in st.session_state:
        st.session_state['theme'] = "Dark"

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-section fade-in">
        <p class="hero-title">Mini-Python Compiler Visualizer 🚀</p>
        <p class="hero-sub">Explore how Python code moves through every compiler phase — Lexer → Parser → Semantic → ICG → Output</p>
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">⚡ Compiler Dashboard</div>', unsafe_allow_html=True)

        # Example loader
        st.markdown('<div class="sidebar-label">📂 Load Example</div>', unsafe_allow_html=True)
        chosen = st.selectbox("Example", list(EXAMPLES.keys()), label_visibility="collapsed")
        if st.button("▶ Load Example", use_container_width=True):
            if EXAMPLES[chosen]:
                st.session_state['code_input'] = EXAMPLES[chosen]
                st.session_state['results'] = None
                st.rerun()

        st.markdown('<div style="margin:8px 0"></div>', unsafe_allow_html=True)

        col_r, col_c = st.columns(2)
        with col_r:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state['code_input'] = ""
                st.session_state['results'] = None
                st.rerun()
        with col_c:
            if st.button("🗑 Clear", use_container_width=True):
                st.session_state['results'] = None
                st.rerun()

        st.markdown("---")

        # Export
        if st.session_state['results']:
            r = st.session_state['results']
            st.markdown('<div class="sidebar-label">📤 Export</div>', unsafe_allow_html=True)
            if r.get('icg_output'):
                st.download_button("⬇ ICG (.txt)", r['icg_output'], "icg.txt", "text/plain", use_container_width=True)
            if r.get('tokens'):
                df = pd.DataFrame(r['tokens'])
                st.download_button("⬇ Tokens (.csv)", df.to_csv(index=False).encode(), "tokens.csv", "text/csv", use_container_width=True)
            if r.get('exec_output'):
                st.download_button("⬇ Output (.txt)", r['exec_output'], "output.txt", "text/plain", use_container_width=True)

        st.markdown("---")

        # Compiler 101
        st.markdown('<div class="sidebar-label">📚 Compiler 101</div>', unsafe_allow_html=True)
        with st.expander("🔤 Lexer"):
            st.caption("Breaks source code into a stream of **tokens** — the first pass of the compiler.")
        with st.expander("🌳 Parser"):
            st.caption("Builds an **Abstract Syntax Tree** from the token stream using grammar rules.")
        with st.expander("🛡 Semantic Analysis"):
            st.caption("Checks **type safety**, variable declarations, and logical correctness.")
        with st.expander("⚙️ ICG"):
            st.caption("Generates **Three-Address Code** — a platform-independent IR for optimisation.")

        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}  |  Mini-Python Compiler v2.0")

    # ── MAIN LAYOUT ───────────────────────────────────────────────────────────
    left, right = st.columns([1, 1], gap="large")

    # ── LEFT: Editor ──────────────────────────────────────────────────────────
    with left:
        st.markdown('<div class="section-header">📝 Source Code Editor</div>', unsafe_allow_html=True)

        code = st.text_area(
            label="Source Code",
            height=420,
            placeholder='# Start typing Mini-Python code here...\n# Supports: variables, loops, functions, try/except\n\nprint("Hello, World!")',
            label_visibility="collapsed",
            key="code_input"
        )

        # Line count hint
        lines = len([l for l in code.splitlines() if l.strip()])
        total_lines = len(code.splitlines())
        st.caption(f"Lines: {total_lines} total, {lines} non-empty")

        run_btn = st.button("⚡  Run / Analyze Pipeline", type="primary", use_container_width=True)

        if run_btn and code.strip():
            with st.spinner("Running through compiler pipeline…"):
                results = run_compiler_pipeline(code)
                st.session_state['results'] = results

        if run_btn and not code.strip():
            st.warning("Please enter some code first.")

    # ── RIGHT: Visualization ──────────────────────────────────────────────────
    with right:
        st.markdown('<div class="section-header">🔍 Analysis Visualization</div>', unsafe_allow_html=True)

        results = st.session_state.get('results')

        if not results:
            st.markdown("""
            <div style="
                background: rgba(99,102,241,0.05);
                border: 1px dashed rgba(99,102,241,0.3);
                border-radius: 12px;
                padding: 48px 24px;
                text-align: center;
                color: #475569;
            ">
                <div style="font-size:2.5rem;margin-bottom:12px">⚡</div>
                <div style="font-size:1rem;font-weight:500;color:#64748b">Run your code to see analysis</div>
                <div style="font-size:0.8rem;margin-top:6px;color:#334155">Results will appear here after running the pipeline</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Pipeline progress
            st.markdown(pipeline_html(results), unsafe_allow_html=True)

            # Stats cards (if tokens available)
            if results.get('tokens'):
                s = compute_stats(results['tokens'], st.session_state.get('code',''))
                st.markdown(f"""
                <div class="stats-grid fade-in">
                    <div class="stat-card"><div class="stat-value">{s['total']}</div><div class="stat-label">Tokens</div></div>
                    <div class="stat-card"><div class="stat-value">{s['keywords']}</div><div class="stat-label">Keywords</div></div>
                    <div class="stat-card"><div class="stat-value">{s['identifiers']}</div><div class="stat-label">Identifiers</div></div>
                    <div class="stat-card"><div class="stat-value">{s['operators']}</div><div class="stat-label">Operators</div></div>
                    <div class="stat-card"><div class="stat-value">{s['literals']}</div><div class="stat-label">Literals</div></div>
                    <div class="stat-card"><div class="stat-value">{s['lines']}</div><div class="stat-label">LOC</div></div>
                </div>
                """, unsafe_allow_html=True)

            # Tabs
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
                ["📊 Lexer", "🌳 Parser (AST)", "🛡️ Semantic", "⚙️ ICG", "🖥 Output", "⏱️ Complexity"]
            )

            # Lexer tab
            with tab1:
                if results.get('lexer_error'):
                    st.error(f"Lexical Error: {results['lexer_error']}")
                elif results.get('tokens'):
                    df = pd.DataFrame(results['tokens'])
                    st.dataframe(df, use_container_width=True, height=380)
                    csv = df.to_csv(index=False).encode()
                    st.download_button("📥 Download CSV", csv, "tokens.csv", "text/csv")
                else:
                    st.info("No tokens produced.")

            # Parser tab
            with tab2:
                if results.get('parser_error'):
                    st.error(f"Syntax Error: {results['parser_error']}")
                elif results.get('ast'):
                    st.success("✔ Syntax Analysis Complete — AST built successfully")
                    viz = ASTVisualizer()
                    try:
                        viz.visualize(results['ast'])
                        st.graphviz_chart(viz.dot, use_container_width=True)
                        st.download_button("📥 Download AST (DOT)", viz.dot.source, "ast.dot", "text/plain")
                    except Exception as e:
                        st.error(f"Visualization Error: {e}")
                else:
                    st.info("No AST produced.")

            # Semantic tab
            with tab3:
                if results.get('semantic_error'):
                    st.error(f"Semantic Error: {results['semantic_error']}")
                elif 'semantic_output' in results:
                    if results['semantic_valid']:
                        st.success("✔ Semantic Integrity Verified — No errors found")
                    else:
                        st.warning("⚠️ Semantic Issues Found")
                    st.code(results['semantic_output'], language="text")
                else:
                    st.info("Semantic analysis not run.")

            # ICG tab
            with tab4:
                if results.get('icg_error'):
                    st.error(f"ICG Error: {results['icg_error']}")
                elif results.get('icg_output'):
                    st.code(results['icg_output'], language="text")
                    st.download_button("📥 Download ICG", results['icg_output'], "icg.txt", "text/plain")
                else:
                    st.info("No ICG output produced.")

            # Output tab
            with tab5:
                if results.get('exec_error'):
                    st.error(f"Runtime Error: {results['exec_error']}")

                out = results.get('exec_output', '')
                lines_out = out.strip().split('\n') if out.strip() else []

                terminal_inner = '<span class="terminal-prompt">$ </span><span class="terminal-out">Running pipeline...</span>\n'
                if lines_out:
                    for ln in lines_out:
                        terminal_inner += f'<span class="terminal-prompt">&gt; </span><span class="terminal-out">{ln}</span>\n'
                    terminal_inner += '\n<span class="terminal-done">✔ Execution complete.</span>'
                elif not results.get('exec_error'):
                    terminal_inner += '\n<span class="terminal-done">✔ Program finished with no output.</span>'

                st.markdown(
                    f'<div class="terminal-box fade-in">{terminal_inner}</div>',
                    unsafe_allow_html=True
                )

            # Complexity tab
            with tab6:
                if results.get('tokens'):
                    cx = analyze_complexity(results['tokens'])
                    st.markdown(f"""
                    <div class="complexity-grid fade-in">
                        <div class="complexity-card card-time">
                            <div class="complexity-header">Time Complexity</div>
                            <div class="complexity-value time-val">{cx['time_o']}</div>
                            <div class="complexity-desc">{cx['time_desc']}</div>
                            <div class="complexity-detail">
                                Loop depth: <b style="color:#e2e8f0">{cx['depth']}</b>
                                <br>{'⚡ Recursive function' if cx['recursive'] else 'No recursion'}
                            </div>
                        </div>
                        <div class="complexity-card card-space">
                            <div class="complexity-header">Space Complexity</div>
                            <div class="complexity-value space-val">{cx['space_o']}</div>
                            <div class="complexity-desc">{cx['space_desc']}</div>
                            <div class="complexity-detail">
                                {'Lists/Arrays detected' if cx['has_lists'] else 'Only scalar variables detected'}
                                <br>{'⚡ Recursive call stack' if cx['recursive'] else 'No recursive depth'}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Run the code to analyze time and space complexity.")

if __name__ == "__main__":
    main()
