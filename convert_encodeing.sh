#!/bin/bash

# 获取所有 m4a 文件
files=$(find "$1" -type f -name "*.m4a")

# 遍历所有文件，将编码转换为 UTF-8
for file in $files; do
  # 假设文件编码为 GBK，您可以根据实际情况修改
  iconv -f GBK -t UTF-8 "$file" > "$file.utf8"
  mv "$file.utf8" "$file"
done
