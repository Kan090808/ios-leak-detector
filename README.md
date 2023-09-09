# Objective-C Source Code Leak Detector Tool

This tool is designed to inspect Objective-C source code files for potential memory leaks, pinpointing functions where `self` is directly used within blocks.

## How to Use

1. **`config.txt`** 
    - `project_path` - Project location.
    - `skip_path` - Paths of directories that should be skipped from checking (multiple paths can be provided).
    - `only_print_leaks` - Whether to print only functions with leaks.
2. **`detector.py`** 
    - Run `python detector.py`. If there's an error prompt, you might need to install required libraries first.
3. **`leak_log.txt`** 
    - After execution, this file will be automatically generated, allowing you to check which functions need modifications.

## Bug
Currently, the `self` within comments or textual content is mistakenly identified as a leak. This will be addressed when time permits.

---
# Objective-C 源碼洩漏檢查工具

這個工具可以檢查 Objective-C 的源碼文件中可能造成記憶體洩漏的情況，找出 block 中直接使用 self 的 functions。

## 如何使用
1. **`config.txt`** 
    - `project_path` - 專案位置
    - `skip_path` - 不需要檢查的資料夾路徑（可填多個路徑）
    - `only_print_leaks` - 是否只印出有 leak 的 function
2. **`detector.py`** 
    - 執行 `python detector.py`，如果有錯誤提示，可以先安裝所需的 library
3. **`leak_log.txt`** 
    - 執行結束會自動產生這個文件，可以在裡面看出哪些 function 需要修正

## bug
目前註解或文案中的 `self` 也會誤判為 leak，有空再修正