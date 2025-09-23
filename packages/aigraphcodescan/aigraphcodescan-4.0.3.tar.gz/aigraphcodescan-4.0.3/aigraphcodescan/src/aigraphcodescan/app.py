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
JSON_OUTPUT_FILENAME = "findings.json" # This constant is now unused for the stdout logic but kept for clarity

# --- (Other functions remain the same) ---

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
    # For JSON output to stdout, we should not have any other logging
    # to avoid corrupting the JSON. We can disable it temporarily.
    if args.json_output:
        logger = setup_logging(False) # or simply use a logger that doesn't print
        logging.getLogger().setLevel(logging.CRITICAL) 
    else:
        logger = setup_logging(args.debug)
        
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
    if not args.json_output:
        logger.info(f"Processing source directory: {args.directory}")
    for dirpath, _, filenames in os.walk(args.directory):
        for fname in filenames:
            file_path = os.path.join(dirpath, fname)
            try:
                with open(file_path, 'r', encoding="utf-8") as f:
                    content = f.read()
                    grag.insert(content)
                if not args.json_output:
                    logger.debug(f"Successfully inserted {file_path}")
            except UnicodeDecodeError:
                if not args.json_output:
                    logger.warning(f"Skipping {file_path} due to encoding issues.")
            except Exception as e:
                if not args.json_output:
                    logger.error(f"Error processing file {file_path}: {e}")

    # 7. Query GraphRAG and handle output
    if not args.json_output:
        logger.info("Executing vulnerability analysis query...")

    query = (
        "Which entities that involve functions, methods, get inputs and are vulnerable to top25 sans attacks.\n"
        "List along with the corresponding file names and line numbers.\n"
        "Please respond with JSON only. No additional text. The format must be a JSON array of objects:\n"
        "```json\n"
        "[\n"
        "  {\n"
        "    \"vulnerability_description\": \"string\",\n"
        "    \"affected_lines\": \"string\",\n"
        "    \"file_name\": \"string\"\n"
        "  }\n"
        "]\n"
        "```"
    )

    data = query_grag_json(grag, query, logger)
    
    if args.json_output:
        if data:
            # Write JSON directly to stdout
            print(json.dumps(data, indent=4))
    else:
        # Original Neo4j logic
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        try:
            if data:
                # Assuming the Neo4j format is a single object, as per the original prompt
                push_to_neo4j(driver, data, logger)
        finally:
            driver.close()
            logger.info("Neo4j driver closed.")

if __name__ == "__main__":
    main()

