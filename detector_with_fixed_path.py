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

def main():
    project_path = ""
    
    # 遍歷 project_path 中的所有文件和子目錄
    for root, dirs, files in os.walk(project_path):
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

if __name__ == "__main__":
    main()
