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

process.GlobalTag.globaltag = '94X_dataRun2_v10'

process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(20))
process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            '/store/data/Run2016B/JetHT/MINIAOD/PromptReco-v2/000/273/503/00000/069FE912-3E1F-E611-8EE4-02163E011DF3.root'
            )
        )

process.out = cms.OutputModule("PoolOutputModule",
        outputCommands = cms.untracked.vstring('keep *'),
        fileName = cms.untracked.string("jme_reference_sample_data_80x.root")
        )

# Jets

### First, apply new JEC over slimmedJets

from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff import updatedPatJetCorrFactors
from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff import updatedPatJets

process.patJetCorrFactorsReapplyJEC = updatedPatJetCorrFactors.clone(
        src = cms.InputTag("slimmedJets"),
        levels = ['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual'],
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
        algo = cms.string('AK4PFchs'),
        algopt = cms.string('AK4PFchs_pt'),
        genJets = cms.InputTag('slimmedGenJets'),
        dRMax = cms.double(0.2),
        dPtMaxFactor = cms.double(3),
        )


# Raw MET
process.uncorrectedMet = cms.EDProducer("RecoMETExtractor",
        correctionLevel = cms.string('raw'),
        metSource = cms.InputTag("slimmedMETs", "", "@skipCurrentProcess")
        )

# Raw PAT MET
from PhysicsTools.PatAlgos.tools.metTools import addMETCollection
addMETCollection(process, labelName="uncorrectedPatMet", metSource="uncorrectedMet")
process.uncorrectedPatMet.addGenMET = False

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

process.p = cms.Path(process.produceTable)
process.end = cms.EndPath(process.out)
