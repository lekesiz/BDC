#!/usr/bin/env python3
import json
import os

def load_json(file_path):
    """Load JSON file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_untranslated_keys(source_dict, target_dict, path=""):
    """Recursively find keys where values are identical to English (untranslated)."""
    untranslated = []
    
    for key, value in source_dict.items():
        current_path = f"{path}.{key}" if path else key
        
        if key not in target_dict:
            untranslated.append((current_path, "Missing key"))
            continue
            
        if isinstance(value, dict):
            # Recursive case
            untranslated.extend(find_untranslated_keys(value, target_dict[key], current_path))
        else:
            # Base case - compare values
            if target_dict[key] == value and value.strip():  # Same as English and not empty
                untranslated.append((current_path, value))
    
    return untranslated

def analyze_translations():
    """Analyze translation files and generate report."""
    base_dir = "/Users/mikail/Desktop/BDC/client/src/i18n/locales"
    
    # Load English as reference
    en_data = load_json(os.path.join(base_dir, "en.json"))
    
    languages = {
        "tr": "Turkish",
        "ar": "Arabic", 
        "es": "Spanish"
    }
    
    report = {}
    
    for lang_code, lang_name in languages.items():
        file_path = os.path.join(base_dir, f"{lang_code}.json")
        if os.path.exists(file_path):
            lang_data = load_json(file_path)
            untranslated = find_untranslated_keys(en_data, lang_data)
            report[lang_name] = {
                "total_untranslated": len(untranslated),
                "untranslated_keys": untranslated[:20]  # Show first 20
            }
        else:
            report[lang_name] = {"error": "File not found"}
    
    return report

if __name__ == "__main__":
    report = analyze_translations()
    
    print("=== Translation Analysis Report ===\n")
    
    for lang, data in report.items():
        print(f"\n{lang}:")
        if "error" in data:
            print(f"  Error: {data['error']}")
        else:
            print(f"  Total untranslated: {data['total_untranslated']}")
            if data['untranslated_keys']:
                print("  First 20 untranslated keys:")
                for key, value in data['untranslated_keys']:
                    print(f"    - {key}: '{value}'")