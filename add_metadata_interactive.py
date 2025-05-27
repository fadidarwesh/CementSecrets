# add_metadata_interactive.py
# -*- coding: utf-8 -*-
import os
import json

# --- Predefined lists for metadata ---
CEMENT_TYPES_OPTIONS = [
    "General/Not Specific", # If the chunk is introductory or covers multiple types
    "G CEM I 32.5N", "G CEM I 32.5R",
    "G CEM I 42.5N", "G CEM I 42.5R",
    "G CEM I 52.5N", "G CEM I 52.5R",
    "W CEM I 32.5N", "W CEM I 32.5R",
    "W CEM I 42.5N", "W CEM I 42.5R",
    "W CEM I 52.5N", "W CEM I 52.5R",
    "Other" # If you need to specify a type not listed
]

TOPIC_OPTIONS = [
    "Introduction/General",
    "Definition",
    "Composition",
    "Physical and Chemical Properties",
    "Typical Applications",
    "Benefits and Advantages",
    "Technical and Commercial Evaluation",
    "Other" # If you need to specify a topic not listed
]

DEFAULT_STANDARD = "EN 197-1"

def get_user_choice(prompt_message, options_list):
    """Displays options and gets a valid choice from the user."""
    print(f"\n{prompt_message}")
    for i, option in enumerate(options_list):
        print(f"{i+1}. {option}")

    while True:
        try:
            choice = int(input(f"Enter your choice (1-{len(options_list)}): "))
            if 1 <= choice <= len(options_list):
                return options_list[choice-1]
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(options_list)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# --- Main part of the script ---
if __name__ == "__main__":
    print("Interactive Metadata Addition Script Running...")

    embeddings_db_path = os.path.join(os.getcwd(), "embeddings_database.json")
    # Output file for enriched data (data from your book only)
    output_enriched_db_path = os.path.join(os.getcwd(), "book_enriched_embeddings.json") 

    # The source file we are focusing on (your book)
    TARGET_SOURCE_FILE = "Cement_Types_CEM_I_Book_chunks.txt"

    if not os.path.exists(embeddings_db_path):
        print(f"Error: Embeddings database file '{embeddings_db_path}' not found.")
        print("Please run the generate_embeddings.py script first.")
    else:
        try:
            with open(embeddings_db_path, "r", encoding="utf-8") as f:
                all_embeddings_data = json.load(f)

            book_chunks_data = [item for item in all_embeddings_data if item.get("source_file") == TARGET_SOURCE_FILE]

            if not book_chunks_data:
                print(f"No chunks found from the source file: {TARGET_SOURCE_FILE}")
            else:
                print(f"Found {len(book_chunks_data)} chunks from '{TARGET_SOURCE_FILE}' to process.")

                enriched_data_list = []

                # Ask user how many chunks to process in this session
                num_to_process_str = input(f"How many chunks would you like to process in this session? (Enter a number, or 'all' for all {len(book_chunks_data)} chunks): ")

                if num_to_process_str.lower() == 'all':
                    num_to_process = len(book_chunks_data)
                else:
                    try:
                        num_to_process = int(num_to_process_str)
                        if not (0 < num_to_process <= len(book_chunks_data)):
                            print(f"Invalid number. Processing all {len(book_chunks_data)} chunks instead.")
                            num_to_process = len(book_chunks_data)
                    except ValueError:
                        print(f"Invalid input. Processing all {len(book_chunks_data)} chunks instead.")
                        num_to_process = len(book_chunks_data)

                for i, chunk_item in enumerate(book_chunks_data[:num_to_process]):
                    print(f"\n--- Processing Chunk {i+1}/{num_to_process} ---")
                    print("Text:")
                    print(chunk_item["text"])
                    print("--------------------")

                    # Get Cement Type
                    cement_type_choice = get_user_choice("Select Cement Type for this chunk:", CEMENT_TYPES_OPTIONS)
                    if cement_type_choice == "Other":
                        cement_type_choice = input("Enter custom Cement Type: ")

                    # Get Main Topic
                    topic_choice = get_user_choice("Select Main Topic for this chunk:", TOPIC_OPTIONS)
                    if topic_choice == "Other":
                        topic_choice = input("Enter custom Main Topic: ")

                    # Get Standard
                    standard_input = input(f"Enter Standard (default is '{DEFAULT_STANDARD}', press Enter to use default): ")
                    if not standard_input.strip():
                        standard_choice = DEFAULT_STANDARD
                    else:
                        standard_choice = standard_input.strip()

                    # Create new enriched item
                    enriched_item = {
                        "source_file": chunk_item["source_file"],
                        "text": chunk_item["text"],
                        "embedding": chunk_item["embedding"],
                        "metadata": {
                            "cement_type": cement_type_choice,
                            "main_topic": topic_choice,
                            "standard": standard_choice
                        }
                    }
                    enriched_data_list.append(enriched_item)
                    print("Metadata added for this chunk.")

                # Save the enriched data
                if enriched_data_list:
                    # If processing in batches, you might want to load existing enriched data and append
                    # For simplicity now, this will overwrite or create a new file each time based on what's processed in the session.
                    # A more robust solution would merge if output_enriched_db_path already exists.
                    # For now, we'll save only what was processed in this session.

                    # Let's try to load existing data if it exists, and append new, unique entries
                    existing_enriched_data = []
                    if os.path.exists(output_enriched_db_path):
                        try:
                            with open(output_enriched_db_path, "r", encoding="utf-8") as f_existing:
                                existing_enriched_data = json.load(f_existing)
                            print(f"\nLoaded {len(existing_enriched_data)} existing enriched entries.")
                        except json.JSONDecodeError:
                            print(f"Warning: Could not decode existing file '{output_enriched_db_path}'. It will be overwritten.")

                    # Simple way to avoid duplicates if re-processing: use text as a key
                    # This is basic; a more robust approach would use unique IDs for chunks.
                    combined_data_dict = {item['text']: item for item in existing_enriched_data}
                    for new_item in enriched_data_list:
                        combined_data_dict[new_item['text']] = new_item # New or updated items will overwrite

                    final_data_to_save = list(combined_data_dict.values())

                    with open(output_enriched_db_path, "w", encoding="utf-8") as f_out:
                        json.dump(final_data_to_save, f_out, ensure_ascii=False, indent=4)
                    print(f"\nSuccessfully saved/updated {len(final_data_to_save)} enriched chunks to: {output_enriched_db_path}")
                else:
                    print("\nNo chunks were processed in this session.")

        except Exception as e:
            print(f"An error occurred: {type(e).__name__} - {e}")

    print("\nScript finished.")
