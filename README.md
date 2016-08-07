### CMS JetMET reference table

A small CMSSW analyzer to produce a reference table that analyzers could check to ensure their private implementation are corrects.

See https://twiki.cern.ch/twiki/bin/view/CMS/JERCReference for more details.

#### Recipe

```bash

export SCRAM_ARCH=slc6_amd64_gcc530
cmsrel CMSSW_8_0_16

cd CMSSW_8_0_16/src
cmsenv

git cms-merge-topic 15250

git clone -b CMSSW_8_0_X https://github.com/cms-jet/JMEReferenceTable.git JetMETCorrections/JMEReferenceTable

scram b -j4

```
