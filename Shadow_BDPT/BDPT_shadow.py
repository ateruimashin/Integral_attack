"""
<プログラム内容>
	Shadowに対するBDPTを利用したIntegral特性探索

	論文"MILP Method of Searching Integral Distinguishers Based on Division Property Using Three Subsets"
	を参考に作成しています。論文名が示されていないページ数は全てこの論文のページ番号です。

	入力:	ブロック長,段数(= ROUND),特性判定したいbit番号(= M)
	出力:	最終段出力のMbit目の特性を標準出力へ表示
	データの並び:	論文"MILP Method of Searching Integral Distinguishers Based on Division Property Using Three Subsets"
					とは異なり (x_0,x_1,..,x_n-1,y_0,y_1,..,y_n-1) の順です。
                    そのため、core operationのbit-rotationでの演算が、論文では(j-1) mod nとなっているところは(j+1) mod nと
                    同じことを示します。
"""


from SCBDP import Simon

'''
関数内で使い回す変数や辞書をグローバル空間で宣言している
'''
WORD_LENGTH = int(8)  # 1wordの長さ

# core operationにおけるLベクトルのBDPTの伝搬
# cf:P.14 Table 5 of Bit-Based Division Property and Application to shadow Family
BDPT_propagation_of_core_operation = {'[0, 0, 0, 0]': [[0, 0, 0, 0]],
                                      '[1, 0, 0, 0]': [[1, 0, 0, 0]],
                                      '[0, 1, 0, 0]': [[0, 1, 0, 0]],
                                      '[1, 1, 0, 0]': [[1, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 1]],
                                      '[0, 0, 1, 0]': [[0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 1, 1]],
                                      '[1, 0, 1, 0]': [[1, 0, 1, 0], [1, 0, 0, 1], [1, 0, 1, 1]],
                                      '[0, 1, 1, 0]': [[0, 1, 1, 0], [0, 1, 0, 1], [0, 1, 1, 1]],
                                      '[1, 1, 1, 0]': [[1, 1, 1, 0], [0, 0, 1, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 0, 1]],
                                      }


def sarchBDPTtrail(ROUND, M, K, L):

    # Mbit目=1の単位ベクトルe
    e = [0 for i in range(WORD_LENGTH * 4)]  # e = 00...0
    e[M] = 1								# Mbit目のみ1にしている
    # ここまででe = 0...010...0となる

    for r in range(ROUND):
        # r段目段関数を分割した各処理の番号(core operationが何回行われるかという意味)
        for num in range(4 * (WORD_LENGTH + 1)):

            if num != 8 and num != 17 and num != 26 and num != 35:  # numが鍵の排他タイミングではない場合
                for k in K:
                    '''
                    r: 現在のラウンド
                    num: Q_iのi
                    k: Kベクトル
                    M: 調べるビット位置
                    '''
                    if (num >= 0 and num <= 7) or (num >= 18 and num <= 25):
                        shadow = Simon(
                            ROUND, r, num % 8, k[: WORD_LENGTH * 2], M, WORD_LENGTH)
                    else:
                        shadow = Simon(
                            ROUND, r, num % 8, k[WORD_LENGTH * 2:], M, WORD_LENGTH)

                    shadow.MakeModel()  # LPファイルの作成
                    solveK_Result = shadow.SolveModel()
                    if solveK_Result == 'unknown':  # Stopping Rule 1☜lazy propagation
                        return('u')  # unknownを返す
                    elif solveK_Result == 'error':
                        exit()
                '''
                論文中はKベクトルから要素kベクトルを取り除くと書いてあるが、この部分はunknownが返るか、ベクトルを取り除かれるかの処理なので、
                Stopping Rule1で終了しなければ全てのベクトルがKベクトルから取り除かれることになる。
                '''
                K = []  # pruning technique

                new_L = []  # L'(i,j)=Φ
                for l in L:
                    '''
                    r: 現在のラウンド
                    num: Q_iのi
                    l: Lベクトル
                    M: 調べるビット位置
                    '''
                    if (num >= 0 and num <= 7) or (num >= 18 and num <= 25):
                        shadow = Simon(
                            ROUND, r, num % 8, l[: WORD_LENGTH * 2], M, WORD_LENGTH)
                    else:
                        shadow = Simon(
                            ROUND, r, num % 8, l[WORD_LENGTH * 2:], M, WORD_LENGTH)
                    shadow.MakeModel()
                    solveL_Result = shadow.SolveModel()
                    if solveL_Result == 'unknown':
                        new_L.append(l)
                    elif solveL_Result == 'error':
                        exit()

                if not new_L:  # Stopping Rule 2☜fast propagation
                    return('b')  # balanceを返す

                L = new_L[:]  # ベクトルをコピーして代入する

                # --------------------------------------BDPTの伝搬規則にしたがって、次のLを求める(Kは空集合のまま)--------------------------------------------------
                next_L = []

                '''
                core operationで対象となるbit番号(アルゴリズム3 19行目)
                shadowはSIMONを4回行い、右16ビットを右側のSIMON、左16ビットを左側のSIMONに通す。
                そのため、どちらか片方を通した後の32ビットを考える必要がある。
                '''
                index = []
                # 左側(0~15ビット目)にcore operationを行うときのindex
                index1 = [(num + 1) % WORD_LENGTH, (num + 7) %
                          WORD_LENGTH, (num + 2) % WORD_LENGTH, WORD_LENGTH + num]
                # 右側(16~31ビット目)にcore operationを行うときのindex
                index2 = [(num + 1) % WORD_LENGTH + 16, (num + 7) % WORD_LENGTH +
                          16, (num + 2) % WORD_LENGTH + 16, WORD_LENGTH + num + 16]
                if (num >= 0 and num <= 7) or (num >= 18 and num <= 25):
                    index = index1[:]
                else:
                    index = index2[:]

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

            else:
                for l in L:
                    # 集合Kの更新
                    for i in range(WORD_LENGTH):
                        # 鍵を排他するビット位置
                        if(num == 8 or num == 26):
                            XOR_key = WORD_LENGTH + i
                        else:
                            XOR_key = 3 * WORD_LENGTH + i

                        if l[XOR_key] == 0:  # BDPTにおける鍵の排他の制約式は1をANDするので、0の場合のみbitの値が変わる
                            new_k = l[:]
                            new_k[i] = 1
                            K.append(new_k)			# 1を排他したベクトルはKベクトルに代入する

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
                            break
                    if jugde:
                        new_L.append(l)

                L = new_L[:]  # 集合Lを更新

                '''
                4つのwordにa,b,c,dと名前をつける。この時numの値によってシャッフルが異なる。以下にシャッフル前後のwordの関係を示す。
                num = 17: a,b,c,d -> b,a,d,c
                num = 35: a,b,c,d -> c,b,a,d
                '''
                if(num == 17):
                    # 集合K内のベクトルをそれぞれswapする
                    '''
                    pythopnのfor文内でオブジェクト内の要素を書き換える時の注意点
                    例えばリスト内から取り出した要素をelementとすると、element+=2としてもリスト内の要素は書き換えられない。
                    書き換えたい場合は、新しいオブジェクトに代入してfor文が終わった後に元のオブジェクトに新しいオブジェクトを代入する、
                    もしくは、次のようにindexも取得してその位置に代入するということを行う。
                    詳細はhttps://ateruimashin.com/diary/2022/01/python-for-list/ に書いたので参照してください。
                    '''
                    for elementIndex, element in enumerate(K):
                        K[elementIndex] = \
                            element[WORD_LENGTH: WORD_LENGTH * 2] +\
                            + element[: WORD_LENGTH] \
                            + element[WORD_LENGTH * 3: WORD_LENGTH * 4] \
                            + element[WORD_LENGTH * 2: WORD_LENGTH * 3]

                    # 集合L内のベクトルをそれぞれswapする
                    for elementIndex, element in enumerate(L):
                        L[elementIndex] = \
                            element[WORD_LENGTH: WORD_LENGTH * 2] +\
                            + element[: WORD_LENGTH] \
                            + element[WORD_LENGTH * 3: WORD_LENGTH * 4] \
                            + element[WORD_LENGTH * 2: WORD_LENGTH * 3]

                elif(num == 35):
                    for elementIndex, element in enumerate(K):
                        K[elementIndex] = element[WORD_LENGTH:] + \
                            element[:WORD_LENGTH]

                    # 集合L内のベクトルをそれぞれswapする
                    L = new_L[:]    # 集合new_Lを集合Lに代入(コピーしてる)
                    for elementIndex, element in enumerate(L):
                        L[elementIndex] = element[WORD_LENGTH:] + \
                            element[:WORD_LENGTH]

                # Stopping Rule 3
                if r == ROUND - 1:
                    if (not K) and (e in L):
                        return('b')
                    else:
                        return('?')


if __name__ == "__main__":

    '''
    ROUND段目の出力暗号文の特性を判定する
    '''

    ROUND = int(input("Input the target round number: "))  # 調べる段数
    while not (ROUND >= 1):
        print("Input a round number greater than 0.")
        ROUND = int(input("Input the target round number again: "))

    # M = int(input("Input the number of m: "))  # 調べる段数の最集段出力の何bit目の特性を判定するか
    # while not (M < WORD_LENGTH*2 and M >= 0):
    #     print("Input a number of activebits with range (0, 64):")
    #     M = int(input("Input the number of m: "))

    # アクティブビット(a)の数、今回は使用しない
    # ACTIVEBITS = int(input("Input the number of acitvebits again: "))

    # KベクトルとLベクトルを空の状態で作成する
    K = []
    L = []
    '''
    P.17 4.3節を参照
    Kベクトルの初期ベクトルは全て1固定でよい
    Lベクトルの初期ベクトルに調べたい平文を入れる
    入力集合 左端=c, その他=a
    '''
    k0 = [1 for i in range(WORD_LENGTH*4)]
    K.append(k0)  # K=[11...1],32ビット
    l0 = [1 for i in range(WORD_LENGTH*4)]
    l0[0] = 0
    L.append(l0)  # L=[011...1],32ビット

    # 結果のリスト
    result = []
    # 全ビットの特性探索
    for M in range(WORD_LENGTH * 4):
        result.append(sarchBDPTtrail(ROUND, M, K, L))

    print(result)
