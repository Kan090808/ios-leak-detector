import re

func = """
code
code
code
"""

leaked_blocks = []

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

match = re.search(r'-\s*\([^)]+\)\s*([^{\s]+)', func)
if match:
    function_name = match.group(1)

    start_index = func.find('{')
    if start_index != -1:
        func = func[start_index:]

    blocks = extract_blocks(func)
    # print(blocks)
    for block in blocks:
        # print(block)
        # Check if "self" is used in the block without being prefixed by "weak" or "strong"
        if re.search(r'\b(?!weak|strong)\bself\b', block):
            # print(block)
            leaked_blocks.append(function_name.strip())

if leaked_blocks:
    print(f"Potential leaks in function: {leaked_blocks[0]}")
else:
    print("No potential leaks found.")
