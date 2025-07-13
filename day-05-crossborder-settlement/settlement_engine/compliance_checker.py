"""
Compliance Engine for Cross-Border Payment Settlement

Automated KYC/AML screening, sanctions checking, and regulatory
compliance validation for cross-border payment transactions.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import re


class ComplianceStatus(Enum):
    APPROVED = "approved"
    PENDING = "pending_review"
    REJECTED = "rejected"
    REQUIRES_DOCUMENTATION = "requires_documentation"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceResult:
    """Comprehensive compliance check result"""
    transaction_id: str
    overall_status: ComplianceStatus
    risk_level: RiskLevel
    kyc_status: Dict[str, str]
    aml_status: Dict[str, str]
    sanctions_status: Dict[str, str]
    regulatory_requirements: List[str]
    required_documentation: List[str]
    compliance_score: float  # 0-100
    review_required: bool
    auto_approval: bool
    expiry_date: datetime


@dataclass
class CustomerProfile:
    """Customer profile for compliance checking"""
    customer_id: str
    name: str
    country: str
    entity_type: str  # individual, corporation, government
    risk_rating: RiskLevel
    kyc_level: str  # basic, enhanced, premium
    last_kyc_update: datetime
    transaction_history: Dict[str, float]
    sanctions_checked: bool
    pep_status: bool  # Politically Exposed Person


class ComplianceChecker:
    """
    Advanced compliance engine for cross-border payment validation

    Provides automated KYC/AML screening, sanctions checking,
    and regulatory compliance validation with real-time risk assessment.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # High-risk countries (mock FATF list)
        self.high_risk_countries = [
            'IRAN', 'NORTH_KOREA', 'MYANMAR', 'AFGHANISTAN',
            'SYRIA', 'YEMEN', 'BELARUS', 'MALI'
        ]

        # Sanctions lists (mock OFAC/UN sanctions)
        self.sanctions_lists = {
            'OFAC_SDN': [
                'BLOCKED_ENTITY_1', 'BLOCKED_ENTITY_2', 'SANCTIONED_INDIVIDUAL_1'
            ],
            'UN_SANCTIONS': [
                'UN_BLOCKED_1', 'UN_BLOCKED_2'
            ],
            'EU_SANCTIONS': [
                'EU_BLOCKED_1', 'EU_BLOCKED_2'
            ]
        }

        # Transaction thresholds for enhanced due diligence
        self.edd_thresholds = {
            'individual': {
                'daily': 50000,
                'monthly': 200000,
                'single_transaction': 25000
            },
            'corporation': {
                'daily': 500000,
                'monthly': 2000000,
                'single_transaction': 100000
            }
        }

        # Regulatory requirements by corridor
        self.regulatory_requirements = {
            ('USD', 'CNY'): ['SAFE_REGISTRATION', 'PBOC_APPROVAL'],
            ('USD', 'INR'): ['RBI_REPORTING', 'FEMA_COMPLIANCE'],
            ('USD', 'PHP'): ['BSP_REGISTRATION', 'AMLC_REPORTING'],
            ('AED', 'INR'): ['CBUAE_APPROVAL', 'RBI_REPORTING'],
            ('EUR', 'USD'): ['ECB_NOTIFICATION', 'FINCEN_REPORTING']
        }

    def perform_comprehensive_compliance_check(
        self,
        customer: CustomerProfile,
        counterparty: CustomerProfile,
        transaction_amount: float,
        from_currency: str,
        to_currency: str,
        transaction_purpose: str
    ) -> ComplianceResult:
        """
        Perform comprehensive compliance validation

        Includes KYC verification, AML screening, sanctions checking,
        and regulatory requirements validation.
        """

        transaction_id = f"COMP_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 1. KYC Verification
        kyc_result = self._verify_kyc(
            customer, counterparty, transaction_amount)

        # 2. AML Screening
        aml_result = self._perform_aml_screening(
            customer, counterparty, transaction_amount, transaction_purpose)

        # 3. Sanctions Checking
        sanctions_result = self._check_sanctions(customer, counterparty)

        # 4. Regulatory Requirements
        regulatory_result = self._check_regulatory_requirements(
            from_currency, to_currency, transaction_amount)

        # 5. Risk Assessment
        risk_level = self._calculate_overall_risk(
            customer, counterparty, transaction_amount, from_currency, to_currency)

        # 6. Determine overall compliance status
        overall_status, compliance_score = self._determine_compliance_status(
            kyc_result, aml_result, sanctions_result, regulatory_result, risk_level
        )

        # 7. Required documentation
        required_docs = self._determine_required_documentation(
            customer, transaction_amount, risk_level, regulatory_result
        )

        # 8. Review requirements
        review_required = risk_level in [
            RiskLevel.HIGH, RiskLevel.CRITICAL] or overall_status == ComplianceStatus.PENDING
        auto_approval = overall_status == ComplianceStatus.APPROVED and risk_level == RiskLevel.LOW

        return ComplianceResult(
            transaction_id=transaction_id,
            overall_status=overall_status,
            risk_level=risk_level,
            kyc_status=kyc_result,
            aml_status=aml_result,
            sanctions_status=sanctions_result,
            regulatory_requirements=regulatory_result,
            required_documentation=required_docs,
            compliance_score=compliance_score,
            review_required=review_required,
            auto_approval=auto_approval,
            expiry_date=datetime.now() + timedelta(days=30)  # 30-day validity
        )

    def _verify_kyc(self, customer: CustomerProfile, counterparty: CustomerProfile, amount: float) -> Dict[str, str]:
        """Verify KYC status for both parties"""

        result = {}

        # Customer KYC verification
        kyc_age = (datetime.now() - customer.last_kyc_update).days

        if kyc_age > 365:  # KYC older than 1 year
            result['customer_kyc'] = 'expired_requires_update'
        elif customer.kyc_level == 'basic' and amount > 10000:
            result['customer_kyc'] = 'requires_enhanced_kyc'
        elif customer.kyc_level in ['enhanced', 'premium']:
            result['customer_kyc'] = 'verified'
        else:
            result['customer_kyc'] = 'requires_verification'

        # Counterparty KYC verification
        counterparty_kyc_age = (
            datetime.now() - counterparty.last_kyc_update).days

        if counterparty_kyc_age > 365:
            result['counterparty_kyc'] = 'expired_requires_update'
        elif counterparty.kyc_level == 'basic' and amount > 10000:
            result['counterparty_kyc'] = 'requires_enhanced_kyc'
        elif counterparty.kyc_level in ['enhanced', 'premium']:
            result['counterparty_kyc'] = 'verified'
        else:
            result['counterparty_kyc'] = 'requires_verification'

        # Identity verification
        result['identity_verification'] = 'verified' if all(
            status in ['verified', 'requires_enhanced_kyc']
            for status in [result['customer_kyc'], result['counterparty_kyc']]
        ) else 'pending'

        return result

    def _perform_aml_screening(
        self,
        customer: CustomerProfile,
        counterparty: CustomerProfile,
        amount: float,
        purpose: str
    ) -> Dict[str, str]:
        """Perform AML screening and transaction monitoring"""

        result = {}

        # Source of funds verification
        if amount > 100000:
            result['source_of_funds'] = 'verification_required'
        elif customer.entity_type == 'corporation':
            result['source_of_funds'] = 'business_verified'
        else:
            result['source_of_funds'] = 'acceptable'

        # Transaction pattern analysis
        customer_thresholds = self.edd_thresholds.get(
            customer.entity_type, self.edd_thresholds['individual'])

        monthly_volume = customer.transaction_history.get('monthly_volume', 0)
        daily_volume = customer.transaction_history.get('daily_volume', 0)

        if (monthly_volume + amount > customer_thresholds['monthly'] or
            daily_volume + amount > customer_thresholds['daily'] or
                amount > customer_thresholds['single_transaction']):
            result['transaction_monitoring'] = 'enhanced_due_diligence_required'
        else:
            result['transaction_monitoring'] = 'normal_patterns'

        # PEP screening
        if customer.pep_status or counterparty.pep_status:
            result['pep_screening'] = 'pep_identified_enhanced_review'
        else:
            result['pep_screening'] = 'no_pep_identified'

        # Purpose verification
        suspicious_purposes = ['cash', 'investment',
                               'loan_repayment', 'gambling']
        if purpose.lower() in suspicious_purposes:
            result['purpose_verification'] = 'requires_documentation'
        else:
            result['purpose_verification'] = 'acceptable'

        return result

    def _check_sanctions(self, customer: CustomerProfile, counterparty: CustomerProfile) -> Dict[str, str]:
        """Check against sanctions lists"""

        result = {}

        # Check customer against sanctions lists
        customer_blocked = self._check_entity_sanctions(
            customer.name, customer.country)
        if customer_blocked:
            result['customer_sanctions'] = f'blocked_{customer_blocked}'
        else:
            result['customer_sanctions'] = 'clear'

        # Check counterparty against sanctions lists
        counterparty_blocked = self._check_entity_sanctions(
            counterparty.name, counterparty.country)
        if counterparty_blocked:
            result['counterparty_sanctions'] = f'blocked_{counterparty_blocked}'
        else:
            result['counterparty_sanctions'] = 'clear'

        # Country sanctions check
        if customer.country.upper() in self.high_risk_countries:
            result['country_sanctions'] = f'high_risk_country_{customer.country}'
        elif counterparty.country.upper() in self.high_risk_countries:
            result['country_sanctions'] = f'high_risk_country_{counterparty.country}'
        else:
            result['country_sanctions'] = 'clear'

        return result

    def _check_entity_sanctions(self, entity_name: str, country: str) -> Optional[str]:
        """Check if entity appears on any sanctions list"""

        # Simplified sanctions checking (in real implementation, use fuzzy matching)
        entity_upper = entity_name.upper()

        for list_name, sanctioned_entities in self.sanctions_lists.items():
            for sanctioned in sanctioned_entities:
                if sanctioned.upper() in entity_upper or entity_upper in sanctioned.upper():
                    return list_name

        return None

    def _check_regulatory_requirements(self, from_currency: str, to_currency: str, amount: float) -> List[str]:
        """Check corridor-specific regulatory requirements"""

        requirements = []

        # Corridor-specific requirements
        corridor = (from_currency, to_currency)
        reverse_corridor = (to_currency, from_currency)

        corridor_reqs = (self.regulatory_requirements.get(corridor) or
                         self.regulatory_requirements.get(reverse_corridor) or [])
        requirements.extend(corridor_reqs)

        # Amount-based requirements
        if amount > 10000:
            # Currency Transaction Report
            requirements.append('CTR_FILING_REQUIRED')

        if amount > 50000:
            # Suspicious Activity Report monitoring
            requirements.append('SAR_MONITORING')

        # Currency-specific requirements
        if from_currency == 'USD' or to_currency == 'USD':
            requirements.append('FINCEN_COMPLIANCE')

        return requirements

    def _calculate_overall_risk(
        self,
        customer: CustomerProfile,
        counterparty: CustomerProfile,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> RiskLevel:
        """Calculate overall transaction risk level"""

        risk_score = 0

        # Customer risk factors
        if customer.risk_rating == RiskLevel.HIGH:
            risk_score += 30
        elif customer.risk_rating == RiskLevel.MEDIUM:
            risk_score += 15

        # Counterparty risk factors
        if counterparty.risk_rating == RiskLevel.HIGH:
            risk_score += 30
        elif counterparty.risk_rating == RiskLevel.MEDIUM:
            risk_score += 15

        # Country risk factors
        if customer.country.upper() in self.high_risk_countries:
            risk_score += 25
        if counterparty.country.upper() in self.high_risk_countries:
            risk_score += 25

        # Amount risk factors
        customer_thresholds = self.edd_thresholds.get(
            customer.entity_type, self.edd_thresholds['individual'])
        if amount > customer_thresholds['single_transaction']:
            risk_score += 20

        # PEP status
        if customer.pep_status or counterparty.pep_status:
            risk_score += 15

        # Determine risk level
        if risk_score >= 70:
            return RiskLevel.CRITICAL
        elif risk_score >= 40:
            return RiskLevel.HIGH
        elif risk_score >= 20:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _determine_compliance_status(
        self,
        kyc_result: Dict[str, str],
        aml_result: Dict[str, str],
        sanctions_result: Dict[str, str],
        regulatory_result: List[str],
        risk_level: RiskLevel
    ) -> Tuple[ComplianceStatus, float]:
        """Determine overall compliance status and score"""

        score = 100
        blocking_issues = []

        # Check for blocking KYC issues
        for status in kyc_result.values():
            if 'expired' in status or 'requires_verification' in status:
                blocking_issues.append('kyc_incomplete')
                score -= 25

        # Check for blocking AML issues
        for status in aml_result.values():
            if 'required' in status or 'pep_identified' in status:
                if 'enhanced' in status:
                    score -= 15
                else:
                    score -= 30

        # Check for sanctions issues
        for status in sanctions_result.values():
            if 'blocked' in status:
                blocking_issues.append('sanctions_blocked')
                score = 0  # Immediate rejection
            elif 'high_risk' in status:
                score -= 20

        # Risk level impact
        if risk_level == RiskLevel.CRITICAL:
            score -= 30
        elif risk_level == RiskLevel.HIGH:
            score -= 20

        # Determine status
        if score == 0 or 'sanctions_blocked' in blocking_issues:
            return ComplianceStatus.REJECTED, score
        elif score < 60 or risk_level == RiskLevel.CRITICAL:
            return ComplianceStatus.PENDING, score
        elif 'kyc_incomplete' in blocking_issues:
            return ComplianceStatus.REQUIRES_DOCUMENTATION, score
        else:
            return ComplianceStatus.APPROVED, score

    def _determine_required_documentation(
        self,
        customer: CustomerProfile,
        amount: float,
        risk_level: RiskLevel,
        regulatory_requirements: List[str]
    ) -> List[str]:
        """Determine required documentation for compliance"""

        docs = []

        # KYC documentation
        if customer.kyc_level == 'basic':
            docs.extend(['government_id', 'proof_of_address'])

        # Enhanced due diligence
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            docs.extend(['source_of_funds_documentation',
                        'business_registration', 'beneficial_ownership'])

        # Large transaction documentation
        if amount > 50000:
            docs.extend(
                ['transaction_purpose_documentation', 'commercial_invoice'])

        # Regulatory documentation
        if 'CTR_FILING_REQUIRED' in regulatory_requirements:
            docs.append('ctr_form')

        if customer.entity_type == 'corporation':
            docs.extend(['corporate_resolution', 'authorized_signatory_list'])

        return list(set(docs))  # Remove duplicates
