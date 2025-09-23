import argparse
import json
from prettytable import PrettyTable
from .core import search_names
from .settings import load_settings, save_settings

def format_results(results, settings):
    fmt = settings.get("output_format", "table")
    max_results = settings.get("max_results", 10)
    results = results[:max_results]

    if fmt == "json":
        return json.dumps(results, indent=2, ensure_ascii=False)
    elif fmt == "minimal":
        return "\n".join([r["name"] for r in results])
    else:
        t = PrettyTable()
        t.field_names = ["Name", "Count", "Nameday"]
        for r in results:
            t.add_row([r["name"], r["count"], r["nameday"] or "-"])
        return t.get_string()

def first_run_banner(settings):
    print("\n=== First run detected ===")
    print("This is the Latvian Names CLI.")
    print("Usage examples:")
    print("  latnames anna peter")
    print("  latnames --settings")
    print("\nDefault settings:")
    for k, v in settings.items():
        print(f"  {k}: {v}")

    choice = input("\nSave these defaults to config.json? (y/n): ").strip().lower()
    if choice == "y":
        save_settings(settings)
        print("✅ Settings saved.")
    else:
        print("⚠️ Using defaults (nothing saved).")

def run():
    parser = argparse.ArgumentParser(description="Latvian Names CLI")
    parser.add_argument("names", nargs="*", help="Names to search")
    parser.add_argument("--settings", action="store_true", help="Open settings menu")
    parser.add_argument("--reset", action="store_true", help="Reset config.json")
    args = parser.parse_args()

    settings, first_run = load_settings()

    if first_run:
        first_run_banner(settings)

    if args.reset:
        import os
        if os.path.exists("settings.json"):
            os.remove("settings.json")
        print("🔄 Settings reset. Next run will trigger first-run setup.")
        return

    if args.settings:
        print("\n--- Settings Menu ---")
        print(f"1) Output format (current: {settings['output_format']})")
        print(f"2) Max results (current: {settings['max_results']})")
        print("0) Save & Exit")

        choice = input("Choose option: ").strip()
        if choice == "1":
            fmt = input("Format (table/json/minimal): ").strip().lower()
            if fmt in ["table", "json", "minimal"]:
                settings["output_format"] = fmt
        elif choice == "2":
            try:
                settings["max_results"] = int(input("Enter max results: "))
            except ValueError:
                pass
        save_settings(settings)
        print("✅ Settings updated.")
        return

    if not args.names:
        parser.print_help()
        return

    results = search_names(*args.names)
    print(format_results(results, settings))
