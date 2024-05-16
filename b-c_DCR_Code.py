import os
import mysql.connector
import re


# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Mm62725",
    database="dcrb_search"
)
cursor = conn.cursor()


# Drop table if exists
drop_table_query = "DROP TABLE IF EXISTS Files"
cursor.execute(drop_table_query)

# Create new table
create_table_query = """
CREATE TABLE Files (
    id INT NOT NULL AUTO_INCREMENT,
    file_name VARCHAR(255) DEFAULT NULL,
    full_path VARCHAR(255) DEFAULT NULL,
    file_type VARCHAR(255) DEFAULT NULL,
    file_size BIGINT DEFAULT NULL,
    readable BOOLEAN,
    file_content_text LONGTEXT,
    PRIMARY KEY (id),
    UNIQUE KEY unique_path (full_path)
)
"""
cursor.execute(create_table_query)

# Commit the changes
conn.commit()


# Function to traverse directory and insert file metadata and content
def traverse_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            file_type = file_name.split(".")[-1]
            if file_type.lower() == 'html':
                readable = True
                # Read content of HTML files
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                # Parse HTML content to extract text
                file_content_text = re.sub('<[^<]+?>', '', file_content)
            else: 
                readable = False
                file_content_text = None
            if os.path.isdir(file_path):
                file_type = "directory"
                file_content_text = None
            file_size = os.path.getsize(file_path)

            # Insert metadata into database
            insert_query = "INSERT INTO Files (file_name, full_path, file_type, file_size, readable, file_content_text) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (file_name, file_path, file_type, file_size, readable, file_content_text))
            conn.commit()

# Specify the root directory of your subtree
root_directory = "D:\\university\\digitalcontent\\files"
traverse_directory(root_directory)


# Function to search for a string in files
def search_files(search_string):
    search_query = "SELECT full_path, file_type, file_content_text FROM Files WHERE file_name LIKE %s OR file_content_text LIKE %s"
    cursor.execute(search_query, ('%' + search_string + '%', '%' + search_string + '%'))
    results = cursor.fetchall()
    return results

# Input search string
search_string = input("Enter search string: ")


# Search for files
search_results = search_files(search_string)

print(f"Total search results: {len(search_results)}")

# Display search results
if search_results:
    print("Search results:")
    for result in search_results:
        full_path, file_type , file_content_text = result
        occurrences = file_content_text.lower().count(search_string.lower())
        occurrencesINname = full_path.lower().count(search_string.lower())

        print(f"File path: {full_path} | File type: {file_type} | count in file name : {occurrencesINname} | count in files: {occurrences}")
else:
    print("No matching files found.")




# Close database connection
cursor.close()
conn.close()
