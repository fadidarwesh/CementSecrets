# cement_database_explorer.py
# -*- coding: utf-8 -*-
import os
import json

DATABASE_FILE = "structured_cement_db.json"

def load_database(db_file):
    """Loads the cement database from the JSON file."""
    if not os.path.exists(db_file):
        print(f"Error: Database file '{db_file}' not found.")
        return None
    try:
        with open(db_file, "r", encoding="utf-8-sig") as f: # Handles potential BOM
            database = json.load(f)
        print(f"Successfully loaded database from '{db_file}'.")
        return database
    except Exception as e:
        print(f"Error loading database: {type(e).__name__} - {e}")
        return None

def print_property_item(item):
    """Helper function to print a property item nicely."""
    if isinstance(item, dict):
        prop_name = item.get('property', item.get('property_note', item.get('note', 'Detail'))) # Prioritize 'property', then 'property_note', then 'note'

        # If the main key is 'note' and it's the only key, it's likely a simple note string.
        if prop_name == 'Detail' and list(item.keys()) == ['note']:
             print(f"  - Note: {item['note']}")
             return

        parts = [f"{prop_name}:"]

        value = item.get('value')
        value_min = item.get('value_min')
        value_max = item.get('value_max')
        unit = item.get('unit', '')
        typical_range = item.get('typical_range')
        typical_values_note = item.get('typical_values_note')
        note = item.get('note', '') # General note for the property

        if value is not None:
            parts.append(str(value))
        if value_min is not None:
            parts.append(str(value_min))
        if value_max is not None:
            if value_min is not None: # if there was a min, add 'to'
                parts[-1] += f" to {value_max.replace('<= ', '').replace('≤ ', '')}" # append to min_value string, remove operator for max
            else:
                parts.append(str(value_max))

        if unit:
            parts.append(unit)

        if typical_range is not None:
            parts.append(f"(Typical Range: {typical_range}")
            if item.get('examples'):
                 parts[-1] += f", Examples: {item['examples']}"
            if item.get('alternative_range'):
                parts[-1] += f", Alt: {item['alternative_range']}"
            parts[-1] += ")"


        # Add notes, ensuring the primary 'note' field is prioritized if 'property' was the main key
        if note and prop_name != item.get('note'): # General note
             parts.append(f"(Note: {note})")
        elif typical_values_note : # Specific note for typical values
            parts.append(f"({typical_values_note})")


        print(f"  - {' '.join(parts)}")

    else: # If the item in the list is just a string
        print(f"  - {item}")


def display_cement_details(cement_data):
    """Displays the details for a selected cement type."""
    if not cement_data:
        print("No data to display for this cement type.")
        return

    cement_display_name = cement_data.get('name_with_color_prefix', 'N/A')
    print(f"\n--- Details for: {cement_display_name} ---")

    categories = {
        "definition": "Definition",
        "composition": "Composition",
        "mandatory_physical_properties": "Mandatory Physical Properties",
        "optional_physical_properties": "Optional Physical Properties",
        "optional_physical_properties_for_white": "Optional Physical Properties (White Cement Specific)",
        "optional_physical_properties_for_white_high_strength": "Optional Physical Properties (White High Strength)",
        "optional_physical_properties_very_high_performance_white": "Optional Physical Properties (White Very High Performance)",
        "mandatory_chemical_properties": "Mandatory Chemical Properties",
        "property_note_for_white": "Chemical Property Note (White Cement)",
        "effects_of_limit_deviations": "Effects of Limit Deviations",
        "effects_of_chemical_limit_deviations": "Effects of Chemical Limit Deviations",
        "effects_of_fineness_and_main_compounds_for_white": "Effects of Fineness & Main Compounds (White Cement)",
        "typical_applications": "Typical Applications",
        "benefits_and_features": "Benefits and Features",
        "star_rating_evaluation": "Star Rating Evaluation",
        "usage_contraindications_or_precautions": "Usage Contraindications/Precautions",
        "usage_notes_from_ocr": "OCR Usage Notes"
    }

    available_categories_in_data = []
    print("\nAvailable information categories:")
    idx = 1
    for key, display_name in categories.items():
        if key in cement_data and cement_data[key]:
            print(f"{idx}. {display_name}")
            available_categories_in_data.append(key)
            idx += 1

    if not available_categories_in_data:
        print("No specific data categories found for this cement type in the database.")
        return

    print(f"{idx}. Display All Information for this Cement Type")
    print(f"{idx+1}. Back to Cement Type Selection")

    try:
        choice_input_str = input(f"Select a category (1-{idx+1}): ")
        if not choice_input_str:
            print("No selection made.")
            return
        choice_input = int(choice_input_str)

        if 1 <= choice_input < idx:
            selected_key = available_categories_in_data[choice_input-1]
            print(f"\n--- {categories[selected_key]} for {cement_display_name} ---")
            data_to_display = cement_data[selected_key]

            if isinstance(data_to_display, dict):
                for sub_key, sub_value in data_to_display.items():
                    print(f"\n  {sub_key.replace('_', ' ').capitalize()}:")
                    if isinstance(sub_value, dict): # e.g., star_rating items, effects_of_limit_deviations
                        for item_key, item_value in sub_value.items():
                            if isinstance(item_value, dict) and "stars" in item_value : # star rating items
                                print(f"    - {item_key.replace('_', ' ').capitalize()}: {item_value.get('rating_text','')} {item_value.get('comment','')}")
                            else: # other dicts like SO3 effects
                                 print(f"    - {item_key.replace('_', ' ').capitalize()}: {item_value}")
                    elif isinstance(sub_value, list): # e.g., details under clinker_k
                        for item in sub_value:
                            print_property_item(item) # Use helper for lists
                    else: # simple string value
                        print(f"    {sub_value}")
            elif isinstance(data_to_display, list): # For lists like physical/chemical properties, applications
                for item in data_to_display:
                    print_property_item(item) # Use helper for lists
            else: # Simple string like definition
                print(data_to_display)

        elif choice_input == idx: # Display All
            print(f"\n--- All Information for {cement_display_name} ---")
            for cat_key in available_categories_in_data: # Iterate only through available categories
                print(f"\n--- {categories[cat_key]} ---")
                data_to_display = cement_data[cat_key]
                if isinstance(data_to_display, dict):
                    for sub_key, sub_value in data_to_display.items():
                        print(f"\n  {sub_key.replace('_', ' ').capitalize()}:")
                        if isinstance(sub_value, dict):
                            for item_key, item_value in sub_value.items():
                                if isinstance(item_value, dict) and "stars" in item_value :
                                    print(f"    - {item_key.replace('_', ' ').capitalize()}: {item_value.get('rating_text','')} {item_value.get('comment','')}")
                                else:
                                     print(f"    - {item_key.replace('_', ' ').capitalize()}: {item_value}")
                        elif isinstance(sub_value, list):
                            for item in sub_value:
                               print_property_item(item)
                        else:
                            print(f"    {sub_value}")
                elif isinstance(data_to_display, list):
                    for item in data_to_display:
                       print_property_item(item)
                else:
                    print(data_to_display)
                print("--------------------")

        elif choice_input == idx+1: # Back
            return
        else:
            print(f"Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An error occurred in display_cement_details: {type(e).__name__} - {e}")


if __name__ == "__main__":
    cement_db = load_database(DATABASE_FILE)

    if cement_db and "cement_types" in cement_db and cement_db["cement_types"]:
        cement_types_list = cement_db["cement_types"]

        while True:
            print("\n--- Cement Database Explorer (EN 197-1) ---")
            print("\nAvailable Cement Types:")
            for i, cement in enumerate(cement_types_list):
                print(f"{i+1}. {cement.get('name_with_color_prefix', 'Unknown Cement Type')}")
            print(f"{len(cement_types_list)+1}. Exit")

            try:
                user_choice_idx_str = input(f"Select a cement type (1-{len(cement_types_list)+1}): ")
                if not user_choice_idx_str:
                    print("No selection made. Please try again.")
                    continue
                user_choice_idx = int(user_choice_idx_str)

                if 1 <= user_choice_idx <= len(cement_types_list):
                    selected_cement = cement_types_list[user_choice_idx-1]
                    # Loop within the details display until user chooses to go back
                    while True:
                        display_cement_details(selected_cement)
                        # The back option in display_cement_details will break its inner loop
                        # We need a way to know if the user chose "Back" to break this outer loop for the cement type
                        # For simplicity, display_cement_details will now just return after "Back"
                        # So we need to present the main menu again, or check if we should exit
                        # Let's refine this: display_cement_details should handle its own loop and return if 'Back' is selected

                        # Re-prompt after displaying details, or break if 'Back' was chosen
                        # This logic is now handled inside display_cement_details's own loop structure
                        # If display_cement_details finishes, it means "Back" was selected or an error occurred.
                        # Let's assume "Back" brings us here.
                        break # Break from the inner cement-specific detail loop to show cement list again

                elif user_choice_idx == len(cement_types_list)+1:
                    print("Exiting Cement Database Explorer. Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except Exception as e:
                print(f"An unexpected error occurred in main loop: {type(e).__name__} - {e}")
    else:
        print("Could not load database or the database is empty/corrupted. Exiting.")

    print("\nScript finished.")
