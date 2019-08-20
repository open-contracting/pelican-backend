
def document_type_coherent(data, key, section):
    value = data[key]

    if value not in code_to_section_mapping:
        return {
            'result': False,
            'value': value,
            'reason': 'unknown documentType code'
        }

    if section in code_to_section_mapping[value]:
        return {'result': True}
    else:
        return {
            'result': False,
            'value': value,
            'reason': 'unsupported combination code-section for documentType'
        }

code_to_section_mapping = {
    'contractGuarantees': ['tender', 'contract'],
    'bidders': ['tender', 'bidder'],
    'illustration': ['tender', 'bid', 'contract', 'implementation'],
    'cancellationDetails': ['tender', 'award', 'contract', 'implementation'],
    'conflictOfInterest': ['tender', 'award', 'contract', 'implementation'],
    'contractArrangements': ['tender', 'award', 'contract'],
    'contractSchedule': ['tender', 'award', 'contract'],
    'contractDraft': ['tender', 'award'],
    'complaints': ['tender', 'award'],
    'evaluationReports': ['tender'],
    'clarifications': ['tender'],
    'billOfQuantity': ['tender'],
    'biddingDocuments': ['tender'],
    'technicalSpecifications': ['tender'],
    'evaluationCriteria': ['tender'],
    'shortlistedFirms': ['tender'],
    'tenderNotice': ['tender'],
    'hearingNotice': ['tender'],
    'eligibilityCriteria': ['tender'],
    'environmentalImpact': ['planning', 'implementation'],
    'needsAssessment': ['planning'],
    'procurementPlan': ['planning'],
    'marketStudies': ['planning'],
    'assetAndLiabilityAssessment': ['planning'],
    'riskProvisions': ['planning'],
    'projectPlan': ['planning'],
    'feasibilityStudy': ['planning'],
    'plannedProcurementNotice': ['planning'],
    'completionCertificate': ['implementation'],
    'debarments': ['implementation'],
    'finalAudit': ['implementation'],
    'physicalProgressReport': ['implementation'],
    'financialProgressReport': ['implementation'],
    'contractSigned': ['contract'],
    'contractNotice': ['contract'],
    'subContract': ['contract'],
    'contractSummary': ['contract'],
    'contractAnnexe': ['contract'],
    'submissionDocuments': ['bid', 'award', 'contract'],
    'winningBid': ['award'],
    'awardNotice': ['award']
}
