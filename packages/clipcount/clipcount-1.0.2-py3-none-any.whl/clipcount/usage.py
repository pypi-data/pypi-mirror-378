def usage_en():
    print("""
Usage: clipcount [options]

Description: Reads the clipboard and outputs the character count.

Features: By default, it outputs the character count, including whitespace characters (line breaks, spaces, full-width spaces, tabs).

Arguments: None

Options:
    -h|--help           Display help
       --help-jp        Display help in Japanese
    -b|--no-break       Exclude line breaks
    -s|--no-space       Exclude half-width spaces
    -S|--no-SPACE       Exclude full-width spaces
    -t|--no-tab         Exclude tabs
       --split          Exclude whitespace characters (line breaks, half-width spaces, full-width spaces, tabs)
    -m|--multi          Treat half-width alphanumeric characters as 0.5 characters each


""")


def usage_jp():
    print("""
使用法: clipcount [オプション] 

説明: クリップボードを読み取り、文字数を出力します。

特徴: デフォルトでは、空白文字（改行、半角空白、全角空白、タブ）を含めた文字数を出力します。

引数: 無し

オプション:
    -h|--help           ヘルプを表示します
       --help-jp        日本語のヘルプを表示します
    -b|--no-break       改行削除
    -s|--no-space       半角空白削除
    -S|--no-SPACE       全角空白削除
    -t|--no-tab         タブ削除
       --split          空白文字（改行、半角空白、全角空白、タブ）削除
    -m|--multi          半角英数を0.5文字として換算する

""")
