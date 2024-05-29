#!/bin/bash

# 检查参数是否为空
if [ $# -eq 0 ]; then
    echo "Usage: $0 directory_path"
    exit 1
fi

# 获取目录路径参数
directory="$1"

# 切换到指定目录
cd "$directory" || exit 1

# 遍历目录下所有的 .m4a 文件
for file in *.m4a; do
    # 使用正则表达式匹配文件名中的数字部分
    if [[ "$file" =~ ^([0-9]+)\. ]]; then
        # 将匹配到的数字部分格式化为三位数，前面补零
        new_number=$(printf "%03d" "${BASH_REMATCH[1]}")
        # 构建新的文件名
        new_file="${new_number}.${file#*.}"
        # 如果新的文件名与原文件名不同，则重命名文件
        if [[ "$new_file" != "$file" ]]; then
            mv "$file" "$new_file"
            echo "Renamed $file to $new_file"
        fi
    fi
done
