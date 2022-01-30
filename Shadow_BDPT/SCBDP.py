# coding:utf-8
#!python2.7
"""
データの並び:	論文"MILP Method of Searching Integral Distinguishers Based on Division Property Using Three Subsets"
				とは異なり (x_0,x_1,..,x_n-1,y_0,y_1,..,y_n-1) の順です。u,vなどについても同様です。
"""

from gurobipy import *


class Simon:
    # 左rotation定数
    R1 = 1
    R2 = 8
    R3 = 2

    def __init__(self, Round, i, j, k, m, word_len):  # SIMON_2nのnがword_len。2nはブロックサイズを表す。
        self.Round = Round  # 何段のSIMONか (self.Round >= 1)
        self.i = i  # i段目から 0 <= i < Round
        self.j = j  # jパートから
        self.k = k  # kベクトル
        self.m = m  # 最終段出力で1とするbit番号
        self.blocksize = 2 * word_len
        self.WORD_LENGTH = word_len
        self.filename_model = "Simon_" + \
            str(word_len * 2) + "_" + str(self.Round) + ".lp"
        fileobj = open(self.filename_model, "w")
        fileobj.close()

    # ----------------------------------------------------以下MILPモデル(=LPファイル)作成--------------------------------------------------------------------------------
    """
    LPファイルに書くべき情報
    ・制約式(初期条件含む)
    ・変数のタイプ(binary)
    """

    def CreateObjectiveFunction(self):
        """
        目的関数の設定
        藤堂さん曰く設定したほうが早くなるらしい
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Minimize\n")
        eqn = []
        for i in range(0, self.WORD_LENGTH):
            eqn.append("x" + "_" + str(self.Round) + "_" + str(i))
        for j in range(0, self.WORD_LENGTH):
            eqn.append("y" + "_" + str(self.Round) + "_" + str(j))
        temp = " + ".join(eqn)
        fileobj.write(temp)
        fileobj.write("\n")
        fileobj.close()

    def CreateVariable(self, n, x):  # n:段数, x:変数名
        """
        変数を生成		 
        """
        variable = []
        for i in range(0, self.WORD_LENGTH):
            variable.append(x + "_" + str(n) + "_" + str(i))  # n段目のibit目の変数x
        return variable

    def VariableRotation(self, x, n):  # x:入力ベクトル, n:左Rotationビット数
        """
        Bit Rotation.
        """
        eqn = []
        for i in range(0, self.WORD_LENGTH):
            eqn.append(x[(i + n) % self.WORD_LENGTH])
        return eqn

    def CreateConstrainsSplit(self, x_in, u, v, w, y_out):  # u,v,w:中間変数
        """
        copyの制約式をLPファイルに書き込み
        関数L1の制約式
        """
        with open(self.filename_model, "a") as fileobj:
            for i in range(0, self.WORD_LENGTH):
                eqn = []
                eqn.append(x_in[i])
                eqn.append(u[i])
                eqn.append(v[i])
                eqn.append(w[i])
                eqn.append(y_out[i])
                temp = " - ".join(eqn)
                temp = temp + " = " + str(0)
                fileobj.write(temp)
                fileobj.write("\n")

    def CreateConstraintsAnd(self, u, v, t):
        """
        andの制約式をLPファイルに書き込み
        関数L2の制約式
        """
        with open(self.filename_model, "a") as fileobj:
            for i in range(0, self.WORD_LENGTH):
                fileobj.write((t[i] + " - " + u[i] + " >= " + str(0)))
                fileobj.write("\n")
                fileobj.write((t[i] + " - " + v[i] + " >= " + str(0)))
                fileobj.write("\n")
                fileobj.write(
                    (t[i] + " - " + u[i] + " - " + v[i] + " <= " + str(0)))
                fileobj.write("\n")

    def CreateConstraintsXor(self, y_in, t, w, x_out):
        """
        xorの制約式をLPファイルに書き込み
        関数L3の制約式
        """
        with open(self.filename_model, "a") as fileobj:
            for i in range(0, self.WORD_LENGTH):
                eqn = []
                eqn.append(x_out[i])
                eqn.append(y_in[i])
                eqn.append(t[i])
                eqn.append(w[i])
                temp = " - ".join(eqn)
                temp = temp + " = " + str(0)
                fileobj.write(temp)
                fileobj.write("\n")

    def ForParticalRound(self, x_out, y_in):
        '''
        self.i段目の途中から探索を開始するための調整
        関数L4の制約式(CBDPのみで探す時はなかった部分)
                [MissSpell]partical→partial
        '''
        with open(self.filename_model, "a") as fileobj:
            for j in range(self.j):
                fileobj.write(x_out[j] + ' - ' + y_in[j] + ' = 0')
                fileobj.write("\n")

    def Init(self):
        """
        self.i段目の段関数への入力集合のBDPをkベクトルで初期化
        """
        with open(self.filename_model, "a") as fileobj:
            x = self.CreateVariable(self.i, "x")
            y = self.CreateVariable(self.i, "y")
            data = x + y
            for i in range(self.WORD_LENGTH * 2):
                fileobj.write(data[i] + " = " + str(self.k[i]))
                fileobj.write("\n")

    def end(self):
        """
        最終段出力の制約式
        """
        with open(self.filename_model, 'a') as fileobj:
            x = self.CreateVariable(self.Round, "x")
            y = self.CreateVariable(self.Round, "y")
            data = x + y
            for i in range(self.WORD_LENGTH * 2):
                if i == self.m:
                    fileobj.write(data[i] + " = 1")
                else:
                    fileobj.write(data[i] + " = 0")
                fileobj.write("\n")

    def CreateConstraints(self):
        """
        制約式の記述
        """
        with open(self.filename_model, "a") as fileobj:
            fileobj.write("Minimize\n")
            fileobj.write("Subject To\n")

        # Init(file)
        x_in = self.CreateVariable(self.i, "x")
        y_in = self.CreateVariable(self.i, "y")
        for i in range(self.i, self.Round):
            u = self.CreateVariable(i, "u")
            v = self.CreateVariable(i, "v")
            w = self.CreateVariable(i, "w")
            t = self.CreateVariable(i, "t")
            x_out = self.CreateVariable((i+1), "x")
            y_out = self.CreateVariable((i+1), "y")

            # partical_round(CBDPのみではなかった部分)
            if i == self.i:
                self.ForParticalRound(x_out, y_in)

            # copy
            self.CreateConstrainsSplit(x_in, u, v, w, y_out)

            # 左rotation
            u = self.VariableRotation(u, Simon.R1)
            v = self.VariableRotation(v, Simon.R2)
            w = self.VariableRotation(w, Simon.R3)

            # and
            self.CreateConstraintsAnd(u, v, t)

            # xor
            self.CreateConstraintsXor(y_in, t, w, x_out)

            # x_in,y_inの更新
            x_in = x_out
            y_in = y_out

    def BinaryVariable(self):
        """
        Specify variable type.
        """
        with open(self.filename_model, "a") as fileobj:
            fileobj.write("Binary\n")
            for i in range(self.i, self.Round):
                for j in range(0, self.WORD_LENGTH):
                    fileobj.write(("x_" + str(i) + "_" + str(j)))
                    fileobj.write("\n")
                for j in range(0, self.WORD_LENGTH):
                    fileobj.write(("y_" + str(i) + "_" + str(j)))
                    fileobj.write("\n")
                for j in range(0, self.WORD_LENGTH):
                    fileobj.write(("u_" + str(i) + "_" + str(j)))
                    fileobj.write("\n")
                for j in range(0, self.WORD_LENGTH):
                    fileobj.write(("v_" + str(i) + "_" + str(j)))
                    fileobj.write("\n")
                for j in range(0, self.WORD_LENGTH):
                    fileobj.write(("w_" + str(i) + "_" + str(j)))
                    fileobj.write("\n")
                for j in range(0, self.WORD_LENGTH):
                    fileobj.write(("t_" + str(i) + "_" + str(j)))
                    fileobj.write("\n")

            # 変数x,yは最終段の出力も考慮
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("x_" + str(self.Round) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("y_" + str(self.Round) + "_" + str(j)))
                fileobj.write("\n")
            fileobj.write("END")

    def MakeModel(self):
        self.CreateConstraints()
        self.Init()
        self.end()
        self.BinaryVariable()

    # -----------------------------------------------------end--------------------------------------------------------------------------------

    def SolveModel(self):
        """
        Solve the MILP model to search the integral distinguisher of Simon.
        """
        m = read(self.filename_model)
        m.optimize()
        # Gurobi syntax: m.Status == 2 represents the model is feasible.
        if m.Status == 2:
            return 'unknown'
        # Gurobi syntax: m.Status == 3 represents the model is infeasible.
        elif m.Status == 3:
            return 'balanced'
        else:
            print("Unknown error!")
            return 'Unknown error!'
