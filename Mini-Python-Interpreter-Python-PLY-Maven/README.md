# 🐍 Mini-Python Compiler Visualizer

A modern, interactive, and professional compiler pipeline visualizer built with **Streamlit**. Explore how a Python subset is tokenized, parsed, and interpreted in real-time.

![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 🚀 Features

- **Interactive Code Editor**: Write Python code with syntax highlighting.
- **Full Compiler Pipeline**:
  - **Lexical Analysis**: Visualize tokens in a structured table.
  - **AST Visualization**: Explore the syntax tree with interactive Graphviz charts.
  - **Semantic Analysis**: Verify type integrity and scope.
  - **Intermediate Code**: Generate and export Three-Address Code.
  - **Execution**: Run code using a custom tree-walking interpreter.
- **Export Options**: Download tokens (CSV), AST (DOT), and ICG (TXT).
- **Educational Tooltips**: Built-in documentation for each compiler phase.

## 🛠️ Project Structure

```
.
├── app.py                  # Streamlit Web App Entry Point
├── requirements.txt        # Updated Dependencies
├── src/                    # Core Compiler Logic (Refactored Package)
│   ├── lexer.py            # Lexical Analyzer
│   ├── myparser.py         # PLY-based Parser
│   ├── ast_nodes.py        # AST Node Definitions
│   ├── interpreter.py      # Tree-walking Interpreter
│   ├── semantic_analyzer.py# Type & Scope Checker
│   ├── icg_generator.py    # Intermediate Code Gen
│   └── utils.py            # AST & Visualization Utilities
├── samples/                # Sample Python Programs
└── README.md
```

## ⚙️ Setup and Installation

1. **Prerequisites**: Ensure Python 3.8+ is installed.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Graphviz (Optional but Recommended)**:
   - For AST visualization, ensure the Graphviz binary is installed on your system.
   - [Download Graphviz](https://graphviz.org/download/)

## 🏃 Running the Application

Launch the web app locally:
```bash
streamlit run app.py
```

## 🎮 Usage

1. Open the local URL provided by Streamlit (usually `http://localhost:8501`).
2. Use the **Sidebar** to load example programs or learn about compiler phases.
3. Write/Edit code in the **Source Code Editor**.
4. Click **Run / Analyze Pipeline** to update all visualization panels.
5. Export your results using the download buttons in each tab.

## 📝 Notes

- The interpreter supports a robust subset of Python (Variables, Loops, Functions, Recursion, Try-Except).
- For professional use: The logic is modularly separated for easy extension or integration.