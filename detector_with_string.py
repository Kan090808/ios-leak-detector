import re

func = """
code
code
code
"""

leaked_blocks = []

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

def count_char_before_index(s, char, index):
    """
    Count the occurrences of 'char' in 's' before the given 'index'.
    """
    return s[:index].count(char)

functions = split_objc_functions(func)
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
    # print(blocks[0])
    for block in blocks:
        # 檢查 block 中的 "self" 前面是否有 "weak" 或 "strong"
        match = re.search(r'\b(?!weak|strong)\bself\b', block)
        if match:
            # print(match.start())
            # print(count_char_before_index(block, '"', match.start()))
            if count_char_before_index(block, '"', match.start()) % 2 == 0:
                print("leaked")
                line_number = func[:func.index(func)].count('\n') + 1
                leaked_blocks.append((function_name.strip(), line_number))
            else:
                print("no leaked")

print(leaked_blocks)