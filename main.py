import os
import re
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AIQueryRequest(BaseModel):
    system: str
    prompt: str
    max_tokens: int = 1000

@app.post("/api/ai-query")
async def secure_ai_query(payload: AIQueryRequest):
    # 1. Extract the table name
    table_matches = re.findall(r'Table "([^"]+)"', payload.prompt)
    table_name = table_matches[-1] if table_matches else "dataset"
    
    # 2. Isolate the ACTUAL question
    question_match = re.search(r'Question:\s*(.*)', payload.prompt, re.IGNORECASE | re.DOTALL)
    user_question = question_match.group(1).strip() if question_match else payload.prompt
    q_lower = user_question.lower()
    
    # ---------------------------------------------------------
    # 3. EXPANDED ROUTING LOGIC (Analysis Operations)
    # ---------------------------------------------------------

    # Scenario A: Searching by Email or Phone (High Priority)
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_question)
    phone_match = re.search(r'\b\d{10}\b', user_question)
    
    if email_match:
        email = email_match.group(0)
        generated_sql = f"SELECT * FROM \"{table_name}\" WHERE email_id = '{email}';"
        explanation = f"Local Engine: Found specific email. Searching for {email}."

    elif phone_match:
        phone_num = phone_match.group(0)
        generated_sql = f'SELECT * FROM "{table_name}" WHERE mobile_number = {phone_num};'
        explanation = f"Local Engine: Found specific mobile. Searching for {phone_num}."

    # Scenario B: Math & Aggregations (Sum, Average, Max, Min)
    elif "average" in q_lower or "avg" in q_lower:
        col = extract_column(q_lower, "average", "avg")
        generated_sql = f'SELECT AVG("{col}") as average_{col} FROM "{table_name}";'
        explanation = f"Local Engine: Calculating the average for '{col}'."

    elif "total" in q_lower or "sum" in q_lower:
        col = extract_column(q_lower, "total", "sum")
        generated_sql = f'SELECT SUM("{col}") as total_{col} FROM "{table_name}";'
        explanation = f"Local Engine: Calculating the total sum for '{col}'."

    elif "highest" in q_lower or "max" in q_lower:
        col = extract_column(q_lower, "highest", "max")
        generated_sql = f'SELECT MAX("{col}") as highest_{col} FROM "{table_name}";'
        explanation = f"Local Engine: Finding the maximum value for '{col}'."

    # Scenario C: Grouping & Counting
    elif "count by" in q_lower or "group by" in q_lower:
        col = extract_column(q_lower, "count by", "group by")
        generated_sql = f'SELECT "{col}", COUNT(*) as count FROM "{table_name}" GROUP BY "{col}" ORDER BY count DESC;'
        explanation = f"Local Engine: Grouping records by '{col}' and counting them."

    # Scenario D: Find Duplicate Records
    elif "duplicate" in q_lower:
        generated_sql = f'SELECT *, COUNT(*) as count FROM "{table_name}" GROUP BY mobile_number HAVING count > 1;'
        explanation = f"Local Engine: Identifying duplicate entries."

   # Scenario E: Show Null/Missing Values
    elif "null" in q_lower or "missing" in q_lower:
        col_match = re.search(r'for\s+(\w+)', q_lower)
        
        if col_match:
            col = col_match.group(1)
            generated_sql = f'SELECT * FROM "{table_name}" WHERE "{col}" IS NULL;'
            explanation = f"Local Engine: Filtering records where column '{col}' is missing."
        else:
            # If they didn't include a column name, give them a helpful hint!
            generated_sql = f'SELECT * FROM "{table_name}" LIMIT 0;' 
            explanation = f"⚠️ Local Engine: Please specify a column! Example: 'Show null values for col_2'."

    # Scenario F: Sorting & Limiting (Top / Bottom)
    elif "top" in q_lower:
        num_match = re.search(r'\b\d+\b', q_lower)
        limit = num_match.group(0) if num_match else "5"
        generated_sql = f'SELECT * FROM "{table_name}" ORDER BY id DESC LIMIT {limit};'
        explanation = f"Local Engine: Displaying the top {limit} records."

    # Scenario G: "Show me all data" or generic "Show me" (CATCH-ALL FIX)
    else:
        generated_sql = f'SELECT * FROM "{table_name}";'
        explanation = f"Local Engine: Displaying all available records for {table_name}."

    # Format the payload exactly as the React frontend expects
    fallback_data = {
        "sql": generated_sql,
        "explanation": explanation
    }
    
    return {"text": json.dumps(fallback_data)}

# --- Helper Function ---
def extract_column(query: str, keyword1: str, keyword2: str = "") -> str:
    """A tiny helper to guess which column the user wants to analyze."""
    words = query.split()
    try:
        if keyword1 in query:
            idx = words.index(keyword1)
        else:
            idx = words.index(keyword2)
        # Assume the word immediately following the keyword is the column name
        # e.g., "average salary" -> returns "salary"
        return words[idx + 1]
    except (ValueError, IndexError):
        return "amount" # A safe fallback column name if it can't figure it out