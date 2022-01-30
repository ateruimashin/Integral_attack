# coding:utf-8
#!python2.7
# 上の2行はSyntaxError: Non-ASCII character ‘\xe3’ in fileというエラーを解決するためのおまじないです
"""
    <プログラム内容>
        SIMON32に対するBDPTを利用したIntegral特性探索

        論文"MILP Method of Searching Integral Distinguishers Based on Division Property Using Three Subsets"
        を参考に作成しています。論文名が示されていないページ数は全てこの論文のページ番号です。
        url: https://eprint.iacr.org/2018/1186

        入力:	ブロック長,段数(= ROUND),特性判定したいbit番号(= M)
        出力:	最終段出力のMbit目の特性を標準出力へ表示
        データの並び:	論文"MILP Method of Searching Integral Distinguishers Based on Division Property Using Three Subsets"
                        とは異なり (x_0,x_1,..,x_n-1,y_0,y_1,..,y_n-1) の順です。

    <検証済み>
    - 動作環境
        Python3.9.1 64-bit
        Gurobi9.5.0
    -結果
        ---14round-SIMON32---
        入力集合:	(caaaaaaaaaaaaaaa, aaaaaaaaaaaaaaaa)
        出力集合:	(????????????????, ?b??????b??????b)

    <製作者>
    Original: Mr. N(M1)
    Editor: Jago39(M2)(it's me.)

    <私の作業範囲>
        - 全てのビットを探索できるよう探索部分を関数にまとめた
        - 論文の参照箇所などをコメントに追記した
        - 全てのビットの特性の出力をまとめて行えるようにした
        - 鍵の排他とswappingのタイミングを調整することで他の暗号にも適用しやすくした
        - 時間を計測している(おまけ)

    <Originalとの変更点>
        - Originalではブロック長を可変にしていたが、このプログラムでは32bit固定とした

    <謝辞>
    論文に記載のアルゴリズム通りにプログラムを記述し、更にゼミで詳しい説明をしてくれた
    M1のMr. Nに感謝を示します。
"""
from re import I
from SCBDP import Simon
import time


def sarchBDPTtrail(WORD_LENGTH, ROUND, M, K, L):

    # Mbit目=1の単位ベクトルe
    e = [0 for i in range(WORD_LENGTH*2)]  # e = 00...0
    e[M] = 1								# Mbit目のみ1にしている
    # ここまででe = 00...0100...0となる

    # core operationにおけるLベクトルのBDPTの伝搬
    # cf:P.14 Table 5 of Bit-Based Division Property and Application to Simon Family
    BDPT_propagation_of_core_operation = {'[0, 0, 0, 0]': [[0, 0, 0, 0]],
                                          '[1, 0, 0, 0]': [[1, 0, 0, 0]],
                                          '[0, 1, 0, 0]': [[0, 1, 0, 0]],
                                          '[1, 1, 0, 0]': [[1, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 1]],
                                          '[0, 0, 1, 0]': [[0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 1, 1]],
                                          '[1, 0, 1, 0]': [[1, 0, 1, 0], [1, 0, 0, 1], [1, 0, 1, 1]],
                                          '[0, 1, 1, 0]': [[0, 1, 1, 0], [0, 1, 0, 1], [0, 1, 1, 1]],
                                          '[1, 1, 1, 0]': [[1, 1, 1, 0], [0, 0, 1, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 0, 1]],
                                          }

    for r in range(ROUND):
        # r段目段関数を分割した各処理の番号(core operationが何回行われるかという意味)
        for num in range(WORD_LENGTH+1):  # Core operationと鍵の排他を1段で4回行うという意味のループ
            if num != WORD_LENGTH:  # 段鍵の排他的論理和以外の演算, 8回演算すると鍵の排他へ行く
                for k in K:
                    simon = Simon(ROUND, r, num, k, M, WORD_LENGTH)
                    simon.MakeModel()  # LPファイルの作成
                    if simon.SolveModel() == 'unknown':  # Stopping Rule 1☜lazy propagation
                        return('?')  # unknownを返す
                '''
                論文中はKベクトルから要素kベクトルを取り除くと書いてあるが、この部分はunknownが返るか、ベクトルを取り除かれるかの処理なので、
                Stopping Rule1で終了しなければ全てのベクトルがKベクトルから取り除かれることになる。
                '''
                K = []  # pruning technique

                new_L = []  # L'(i,j)=Φ
                for l in L:
                    simon = Simon(ROUND, r, num, l, M, WORD_LENGTH)
                    simon.MakeModel()
                    if simon.SolveModel() == 'unknown':
                        new_L.append(l)

                if not new_L:  # Stopping Rule 2☜fast propagation
                    return('b')  # balanceを返す

                L = new_L[:]  # ベクトルをコピーして代入する

                # --------------------------------------BDPTの伝搬規則にしたがって、次のLを求める(Kは空集合のまま)--------------------------------------------------
                next_L = []

                # core operationで対象となるbit番号(アルゴリズム3 19行目)
                index = [(num+1) % WORD_LENGTH, (num+8) %
                         WORD_LENGTH, (num+2) % WORD_LENGTH, WORD_LENGTH + num]

                # core operationでのBDPT伝搬
                for l in L:
                    part_l = [l[i] for i in index]
                    key = str(part_l)
                    if key in BDPT_propagation_of_core_operation.keys():  # 辞書に含まれる全てのキーを取得し、存在するか調べる
                        # キーに対応する辞書に含まれる全ての値を取得する
                        for next_part_l in BDPT_propagation_of_core_operation[key]:
                            next_l = l[:]
                            for i in range(len(index)):
                                next_l[index[i]] = next_part_l[i]
                            if next_l in next_L:
                                next_L.remove(next_l)
                            else:
                                next_L.append(next_l)
                    else:
                        if l in next_L:
                            next_L.remove(l)
                        else:
                            next_L.append(l)

                L = next_L[:]

            else:  # 段鍵の排他的論理和(Q_{i,n}の時の処理)
                for l in L:
                    '''
                    集合Kの更新
                    BDPT後のpuring techniqueによって、最初の集合Kは空集合になっている。
                    この後、集合L内から条件を満たすベクトルを見つけ、それを集合Kに代入していく。
                    '''
                    for i in range(WORD_LENGTH):
                        # 鍵をXORする場所は右側なので、そのビット位置を算出する
                        XOR_key = WORD_LENGTH + i
                        if l[XOR_key] == 0:  # BDPTにおける鍵の排他の制約式は1をANDするので、0の場合のみbitの値が変わる
                            new_k = l[:]
                            new_k[XOR_key] = 1
                            K.append(new_k)			# 1を排他したベクトルは集合Kに代入する

                # 余分なベクトルlを集合Lから除く
                new_L = []
                for l in L:
                    jugde = True
                    for k in K:
                        temp = []
                        for a, b in zip(k, l):
                            temp.append(a and b)
                        if temp == k:
                            jugde = False
                            break   # 冗長なベクトルを除外する
                    if jugde:
                        new_L.append(l)  # それ以外を再びnew_Lに入れる

                # 集合Lの更新(冗長なベクトルが取り除かれた集合Lが得られる)
                L = new_L[:]

                '''
                集合K内のベクトルをそれぞれswapする
                pythopnのfor文内でオブジェクト内の要素を書き換える時の注意点
                例えばリスト内から取り出した要素をelementとすると、element+=2としてもリスト内の要素は書き換えられない。
                書き換えたい場合は、新しいオブジェクトに代入してfor文が終わった後に元のオブジェクトに新しいオブジェクトを代入する、
                もしくは、次のようにindexも取得してその位置に代入するということを行う。
                詳細はhttps://ateruimashin.com/diary/2022/01/python-for-list/ に書いたので参照してください。
                '''

                for elementIndex, element in enumerate(K):
                    K[elementIndex] = \
                        element[WORD_LENGTH:] \
                        + element[:WORD_LENGTH]

                # 集合L内のベクトルをそれぞれswapする
                for elementIndex, element in enumerate(L):
                    L[elementIndex] = \
                        element[WORD_LENGTH:] \
                        + element[:WORD_LENGTH]

                # Stopping Rule 3
                if r == ROUND - 1:
                    if (not K) and (e in L):
                        return('b')
                    else:
                        return('?')


if __name__ == "__main__":
    '''
    時間計測
    '''
    start = time.time()

    '''
    ROUND段目の出力暗号文の特性を判定する
    '''

    ROUND = int(input("Input the target round number: "))  # 調べる段数
    while not (ROUND >= 1):
        print("Input a round number greater than 0.")
        ROUND = int(input("Input the target round number again: "))

    WORD_LENGTH = int(16)  # 1wordの長さ

    # M = int(input("Input the number of m: "))  # 調べる段数の最集段出力の何bit目の特性を判定するか
    # while not (M < WORD_LENGTH*2 and M >= 0):
    #     print("Input a number of activebits with range (0, 64):")
    #     M = int(input("Input the number of m: "))

    # アクティブビット(a)の数、今回は使用しない
    # ACTIVEBITS = int(input("Input the number of acitvebits again: "))

    result = []
    # 全ビットの特性探索
    for M in range(WORD_LENGTH*2):
        # KベクトルとLベクトルを空の状態で作成する
        K = []
        L = []

        '''
        初期ベクトルの作成
        P.17 4.3節を参照
        Kベクトルの初期ベクトルは全て1固定でよい
        Lベクトルの初期ベクトルに調べたい平文を入れる
        入力集合 左端=c, その他=a
        '''
        k0 = [1 for i in range(WORD_LENGTH*2)]
        K.append(k0)  # K=[11...1],32ビット
        l0 = [1 for i in range(WORD_LENGTH*2)]
        l0[0] = 0
        L.append(l0)  # L=[011...1],32ビット

        # 特性探索
        result.append(sarchBDPTtrail(WORD_LENGTH, ROUND, M, K, L))

    print(result)

    processTime = time.time() - start
    print(processTime)
