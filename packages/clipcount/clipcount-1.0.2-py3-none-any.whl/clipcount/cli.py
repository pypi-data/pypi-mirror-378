import sys
from .core import clipcount
from .usage import usage_en, usage_jp

class OptionFormatError(Exception):
    """オプションの形式が不正な場合に投げる例外"""
    pass

def main():
    i = 1
    options = set()  # 使用されたオプションを保存するための集合
    try:
        while i < len(sys.argv):
            if sys.argv[i] in ["-h", "--help"]:
                usage_en()
                sys.exit(0)
            elif sys.argv[i] in ["--help-jp","--help_jp"]:
                usage_jp()
                sys.exit(0)
            elif sys.argv[i] in ["--split"]:
                options.update({sys.argv[i]})
                i += 1
            elif sys.argv[i] in ["--no-break"]:
                options.update({sys.argv[i]})
                i += 1
            elif sys.argv[i] in ["--no-space"]:
                options.update({sys.argv[i]})
                i += 1
            elif sys.argv[i] in ["--no-SPACE"]:
                options.update({sys.argv[i]})
                i += 1
            elif sys.argv[i] in ["--no-tab"]:
                options.update({sys.argv[i]})
                i += 1
            elif sys.argv[i] in ["--multi"]:
                options.update({sys.argv[i]})
                i += 1
            elif sys.argv[i].startswith("--"):
                raise OptionFormatError(f"無効なオプションです。--help を使用してください: {sys.argv[i]}")
            elif sys.argv[i].startswith("-"):
                # オプションが複数組み合わさっている場合も考慮して、一文字ずつ分割
                options.update(sys.argv[i][1:])
                i += 1
            else:
                raise OptionFormatError(f"オプションはハイフンで始める必要があります: {sys.argv[i]}")

    except OptionFormatError as e:
        print(f"\033[91mError: Invalid Option\n{e}\033[0m")
        sys.exit(1)
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
        sys.exit(1)


    print(clipcount(options))
