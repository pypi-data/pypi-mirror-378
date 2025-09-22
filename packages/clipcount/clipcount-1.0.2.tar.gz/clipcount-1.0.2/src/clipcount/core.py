import pyperclip
import unicodedata
import sys

def calc_display_width(text: str) -> float:
    """
    与えられた文字列の表示幅を計算する。
    - 全角(F, W, A)の文字は幅1
    - それ以外は幅0.5
    """
    count = 0
    for c in text:
        # Unicode の「東アジア幅プロパティ」を取得
        #   F = Fullwidth（全角）
        #   W = Wide（全角扱い）
        #   A = Ambiguous（環境により全角/半角が変わる文字）
        #   H = Halfwidth（半角）
        #   Na = Narrow（狭い、通常のASCII文字）
        #   N = Neutral（幅が特定されない記号など）
        #
        # F, W, A の場合は「全角扱い」で幅 1 とする
        if unicodedata.east_asian_width(c) in "FWA":
            count += 1
        else:
            count += 0.5
    return count


def clipcount(options=set()):
    try:
        # デフォルトの空dict判定を修正
        if options == {}:
            options = set()
        elif not isinstance(options, set):
            raise TypeError("options は set 型である必要があります")

        # クリップボードの取得
        txt = "".join(pyperclip.paste())

        # オプション処理
        if {"--split","split"} & options:
            txt = "".join(txt.split())
        else:
            if {"-b","b","--no-break","no-break"} & options:
                txt = "".join(txt.splitlines())
            if {"-s","s","--no-space","no-space"} & options:
                txt = "".join(txt.split(" "))
            if {"-S","S","--no-SPACE","no-SPACE"} & options:
                txt = "".join(txt.split("　"))
            if {"-t","t","--no-tab","no-tab"} & options:
                txt = "".join(txt.split("\t"))

        # カウント方法切り替え
        if {"-m","m","--multi","multi"} & options:
            return calc_display_width(txt)
        else:
            return len(txt)

    except pyperclip.PyperclipException as e:
        print(f"\033[91mクリップボードの操作に失敗しました: {e}\033[0m")
        sys.exit(1)
    except Exception as e:
        print(f"\033[91mエラーが発生しました: {e}\033[0m")
        sys.exit(1)
