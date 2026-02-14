import streamlit as st
import pandas as pd
import io
import sys
import os

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Mini-Python Compiler",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for dark theme and better styling
st.markdown("""
<style>
    .stTextArea textarea {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }
    .reportview-container {
        background: #0e1117;
    }
    .sidebar .sidebar-content {
        background: #262730;
    }
</style>
""", unsafe_allow_html=True)

# Import local modules
try:
    from src.lexer import tokenize
    from src.myparser import parser
    from src.semantic_analyzer import semantic_analysis
    from src.icg_generator import generate_icg
    from src.interpreter import Interpreter
    from src.utils import ASTVisualizer
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

def run_compiler_pipeline(code):
    results = {}
    
    # 1. Lexical Analysis
    try:
        tokens = tokenize(code)
        results['tokens'] = tokens
        results['lexer_error'] = None
    except Exception as e:
        results['tokens'] = []
        results['lexer_error'] = str(e)
        return results

    # 2. Parsing (Syntax & AST)
    try:
        # Reset parser state if needed (though creating new parser instance is safer if possible, 
        # but yacc.yacc() returns a parser object)
        ast = parser.parse(code)
        results['ast'] = ast
        results['parser_error'] = None
    except Exception as e:
        results['ast'] = None
        results['parser_error'] = str(e)
        return results

    if not ast:
        return results

    # 3. Semantic Analysis
    try:
        is_valid, sem_output = semantic_analysis(ast)
        results['semantic_valid'] = is_valid
        results['semantic_output'] = sem_output
        results['semantic_error'] = None
    except Exception as e:
        results['semantic_error'] = str(e)

    # 4. Intermediate Code Generation
    try:
        icg_output = generate_icg(ast)
        results['icg_output'] = icg_output
        results['icg_error'] = None
    except Exception as e:
        results['icg_error'] = str(e)

    # 5. Execution (Interpreter)
    try:
        output_buffer = io.StringIO()
        interpreter = Interpreter(output_buffer=output_buffer)
        interpreter.execute(code)
        results['exec_output'] = output_buffer.getvalue()
        results['exec_error'] = None
    except Exception as e:
        results['exec_output'] = ""
        results['exec_error'] = str(e)

    return results

def main():
    st.title("🐍 Mini-Python Compiler Visualizer")
    
    # Sidebar
    with st.sidebar:
        st.header("Controls")
        
        # Example Loader
        examples = {
            "Select an Example": "",
            "Hello World": 'print("Hello Mini-Python!")',
            "Variables & Math": 'x = 10\ny = 5\nprint(x + y * 2)',
            "Conditionals": 'x = 42\nif x > 50:\n    print("Big")\nelse:\n    print("Small")',
            "Loops": 'print("Counting:")\nfor i in range(5):\n    print(i)',
            "Functions": 'def greet(name):\n    print("Hello " + name)\n\ngreet("User")'
        }
        
        selected_example = st.selectbox("Load Example", list(examples.keys()))
        
        st.markdown("---")
        st.markdown("### Export Results")
        if 'results' in locals() or 'results' in st.session_state:
            # We'll use session state to keep results between clicks if needed, 
            # but for now let's just check if they exist in local scope from the Run click
            pass
            
        st.markdown("### 📚 Compiler 101")
        with st.expander("What is a Lexer?"):
            st.write("The Lexical Analyzer (Lexer) breaks the source code into a stream of **tokens** (keywords, identifiers, literals). This is the first step in understanding the code structure.")
        with st.expander("What is a Parser?"):
            st.write("The Parser takes tokens and arranges them into an **Abstract Syntax Tree (AST)** based on the language's grammar rules.")
        with st.expander("Semantic Analysis?"):
            st.write("This phase ensures that the code makes sense (e.g., variables are declared before use, types are compatible in operations).")
        with st.expander("What is ICG?"):
            st.write("Intermediate Code Generation (ICG) creates a platform-independent representation of the code, like Three-Address Code, which is easier to optimize.")

    # Main Layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Source Code Editor")
        initial_code = examples[selected_example] if selected_example != "Select an Example" else ""
        code = st.text_area("Input Code", value=initial_code, height=400, placeholder="Type your python code here...", help="Support for: variables, loops, functions, recursion, and try-except.")
        
        analyze_btn = st.button("🚀 Run / Analyze Pipeline", type="primary", use_container_width=True)

    with col2:
        st.subheader("🔍 Analysis Visualization")
        
        if analyze_btn and code:
            with st.spinner("Processing through compiler pipeline..."):
                results = run_compiler_pipeline(code)
                # Store in session state for cross-interaction access
                st.session_state['last_results'] = results
                
            # Tabs for different phases
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Lexer", "🌳 Parser (AST)", "🛡️ Semantic", "⚙️ ICG", "🏁 Output"
            ])
            
            # 1. Lexer Tab
            with tab1:
                if results.get('lexer_error'):
                    st.error(f"Lexical Error: {results['lexer_error']}")
                elif results.get('tokens'):
                    tokens = results['tokens']
                    df = pd.DataFrame(tokens)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download Tokens CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Tokens (CSV)", csv, "tokens.csv", "text/csv")

            # 2. Parser Tab (AST)
            with tab2:
                if results.get('parser_error'):
                    st.error(f"Syntax Error: {results['parser_error']}")
                elif results.get('ast'):
                    st.success("Syntax Analysis Complete")
                    visualizer = ASTVisualizer()
                    try:
                        visualizer.visualize(results['ast'])
                        st.graphviz_chart(visualizer.dot)
                        # Download DOT
                        st.download_button("📥 Download AST (DOT)", visualizer.dot.source, "ast.dot", "text/plain")
                    except Exception as e:
                        st.error(f"Visualization Error: {e}")

            # 3. Semantic Analysis Tab
            with tab3:
                if results.get('semantic_error'):
                    st.error(f"Semantic Error: {results['semantic_error']}")
                elif 'semantic_output' in results:
                    if results['semantic_valid']:
                        st.success("Semantic Integrity Verified")
                    else:
                        st.warning("Semantic Warnings/Errors Found")
                    st.code(results['semantic_output'], language="text")

            # 4. ICG Tab
            with tab4:
                if results.get('icg_error'):
                    st.error(f"ICG Generation Failed: {results['icg_error']}")
                elif results.get('icg_output'):
                    st.code(results['icg_output'], language="text")
                    st.download_button("📥 Download ICG", results['icg_output'], "icg.txt", "text/plain")

            # 5. Execution Tab
            with tab5:
                if results.get('exec_error'):
                    st.error(f"Execution Error: {results['exec_error']}")
                
                output = results.get('exec_output', '')
                if output:
                    st.markdown("#### Program Output")
                    st.code(output, language="text")
                elif not results.get('exec_error'):
                     st.info("Program finished with no output.")

if __name__ == "__main__":
    main()
