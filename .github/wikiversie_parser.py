import os
import re
import csv
import yaml
import argparse
from pathlib import Path


"""
Parse the lookup table from a YAML file.
"""
def parse_lookup_table(lookup_file):
    with open(lookup_file, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

"""
Parse the dataset file from a CSV file to a list.
"""
def parse_dataset_file(dataset_file):
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252']  # List of encodings to try
    for encoding in encodings:
        try:
            with open(dataset_file, newline='', encoding=encoding) as file:
                reader = csv.reader(file, delimiter=';', quotechar='|')
                return list(reader)
        except UnicodeDecodeError:
            print(f"Failed to decode {dataset_file} with encoding {encoding}. Trying next encoding.")
    raise UnicodeDecodeError(f"Failed to decode {dataset_file} with available encodings.")

"""
Extract the 'taxonomie' value(s) from the content of a markdown file.
"""
def extract_taxonomie(content):
    lines = content.splitlines()
    taxonomie = []

    for i, line in enumerate(lines):
        if line.startswith('taxonomie:'):
            # Handle case where taxonomie is a single value
            if ':' in line and len(line.split(':', 1)[1].strip()) > 0:
                taxonomie.append(line.split(':', 1)[1].strip())
            else:
                # Handle case where taxonomie is a list
                for j in range(i + 1, len(lines)):
                    sub_line = lines[j].strip()
                    if sub_line.startswith('- '):
                        taxonomie.append(sub_line.lstrip('- ').strip())
                    else:
                        break
            break

    return taxonomie if taxonomie else None

"""
Split the taxonomie value into a list of individual taxonomie parts.
"""
def split_taxonomie(taxonomie):
    if re.match(r'^[a-z]{2}-\d+\.\d+[.-][a-zA-Z\d-]+$', taxonomie):
        return taxonomie.split('.')
    return None

"""
Generate tags based on the taxonomie values
"""
def generate_tags(taxonomies, lookup_table, dataset):
    tags = []
    errors = []

    if taxonomies is not None:
        for taxonomie in taxonomies:
            splitted_taxonomie = split_taxonomie(taxonomie)

            # Check if the taxonomie value is in the lookup table
            if splitted_taxonomie is not None:
                # Check if the first part of the taxonomie is in the lookup table
                if splitted_taxonomie[0] in lookup_table['codes']['part-1']:
                    # Loop through the dataset to find the corresponding row
                    for row in dataset:
                        # Get the Proces (column 4) and Processtap (column 5) values
                        if row[6] == splitted_taxonomie[0]:
                            # Add the Proces and Processtap values to the tags list
                            if row[4] not in tags:
                                tags.append(row[4])
                            if row[5] not in tags:
                                tags.append(row[5])
                    
                    # Check if the second part of the taxonomie is in the lookup table
                    new_tag = "HBO-i/niveau-" + splitted_taxonomie[1]
                    if int(splitted_taxonomie[1]) in lookup_table['codes']['part-2'] and new_tag not in tags:
                        tags.append(new_tag)

                # If the taxonomie value is not in the lookup table
                # In the future this could also fail the script / pipeline, depends on the requirements
                else: 
                    errors.append("Undefined taxonomie " + taxonomie)

    tags.sort(key=lambda x: x.startswith('HBO-i'), reverse=True)
    return tags, errors

"""
Generate a markdown table string from a list of rows and headers.
"""
def generate_markdown_table(headers, rows):
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in rows:
        table += "| " + " | ".join(row) + " |\n"
    return table

"""
Format the taxonomie report table.
"""
def format_taxonomie_table(taxonomie_report, dataset):
    headers = ["TC-1", "Processtap", "4CID onderdeel", "Niveau 1", "Niveau 2", "Niveau 3"]
    rows = []

    for row in dataset[1:]:
        process_step = row[6]
        process_name = row[5]
        niveau_1 = "✔️" if taxonomie_report.get(process_step, {}).get("niveau-1") else "❌"
        niveau_2 = "✔️" if taxonomie_report.get(process_step, {}).get("niveau-2") else "❌"
        niveau_3 = "✔️" if taxonomie_report.get(process_step, {}).get("niveau-3") else "❌"
        rows.append([process_step, process_name, "X", niveau_1, niveau_2, niveau_3])

    return generate_markdown_table(headers, rows)

"""
Format the success or failed report table.
"""
def format_file_report_table(file_report, title):
    headers = ["Status", "File", "Path", "Taxonomie", "Tags", "Errors"]
    rows = [[
        file['status'], 
        file['file'], 
        file['path'], 
        file['taxonomie'], 
        file['tags'],
        file['errors']
    ] for file in file_report]

    table = generate_markdown_table(headers, rows)
    return f"## {title}\n\n" + table

"""
Create a file report based on the status, file path, taxonomie, and tags.
"""
def create_file_report(status, file_path, src_dir, taxonomie, tags, errors):
    return {
        "status": status,
        "file": file_path.stem,
        "path": str(file_path.relative_to(src_dir)),
        "taxonomie": '<br>'.join(taxonomie) if taxonomie else "N/A",
        "tags": '<br>'.join(tags) if tags else "N/A",
        "errors": '<br>'.join(errors) if errors else "N/A"
    }

"""
Generate the report based on the taxonomie report, success, and failed reports.
"""
def generate_report(taxonomie_report, dataset, successful_files, failed_files):
    report_path = "report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write('---\ndraft: true\n---\n')
        
        # Taxonomie Mapping Section
        f.write('## Taxonomie Mapping\n')
        f.write('De onderstaande tabel toont de status van de taxonomie mapping.\n\n')
        f.write(format_taxonomie_table(taxonomie_report, dataset))

        f.write('\n\n')

        # Passed Files Section
        f.write(format_file_report_table(successful_files, "Geslaagde bestanden"))

        f.write('\n\n')

        # Failed Files Section
        f.write(format_file_report_table(failed_files, "Gefaalde bestanden"))

    # Print reports for quick feedback
    print(format_taxonomie_table(taxonomie_report, dataset))
    print(format_file_report_table(successful_files, "Passed files"))
    print(format_file_report_table(failed_files, "Failed files"))

"""
Update markdown files in the source directory with taxonomie tags and generate reports.
"""
def parse_markdown_files(src_dir, dest_dir, lookup_table, dataset):
    dest_dir.mkdir(parents=True, exist_ok=True)
    taxonomie_report = {} # Track which taxonomies are associated with which levels
    successful_files = [] # Track the status of each file
    failed_files = [] # Track the status of each file    

    # Loop through all markdown files in the source directory
    for file_path in Path(src_dir).rglob('*.md'):
        relative_path = file_path.relative_to(src_dir)
        dest_path = dest_dir / relative_path

        print(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Gets the tags based on the taxonomie value
            taxonomie = extract_taxonomie(content)
            tags, errors = generate_tags(taxonomie, lookup_table, dataset)

            # Create the new content with updated tags
            new_content = (
                f"---\ntitle: {file_path.stem}\ntaxonomie: {taxonomie}\ntags:\n" +
                '\n'.join([f"- {tag}" for tag in tags]) +
                "\n---\n" +
                content.split('---', 2)[-1]
            )

            # Track which taxonomies are associated with which levels
            if taxonomie:
                for tax in taxonomie:
                    # Split the taxonomie value into its components
                    splitted = split_taxonomie(tax)
                    if splitted:
                        niveau = int(splitted[1])
                        process_step = splitted[0]

                        # Add the process step to the taxonomie_report
                        if process_step not in taxonomie_report:
                            taxonomie_report[process_step] = {"niveau-1": False, "niveau-2": False, "niveau-3": False}

                        taxonomie_report[process_step][f"niveau-{niveau}"] = True

            # Determine file report status and append to the appropriate list
            status = "✔️" if taxonomie and tags and not errors else "⚠️" if errors else "❌"
            file_report = create_file_report(status, file_path, src_dir, taxonomie, tags, errors)

            if status == "✔️":
                successful_files.append(file_report)
            else:
                failed_files.append(file_report)

            # Create the destination directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the new content to the destination file
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

    generate_report(taxonomie_report, dataset, successful_files, failed_files)

def main():
    """
    Main entry point of the script.
    """
    parser = argparse.ArgumentParser(description="Update markdown files with taxonomie tags and generate reports.")
    parser.add_argument("--src", required=True, help="Source directory containing markdown files.")
    parser.add_argument("--dest", required=True, help="Destination directory to save updated markdown files and reports.")
    parser.add_argument("--lookup", required=True, help="Path to the lookup table (YAML file).")
    parser.add_argument("--dataset", required=True, help="Path to the dataset file (CSV file).")

    args = parser.parse_args()
    src_dir = Path(args.src).resolve()
    dest_dir = Path(args.dest).resolve()
    lookup_table = parse_lookup_table(args.lookup)
    dataset = parse_dataset_file(args.dataset)

    parse_markdown_files(src_dir, dest_dir, lookup_table, dataset)

if __name__ == "__main__":
    main()
