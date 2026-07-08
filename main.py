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
    # 1. Extract the table name from the hidden schema
    table_match = re.search(r'Table "([^"]+)"', payload.prompt)
    table_name = table_match.group(1) if table_match else "dataset"
    
    # 2. THE FIX: Isolate the ACTUAL question the user typed
    # The frontend sends "Question: [user input]". We only want to analyze that part!
    question_match = re.search(r'Question:\s*(.*)', payload.prompt, re.IGNORECASE | re.DOTALL)
    user_question = question_match.group(1).strip() if question_match else payload.prompt
    q_lower = user_question.lower()
    
    # Default fallback
    generated_sql = f'SELECT * FROM "{table_name}" LIMIT 15;'
    explanation = f"Local Engine: Executing default table preview."

    # 3. Comprehensive Routing Logic (Based strictly on the user's question)
    
    # Scenario A: "Show all records"
    if "all" in q_lower and ("record" in q_lower or "recod" in q_lower or "data" in q_lower):
        generated_sql = f'SELECT * FROM "{table_name}";'
        explanation = f"Local Engine: Displaying all available records for {table_name}."
        
    # Scenario B: "Show null values for time"
    elif "null" in q_lower:
        # Try to figure out which column they want nulls for (e.g., "for time")
        col_match = re.search(r'for\s+(\w+)', q_lower)
        col = col_match.group(1) if col_match else "time"
        generated_sql = f'SELECT * FROM "{table_name}" WHERE "{col}" IS NULL;'
        explanation = f"Local Engine: Filtering records where column '{col}' is null."
        
    # Scenario C: "Find duplicate records"
    elif "duplicate" in q_lower:
        generated_sql = f'SELECT *, COUNT(*) as count FROM "{table_name}" GROUP BY mobile_number HAVING count > 1;'
        explanation = f"Local Engine: Identified duplicate entries based on mobile numbers."
        
    # Scenario D: Search by Email or Phone
    else:
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_question)
        phone_match = re.search(r'\b\d{10}\b', user_question)
        
        if email_match:
            email = email_match.group(0)
            generated_sql = f"SELECT * FROM \"{table_name}\" WHERE email_id = '{email}';"
            explanation = f"Local Engine: Extracted email. Searching for {email}."
            
        elif phone_match:
            phone_num = phone_match.group(0)
            generated_sql = f'SELECT * FROM "{table_name}" WHERE mobile_number = {phone_num};'
            explanation = f"Local Engine: Extracted mobile. Searching for {phone_num}."
            
        # Scenario E: "Show top X customers"
        elif "top" in q_lower or "limit" in q_lower:
            num_match = re.search(r'\b\d+\b', q_lower)
            limit = num_match.group(0) if num_match else "5"
            generated_sql = f'SELECT * FROM "{table_name}" LIMIT {limit};'
            explanation = f"Local Engine: Displaying the top {limit} records."

    # Format the payload exactly as the React frontend expects
    fallback_data = {
        "sql": generated_sql,
        "explanation": explanation
    }
    
    return {"text": json.dumps(fallback_data)}