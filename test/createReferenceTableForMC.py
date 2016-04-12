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

process.GlobalTag.globaltag = '76X_mcRun2_asymptotic_RunIIFall15DR76_v1'

process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(20))
process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            '/store/mc/RunIIFall15MiniAODv2/TT_TuneCUETP8M1_13TeV-powheg-pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12_ext3-v1/00000/02837459-03C2-E511-8EA2-002590A887AC.root'
            )
        )

process.out = cms.OutputModule("PoolOutputModule",
        outputCommands = cms.untracked.vstring('keep *'),
        fileName = cms.untracked.string("jme_reference_sample_mc.root")
        )

# Jets

### First, apply new JEC over slimmedJets

from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff import patJetCorrFactorsUpdated
from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff import patJetsUpdated

process.patJetCorrFactorsReapplyJEC = patJetCorrFactorsUpdated.clone(
        src = cms.InputTag("slimmedJets"),
        levels = ['L1FastJet', 'L2Relative', 'L3Absolute'],
        payload = 'AK4PFchs'
        )

process.slimmedJetsNewJEC = patJetsUpdated.clone(
        jetSource = cms.InputTag("slimmedJets"),
        jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetCorrFactorsReapplyJEC"))
        )


#### Second, smear newly corrected jets

process.slimmedJetsSmeared = cms.EDProducer('SmearedPATJetProducer',
        src = cms.InputTag('slimmedJetsNewJEC'),
        enabled = cms.bool(True),
        rho = cms.InputTag("fixedGridRhoFastjetAll"),
        resolutionFile = cms.FileInPath('JetMETCorrections/JMEReferenceTable/data/Summer15_25nsV6_MC_PtResolution_AK4PFchs.txt'),
        scaleFactorFile = cms.FileInPath('JetMETCorrections/JMEReferenceTable/data/Summer15_25nsV6_MC_SF_AK4PFchs.txt'),

        genJets = cms.InputTag('slimmedGenJets'),
        dRMax = cms.double(0.2),
        dPtMaxFactor = cms.double(3),
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
        isMC = cms.bool(True),
        jetCorrLabel = cms.InputTag("L3Absolute"),
        jetCorrLabelRes = cms.InputTag("L2L3Residual"),
        offsetCorrLabel = cms.InputTag("L1FastJet"),
        skipEM = cms.bool(True),
        skipEMfractionThreshold = cms.double(0.9),
        skipMuonSelection = cms.string('isGlobalMuon | isStandAloneMuon'),
        skipMuons = cms.bool(True),
        src = cms.InputTag("slimmedJetsNewJEC"),
        type1JetPtThreshold = cms.double(15.0),
        type2ExtraCorrFactor = cms.double(1.0),
        type2ResidualCorrEtaMax = cms.double(9.9),
        type2ResidualCorrLabel = cms.InputTag(""),
        type2ResidualCorrOffset = cms.double(0.0)
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
