import os

import pypinyin


def cn2py(word) -> str:
    """保存声调，防止出现类似方舟干员红与吽拼音相同声调不同导致红照片无法保存的问题"""
    temp = ""
    for i in pypinyin.pinyin(word, style=pypinyin.Style.TONE3):
        temp += "".join(i)
    return temp


def rename_files(directory):
    """
    将目录下文件名中文字重命名为拼音，全角符号去掉。

    Args:
      directory: 目录路径。
    """

    for filename in os.listdir(directory):
        # 获取文件路径
        file_path = os.path.join(directory, filename)
        # 忽略目录
        if os.path.isdir(file_path):
            continue

        print("filename: ", filename)
        # 将文件名中的中文转换为拼音
        new_filename = cn2py(filename)
        # 去掉文件名中的全角符号
        new_filename = "".join(
            c for c in new_filename if c == "." or ("\u4e00" <= c <= "\u9fa5")
        )
        print("new_filename: ", new_filename)
        # 重命名文件
        os.rename(file_path, os.path.join(directory, new_filename))

    print(f"重命名完成！目录：{directory}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python rename.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    rename_files(directory)
