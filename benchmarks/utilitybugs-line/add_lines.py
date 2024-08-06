import sys

def insert_newlines(filename, n):
    with open(filename, 'r') as file:
        content = file.read()
    
    # Insert newline every n characters
    new_content = '\n'.join([content[i:i+n] for i in range(0, len(content), n)])
    
    # Overwrite the file with the new content
    with open(filename, 'w') as file:
        file.write(new_content)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <filename> <n>")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        n = int(sys.argv[2])
    except ValueError:
        print("The value of <n> should be an integer.")
        sys.exit(1)
    
    insert_newlines(filename, n)
    print(f"Inserted newline every {n} characters in file '{filename}'.")

