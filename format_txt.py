import pandas as pd
import csv
import re

def process_dept_data(df_dept, csv_writer, last_updated_date):
    for index, row in df_dept.iterrows():
        if pd.isna(row["Verkefnaheiti"]) or row["Verkefnaheiti"] == '':
            continue
        project_name = row["Verkefnaheiti"]#.replace(',', '')#.replace('/','-').replace('&','And').replace("'",' ').replace(".",'')  # Remove commas
        phase = row["Undirheiti"].strip()
        department = row["Department"]  # Read the department
        pm = row["Ábyrgð"]
        location = row["Location "]
        project_type = row["Type"]#.replace('&','og')
        Tier=int(row["Tier"])
        current_category="Project"

        # Determine the front PM based on the hierarchy (PML > DM > PM1 > PM2)
        front_pm = pm
        
        # Convert the phase to match the text file terminology
        if phase in ["PME & RFP", "Útboðsferli og samningur"]:
            phase = "Procurement"
        elif phase == "Innleiðing":
            phase = "Stage 5"
        elif phase == "Innleiðing ":
            phase = "Stage 5"
        elif phase == "Skipting og hönnun á svæði":
            phase = "Stage 4"
        else:
            continue
        # Find the start and finish based on the percentages
        start_date = None
        finish_date = None
        for month_col in df_dept.columns[8:]:
            cell_value = row[month_col]
            if pd.notna(cell_value) and cell_value != '':
                if not start_date:
                    start_date = month_col  # The first month with a percentage is the start
                finish_date = month_col  # The last month with a percentage is the finish

        if start_date and finish_date:
            # Convert column names (dates) to datetime objects
            start_date = pd.to_datetime(start_date).date()
            finish_date = pd.to_datetime(finish_date).date()
            start_date = start_date.strftime('%d-%b-%y')
            finish_date = finish_date.strftime('%d-%b-%y')
            dates=[start_date, finish_date]

            # Write to the CSV using writerow
            csv_writer.writerow([
                last_updated_date,
                current_category,
                department,
                location,
                project_type,
                project_name,
                phase,
                Tier,   
                front_pm,             
                "",
                "",
                pm,
                "",
                dates[0],
                dates[1]
            ])



# Read the Excel file with two header rows for merged cells
df = pd.read_excel('Projects_info.xlsx', header=[0, 1], engine='openpyxl')

# Flatten the multi-level header and create a single header row
# Convert all elements to strings before joining
df.columns = [' '.join(str(col) for col in cols).strip() for cols in df.columns.values]

print("Column headers after flattening:", df.columns.tolist())

last_updated_date = '2023-12-12'

# Use the corrected column names after flattening the headers
project_name_column = 'Project Name Unnamed: 0_level_1'
category_column = 'Category Unnamed: 1_level_1'
department_column = 'Department Unnamed: 2_level_1'
location_column = 'Location Unnamed: 3_level_1'
type_column = 'Type Unnamed: 4_level_1'
tier_column = 'Tier Unnamed: 5_level_1'

# Create a dictionary to store project information
project_dict = {}
for index, row in df.iterrows():
    project_name = row[project_name_column]#[0]  # Use the correct project name column header
    project_info = {
        "Category": row[category_column],
        "Department": row[department_column],
        "Location": row[location_column],
        "Type": row[type_column],
        "Tier": row[tier_column],
        # Initialize stages info with empty dictionaries
        "Strategies and Plans": {},
        "Stage 0": {},
        "Stage 1": {},
        "Stage 2": {},
        "Stage 3": {},
        "Stage 4": {},
        "Procurement": {},
        "Stage 5": {},
        "Stage 6": {}
    }

    # Update project_info with PM details for each stage
    for stage in project_info.keys():
        if project_info[stage] is not None and isinstance(project_info[stage], dict):  # Ensure project_info[stage] is a dictionary
            if stage in ['Strategies and Plans', 'Stage 0', 'Stage 1', 'Stage 2']:
                project_info[stage]['PM1'] = row.get(f'{stage} PM', None)
                project_info[stage]['PM2'] = row.get(f'{stage} PM1', None)
            else:  # For 'Stage 3', 'Stage 4', 'Stage 5', 'Stage 6'
                project_info[stage]['PML'] = row.get(f'{stage} PML', None)
                project_info[stage]['DM'] = row.get(f'{stage} DM', None)
                project_info[stage]['PM1'] = row.get(f'{stage} PM1', None)
                project_info[stage]['PM2'] = row.get(f'{stage} PM2', None)
    project_dict[project_name] = project_info

# Debug: Print a sample from the project dictionary to verify its structure
print("Sample project info from the dictionary:", next(iter(project_dict.items())))


#print(project_dict)
# Extract project names from the DataFrame
project_names = df[project_name_column].tolist()  # Use the correct project name column header
project_names = sorted(project_names, key=len, reverse=True)
#print(project_dict)

with open("raw_data.txt", "r") as f:
    lines = f.readlines()

with open("formatted_data.csv", "w", newline='') as output_file:
    writer = csv.writer(output_file)
    # Write the header for the output file
    writer.writerow(["Last Updated Date", "Category", "Department", "Location", "Type", "Task", "Phase", "Tier", "PM", "PML", "DM", "PM1", "PM2", "Start", "Finish"])
    
    df_vv = pd.read_excel('Verkefnaplan í VOS.xlsx', sheet_name='V&V', header=1, engine='openpyxl')
    df_sof = pd.read_excel('Verkefnaplan í VOS.xlsx', sheet_name='SOF', header=1, engine='openpyxl')
    process_dept_data(df_vv, writer, last_updated_date)
    process_dept_data(df_sof, writer, last_updated_date)



    current_project = None
    current_phase, current_category = None, None

    for line in lines:
        stripped_line = line.strip()
        # ... (rest of the code for line processing)

        # Debug: Print the current line being processed
        print(f"Processing line: {stripped_line}")

        # Refactored project name matching logic using .startswith()
        for project in project_names:
            if stripped_line.lower().startswith(project.lower()):
                current_project = project
                print(f"Matched project: {current_project} in line: {stripped_line}")
                break  # Break out of the loop once a match is found

        current_category="Project"
        # Identify the current phase from the line
        if stripped_line.lower().startswith("stage"):
            current_phase = " ".join(stripped_line.split()[:2])
        elif stripped_line.lower().startswith("construction"):
            current_phase = "Stage 5"        
        elif stripped_line.lower().startswith("procurement"):
            current_phase = "Procurement"
        elif stripped_line.lower().startswith("orat"):  # Check for 'ORAT' to set it as 'Stage 6'
            current_phase = "Stage 6"            
        elif stripped_line.lower().startswith("strategic plan"): 
            current_phase = "Strategies and Plans"
            current_category="Strategies and Plans"
            
        #print(f"Processing line: {stripped_line}")  # Debugging statement
        #print(f"Current project: {current_project}")  # Debugging statement
        #print(f"Current phase: {current_phase}")  # Debugging statement
        #print(current_project)
        # Process the data if a phase is identified
        if current_phase:
            # Debug: Print details about the matched project and phase
            print(f"Matched project: {current_project}, phase: {current_phase}")
            print(stripped_line)
            #print(current_project)
            # Get the project info from the project_dict
            proj_info = project_dict.get(current_project)
            if proj_info and current_phase in proj_info:
                phase_info = proj_info[current_phase]
                # Extract dates from the line
                parts = stripped_line.split()
                dates = [part for part in parts if "-" in part and part != 'A'][-2:]
                
                # Determine the front PM based on the hierarchy (PML > DM > PM1 > PM2)
                front_pm = phase_info.get('PML', '') or phase_info.get('DM', '') or phase_info.get('PM1', '') or phase_info.get('PM2', '')

                writer.writerow([
                    last_updated_date, 
                    current_category, 
                    proj_info["Department"], 
                    proj_info["Location"],
                    proj_info["Type"], 
                    current_project, 
                    current_phase, 
                    proj_info["Tier"], 
                    front_pm,  # Use the determined front PM
                    phase_info.get('PML', ''),  # Get PML name if available
                    phase_info.get('DM', ''),   # Get DM name if available
                    phase_info.get('PM1', ''),  # Get PM1 name if available
                    phase_info.get('PM2', ''),  # Get PM2 name if available
                    dates[0] if len(dates) > 0 else None, 
                    dates[1] if len(dates) > 1 else None
                ])
                #print(f"Wrote data for project: {current_project}, phase: {current_phase}")  # Debugging statement
                # Debug: Print details about the data being written to CSV
                print(f"Writing data for project: {current_project}, phase: {current_phase}")


        # Reset current phase after processing the line
        current_phase = None