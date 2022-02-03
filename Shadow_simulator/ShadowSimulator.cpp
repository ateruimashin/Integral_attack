#include <bits/stdc++.h>
#define rep(i, n) for (int i = 0; i < (n); i++)
#define rep2(i, s, n) for (int i = (s); i < (n); i++)
using namespace std;
using ll = long long;
using P = pair<int, int>;

//乱数生成
random_device rnd;
mt19937_64 mt(rnd());
// 0~2^33-1までの乱数を得る乱数生成器を作成、正規分布する(1wordずつ生成)
uniform_int_distribution<> makePlanetext(0, (1 << 9) - 1);
// 0~2^9-1までの乱数を得る乱数生成器を作成(8bitの鍵を生成)
uniform_int_distribution<> makeKey(0, (1 << 9) - 1);


//左巡回シフト
bitset<8> calaculateRotation(const bitset<8> &input_word,
                            const int rotation_num) {
return (input_word << rotation_num) | (input_word >> (8 - rotation_num));
}


bitset<32> encript(bitset<32> planetext, int round){
    //ビット列を文字列に変換して1word(8bit)ごとに分割
    string planeString = planetext.to_string();
    bitset<8> a(planeString.substr(0, 8));
    bitset<8> b(planeString.substr(8, 8));
    bitset<8> c(planeString.substr(16, 8));
    bitset<8> d(planeString.substr(24, 8));

    //暗号化
    for(int r = 0; r < round; r++){
        //half round前半
        //copyとローテーション
        bitset<8> tmp1 = calaculateRotation(a, 1);
        bitset<8> tmp2 = calaculateRotation(a, 7);
        bitset<8> tmp3 = calaculateRotation(a, 2);
        bitset<8> tmp4 = calaculateRotation(c, 1);
        bitset<8> tmp5 = calaculateRotation(c, 7);
        bitset<8> tmp6 = calaculateRotation(c, 2);

        //AND演算
        tmp1 &= tmp2;
        tmp4 &= tmp5;

        //XOR
        b ^= tmp1;
        b ^= tmp3;
        c ^= tmp4;
        c ^= tmp6;

        //key XOR
        bitset<8> key1(makeKey(mt));
        bitset<8> key2(makeKey(mt));

        b ^= key1;
        d ^= key2;

        //swap
        bitset<8> swap1 = a;
        a = b;
        b = swap1;
        bitset<8> swap2 = c;
        c = d;
        d = swap2;

        /*half round後半*/
                //copyとローテーション
        tmp1 = calaculateRotation(a, 1);
        tmp2 = calaculateRotation(a, 7);
        tmp3 = calaculateRotation(a, 2);
        tmp4 = calaculateRotation(c, 1);
        tmp5 = calaculateRotation(c, 7);
        tmp6 = calaculateRotation(c, 2);

        //AND演算
        tmp1 &= tmp2;
        tmp4 &= tmp5;

        //XOR
        b ^= tmp1;
        b ^= tmp3;
        c ^= tmp4;
        c ^= tmp6;

        //key XOR
        bitset<8> key3(makeKey(mt));
        bitset<8> key4(makeKey(mt));

        b ^= key3;
        d ^= key4;

        if(r != round - 1){
            //swap
            bitset<8> swap3 = a;
            a = c;
            c = swap3;
        }
    }
    //文字列に変換
    string s_a = a.to_string();
    string s_b = b.to_string();
    string s_c = c.to_string();
    string s_d = d.to_string();
    //結合
    string encriptString = s_a + s_b + s_c + s_d;
    //ビット列に変換してreturn
    bitset<32> encriptBit(encriptString);
    return encriptBit;
}

int main(){
    // ラウンド数
    int round;
    cout << "round:";
    cin >> round;
    cout << endl;

    //試行回数
    int ATEMPT = 10;

    //各試行の結果を集計するvector
    vector<ll> sum(32, 0);
    vector<char> eachResult(32);
    vector<char> allResult(32);

    // インジケータを作成(遊びで入れている)
    string processing(ATEMPT, "-");
    int percentage = 0;

    //試行
    for(int tryNum = 0; tryNum < ATEMPT; tryNum++){
        //インジケータ(遊びで入れている)
        processing[tryNum] = '*';
        percentage = tryNum / ATEMPT * 100;
        cout << processing << " " << percentage << "%"<< flush;

        //1wordごとに乱数生成
        bitset<8> word1(makePlanetext(mt));
        bitset<8> word2(makePlanetext(mt));
        bitset<8> word3(makePlanetext(mt));
        bitset<8> word4(makePlanetext(mt));

        string stringWord1 = word1.to_string();
        string stringWord2 = word2.to_string();
        string stringWord3 = word3.to_string();
        string stringWord4 = word4.to_string();

        //全て結合して一つの入力(32bit)を得る
        bitset<32> mainPlanetext(stringWord1 + stringWord2 + stringWord3+ stringWord4);

        //各平文をXORした結果
        bitset<32> xorSum(0);
        //平文を特性に直して、各平文を暗号化する
        for(unsigned int planetextNum = 0; planetextNum < (1<<31); planetextNum++){
            // AAAAAAAaaac(32ビット)にする
            bitset<32> tryPlanetext = mainPlanetext;    //コピー
            bitset<32> deltaP(planetextNum);
            tryPlanetext ^= (deltaP << 1);
            
            //暗号化して暗号文のXORを取る
            bitset<32> encripText =  encript(tryPlanetext, round);

            //最集団出力のintegral特性を計算
            for(int k = 0; k < 32; k++){
                if(encript[k]) sum[k]++;    //ビットが立っているとインクリメント
            }
        }
        //個別の平文の結果を特性に変換する
        for(int i = 0; i < 32; i++){
            if(sum[i] == 0 || sum[i] == (1 << 32)){
                //『sum == 0』⇒そのbit位置の値が全て0  『sum == 1 << active_bits』 ⇒あるそのbit位置の値が全て1
                eachResult[i] == 'c';
            }else if(sum[i] == (1 << 31)/2){
                //『sumが中央値』 ⇒0と1が同数回現れる
                eachResult[i] = 'a';
            }else if(sum[i] % 2 == 0){
                //『sumが2で割り切れる』 ⇒XOR総和は0
                eachResult[i] = 'b';
            }else{
                //『sumが2で割り切れない』 ⇒XOR総和は1
                eachResult[i] = 's';
            }
        }

        //個別の特性をまとめる
        for(int i = 0; i < 32; i++){
            if(i == 0){ 
                allResult = eachResult;
            }else{
                if(allResult[i] == eachResult[i] || allResult[i] == 'u'){
                    allResult[i] = 'u'
                }else if(allResult[i] == 's' || eachResult[i] == 's'){
                    allREsult = 'u';
                }else{
                    allResult[i] = 'b';
                }
            }
        }
    }
    // flushの動作がわからないので
    cout << endl;
    // 出力
    for(char c: allResult){
        cout << c;
    }
    cout << endl;
return 0;
}