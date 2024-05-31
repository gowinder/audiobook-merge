#!/usr/bin/env bash

####################################################
# Required Libraries
#
# library name | commands used   | verified version
# ------------------------------------------------
# ffmpeg       | ffmpeg/ffprobe  | 3.1.4 3.2
# gpac         | mp4box          | 0.6.1
# mp4v2        | mp4chaps        | 2.0.0
# coreutils    | find/gdate | 8.25
#
# Usage
# ./mp4.sh merge_as_chapter input_dir output.mp4
#
####################################################
check_dependency(){
    echo "ffmpeg    $(echo_if $(program_is_installed ffmpeg))"
    echo "gpac      $(echo_if $(program_is_installed mp4box))"
    echo "mp4v2     $(echo_if $(program_is_installed mp4chaps))"
    echo "coreutils $(echo_if $(program_is_installed find))" # 使用 find
}

# Merge multiple mp4 files as chapters
#   - Each input file name will be the chapter title
#   - Chapter markers in the input files will NOT be preserved
#   - Each input file must be extractly same format
merge_as_chapter(){
    echo "### Merge As Chapter ###, $#, $1, $2, $3"

    if [ "$#" -lt 2 ]; then
        echo "Error: Wrong number of parameters:"
        echo "Usage: merge_as_chapter input_dir output.m4b"
        return
    fi

    local input_dir="$1"
    local output="$2"

    echo "input_dir:" "$input_dir"
    echo "output   :" "$output"

    local chapterfile=$(printf "%s-%s" "/tmp/chapterfile" "$(basename ${output} .${output##*.})")

    local files=($(find "$input_dir" -type f -name "*.m4a" | sort -V))
    merge_file "${files[@]}" "$output" &&
    create_chapterfile "${files[@]}" > "$chapterfile" &&
    add_chaptermark "$chapterfile" "$output"
}

# Merge multiple m4a/mp3 files
#   - Chapter markers in the input files will NOT be preserved
#   - Each input file must be extractly same format
merge_file(){
    echo "### Merge File ###"

    if [ "$#" -lt 2 ]; then
        echo "Usage: merge_file input.m4a [input.m4a...] output.m4b"
        return
    fi

    local output=${!#}
    set -- "${@:1:$# -1}"

    echo "input :" "$@"
    echo "output:" "$output"

    ffmpeg -n -f concat -safe 0 -i <(create_filelist "$@") -c copy "$output"
}

add_chaptermark(){
    echo "### Add Chaptermark ###"

    if [ "$#" -ne 2 ]; then
        echo "Usage: add_chaptermark chapterfile file.m4b"
        return
    fi

    local chapterfile="$1"
    local input="$2"
    echo "chapterfile:" "$chapterfile"
    echo "input file:" "$input"

    # 显示章节文件的内容以进行调试
    echo "Content of chapterfile:"
    cat "$chapterfile"

    # 添加章节标记并打印调试信息
    if mp4box -chap "$chapterfile" "$input"; then
        echo "mp4box completed successfully"
    else
        echo "mp4box encountered an error"
        return 1
    fi

    # 转换章节标记并打印调试信息
    if mp4chaps --convert --chapter-qt "$input"; then
        echo "mp4chaps completed successfully"
    else
        echo "mp4chaps encountered an error"
        return 1
    fi
}


create_chapterfile(){
    echo "### Create Chapterfile ###"

    if [ "$#" -lt 1 ]; then
        echo "Usage: create_chapterfile input.m4a [input.m4a...]"
        return
    fi

    local chapter_start=0
    local chapter_end=0
    local files=("$@")
    # 按数字排序
    files=( $(sort -V <<< "${files[@]}") )
    for ((i=0; i<${#files[@]}; i++)); do
        file="${files[$i]}"
        local chapter_name=$(basename "$file" .m4a)
        local chapter_number=$(printf "CHAPTER%s" $((i+1)))
        local duration=$(duration "$file")

        printf "%s=%s\n" "$chapter_number" $(gdate -d@"$chapter_start" -u +%T.%3N) | tee -a /tmp/create_chapterfile.log
        printf "%sNAME=%s\n" "$chapter_number" "$chapter_name" | tee -a /tmp/create_chapterfile.log

        # 添加间隔
        chapter_end=$(bc <<< "scale=6;$chapter_end+ $duration + 0.001")
        chapter_start=$(bc <<< "scale=6;$chapter_end")
    done
}

create_filelist() {
    for file in "$@"; do
        printf "file %q\n" "$file" | tee -a /tmp/create_filelist.log
    done
}

duration(){
        ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$1"
}


# ==============================================
# https://gist.github.com/JamieMason/4761049
# ==============================================
function program_is_installed {
  local return_=1
  type $1 >/dev/null 2>&1 || { local return_=0; }
  echo "$return_"
}

function echo_fail {
  printf "\e[31m✘ ${1}"
  echo -e "\033[0m"
}

function echo_pass {
  printf "\e[32m✔ ${1}"
  echo -e "\033[0m"
}

function echo_if {
  if [ $1 == 1 ]; then
    echo_pass $2
  else
    echo_fail $2
  fi
}

# ==============================================

# call arguments verbatim:
"$@"
