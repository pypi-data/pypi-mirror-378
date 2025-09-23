# src/aigraphcodescan/app.py
import json
import os
import uuid
import logging
import argparse
import sys
import time
from neo4j import GraphDatabase
from fast_graphrag import GraphRAG

# --- Configuration Constants ---
DEFAULT_WORKING_DIR = "./.graph"
MAX_JSON_RETRIES = 5
RETRY_DELAY_SECONDS = 2
JSON_OUTPUT_FILENAME = "findings.json"

# --- Logger Setup ---
def setup_logging(debug_mode, json_output_mode=False):
    """Configures the application's logging."""
    if json_output_mode:
        logging_level = logging.CRITICAL
    else:
        logging_level = logging.DEBUG if debug_mode else logging.INFO

    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

# --- GraphRAG and Neo4j Configuration ---
def get_graph_rag_config():
    """Returns a dictionary of GraphRAG configuration."""
    domain_description = (
        "You are a highly skilled and meticulous security code review expert. Your primary task is to identify and "
        "analyze potential security vulnerabilities within a given code snippet. Your analysis must be thorough, "
        "focusing on the entire data lifecycle, from input to a potential security sink.\n\n"
        "Your analysis should consider and report on the following aspects:\n"
        "- **Input Flow:** Describe how user input is received and where it enters the codebase.\n"
        "- **Data & Control Flow:** Trace the path of user-controlled data. Note if it reaches a sensitive function (a \"sink\") without proper handling.\n"
        "- **Input Validation & Sanitization:** Evaluate whether the code adequately validates, sanitizes, or encodes user input to neutralize malicious payloads.\n"
        "- **Vulnerability Identification:** Identify and explain any specific security flaws, such as SQL Injection, Cross-Site Scripting (XSS), Command Injection, or Path Traversal.\n"
        "- **Taint Analysis:** Perform a high-level taint analysis, determining if untrusted input is properly \"tainted\" and if this tainted data flows into a sink.\n\n"
        "You must provide your final output in a structured, actionable report format with the following sections:\n"
        "- **Vulnerability Description:** A clear and concise explanation of the security flaw.\n"
        "- **Affected Code:** The specific lines or a small block of code where the vulnerability exists.\n"
        "- **Suggested Fix:** A concrete, secure coding recommendation to remediate the vulnerability.\n"
    )

    example_queries = [
        "What are the functions used?", "What are the objects and methods used?",
        "Which functions take input from the user?", "What are the sinks?",
        "What is the control flow?", "What is the data flow?",
        "Which vulnerable functions are used?",
        "Which inputs are not tainted after reaching the sink?",
        "What is the filename?", "What is the linenumber?",
    ]
    entity_types = [
        "Type", "Category", "Filename", "Linenumber", "Input",
        "Function", "Object", "Method", "Tainted", "Untainted", "Sink"
    ]
    
    return {
        "domain": domain_description,
        "example_queries": "\n".join(example_queries),
        "entity_types": entity_types,
    }

# --- Neo4j Database Operations ---
def test_connection(driver, logger):
    """Tests the Neo4j connection by running a simple query."""
    try:
        with driver.session() as session:
            session.run("RETURN 'Connection Successful' AS message")
            logger.info("Connection to Neo4j successful.")
    except Exception as e:
        logger.critical(f"Connection test failed: {e}")
        sys.exit(1)

def clear_database(driver, logger):
    """Deletes all nodes and relationships in the database."""
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared.")
    except Exception as e:
        logger.error(f"Error clearing the database: {e}")

def initialize_database(driver, logger):
    """Initializes the Neo4j database with constraints."""
    try:
        with driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE")
            logger.info("Database initialized with constraints.")
    except Exception as e:
        logger.error(f"Error initializing the database: {e}")

# --- Main Application Logic ---
def query_grag_json(grag, query, logger):
    """
    Queries grag and ensures the response is valid JSON.
    Retries with a backoff strategy until it gets valid JSON or reaches the limit.
    """
    for attempt in range(MAX_JSON_RETRIES):
        try:
            response = grag.query(query).response
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Response (Attempt {attempt + 1}): {response}")
            
            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON, retrying in {RETRY_DELAY_SECONDS}s... "
                           f"Error: {e} (Attempt {attempt + 1}/{MAX_JSON_RETRIES})")
            time.sleep(RETRY_DELAY_SECONDS)
        except Exception as e:
            logger.error(f"An unexpected error occurred during query: {e}")
            break
            
    logger.error("Failed to get valid JSON response after multiple retries.")
    return None

def push_to_neo4j(driver, json_data, logger):
    """Pushes JSON data to Neo4j, handling both single objects and lists."""
    if not json_data:
        logger.info("No data to push to Neo4j.")
        return

    # Ensure json_data is a list
    if not isinstance(json_data, list):
        json_data = [json_data]

    try:
        with driver.session() as session:
            for item in json_data:
                # Use a unique ID for each entity
                entity_id = str(uuid.uuid4())
                filename = item.get("filename", "Unknown")
                vulnerability = item.get("description", "Unknown") # Updated key here
                linenumber = item.get("line", "Unknown") # Updated key here

                query = """
                MERGE (n:Entity {
                    id: $id,
                    Filename: $filename,
                    vulnerability: $vulnerability,
                    Linenumber: $linenumber
                })
                """
                session.run(query, id=entity_id, filename=filename, vulnerability=vulnerability, linenumber=linenumber)

        logger.info("Graph data successfully pushed to Neo4j.")
    except Exception as e:
        logger.error(f"Error pushing data to Neo4j: {e}")

def main():
    """Main function to parse arguments, run the analysis, and handle output."""
    # 1. Argument Parsing
    parser = argparse.ArgumentParser(description="Analyze code for security vulnerabilities using GraphRAG and Neo4j.")
    parser.add_argument('--debug', action='store_true', help='Enable debug logging.')
    parser.add_argument('--directory', type=str, required=True, help='Directory with source code to analyze.')
    parser.add_argument('--graphdirectory', type=str, default=DEFAULT_WORKING_DIR, help='Directory to store generated graphs.')
    parser.add_argument('--json-output', action='store_true', help='Output findings to standard output as JSON.')
    args = parser.parse_args()

    # 2. Setup Logging and Initial Checks
    logger = setup_logging(args.debug, args.json_output)
    
    if not os.path.isdir(args.directory):
        logger.critical(f"Source directory not found: {args.directory}")
        sys.exit(1)

    # 3. Environment-driven Configuration
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not args.json_output and not neo4j_password:
        logger.critical("NEO4J_PASSWORD environment variable is not set. Exiting.")
        sys.exit(1)

    # 4. Initialize Components
    grag_config = get_graph_rag_config()
    grag = GraphRAG(
        working_dir=args.graphdirectory,
        domain=grag_config["domain"],
        example_queries=grag_config["example_queries"],
        entity_types=grag_config["entity_types"],
    )
    
    # 5. Database operations or JSON output based on flag
    if not args.json_output:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        try:
            test_connection(driver, logger)
            clear_database(driver, logger)
            initialize_database(driver, logger)
        finally:
            driver.close()

    # 6. Insert Files into GraphRAG
    logger.info(f"Processing source directory: {args.directory}")
    for dirpath, _, filenames in os.walk(args.directory):
        for fname in filenames:
            file_path = os.path.join(dirpath, fname)
            try:
                with open(file_path, 'r', encoding="utf-8") as f:
                    content = f.read()
                    grag.insert(content)
                logger.debug(f"Successfully inserted {file_path}")
            except UnicodeDecodeError:
                logger.warning(f"Skipping {file_path} due to encoding issues.")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")

    # 7. Query GraphRAG and handle output
    logger.info("Executing vulnerability analysis query...")

    query = (
        "Which entities that involve functions, methods, get inputs and are vulnerable to top25 sans attacks.\n"
        "List along with the corresponding file names and line numbers.\n"
        "Please respond with JSON only. No additional text. The format must be a JSON array of objects:\n"
        "```json\n"
        "[\n"
        "  {\n"
        "    \"description\": \"string\",\n"
        "    \"line\": \"string\",\n"
        "    \"filename\": \"string\"\n"
        "  }\n"
        "]\n"
        "```"
    )

    data = query_grag_json(grag, query, logger)
    
    if args.json_output:
        if data:
            print(json.dumps(data, indent=4))
    else:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        try:
            if data:
                push_to_neo4j(driver, data, logger)
        finally:
            driver.close()
            logger.info("Neo4j driver closed.")

if __name__ == "__main__":
    main()
