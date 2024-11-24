import streamlit as st
import json
import re
import os
from datetime import datetime

COUNTRY_CODES = {
    "UAE (+971)": "971",
    "Saudi Arabia (+966)": "966",
    "Kuwait (+965)": "965",
    "Bahrain (+973)": "973",
    "Qatar (+974)": "974",
    "Oman (+968)": "968"
}

def standardize_uae_number(phone):
    # Remove all non-numeric characters
    number = re.sub(r'\D', '', phone)
    
    # Handle numbers starting with '00'
    if number.startswith('00'):
        number = number[2:]  # Remove the '00' prefix
    
    # Handle numbers starting with country code
    if number.startswith('971'):
        # Remove any zero that immediately follows 971
        if len(number) > 3 and number[3] == '0':
            number = number[:3] + number[4:]
        formatted = f"+{number}"
    # Handle numbers starting with 0
    elif number.startswith('0'):
        # Remove leading zero and add country code
        formatted = f"+971{number[1:]}"
    # If number starts with 5, it's a UAE mobile number without country code
    elif number.startswith('5'):
        formatted = f"+971{number}"
    else:
        return None, f"Invalid UAE number format: {phone}"
    
    # Verify the length (UAE numbers should be 12 digits including country code)
    if len(formatted) != 13:  # +971 + 9 digits
        return None, f"Invalid number length: {phone}"
        
    return formatted, None

def process_json_file(content):
    errors = []
    modified = False
    total_records = 0
    corrected_records = 0
    
    # Create a copy of the data to modify
    new_data = content.copy()
    
    # Process each person's phone number
    for person in new_data['people']:
        total_records += 1
        if 'phone' in person:
            # Remove parentheses and spaces before standardization
            cleaned_phone = re.sub(r'[\s()]+', '', person['phone'])
            standardized_number, error = standardize_uae_number(cleaned_phone)
            if error:
                errors.append(f"Error for {person['name']}: {error}")
            else:
                if person['phone'] != standardized_number:
                    person['phone'] = standardized_number
                    modified = True
                    corrected_records += 1
    
    return new_data, errors, modified, total_records, corrected_records

def main():
    st.title("Phone Number Validator")
    
    # Application description
    st.markdown("""
    ### What this application does:
    1. Validates and standardizes phone numbers in your JSON file
    2. Creates a new file with standardized numbers
    3. Generates a validation log
    4. The original file will **NOT** be modified
    
    ### Expected JSON format:
    ```json
    {
        "people": [
            {"name": "John Doe", "phone": "0501234567"},
            {"name": "Jane Smith", "phone": "971502345678"}
        ]
    }
    ```
    """)
    
    # Create two columns for input controls
    input_col1, input_col2 = st.columns(2)
    
    with input_col1:
        # Country code selector
        selected_country = st.selectbox(
            "Select Country Code",
            options=list(COUNTRY_CODES.keys()),
            index=0,
            help="Currently supporting UAE numbers only. More countries coming soon."
        )
    
    with input_col2:
        uploaded_file = st.file_uploader(
            "Upload your JSON file",
            type=['json'],
            help="File must contain a 'people' array with 'name' and 'phone' fields"
        )
    
    # Add separator
    st.markdown("---")
    
    # Create two columns for results
    col1, col2 = st.columns([3, 2])
    
    if uploaded_file:
        try:
            # Read the JSON content
            content = json.load(uploaded_file)
            
            # Process the file
            new_data, errors, modified, total_records, corrected_records = process_json_file(content)
            
            # Display summary statistics
            st.info(f"Total records processed: {total_records}")
            if modified:
                st.info(f"Records corrected: {corrected_records}")
            
            # Display errors if any
            if errors:
                st.error("Validation Errors Found:")
                for error in errors:
                    st.write(error)
            
            # Display JSON output in side column
            with col2:
                st.subheader("Processed JSON")
                st.json(new_data)
            
            # Create new filename
            original_filename = uploaded_file.name
            base_name = original_filename.rsplit('.', 1)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{base_name}_validated_{timestamp}.json"
            
            # Save the new JSON file
            if modified or errors:
                with open(new_filename, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, indent=2, ensure_ascii=False)
                
                # Provide download button
                with open(new_filename, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="Download Validated JSON",
                        data=f.read(),
                        file_name=new_filename,
                        mime="application/json"
                    )
                
                # Create log file
                log_filename = f"validation_log_{timestamp}.txt"
                with open(log_filename, 'w', encoding='utf-8') as f:
                    f.write(f"Validation Log for {original_filename}\n")
                    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    if errors:
                        f.write("Errors found:\n")
                        for error in errors:
                            f.write(f"- {error}\n")
                    else:
                        f.write("No validation errors found.\n")
                    
                    if modified:
                        f.write("\nPhone numbers were standardized in the output file.\n")
                
                # Clean up files
                if os.path.exists(new_filename):
                    os.remove(new_filename)
                
            else:
                st.success("All phone numbers are already in the correct format!")
            
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid JSON file.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 