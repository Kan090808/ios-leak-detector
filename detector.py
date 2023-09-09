import re
import os

# Define counters
total_files_checked = 0
total_functions_checked = 0
total_functions_without_leaks = 0
total_functions_with_leaks = 0

def split_objc_functions(source_code):
    functions = []
    function_buffer = ""
    brace_count = 0
    capturing_function = False
    
    for line in source_code.splitlines():
        if line.strip().startswith("-") or line.strip().startswith("+"):
            capturing_function = True
        
        if capturing_function:
            brace_count += line.count("{") - line.count("}")
            function_buffer += line + "\n"
            
        if brace_count == 0 and capturing_function and function_buffer.strip():
            functions.append(function_buffer.strip())
            function_buffer = ""
            capturing_function = False

    return functions


def find_leaked_blocks(file_path):
    global total_functions_checked

    with open(file_path, "r") as f:
        source = f.read()

    functions = split_objc_functions(source)
    total_functions_checked += len(functions)
    # print(functions[-1])
    leaked_blocks = []

    for func in functions:
        match = re.search(r'-\s*\([^)]+\)\s*([^{\s]+)', func)
        if not match:
            continue
        function_name = match.group(1)

        start_index = func.find('{')
        if start_index != -1:
            func = func[start_index:]

        # blocks = re.findall(r'\^.*?\{.*?\}', func, re.DOTALL)
        blocks = extract_blocks(func)
        # print(len(blocks))
        for block in blocks:
          # 檢查 block 中的 "self" 前面是否有 "weak" 或 "strong"
          if re.search(r'\b(?!weak|strong)\bself\b', block):
              line_number = source[:source.index(func)].count('\n') + 1
            #   if 'OLSCIMWebServicer+Message' in file_path:
            #     print(block)
              leaked_blocks.append((function_name.strip(), line_number))
        # print(" ")

    return leaked_blocks

def read_config():
    with open("config.txt", "r") as f:
        lines = f.readlines()

    project_path = None
    skip_paths = []
    only_print_leaks = False

    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith("project_path:"):
            current_section = "project_path"
        elif line.startswith("skip_path:"):
            current_section = "skip_path"
        elif line.startswith("only_print_leaks:"):
            only_print_leaks = line.split(":")[1].strip().lower() == "true"
            current_section = None  # reset the section after reading this line
        else:
            if current_section == "project_path" and project_path is None:
                project_path = line
            elif current_section == "skip_path":
                if len(line) == 0:
                    current_section = None
                    continue
                line = project_path + line
                # print(line)
                skip_paths.append(line)

    return project_path, skip_paths, only_print_leaks

def extract_blocks(s):
    blocks = []
    start = -1  # start position of the current block
    count = 0   # count of unmatched curly braces

    # Flag to detect if the current sequence started with '^'
    in_caret_sequence = False

    for i, c in enumerate(s):
        
        if c == '^':
            in_caret_sequence = True
        elif in_caret_sequence and c == '{':
            if start == -1:  # if this is the start of a block
              start = i
            count += 1
        elif in_caret_sequence and c == '}':
            count -= 1
            if count == 0 and start != -1:  # end of the current block
                blocks.append(s[start:i+1])  # capture the entire block
                start = -1  # reset start position
                in_caret_sequence = False  # reset the flag

    return blocks

def main():
    global total_files_checked, total_functions_checked, total_functions_without_leaks, total_functions_with_leaks

    # Check for the existence of config.txt file
    if os.path.exists("config.txt"):
        project_path, skip_paths, only_print_leaks = read_config()
    else:
        project_path, skip_paths = '', []

    print(project_path, only_print_leaks, skip_paths)

    # Perform the check
    with open("leak_log.txt", "w") as log_file:
        # Traverse through all the files and subdirectories in project_path
        for root, dirs, files in os.walk(project_path):
            # Check if the current directory is in skip_paths
            if any(os.path.abspath(root).startswith(os.path.abspath(skip)) for skip in skip_paths):
                continue
            for file in files:
                if file.endswith('.m'):
                    total_files_checked += 1
                    file_path = os.path.join(root, file)
                    leaked_blocks = find_leaked_blocks(file_path)

                    total_functions_checked += len(leaked_blocks)

                    if only_print_leaks is False:
                        log_file.write(f"檢查文件: {file_path}\n")

                    if leaked_blocks:
                        total_functions_with_leaks += len(leaked_blocks)
                        if only_print_leaks is True:
                            log_file.write(f"檢查文件: {file_path}\n")
                        log_file.write("可能洩漏 block 的 function：\n")
                        for function, line_number in leaked_blocks:
                            log_file.write(f"    function: {function}, line: {line_number}\n")
                        log_file.write("------------------------------------------------------\n")
                    else:
                        
                        if only_print_leaks is False:
                            log_file.write("沒有可能洩漏 block 的 function。\n")
                            log_file.write("------------------------------------------------------\n")

    total_functions_without_leaks = total_functions_checked - total_functions_with_leaks
    print("檢查成功請查看 leak_log.txt")
    print(f"總共檢查了 {total_files_checked} 個檔案")
    print(f"總functions數量: {total_functions_checked}")
    print(f"沒有leak的function數量: {total_functions_without_leaks}")
    print(f"leak的function數量: {total_functions_with_leaks}")
    print("")

if __name__ == "__main__":
    main()
