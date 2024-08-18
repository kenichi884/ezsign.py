# ezsign.py

株式会社サンテクノロジーの電子ペーパーディスプレイ「Santek EZ Sign 4.2” E-paper Display」とUSBシリアル通信して指定のページを表示、指定のページのイメージデータを読み取ってファイル保存、指定のページに画像ファイルのデータ書き込みするライブラリです。

[Santek EZ Sign 4.2](https://www.santekshop.jp/product/santek-ez-sign-4-2-e-paper-display/)



## 使い方

PCなどと有線USB接続し、シリアルポート名を確認します。Windowsではデバイスマネージャから接続したときに発生したCOMポート名を調べます。

Linuxなどではmessagesログに名前が出ると思うのでそちらを調べます。

シリアルポート名の例

    COM3 
    /dev/ttyACM0 
    /dev/tty.usbserial-Disabled

EZ Sign 4.2の電源をオン状態にしてください。オフ状態でもPC側ではシリアルポートとして認識されますが、EZSignライブラリからコマンドを送っても反応しません。

EZ Sign 4.2の電源がオン状態(LEDが青点灯)で使用してください。

Pythonライブラリのpyserial、Pillow、argparseが必要です。インストールされていない場合は pip install pyserial pillow argparse などとしてインストールしておいてください。

### pythonライブラリとして使う場合

pythonライブラリして使う場合は所定のライブラリディレクトリに配置して、 EZSignクラスを呼び出してください。

シリアルポートをpyserialで開いてそれをEZSignのコンストラクタの第一引数に渡します。ボーレートとパリティ設定は以下のようにしてください。

    Serial_Port=serial.Serial('COM3', baudrate=38400, parity= 'N')
    ezsign = EZSign(Serial_Port)

#### 指定のページを表示

    ezsign.showpage(ページ番号)

ページ番号は1～5まで。EZSign.NEXTを指定すると次のページ、EZSign.PREVを指定すると前のページへの切り替えになります。

ページ書き換えは30秒程度かかります。書き換え中はEZ Sign 4.2のLEDが点滅します。

#### 指定のページのイメージデータを読み取ってファイル保存

    ezsign.readimage(ページ番号, 保存先ファイル名)

ページ番号は1～5まで。保存先ファイル名は'image01.png'などを指定します。

Pillowのsave()を使っているので拡張子を指定することでそのフォーマットになります。

EzSignの電子ペーパーで黒がRGB(0,0,0)、白がRGB(255,255,255)、赤がRGB(255,0,0)のピクセルとしてファイル保存されます。

#### 指定のページに画像ファイルのデータを書き込む

    ezsign.writeimage(ページ番号, 保存先ファイル名)

ページ番号は1～5まで。書き込む画像ファイル名は'image01.png'などを指定します。

Pillowのopen()を使っているのでPillowが対応している画像ファイルは読み込むことができます。

画像ファイル中の黒ピクセルRGB(0,0,0)、白ピクセルRGB(255, 255, 255)、赤ピクセルRGB(255, 0, 0)が電子ペーパーに反映されます。

画像ファイルの幅、高さはなんでも大丈夫ですが、内部で400x300にリサイズされますので400x300以外のサイズの画像データではゆがんだり、リサイズ時のノイズが乗ったりします。


### そのまま実行する場合のコマンドライン引数

シリアルポート名と、コマンドと引数を指定します。以下の説明例ではCOM3がシリアルポートの場合です。

画像ファイル名は非圧縮フォーマットの.pngなどを指定するようにしてください。jpgなどの圧縮フォーマットでも使えますが、黒ピクセルRGB(0,0,0)、白ピクセルRGB(255, 255, 255)、赤ピクセルRGB(255, 0, 0)以外の値のピクセルでファイル保存されたり、電子ペーパへの書き込みの際に表示されなかったりします。

#### 指定のページを表示

    例 1ページ目を表示
    python EZSign.py COM3 -s 1

#### 指定のページのイメージデータを読み取ってファイル保存

    例 1ページ目のイメージデータを 読み取ってimage.pngに保存
    python EZSign.py COM3 -r 1 image.png

#### 指定のページに画像ファイルのデータを書き込む

    例 image.pngを1ページ目として書き込む
    python EZSign.py COM3 -w 1 image.png

EZSign.pyでEZ Sign 4.2を操作しようとしてもうんともすんとも言わなくなった場合は、PCとEZ Sign 4.2の有線USB接続をいったん外して、再度接続してから試してみてください。EZ Sign 4.2が電源オン状態(LEDが青点灯、緑ではありません)かどうかを確認してください。



-----------------------------------
# 赤黒2色変換スクリプト conv2bwr.py

Pillowの機能を使って画像ファイルをEzSign 4.2の赤黒2色電子ペーパーで表示できる赤黒白の3色の画像に変換するスクリプトです。

変換後の画像ファイルはezsign.pyの-wオプションでEZ Sign 4.2に書き込むことができます。

変換先の画像ファイル名は非圧縮フォーマットの.pngなどを指定するようにしてください。

変換前の画像ファイルの画像ファイルの幅、高さはなんでもいいですが、このスクリプトで変換するとすべて400x300にリサイズされます。4:3のアスペクト比じゃない画像を変換した場合は画像が歪みますので注意してください。

白黒２値への変換はPillowのデフォルトの変換(誤差拡散法)を使っています。

赤色についてはHSV変換をかけた後、Hue(色相)の0(赤)に近いピクセルで、SatulationとValueの値が一定より大きい場合、その値を赤ピクセルの濃さとして使い、Pillowの機能で２値化した後、白黒の画像に合成するという方法をとっています。
(このため、元画像によっては不自然な赤色が乗ってしまうことがあります。-b オプションで赤色を出さないようにするか、--huerange、--redvalue オプションで調整してみてください。)

## 使い方

入力画像ファイル名と赤黒白に変換後の画像ファイル名を指定します。

以下の例での入力画像ファイル [Fooocus](https://github.com/lllyasviel/Fooocus)で適当に生成したレース用バイクの画像

![inputfile.png](/images/MotoGPimage2.png)


### 基本の使い方

    例 inputfile.pngを赤黒白の400x300画像に変換してoutputfile.pngに書き込む
    python conv2bwr.py inputfile.png outputfile.png

![outputfile_BWR.png](/images/MotoGPimage2_BWR.png)

### -b オプション 赤色を出さない

    例 inputfile.pngを黒白の400x300画像に変換してoutputfile.pngに書き込む
    python conv2bwr.py -b  inputfile.png outputfile.png

![outputfile_BW.png](/images/MotoGPimage2_BW.png)

### --avoidresize 400x300にリサイズしない

    例 inputfile.pngを赤黒白の画像に変換してoutputfile.pngに書き込む。この段階では400x300にリサイズしないが、ezsign.pyで電子ペーパー書き込む際には400x300にリサイズされる。
    python conv2bwr.py --avoidresize  inputfile.png outputfile.png

### --huerange 赤色のピクセルと判断する色相の範囲を指定する

    例 inputfile.pngを赤黒白の画像に変換してoutputfile.pngに書き込む。赤色と判断する色相の範囲を±40とする。デフォルト20。値を大きくすると赤と判断される色の範囲が広くなる。小さくすると狭くなる。
    python conv2bwr.py --huerange 40  inputfile.png outputfile.png

![outputfile_hue40.png](/images/MotoGPimage2_hue40.png)

### --redvalue 赤色として反映させるピクセルの値の閾値を指定する

    例 inputfile.pngを赤黒白の画像に変換してoutputfile.pngに書き込む。赤色ピクセルとして反映されるピクセル値の閾値を200以上とする。デフォルト170。値を大きくすると濃い赤色でないと赤色が出力されず、小さくすると薄い赤色でも赤色と判断される。
    python conv2bwr.py --redvalue 100  inputfile.png outputfile.png

![outputfile_value100.png](/images/MotoGPimage2_value100.png)

## 変換例、表示例

    生成AIで作ったレース用バイクの画像
    python conv2bwr.py  MotoGPimage2.png MotoGPimage2_BWR.png
    EZ Sign 4.2の３ページ目に書き込み
    python ezsign.py COM3 -w 3 MotoGPimage2_BWR.png

![MotoGPimage2.png](/images/MotoGPimage2.png) ![MotoGPimage2_BWR.png](/images/MotoGPimage2_BWR.png)

![EZSign display sample1](/images/EZsignDisplaySample1.jpg)

    いらすとやの1万円札
    python conv2bwr.py --huerange 20 --redvalue 140 money_10000_shibusawa.png money_10000_shibusawa_BWR.png
    EZ Sign 4.2の４ページ目に書き込み
    python ezsign.py COM3 -w 4 money_10000_shibusawa_BWR.png

![money_10000_shibusawa.png](/images/money_10000_shibusawa.png) ![money_10000_shibusawa_BWR.png](/images/money_10000_shibusawa_BWR.png)

![EZSign display sample2](/images/EZsignDisplaySample2.jpg)

    いらすとやの雷門
    python conv2bwr.py  kankou_kaminarimon.png .\kankou_kaminarimon_BWR.png
    EZ Sign 4.2の５ページ目に書き込み
    python ezsign.py COM3 -w 5 mkankou_kaminarimon_BWR.png

![kankou_kaminarimon.pn](/images/kankou_kaminarimon.png) ![kankou_kaminarimon_BWR.png](/images/kankou_kaminarimon_BWR.png)

![EZSign display sample3](/images/EZsignDisplaySample3.jpg)
