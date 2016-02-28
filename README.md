### CMS JetMET reference table

A small CMSSW analyzer to produce a reference table that analyzers could check to ensure their private implementation are corrects.

See https://twiki.cern.ch/twiki/bin/view/CMS/JERCReference for more details.

#### Recipe

```bash

export SCRAM_ARCH=slc6_amd64_gcc493
cmsrel CMSSW_7_6_3_patch2

cd CMSSW_7_6_3_patch2/src
cmsenv

git cms-merge-topic blinkseb:smeared_jet_producer
git cms-merge-topic blinkseb:PATJetUpdater-fix

git clone https://github.com/cms-jet/JMEReferenceTable.git JetMETCorrections/JMEReferenceTable

scram b -j4

```
