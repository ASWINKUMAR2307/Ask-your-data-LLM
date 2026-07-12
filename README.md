# Ask-your-data-LLM
DataQuery — Ask Your Data

SQL, in plain English. Upload a CSV or Excel file, ask a question the way you'd ask a colleague, and get back the generated SQL, a live results table, and one‑click charts — all running against an in‑browser SQLite database.

🎥 Demo video: Watch here link :https://drive.google.com/file/d/1yo2sxBQO3dVkf4x_jpyB_CQdqxjBsOY2/view?usp=drive_link


✨ Features


Drag‑and‑drop ingestion — Drop a .csv, .xlsx, or .xls file and it's automatically parsed, type‑inferred, and loaded into an in‑browser SQLite table (via sql.js).
Ask in plain English — Type a question like "show top 10 customers by revenue" and the app turns it into a real SQL query.
Transparent SQL — Every answer shows the exact generated SQL alongside the results, so nothing is a black box.
Safety‑first query execution — Only single SELECT/WITH statements are allowed; destructive keywords (DROP, DELETE, UPDATE, ALTER, ATTACH, PRAGMA, etc.) are blocked before anything touches the database.
Instant visualization — Turn any result set into a bar, line, or pie chart with a couple of clicks (via Chart.js), or export it straight to CSV.
Multi‑table support — Load several files and query across tables; the sidebar shows live schema cards (columns, types, row counts) for everything you've uploaded.
Table insights — One click on a table gives you row counts, duplicate detection, and quick summary stats.
Query history — Every question you ask is saved and can be re‑run instantly from the sidebar.
100% local data processing — Your dataset never leaves the browser; only the natural‑language question (with table/column names) is sent to the query‑generation backend.



🏗️ How it works

┌─────────────────┐        ┌──────────────────────┐        ┌───────────────────────┐
│   Your CSV /     │  load  │   index.html          │  ask   │   FastAPI backend      │
│   Excel file     ├───────▶│   (sql.js / SQLite)    ├───────▶│   (main.py)            │
└─────────────────┘        │   Runs entirely in     │        │   Natural language →   │
                            │   the browser           │◀───────┤   SQL translation      │
                            └──────────────────────┘  SQL    └───────────────────────┘


Upload — index.html parses your file with PapaParse (CSV) or SheetJS (Excel), infers column types (INTEGER / REAL / TEXT), and creates a table in an in‑memory SQLite database running via WebAssembly.
Ask — Your question, together with the table schema and a couple of sample rows, is sent to the /api/ai-query endpoint.
Translate — The backend (main.py) parses your question and generates the matching SQL — handling lookups by email/phone, averages/sums/max, group‑by counts, duplicate detection, null checks, top‑N sorting, and generic "show me the data" queries.
Validate & execute — The frontend double‑checks the returned SQL (single statement, SELECT/WITH only, no destructive keywords) before running it against the local SQLite database.
Explore — Results render as a table you can sort through, chart, or export as CSV.



📁 Project structure

Ask-your-data-LLM/
├── index.html        # Entire frontend: UI, SQLite (sql.js) engine, chat, charts
├── main.py            # FastAPI backend that turns a question into SQL
├── export.py          # Utility script to dump a MySQL table to amazon_users.csv
├── amazon_users.csv   # Sample dataset for trying the app out
└── .gitignore


🚀 Getting started

Prerequisites


Python 3.9+
A modern browser (Chrome, Edge, Firefox)


1. Clone the repo

bashgit clone https://github.com/ASWINKUMAR2307/Ask-your-data-LLM.git
cd Ask-your-data-LLM

2. Run the backend

bashpip install fastapi uvicorn pydantic
uvicorn main:app --reload --port 8000

This starts the query‑generation API at http://127.0.0.1:8000, which index.html calls at /api/ai-query.

3. Open the frontend

Simply open index.html in your browser (or serve it with any static file server), then:


Drop in amazon_users.csv (included) or your own CSV/Excel file.
Ask a question, or click one of the example chips to get started.



💬 Example questions to try


"Show top 10 customers by revenue"
"Find duplicate records"
"What's the average order amount?"
"Show records with missing values for email"
"Count by city"
"Show me all data"



🔒 Security notes


The frontend only ever sends SELECT/WITH statements to the database — write/DDL operations are rejected client‑side before execution.
All uploaded data stays in‑browser (SQLite via WebAssembly); it is never uploaded to the backend.
export.py is a standalone helper for regenerating amazon_users.csv from a local MySQL instance and is not part of the running app. If you use it, move the database credentials into environment variables rather than hardcoding them.



🛠️ Tech stack

LayerTechnologyIn‑browser databasesql.js (SQLite compiled to WebAssembly)File parsingPapaParse (CSV), SheetJS (Excel)ChartsChart.jsBackend APIFastAPIFontsSpace Grotesk, Inter, JetBrains Mono


📌 Roadmap ideas


 Swap the rule‑based query engine for a full LLM‑backed NL→SQL pipeline
 Support joins across multiple uploaded tables from natural language
 Persist query history across sessions
 Add authentication for multi‑user deployments



📄 License

if you plan to accept contributions or public use.

