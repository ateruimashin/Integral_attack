# MILP-aided Method of Searching Division Property Using Three Subsets and Applications against SIMON32 and Shadow32
[MILP Method of Searching Integral Distinguishers Based on Division Property Using Three Subsets](https://eprint.iacr.org/2018/1186)に記載のアルゴリズムを参考に[SIMON](https://eprint.iacr.org/2013/404.pdf)と[Shadow](https://ieeexplore.ieee.org/abstract/document/9372286)に対してIntegral特性を探索するプログラムです。  
それぞれSIMON32とShadow32に対して特性探索を行っています。  

# CAUTION
混合整数線形計画法(MILP)を用いるため、MILPのソルバーが必要になります。  
研究室ではMILPソルバーに[Gurobi](https://www.gurobi.com/)を用いています。  
解析のためにGurobiをインストール後、インストール先のフォルダ内からgurobipy.pydを探し、SCBDP.pyと同じディレクトリに配置します。
また、Gurobiインストール後にライセンス認証を行う必要があります。  
最後に、BDPT_(cipher name)をpython2.7系で走らせると解析が始まります。

# References
- [THE SIMON AND SPECK FAMILIES OF LIGHTWEIGHT BLOCK CHIPERS](https://eprint.iacr.org/2013/404.pdf)  
- [Shadow: A Lightweight Block Cipher for IoT Nodes](https://ieeexplore.ieee.org/abstract/document/9372286)  
- [Bit-Based Division Property and Application to Simon Family](https://eprint.iacr.org/2016/285.pdf)  
- [MILP Method of Searching Integral Distinguishers Based on Division Property Using Three Subsets](https://eprint.iacr.org/2018/1186)  
