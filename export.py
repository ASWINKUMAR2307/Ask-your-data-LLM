import csv
from sqlalchemy import create_engine, text

# 1. Connect to your database
DATABASE_URL = "mysql+pymysql://root:AswinKumar@localhost:3306/amazon_data"
engine = create_engine(DATABASE_URL)

print("Connecting to database...")

try:
    with engine.connect() as connection:
        # 2. Run a query to get the data you want (Let's grab the users table!)
        query = text("SELECT * FROM users;")
        result = connection.execute(query)
        
        # 3. Create a new CSV file
        with open("amazon_users.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            
            # Write the column headers (user_id, first_name, etc.)
            writer.writerow(result.keys())
            
            # Write all the rows of data (Alice, Bob, etc.)
            writer.writerows(result.fetchall())
            
    print("Success! 'amazon_users.csv' has been created in your folder.")

except Exception as e:
    print("An error occurred:", e)