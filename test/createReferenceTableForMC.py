import FWCore.ParameterSet.Config as cms

process = cms.Process("JME")

process.options = cms.untracked.PSet(
        wantSummary = cms.untracked.bool(False),
        allowUnscheduled = cms.untracked.bool(True)
        )

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('FWCore.MessageLogger.MessageLogger_cfi')

process.GlobalTag.globaltag = '94X_mcRun2_asymptotic_v3'

# JEC
jecFile = 'Summer16_07Aug2017_V11_MC'
from CondCore.CondDB.CondDB_cfi import CondDB
if hasattr(CondDB, 'connect'): delattr(CondDB, 'connect')
process.jec = cms.ESSource("PoolDBESSource",CondDB,
    connect = cms.string('sqlite_fip:nano/nanoAOD/data/jec/%s.db'%jecFile),            
    toGet = cms.VPSet(
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_%s_AK4PF"%jecFile),
            label= cms.untracked.string("AK4PF")),
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_%s_AK4PFchs"%jecFile),
            label= cms.untracked.string("AK4PFchs")),
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_%s_AK4PFPuppi"%jecFile),
            label= cms.untracked.string("AK4PFPuppi")),
        )
    )
process.es_prefer_jec = cms.ESPrefer("PoolDBESSource","jec")
print "JEC based on", process.jec.connect

process.MessageLogger.cerr.FwkReport.reportEvery = 100

#process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(20))
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(500))
process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            #'/store/mc/RunIISpring16MiniAODv2/TT_TuneCUETP8M1_13TeV-powheg-pythia8/MINIAODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext3-v2/70000/041A166C-B53F-E611-BF34-5CB90179CCC0.root'
            '/store/mc/RunIISummer16MiniAODv2/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/0806AB92-99BE-E611-9ECD-0025905A6138.root'
            )
        )

process.out = cms.OutputModule("PoolOutputModule",
        outputCommands = cms.untracked.vstring('keep *'),
        fileName = cms.untracked.string("jme_reference_sample_mc_80x.root")
        )

# Jets

### First, apply new JEC over slimmedJets

from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff import updatedPatJetCorrFactors
from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff import updatedPatJets

process.patJetCorrFactorsReapplyJEC = updatedPatJetCorrFactors.clone(
        src = cms.InputTag("slimmedJets"),
        levels = ['L1FastJet', 'L2Relative', 'L3Absolute'],
        payload = 'AK4PFchs'
        )

process.slimmedJetsNewJEC = updatedPatJets.clone(
        jetSource = cms.InputTag("slimmedJets"),
        jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetCorrFactorsReapplyJEC"))
        )


#### Second, smear newly corrected jets

process.slimmedJetsSmeared = cms.EDProducer('SmearedPATJetProducer',
        src = cms.InputTag('slimmedJetsNewJEC'),
        enabled = cms.bool(True),
        rho = cms.InputTag("fixedGridRhoFastjetAll"),
        #algo = cms.string('AK4PFchs'),
        #algopt = cms.string('AK4PFchs_pt'),
        resolutionFile = cms.FileInPath("nano/analysis/data/jer/Summer16_25nsV1_MC_PtResolution_AK4PFchs.txt"), 
        scaleFactorFile = cms.FileInPath("nano/analysis/data/jer/Summer16_25nsV1_MC_SF_AK4PFchs.txt"), 

        genJets = cms.InputTag('slimmedGenJets'),
        dRMax = cms.double(0.2),
        dPtMaxFactor = cms.double(3),

        debug = cms.untracked.bool(False)
        )


# MET

process.genMet = cms.EDProducer("GenMETExtractor",
        metSource = cms.InputTag("slimmedMETs", "", "@skipCurrentProcess")
        )

# Raw MET
process.uncorrectedMet = cms.EDProducer("RecoMETExtractor",
        correctionLevel = cms.string('raw'),
        metSource = cms.InputTag("slimmedMETs", "", "@skipCurrentProcess")
        )

# Raw PAT MET
from PhysicsTools.PatAlgos.tools.metTools import addMETCollection
addMETCollection(process, labelName="uncorrectedPatMet", metSource="uncorrectedMet")
process.uncorrectedPatMet.genMETSource = cms.InputTag('genMet')

# Type-1 correction
process.Type1CorrForNewJEC = cms.EDProducer("PATPFJetMETcorrInputProducer",
        src = cms.InputTag("slimmedJetsNewJEC"),
        jetCorrLabel = cms.InputTag("L3Absolute"),
        jetCorrLabelRes = cms.InputTag("L2L3Residual"),
        offsetCorrLabel = cms.InputTag("L1FastJet"),
        skipEM = cms.bool(True),
        skipEMfractionThreshold = cms.double(0.9),
        skipMuonSelection = cms.string('isGlobalMuon | isStandAloneMuon'),
        skipMuons = cms.bool(True),
        type1JetPtThreshold = cms.double(15.0)
        )

process.slimmedMETsNewJEC = cms.EDProducer('CorrectedPATMETProducer',
        src = cms.InputTag('uncorrectedPatMet'),
        srcCorrections = cms.VInputTag(cms.InputTag('Type1CorrForNewJEC', 'type1'))
        )

process.shiftedMETCorrModuleForSmearedJets = cms.EDProducer('ShiftedParticleMETcorrInputProducer',
        srcOriginal = cms.InputTag('slimmedJetsNewJEC'),
        srcShifted = cms.InputTag('slimmedJetsSmeared')
        )

process.slimmedMETsSmeared = cms.EDProducer('CorrectedPATMETProducer',
        src = cms.InputTag('slimmedMETsNewJEC'),
        srcCorrections = cms.VInputTag(cms.InputTag('shiftedMETCorrModuleForSmearedJets'))
        )

process.produceTable = cms.EDAnalyzer('JMEReferenceTableAnalyzer',
        plain_jets = cms.InputTag('slimmedJets'),
        recorrected_jets = cms.InputTag('slimmedJetsNewJEC'),
        smeared_jets = cms.InputTag('slimmedJetsSmeared'),

        plain_met = cms.InputTag('slimmedMETs'),
        recorrected_met = cms.InputTag('slimmedMETsNewJEC'),
        smeared_met = cms.InputTag('slimmedMETsSmeared')
        )

#process.p = cms.Path(process.patJetCorrFactorsReapplyJEC+process.slimmedJetsNewJEC+process.slimmedJetsSmeared+process.produceTable)
process.p = cms.Path(process.patJetCorrFactorsReapplyJEC+process.slimmedJetsNewJEC+process.slimmedJetsSmeared)
process.end = cms.EndPath(process.out)
