#!/bin/sh
cd ~/install
wget http://downloads.sourceforge.net/project/cmusphinx/sphinxbase/0.8/sphinxbase-0.8.tar.gz
wget http://downloads.sourceforge.net/project/cmusphinx/pocketsphinx/0.8/pocketsphinx-0.8.tar.gz
svn co https://svn.code.sf.net/p/cmusphinx/code/trunk/cmuclmtk/

wget http://distfiles.macports.org/openfst/openfst-1.3.4.tar.gz
wget https://github.com/mitlm/mitlm/releases/download/v0.4.1/mitlm_0.4.1.tar.gz
wget https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/m2m-aligner/m2m-aligner-1.2.tar.gz
wget https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/phonetisaurus/is2013-conversion.tgz
