import json
import os
import base64

def extract_visuals_from_notebooks():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)

    notebook_dir = os.path.join(project_root, "notebooks")
    output_dir = os.path.join(project_root, "all_visuals")
    
    notebook_files = [
        "01_data_overview_and_eda.ipynb",
        "02_sql_user_segmentation.ipynb",
        "03_sql_retention_analysis.ipynb",
        "04_product_insights_and_visuals.ipynb",
        "05_final_summary_dashboard.ipynb"
    ]

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for notebook_file_name in notebook_files:
        notebook_path = os.path.join(notebook_dir, notebook_file_name)
        
        if not os.path.exists(notebook_path):
            print(f"Warning: Notebook file not found: {notebook_path}")
            continue

        print(f"Processing {notebook_file_name}...")
        
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook_content = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {notebook_file_name}. Skipping.")
            continue
        except Exception as e:
            print(f"Error reading {notebook_file_name}: {e}. Skipping.")
            continue

        image_count = 0
        for cell_index, cell in enumerate(notebook_content.get('cells', [])):
            cell_type = cell.get('cell_type')

            # Extract from markdown cell attachments
            if cell_type == 'markdown':
                attachments = cell.get('attachments')
                if attachments:
                    for attachment_name, attachment_data in attachments.items():
                        # attachments_data is a dict where keys are mime-types
                        for mime_type, base64_encoded_data in attachment_data.items():
                            if mime_type.startswith('image/'):
                                try:
                                    image_data = base64.b64decode(base64_encoded_data)
                                    file_ext = mime_type.split('/')[-1]
                                    # Sanitize attachment_name for use as a filename
                                    safe_attachment_name = "".join(c if c.isalnum() or c in ('.', '_') else '_' for c in attachment_name)
                                    output_filename = f"{os.path.splitext(notebook_file_name)[0]}_md_cell_{cell_index}_{safe_attachment_name}"
                                    # Ensure filename has an extension
                                    if not os.path.splitext(output_filename)[1]:
                                         output_filename = f"{output_filename}.{file_ext}"

                                    output_path = os.path.join(output_dir, output_filename)
                                    with open(output_path, 'wb') as img_f:
                                        img_f.write(image_data)
                                    image_count += 1
                                    print(f"  Saved image: {output_filename}")
                                except Exception as e:
                                    print(f"  Error processing markdown attachment {attachment_name} in {notebook_file_name}: {e}")
            
            # Extract from code cell outputs
            elif cell_type == 'code':
                outputs = cell.get('outputs', [])
                for output_index, output in enumerate(outputs):
                    data = output.get('data')
                    if data:
                        for mime_type, base64_encoded_data in data.items():
                            if mime_type.startswith('image/'):
                                try:
                                    # Sometimes data can be a list of strings (e.g. for gifs)
                                    if isinstance(base64_encoded_data, list):
                                        base64_encoded_data = "".join(base64_encoded_data)
                                    
                                    image_data = base64.b64decode(base64_encoded_data)
                                    file_ext = mime_type.split('/')[-1]
                                    if file_ext == "svg+xml": # handle svg extension
                                        file_ext = "svg"
                                    
                                    output_filename = f"{os.path.splitext(notebook_file_name)[0]}_code_cell_{cell_index}_output_{output_index}.{file_ext}"
                                    output_path = os.path.join(output_dir, output_filename)
                                    
                                    with open(output_path, 'wb') as img_f:
                                        img_f.write(image_data)
                                    image_count += 1
                                    print(f"  Saved image: {output_filename}")
                                except TypeError as te:
                                    print(f"  TypeError processing output in {notebook_file_name}, cell {cell_index}, output {output_index} for mime_type {mime_type}. Data: {base64_encoded_data[:100]}... Error: {te}")
                                except Exception as e:
                                    print(f"  Error processing output in {notebook_file_name}, cell {cell_index}, output {output_index}: {e}")
        
        if image_count == 0:
            print(f"  No images found in {notebook_file_name}.")

if __name__ == "__main__":
    extract_visuals_from_notebooks()
    print("Visual extraction process complete.") 