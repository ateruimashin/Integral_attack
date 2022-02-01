# MILP-aided Method of Searching Division Property Using Three Subsets and Applications against SIMON32 and Shadow32
[MILP Method of Searching Integral Distinguishers Based on Division Property Using Three Subsets](https://eprint.iacr.org/2018/1186)に記載のアルゴリズムを参考に[SIMON](https://eprint.iacr.org/2013/404.pdf)と[Shadow](https://ieeexplore.ieee.org/abstract/document/9372286)に対してIntegral特性を探索するプログラムです。  
それぞれSIMON32とShadow32に対して特性探索を行っています。  

# CAUTION
混合整数線形計画法(MILP)を用いるため、MILPのソルバーが必要になります。  
研究室ではMILPソルバーに[Gurobi](https://www.gurobi.com/)を用いています。  
解析のためにGurobiをインストール後、インストール先のフォルダ内からライブラリをコピーする必要があります。  

> 例: Gurobi9.5.0の場合
> [Gurobi Optimizer – Get the Software](https://www.gurobi.com/downloads/gurobi-software/)からインストーラーを入手します。インストール終了後、ライセンス認証を行います。その後、インストール先からPython用のライブラリを取り出します。ライブラリはPythonのバージョンごとに分けられています。Python3.9.xの場合パスは次の通りです。  
> インストール先/gurobi950/win64/python39  
> 最後にその中にあるlibフォルダをPythonのインストール先にあるLib内にコピーします。

# References
- [THE SIMON AND SPECK FAMILIES OF LIGHTWEIGHT BLOCK CHIPERS](https://eprint.iacr.org/2013/404.pdf)  
- [Shadow: A Lightweight Block Cipher for IoT Nodes](ht/ieeexplore.ieee.org/abstract/document/9372286)  
- [Bit-Based Division Property and Application to Simon Family](https://eprint.iacr.org/2016/285.pdf)  
- [MILP Method of Searching Integral Distinguishers Based on Division Property Using Three Subsets](https://eprint.iacr.org/2018/1186)  
