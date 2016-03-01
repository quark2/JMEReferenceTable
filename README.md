### CMS JetMET reference table

A small CMSSW analyzer to produce a reference table that analyzers could check to ensure their private implementation are corrects.

See https://twiki.cern.ch/twiki/bin/view/CMS/JERCReference for more details.

#### Recipe

```bash

export SCRAM_ARCH=slc6_amd64_gcc491
cmsrel CMSSW_7_4_15

cd CMSSW_7_4_15/src
cmsenv

git cms-merge-topic blinkseb:jer_gt_74x_fix
git cms-merge-topic blinkseb:74x_smeared_jet_producer
git cms-merge-topic blinkseb:74x-PATJetUpdater-fix

git clone -b CMSSW_7_4_X https://github.com/cms-jet/JMEReferenceTable.git JetMETCorrections/JMEReferenceTable

scram b -j4

```
