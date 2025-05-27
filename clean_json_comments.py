# clean_json_comments.py
# -*- coding: utf-8 -*-
import os
import re

INPUT_JSON_FILE = "structured_cement_db.json" 
# سنقوم بحفظ الملف النظيف باسم جديد لتجنب الكتابة فوق الأصلي مباشرة في حال أردنا مراجعته
OUTPUT_JSON_FILE = "structured_cement_db_cleaned.json" 

def remove_json_comments(file_path):
    """
    Reads a file, removes lines or parts of lines starting with //,
    and returns the cleaned content as a single string.
    """
    cleaned_lines = []
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' not found.")
        return None

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f: # utf-8-sig to handle potential BOM
            for line in f:
                # Remove comments starting with //
                # This will remove the comment and anything after it on the same line
                cleaned_line = re.sub(r"//.*$", "", line)
                cleaned_lines.append(cleaned_line)

        # Join all lines back into a single string
        return "".join(cleaned_lines)
    except Exception as e:
        print(f"Error reading or processing file '{file_path}': {type(e).__name__} - {e}")
        return None

if __name__ == "__main__":
    print(f"Starting to clean comments from '{INPUT_JSON_FILE}'...")

    cleaned_json_content = remove_json_comments(INPUT_JSON_FILE)

    if cleaned_json_content:
        try:
            # Attempt to save the cleaned content
            with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f_out: # Save as UTF-8 (without BOM by default from Python's open)
                f_out.write(cleaned_json_content)
            print(f"Successfully removed comments and saved cleaned data to '{OUTPUT_JSON_FILE}'.")
            print("Please now try using this cleaned file with 'cement_database_explorer.py'.")
            print(f"You might need to rename '{OUTPUT_JSON_FILE}' to '{INPUT_JSON_FILE}'")
            print(f"or change the DATABASE_FILE variable in 'cement_database_explorer.py' to '{OUTPUT_JSON_FILE}'.")
        except Exception as e:
            print(f"Error writing cleaned file '{OUTPUT_JSON_FILE}': {type(e).__name__} - {e}")
    else:
        print("No content was cleaned or an error occurred during reading.")

    print("\nCleaning script finished.")
