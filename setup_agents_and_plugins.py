from semantic_kernel import Kernel
from semantic_kernel.agents.open_ai import OpenAIAssistantAgent
from Agents.data_catalogue_agent import DataCatalogueAgent
from Agents.sql_query_generator_agent import SQLQueryGeneratorAgent
from Agents.data_extractor_agent import DataExtractorAgent
from Agents.data_viz_agent import DataVizAgent
from Agents.data_catalogue_agent import get_db_connection
from semantic_kernel.agents.group_chat.agent_group_chat import AgentGroupChat
from semantic_kernel.agents.strategies.selection.kernel_function_selection_strategy import KernelFunctionSelectionStrategy
from semantic_kernel.functions.kernel_function_from_prompt import KernelFunctionFromPrompt
import asyncio
import config
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
# Define constants for agent names
DATA_VIZ = "DataViz"
DATA_EXT = "DataExtractor"
SQL_QUERY = "QueryGen"
CATALOG = "Cataloging"

async def setup_agents(user_input):
    # Initialize the kernel
    kernel = Kernel()

    # Establish the database connection
    connection = get_db_connection()

    # Add plugins to the kernel
    kernel.add_plugin(DataCatalogueAgent(connection), plugin_name="DataCatalogue")
    kernel.add_plugin(DataExtractorAgent(connection), plugin_name="DataExtractor")
    kernel.add_plugin(SQLQueryGeneratorAgent(), plugin_name="SQLQueryGenerator")
    kernel.add_plugin(DataVizAgent(DataExtractorAgent(connection)), plugin_name="DataViz")

    # Add services to the kernel
    kernel.add_service(OpenAIChatCompletion(ai_model_id= "gpt-4o", service_id=CATALOG, api_key=config.OPENAI_API_KEY))
    kernel.add_service(OpenAIChatCompletion(ai_model_id= "gpt-4o",service_id=SQL_QUERY, api_key=config.OPENAI_API_KEY))
    kernel.add_service(OpenAIChatCompletion(ai_model_id= "gpt-4o",service_id=DATA_EXT, api_key=config.OPENAI_API_KEY))
    kernel.add_service(OpenAIChatCompletion(ai_model_id= "gpt-4o",service_id=DATA_VIZ, api_key=config.OPENAI_API_KEY))

    # Create agents using constants for service_id and name
    try:
        cataloging_agent = await OpenAIAssistantAgent.create(
            kernel=kernel,
            service_id=CATALOG,  # Use constant CATALOG as service_id
            name=CATALOG,
            instructions="This agent handles cataloging tasks using the DataCatalogue plugin.",
            api_key=config.OPENAI_API_KEY,
            ai_model_id="gpt-4o"
        )

        query_gen_agent = await OpenAIAssistantAgent.create(
            kernel=kernel,
            service_id=SQL_QUERY,  # Use constant SQL_QUERY as service_id
            name=SQL_QUERY,
            instructions="This agent generates SQL queries based on user input using the SQLQueryGenerator plugin.",
            api_key=config.OPENAI_API_KEY,
            ai_model_id="gpt-4o"
        )

        data_extractor_agent = await OpenAIAssistantAgent.create(
            kernel=kernel,
            service_id=DATA_EXT,  # Use constant DATA_EXT as service_id
            name=DATA_EXT,
            instructions="This agent executes SQL queries and retrieves data using the DataExtractor plugin.",
            api_key=config.OPENAI_API_KEY,
            ai_model_id="gpt-4o"
        )

        data_viz_agent = await OpenAIAssistantAgent.create(
            kernel=kernel,
            service_id=DATA_VIZ,  # Use constant DATA_VIZ as service_id
            name=DATA_VIZ,
            instructions="""
                Your responsibility is to generate insightful and accurate visualizations based on data retrieved by the DataExtractorAgent.
                
                You should:
                - Choose the most appropriate visualization type based on the structure and nature of the dataset.
                - Use Matplotlib or any other suitable libraries to generate the plots.
                - When creating visualizations, ensure clarity and relevance. Label axes, provide legends, and use appropriate color schemes.
                - Handle various types of user queries including bar charts, line graphs, scatter plots, pie charts, and histograms.
                - If previous data has been fetched by DataExtractorAgent, use it to create visualizations upon request.

                RULES:
                - Never fetch data directly from the database. Only visualize the data retrieved by the DataExtractorAgent.
                - If the user requests clarification or changes to the visualization, adapt accordingly and regenerate the visualization.
                - Always ensure the visualization is contextually relevant to the query, and explain the plot if needed.
                """,
            api_key=config.OPENAI_API_KEY,
            ai_model_id="gpt-4o"
        )

    except Exception as e:
        print(f"Error during agent creation: {e}")

    # Custom selection strategy based on user input
    selection_function = KernelFunctionFromPrompt(
        function_name="agent_selection",
        prompt=f"""
        Based on the user query, select the appropriate agent:
        - If the query involves data retrieval or executing SQL queries, use {DATA_EXT}.
        - If the query involves generating visualizations based on previously retrieved data, use {DATA_VIZ}.
        - If the user specifically asks for an SQL query generation, use {SQL_QUERY}.
        - Always ensure the DataViz agent references results from the DataExtractor if the user requests a plot.

        Consider the conversation history to determine which agent should act next:
        - If the DataExtractor has already retrieved results, pass the retrieved data to DataViz for visualization.
        - Use chat history to fetch the most recent result data from DataExtractor for DataViz to create the appropriate visualization.

        State only the name of the agent selected and nothing more.
        
        User query: '{user_input}'
        
        Available agents:
        - {CATALOG}
        - {SQL_QUERY}
        - {DATA_EXT}
        - {DATA_VIZ}

        History:
        {{{{$history}}}}
        """,
    )

    # Define a function to log and parse the result
    def log_and_parse_result(result):
        print(f"Selection Function Result: {result}")  # Log the entire result object
        if result.value is not None:
            return str(result.value[0])  # Return the first value (agent name)
        else:
            return DATA_EXT
    # Add agents to the group chat using their constants as service_id
    agent_group_chat = AgentGroupChat(
        agents=[cataloging_agent, query_gen_agent, data_extractor_agent, data_viz_agent],
        selection_strategy=KernelFunctionSelectionStrategy(
            function=selection_function,
            kernel=kernel,
            result_parser=lambda result: log_and_parse_result(result),
            agent_variable_name="agents",
            history_variable_name="history",
        )
    )
    
    history = []
    async for message in agent_group_chat.get_chat_messages():
        history.append(message)


    print("Plugins and agents have been successfully set up in the kernel and added to the AgentGroupChat.")
    print(f"History so far is :{history}")
    agents = {
    'cataloging_agent': cataloging_agent,
    'query_gen_agent': query_gen_agent,
    'data_extractor_agent': data_extractor_agent,
    'data_viz_agent': data_viz_agent
    }
    return agent_group_chat, agents
