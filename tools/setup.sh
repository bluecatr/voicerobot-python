#!/bin/sh
CUR_DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
echo $CUR_DIR

CONFIGURATION_HOME=~/.voicerobot
mkdir $CONFIGURATION_HOME

#建议手动在外先执行这两个命令
sudo apt-get update
sudo apt-get upgrade --yes

#For All
sudo apt-get install nano git-core python-dev bison libasound2-dev libportaudio2 python-pyaudio python-six --yes

ostype=`lsb_release -a | grep Ubuntu`
if [ -z "$ostype" ]
then
    echo "Special packages for Raspberrypi"
    $CUR_DIR/setup_raspberrypi.sh
else
    echo "Special packages for Ubuntu"
    $CUR_DIR/setup_ubuntu.sh
fi

#百度的语音合成结果,MP3播放器
sudo apt-get install sox libsox-fmt-mp3 --yes

#Allows Python programs to use the MPEG Audio Decoder library
sudo apt-get install python-pymad --yes

#For Snowboy
sudo apt-get install libatlas-base-dev --yes

#For SVN download
sudo apt-get install subversion autoconf libtool automake gfortran g++ --yes

#语音文件处理
sudo apt-get install ffmpeg --yes

#加密图灵数据用来调用java程序
sudo apt-get install python-jpype --yes

#消息引擎
sudo apt-get install mosquitto

sudo pip install --upgrade setuptools
sudo pip install -r $CUR_DIR/../static/requirements.txt


#Specialy for accessing USB device without sudo, Note: restart is required
echo 'SUBSYSTEM=="usb", MODE="0666"' | sudo tee -a /etc/udev/rules.d/60-usb.rules
sudo udevadm control -R


#####################################################################
#mkdir ~/install
#Download the images
#$CUR_DIR/download_images.sh
#####################################################################

cd ~/install
tar -zxvf sphinxbase-0.8.tar.gz
tar -zxvf pocketsphinx-0.8.tar.gz

cd ~/install/sphinxbase-0.8/
./configure --enable-fixed
make
sudo make install

cd ~/install/pocketsphinx-0.8/
./configure
make
sudo make install

cd ~/install
tar -zxvf cmuclmtk.tar.gz
cd cmuclmtk
./autogen.sh && make && sudo make install

cd ~/install
tar -xvf m2m-aligner-1.2.tar.gz
tar -xvf openfst-1.3.4.tar.gz
tar -xvf is2013-conversion.tgz
tar -xvf mitlm_0.4.1.tar.gz

cd ~/install/openfst-1.3.4/
sudo ./configure --enable-compact-fsts --enable-const-fsts --enable-far --enable-lookahead-fsts --enable-pdt
sudo make install


cd ~/install/m2m-aligner-1.2/
sudo make
sudo cp ~/install/m2m-aligner-1.2/m2m-aligner /usr/local/bin/m2m-aligner

cd ~/install/mitlm-0.4.1/
sudo ./configure
sudo make install

cd ~/install/is2013-conversion/phonetisaurus/src
sudo make
sudo cp ~/install/is2013-conversion/bin/phonetisaurus-g2p /usr/local/bin/phonetisaurus-g2p

cd ~/install
tar -zxvf g014b2b.tgz
mv g014b2b $CONFIGURATION_HOME/g014b2b
cd $CONFIGURATION_HOME/g014b2b
#add /usr/local/lib into system library
sudo ldconfig
./compile-fst.sh


