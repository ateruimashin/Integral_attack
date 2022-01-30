# coding:utf-8
"""
暗号名:   Shadow
ワード長: 8bit or self.wordlenbit
段数:     self.wordlen段 or 32段
入力変数: xleft,yleft,xright,yright
"""
from gurobipy import *


class Shadow:
    def __init__(self, Round, i, j, k, m, word_len):  # SIMON_2nのnがword_len。2nはブロックサイズを表す。
        self.Round = Round  # 何段のSIMONか (self.Round >= 1)
        self.i = i  # i段目から 0 <= i < Round
        self.j = j  # jパートから
        self.k = k  # kベクトル
        self.m = m  # 最終段出力で1とするbit番号
        self.blocksize = 2 * word_len
        self.WORD_LENGTH = word_len
        self.filename_model = "Simon_" + \
            str(word_len * 4) + "_" + str(self.Round) + ".lp"
        fileobj = open(self.filename_model, "w")
        fileobj.close()

    # ローテーションbit数
    R1 = 1
    R2 = 7
    R3 = 2

    def CreateObjectiveFunction(self):
        """
        目的関数の作成
        藤堂さん曰く設定したほうが早くなるらしい
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Minimize\n")
        eqn = []
        for i in range(0, self.WORD_LENGTH):
            eqn.append("x0" + "_" + str(self.Round) + "_" + str(i))
        for i in range(0, self.WORD_LENGTH):
            eqn.append("x1" + "_" + str(self.Round) + "_" + str(i))
        for i in range(0, self.WORD_LENGTH):
            eqn.append("x2" + "_" + str(self.Round) + "_" + str(i))
        for i in range(0, self.WORD_LENGTH):
            eqn.append("x3" + "_" + str(self.Round) + "_" + str(i))
        temp = " + ".join(eqn)
        fileobj.write(temp)
        fileobj.write("\n")
        fileobj.close()

    def CreateVariable(self, n, x):
        """
        モデル内で使う変数を作る(書き換えなくて良い)
        """
        variable = []
        for i in range(0, self.WORD_LENGTH):
            variable.append(x + "_" + str(n) + "_" + str(i))
        return variable

    def VariableRotation(self, x, n):
        """
        左bitローテーション(書き換えなくて良い)
        """
        eqn = []
        for i in range(0, self.WORD_LENGTH):
            eqn.append(x[(i + n) % self.WORD_LENGTH])
        return eqn

    def CreateConstrainsSplit(self, x_in, u, v, w, y_out):
        """
        分岐の作成
        今回はx_inがu,v,wとy_outに分岐する
        """
        fileobj = open(self.filename_model, "a")
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
        fileobj.close()

    def CreateConstraintsAnd(self, u, v, t):
        """
        AND演算(u AND v = t)
        """
        fileobj = open(self.filename_model, "a")
        for i in range(0, self.WORD_LENGTH):
            fileobj.write((t[i] + " - " + u[i] + " >= " + str(0)))
            fileobj.write("\n")
            fileobj.write((t[i] + " - " + v[i] + " >= " + str(0)))
            fileobj.write("\n")
            fileobj.write(
                (t[i] + " - " + u[i] + " - " + v[i] + " <= " + str(0)))
            fileobj.write("\n")
        fileobj.close()

    def CreateConstraintsXor(self, y_in, t, w, x_out):
        """
        XOR演算(y_in XOR t XOR w = x_out)
        """
        fileobj = open(self.filename_model, "a")
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
        fileobj.close()

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
        DPの初期条件を設定する
        self.i段目の段関数への入力集合のBDPをkベクトルで初期化
        """
        fileobj = open(self.filename_model, "a")
        x0 = self.CreateVariable(0, "x0")
        x1 = self.CreateVariable(0, "x1")
        x2 = self.CreateVariable(0, "x2")
        x3 = self.CreateVariable(0, "x3")
        data = x0 + x1 + x2 + x3
        for i in range(self.WORD_LENGTH * 4):
            fileobj.write(data[i] + " = " + str(self.k[i]))
            fileobj.write("\n")
        fileobj.close()

    def end(self):
        """
        最終段出力の制約式
        """
        with open(self.filename_model, 'a') as fileobj:
            x0 = self.CreateVariable(self.Round, "x0")
            x1 = self.CreateVariable(self.Round, "x1")
            x2 = self.CreateVariable(self.Round, "x2")
            x3 = self.CreateVariable(self.Round, "x3")

            data = x0 + x1 + x2 + x3
            for i in range(self.WORD_LENGTH * 4):
                if i == self.m:
                    fileobj.write(data[i] + " = 1")
                else:
                    fileobj.write(data[i] + " = 0")
                fileobj.write("\n")

    def Constraint(self):
        """
        暗号器の構造を記述する
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Subject To\n")
        fileobj.close()

        # 一番最初の入力の変数を作成
        x0_in = self.CreateVariable(0, "x0")
        x1_in = self.CreateVariable(0, "x1")
        x2_in = self.CreateVariable(0, "x2")
        x3_in = self.CreateVariable(0, "x3")

        for i in range(0, self.Round):
            # 変数を記述する
            # 出力
            x0_out = self.CreateVariable((i+1), "x0")
            x1_out = self.CreateVariable((i+1), "x1")
            x2_out = self.CreateVariable((i+1), "x2")
            x3_out = self.CreateVariable((i+1), "x3")

            # 各演算箇所での変数
            # 左側前半
            al = self.CreateVariable(i, "al")
            bl = self.CreateVariable(i, "bl")
            cl = self.CreateVariable(i, "cl")
            dl = self.CreateVariable(i, "dl")
            # 左側後半
            el = self.CreateVariable(i, "el")
            fl = self.CreateVariable(i, "fl")
            gl = self.CreateVariable(i, "gl")
            hl = self.CreateVariable(i, "hl")
            # 右側前半
            ar = self.CreateVariable(i, "ar")
            br = self.CreateVariable(i, "br")
            cr = self.CreateVariable(i, "cr")
            dr = self.CreateVariable(i, "dr")
            # 右側後半
            er = self.CreateVariable(i, "er")
            fr = self.CreateVariable(i, "fr")
            gr = self.CreateVariable(i, "gr")
            hr = self.CreateVariable(i, "hr")

            # 途中のシャッフル部分
            y3 = self.CreateVariable(i, "y0")
            y2 = self.CreateVariable(i, "y1")
            y1 = self.CreateVariable(i, "y2")
            y0 = self.CreateVariable(i, "y3")

            # partical_round(CBDPのみではなかった部分)
            if i == self.i:
                self.ForParticalRound(x0_out, x1_in)
                self.ForParticalRound(x1_out, x2_in)
                self.ForParticalRound(x2_out, x3_in)
                self.ForParticalRound(x3_out, x0_in)

            # 構造を記述
            # 前半
            """
            入力: x0_in, x1_in, x2_in, x3_in
            出力: y0   , y1   , y2   , y3
            """
            self.CreateConstrainsSplit(x0_in, al, bl, cl, y1)  # 左側分岐
            self.CreateConstrainsSplit(x2_in, ar, br, cr, y3)  # 右側分岐
            al = self.VariableRotation(al, Shadow.R1)  # 左側1bit左シフト
            bl = self.VariableRotation(bl, Shadow.R2)  # 左側7bit左シフト
            cl = self.VariableRotation(cl, Shadow.R3)  # 左側2bit左シフト
            ar = self.VariableRotation(ar, Shadow.R1)  # 右側1bit左シフト
            br = self.VariableRotation(br, Shadow.R2)  # 右側7bit左シフト
            cr = self.VariableRotation(cr, Shadow.R3)  # 右側2bit左シフト
            self.CreateConstraintsAnd(al, bl, dl)  # 左側AND演算
            self.CreateConstraintsAnd(ar, br, dr)  # 右側AND演算
            self.CreateConstraintsXor(x1_in, cl, dl, y0)  # 左側XOR演算
            self.CreateConstraintsXor(x3_in, cr, dr, y2)  # 右側XOR演算

            # 後半
            """
            入力: y0    , y1    , y2    , y3
            出力: x0_out, x1_out, x2_out, x3_out
            """

            self.CreateConstrainsSplit(y0, el, fl, gl, x2_out)  # 左側分岐
            self.CreateConstrainsSplit(y2, er, fr, gr, x0_out)  # 右側分岐
            el = self.VariableRotation(el, Shadow.R1)  # 左側1bit左シフト
            fl = self.VariableRotation(fl, Shadow.R2)  # 左側7bit左シフト
            gl = self.VariableRotation(gl, Shadow.R3)  # 左側2bit左シフト
            er = self.VariableRotation(er, Shadow.R1)  # 右側1bit左シフト
            fr = self.VariableRotation(fr, Shadow.R2)  # 右側7bit左シフト
            gr = self.VariableRotation(gr, Shadow.R3)  # 右側2bit左シフト
            self.CreateConstraintsAnd(el, fl, hl)  # 左側AND演算
            self.CreateConstraintsAnd(er, fr, hr)  # 右側AND演算
            self.CreateConstraintsXor(y1, hl, gl, x1_out)  # 左側XOR演算
            self.CreateConstraintsXor(y3, hr, gr, x3_out)  # 右側XOR演算

            # take over
            x0_in = x0_out
            x1_in = x1_out
            x2_in = x2_out
            x3_in = x3_out

    def BinaryVariable(self):
        """
        変数の値を0か1に制約する
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Binary\n")
        for i in range(self.i, self.Round):
            # 入力
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("x0_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("x1_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("x2_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("x3_" + str(i) + "_" + str(j)))
                fileobj.write("\n")

            # half round終了後の状態
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("y0_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("y1_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("y2_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("y3_" + str(i) + "_" + str(j)))
                fileobj.write("\n")

            # 左側
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("al_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("bl_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("cl_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("dl_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("el_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("fl_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("gl_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("hl_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            # 右側
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("ar_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("br_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("cr_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("dr_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("er_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("fr_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("gr_" + str(i) + "_" + str(j)))
                fileobj.write("\n")
            for j in range(0, self.WORD_LENGTH):
                fileobj.write(("hr_" + str(i) + "_" + str(j)))
                fileobj.write("\n")

        # 変数x,yは最終段の出力も考慮
        for j in range(0, self.WORD_LENGTH):
            fileobj.write(("x0_" + str(self.Round) + "_" + str(j)))
            fileobj.write("\n")
        for j in range(0, self.WORD_LENGTH):
            fileobj.write(("x1_" + str(self.Round) + "_" + str(j)))
            fileobj.write("\n")
        for j in range(0, self.WORD_LENGTH):
            fileobj.write(("x2_" + str(self.Round) + "_" + str(j)))
            fileobj.write("\n")
        for j in range(0, self.WORD_LENGTH):
            fileobj.write(("x3_" + str(self.Round) + "_" + str(j)))
            fileobj.write("\n")

        fileobj.write("END")
        fileobj.close()

    def MakeModel(self):
        """
        MILPモデルの作成
        """
        self.CreateObjectiveFunction()
        self.Constraint()
        self.Init()
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
            return 'error'
