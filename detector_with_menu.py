import re
import os

# 在你的main函數的開始或其他合適的地方
log_file = open("leak_log.txt", "w")  # 打開一個名為 "leak_log.txt" 的文件用於寫入

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
    with open(file_path, "r") as f:
        source = f.read()

    functions = split_objc_functions(source)
    # print(functions[-1])
    leaked_blocks = []

    for func in functions:
        # print(func)
        blocks = re.findall(r'\^.*?\{.*?\}', func, re.DOTALL)
        # print(len(blocks))
        for block in blocks:
          # 檢查 block 中的 "self" 前面是否有 "weak" 或 "strong"
          if re.search(r'\b(?!weak|strong)\bself\b', block):
              line_number = source[:source.index(func)].count('\n') + 1
              match = re.search(r'-\s*\([^)]+\)\s*([^{\s]+)', func)
              if not match:
                  continue
              function_name = match.group(1)
              leaked_blocks.append((function_name.strip(), line_number))
        # print(" ")

    return leaked_blocks

def read_config():
    """
    Parses config.txt and returns the project_path and a list of skip_paths
    """
    with open("config.txt", "r") as f:
        lines = f.readlines()
    
    project_path = None
    skip_paths = []

    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith("project_path:"):
            current_section = "project_path"
            continue
        elif line.startswith("skip_path:"):
            current_section = "skip_path"
            continue

        if current_section == "project_path":
            project_path = line
        elif current_section == "skip_path":
            skip_paths.append(line)
    
    return project_path, skip_paths


def main():
    while True:
        # Check for the existence of config.txt file
        if os.path.exists("config.txt"):
            project_path, skip_paths = read_config()
        else:
            project_path, skip_paths = '', []

        # If config.txt file doesn't exist or content is empty, prompt user
        if not project_path:
            project_path = input("請輸入 project_path: ")
            with open("config.txt", "w") as f:
                f.write("project_path:\n" + project_path + "\n\nskip_path:\n")

        # Display menu
        choice = input("選擇操作：\n1: 更改project_path\n2: 執行檢查\n3: 結束\n請輸入選項：")

        if choice == '1':
            # Update project_path
            new_path = input("請輸入新的 project_path: ")
            with open("config.txt", "w") as f:
                f.write("project_path:\n" + new_path + "\n\nskip_path:\n")
            print("project_path 已更新！")
            print("")
        elif choice == '2':
            # Perform the check
            with open("leak_log.txt", "w") as log_file:
                # Traverse through all the files and subdirectories in project_path
                for root, dirs, files in os.walk(project_path):
                    # Check if the current directory is in skip_paths
                    if any(os.path.abspath(root).startswith(os.path.abspath(skip)) for skip in skip_paths):
                        continue
                    for file in files:
                        if file.endswith('.m'):
                            file_path = os.path.join(root, file)
                            leaked_blocks = find_leaked_blocks(file_path)

                            log_file.write(f"檢查文件: {file_path}\n")

                            if leaked_blocks:
                                log_file.write("可能洩漏 block 的 function：\n")
                                for function, line_number in leaked_blocks:
                                    log_file.write(f"    function: {function}, line: {line_number}\n")
                            else:
                                log_file.write("沒有可能洩漏 block 的 function。\n")
                            log_file.write("------------------------------------------------------\n")
            print("檢查成功請查看 leak_log.txt")
            print("")
        elif choice == '3':
            break
        else:
            print("無效的選項，請重新選擇。")
            print("")


if __name__ == "__main__":
    main()
