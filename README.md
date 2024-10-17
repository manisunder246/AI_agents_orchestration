# SK-GenAI-Orchestrator
A project leveraging Semantic Kernel (SK) to orchestrate AI agents for automating database tasks. It simplifies data cataloging, extraction, SQL query generation, and visualisation, making it easier to analyze and manage data from databases efficiently.

## **Table of Contents**
- [Overview](#overview)
- [Architecture](#architecture)
- [Agents](#agents)
  - [DataExtractorAgent](#dataextractoragent)
  - [SQLQueryGeneratorAgent](#sqlquerygeneratoragent)
  - [DataVizAgent](#datavizagent)
  - [CatalogingAgent](#catalogingagent)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)

---

## **Overview**

This project leverages **Semantic Kernel** to orchestrate multiple agents for automating database tasks. The agents collaborate to generate SQL queries, extract data from the database, and visualize the results, all driven by natural language input from the user. Each agent performs a specific role, and the orchestration framework ensures seamless communication between them.

---

## **Architecture**

The architecture revolves around four key agents that work together in a conversational setting, responding to user queries:

- **SQLQueryGeneratorAgent**: Generates SQL queries based on user input.
- **DataExtractorAgent**: Executes SQL queries and retrieves the relevant data.
- **DataVizAgent**: Creates visualizations from the data retrieved.
- **CatalogingAgent**: Handles metadata and data cataloging tasks.

The agents collaborate through **AgentGroupChat** to respond to user queries and process the requested operations on a database.

---

## **Agents**

### **DataExtractorAgent**
- **Role**: Executes the SQL queries generated by the `SQLQueryGeneratorAgent` and fetches the data from the database.
- **Key Functionality**: 
  - Cleans SQL queries before execution.
  - Maps results into a pandas DataFrame.
  - Provides extracted data for visualization or further analysis.

### **SQLQueryGeneratorAgent**
- **Role**: Generates valid SQL queries based on the user’s natural language input.
- **Key Functionality**:
  - Constructs SQL queries that can be executed by the `DataExtractorAgent`.
  - Integrates database schema and table summaries for precise query generation.

### **DataVizAgent**
- **Role**: Visualizes the data extracted from the database, generating plots and charts based on user requests.
- **Key Functionality**:
  - Uses extracted data to create various types of visualizations (e.g., bar, line, pie charts).
  - Communicates with the `DataExtractorAgent` to ensure accurate data representation.

### **CatalogingAgent**
- **Role**: Manages the metadata of the database tables and columns.
- **Key Functionality**:
  - Keeps track of table schemas and summaries.
  - Facilitates metadata access for query generation and execution.

---

## **How It Works**

1. **User Input**: The user provides a natural language query, such as "What are the top 5 products ordered?"
2. **SQLQuery Generation**: The `SQLQueryGeneratorAgent` processes the input and generates an SQL query.
3. **Data Extraction**: The `DataExtractorAgent` executes the generated SQL query and retrieves the data from the database.
4. **Visualization**: If requested, the `DataVizAgent` generates visualizations based on the extracted data.

---

## **Installation**

To set up the project locally, follow these steps:
1. Clone the repository:
   ```bash
   https://github.com/manisunder246/SK-GenAI-Orchestrator.git
2.Install the required dependencies:
  pip install -r requirements.txt

3. Set up your OpenAI API key in the config.py file.

4. Run the main script:
  ```python
      python main.py
   
