import os
from openai import AsyncOpenAI
import config
from semantic_kernel.functions import kernel_function

class SQLQueryGeneratorAgent:
    def __init__(self, summaries_dir="LLM_Summaries", db_names_file="schema_details/db_names.txt"):
        # Load table summaries from the local directory
        self.summaries = self.load_summaries(summaries_dir)
        self.table_schemas = self.load_table_schemas(db_names_file)  # Load table schemas

    @kernel_function
    def load_summaries(self, summaries_dir):
        """Load table summaries from the LLM_Summaries folder."""
        summaries = {}
        for filename in os.listdir(summaries_dir):
            if filename.endswith('_summary.txt'):
                table_name = filename.replace('_summary.txt', '')
                with open(os.path.join(summaries_dir, filename), 'r') as file:
                    summaries[table_name] = file.read()
        return summaries

    @kernel_function
    def load_table_schemas(self, db_names_file):
        """Load table names and schemas from the provided file."""
        table_schemas = {}
        with open(db_names_file, 'r') as file:
            for line in file:
                parts = line.split(':')
                if len(parts) == 2:
                    table_name = parts[0].strip()
                    schema_name = parts[1].strip()
                    table_schemas[table_name] = schema_name
        return table_schemas

    @kernel_function
    async def generate_sql_query(self, user_query):
        print(f"Generating SQL query for user input: {user_query}")
        """Generate an SQL query using LLM based on user query and table summaries."""
        # Step 1: Construct the LLM prompt
        prompt = self.construct_prompt(user_query)

        # Step 2: Call the LLM API to generate the SQL query
        return await self.call_llm_to_generate_sql(prompt)

    @kernel_function
    def construct_prompt(self, user_query):
        """Construct a detailed prompt for LLM based on user query and table summaries."""
        summary_text = "\n\n".join([f"Table: {self.table_schemas[table]}\n{summary}" for table, summary in self.summaries.items() if table in self.table_schemas])
        
        prompt = f"""
        The user has asked the following question: '{user_query}'.

        You have access to the following database tables and their summaries:
        {summary_text}

        Your task is to generate a valid SQL query based on the user's question and the provided table summaries. 
        Ensure that the SQL query is compatible with **SQL Server** syntax. Follow the below instructions.

        IMPORTANT INSTRUCTIONS:
        - Use `TOP` instead of `LIMIT` to limit results.
        - Use `+` for string concatenation.
        - Use `GETDATE()` instead of `NOW()` for current date and time.
        - Use `ISNULL(expression, replacement)` instead of `IFNULL()`.
        - Use `IDENTITY` instead of `AUTO_INCREMENT` for auto-increment columns.
        - In SQL Server, `GROUP BY` does not require all `SELECT` columns to be part of the aggregation.
        - Use `BIT` for boolean values (`1` for true, `0` for false).
        - Use single quotes (`'`) for string literals.
        - Avoid redundant prefixes when referencing tables.
        

        And follow SQL Server conventions. Use the table_name as is. DON'T USE any other convention w.r.t the table name.
        Important: The output will be directly executed, so only return the SQL query without any extra text.
        """
        return prompt

    @kernel_function
    async def call_llm_to_generate_sql(self, prompt):
        """Call OpenAI's GPT-4 to generate SQL query based on the prompt."""
        client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating SQL query: {e}")
            return "Error generating SQL query."
