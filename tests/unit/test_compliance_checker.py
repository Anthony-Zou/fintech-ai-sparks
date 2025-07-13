"""
Unit Tests for Compliance Checker Module

Tests all functions in the ComplianceChecker class including:
- KYC verification
- AML screening
- Sanctions checking
- Regulatory compliance
- Risk assessment
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from settlement_engine.compliance_checker import (
    ComplianceChecker,
    ComplianceResult,
    CustomerProfile,
    ComplianceStatus,
    RiskLevel
)


class TestComplianceChecker:
    """Test suite for ComplianceChecker class"""

    @pytest.fixture
    def compliance_checker(self):
        """Create a ComplianceChecker instance for testing"""
        return ComplianceChecker()

    @pytest.fixture
    def sample_customer(self):
        """Create a sample customer profile for testing"""
        return CustomerProfile(
            customer_id="CUST001",
            name="John Smith",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="enhanced",
            last_kyc_update=datetime(2024, 1, 15),
            transaction_history={
                "monthly_volume": 15000, "daily_volume": 2000},
            sanctions_checked=True,
            pep_status=False
        )

    @pytest.fixture
    def sample_counterparty(self):
        """Create a sample counterparty profile for testing"""
        return CustomerProfile(
            customer_id="BENE001",
            name="Maria Santos",
            country="Philippines",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="basic",
            last_kyc_update=datetime(2023, 12, 1),
            transaction_history={"monthly_volume": 3000, "daily_volume": 500},
            sanctions_checked=True,
            pep_status=False
        )

    def test_initialization(self, compliance_checker):
        """Test ComplianceChecker initialization"""
        assert compliance_checker is not None
        assert hasattr(compliance_checker, 'high_risk_countries')
        assert hasattr(compliance_checker, 'sanctions_lists')
        assert hasattr(compliance_checker, 'edd_thresholds')
        assert hasattr(compliance_checker, 'regulatory_requirements')

        # Test configuration
        assert 'IRAN' in compliance_checker.high_risk_countries
        assert 'NORTH_KOREA' in compliance_checker.high_risk_countries
        assert 'OFAC_SDN' in compliance_checker.sanctions_lists
        assert 'individual' in compliance_checker.edd_thresholds
        assert 'corporation' in compliance_checker.edd_thresholds

    def test_compliance_status_enum(self):
        """Test ComplianceStatus enum values"""
        assert ComplianceStatus.APPROVED.value == "approved"
        assert ComplianceStatus.PENDING.value == "pending_review"
        assert ComplianceStatus.REJECTED.value == "rejected"
        assert ComplianceStatus.REQUIRES_DOCUMENTATION.value == "requires_documentation"

    def test_risk_level_enum(self):
        """Test RiskLevel enum values"""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"

    def test_customer_profile_dataclass(self):
        """Test CustomerProfile dataclass functionality"""
        profile = CustomerProfile(
            customer_id="TEST001",
            name="Test Customer",
            country="Singapore",
            entity_type="corporation",
            risk_rating=RiskLevel.MEDIUM,
            kyc_level="premium",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 100000, "daily_volume": 5000},
            sanctions_checked=True,
            pep_status=True
        )

        assert profile.customer_id == "TEST001"
        assert profile.name == "Test Customer"
        assert profile.country == "Singapore"
        assert profile.entity_type == "corporation"
        assert profile.risk_rating == RiskLevel.MEDIUM
        assert profile.kyc_level == "premium"
        assert profile.pep_status == True

    def test_edd_thresholds_configuration(self, compliance_checker):
        """Test EDD thresholds configuration"""
        individual_thresholds = compliance_checker.edd_thresholds['individual']
        corporation_thresholds = compliance_checker.edd_thresholds['corporation']

        assert individual_thresholds['daily'] == 50000
        assert individual_thresholds['monthly'] == 200000
        assert individual_thresholds['single_transaction'] == 25000

        assert corporation_thresholds['daily'] > individual_thresholds['daily']
        assert corporation_thresholds['monthly'] > individual_thresholds['monthly']
        assert corporation_thresholds['single_transaction'] > individual_thresholds['single_transaction']

    def test_regulatory_requirements_configuration(self, compliance_checker):
        """Test regulatory requirements configuration"""
        assert ('USD', 'CNY') in compliance_checker.regulatory_requirements
        assert ('USD', 'INR') in compliance_checker.regulatory_requirements
        assert ('USD', 'PHP') in compliance_checker.regulatory_requirements

        usd_cny_reqs = compliance_checker.regulatory_requirements[(
            'USD', 'CNY')]
        assert 'SAFE_REGISTRATION' in usd_cny_reqs
        assert 'PBOC_APPROVAL' in usd_cny_reqs

    def test_verify_kyc_current_and_enhanced(self, compliance_checker, sample_customer, sample_counterparty):
        """Test KYC verification with current and enhanced profiles"""
        result = compliance_checker._verify_kyc(
            sample_customer, sample_counterparty, 5000.0)

        assert isinstance(result, dict)
        assert 'customer_kyc' in result
        assert 'counterparty_kyc' in result
        assert 'identity_verification' in result

        # Customer has enhanced KYC and recent update
        assert result['customer_kyc'] == 'verified'
        # Counterparty has basic KYC and older update
        assert result['counterparty_kyc'] == 'expired_requires_update'

    def test_verify_kyc_expired_kyc(self, compliance_checker):
        """Test KYC verification with expired KYC"""
        old_customer = CustomerProfile(
            customer_id="OLD001",
            name="Old Customer",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="enhanced",
            last_kyc_update=datetime(2022, 1, 1),  # Very old
            transaction_history={"monthly_volume": 5000, "daily_volume": 500},
            sanctions_checked=True,
            pep_status=False
        )

        current_customer = CustomerProfile(
            customer_id="CURR001",
            name="Current Customer",
            country="Singapore",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="basic",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={"monthly_volume": 5000, "daily_volume": 500},
            sanctions_checked=True,
            pep_status=False
        )

        result = compliance_checker._verify_kyc(
            old_customer, current_customer, 5000.0)

        assert result['customer_kyc'] == 'expired_requires_update'
        assert result['counterparty_kyc'] == 'verified'

    def test_verify_kyc_basic_level_high_amount(self, compliance_checker):
        """Test KYC verification with basic level and high amount"""
        basic_customer = CustomerProfile(
            customer_id="BASIC001",
            name="Basic Customer",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="basic",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={"monthly_volume": 5000, "daily_volume": 500},
            sanctions_checked=True,
            pep_status=False
        )

        enhanced_customer = CustomerProfile(
            customer_id="ENH001",
            name="Enhanced Customer",
            country="Singapore",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="enhanced",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={"monthly_volume": 5000, "daily_volume": 500},
            sanctions_checked=True,
            pep_status=False
        )

        result = compliance_checker._verify_kyc(
            basic_customer, enhanced_customer, 15000.0)

        assert result['customer_kyc'] == 'requires_enhanced_kyc'
        assert result['counterparty_kyc'] == 'verified'

    def test_perform_aml_screening_normal(self, compliance_checker, sample_customer, sample_counterparty):
        """Test AML screening with normal transaction"""
        result = compliance_checker._perform_aml_screening(
            sample_customer,
            sample_counterparty,
            5000.0,
            'family_support'
        )

        assert isinstance(result, dict)
        assert 'source_of_funds' in result
        assert 'transaction_monitoring' in result
        assert 'pep_screening' in result
        assert 'purpose_verification' in result

        assert result['source_of_funds'] == 'acceptable'
        assert result['transaction_monitoring'] == 'normal_patterns'
        assert result['pep_screening'] == 'no_pep_identified'
        assert result['purpose_verification'] == 'acceptable'

    def test_perform_aml_screening_large_amount(self, compliance_checker, sample_customer, sample_counterparty):
        """Test AML screening with large amount"""
        result = compliance_checker._perform_aml_screening(
            sample_customer,
            sample_counterparty,
            150000.0,  # Large amount
            'business_payment'
        )

        assert result['source_of_funds'] == 'verification_required'
        assert result['transaction_monitoring'] == 'enhanced_due_diligence_required'

    def test_perform_aml_screening_corporate_entity(self, compliance_checker, sample_counterparty):
        """Test AML screening with corporate entity"""
        corporate_customer = CustomerProfile(
            customer_id="CORP001",
            name="TechCorp Inc",
            country="United States",
            entity_type="corporation",
            risk_rating=RiskLevel.LOW,
            kyc_level="premium",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 500000, "daily_volume": 25000},
            sanctions_checked=True,
            pep_status=False
        )

        result = compliance_checker._perform_aml_screening(
            corporate_customer,
            sample_counterparty,
            75000.0,
            'supplier_payment'
        )

        assert result['source_of_funds'] == 'business_verified'
        assert result['transaction_monitoring'] == 'normal_patterns'

    def test_perform_aml_screening_pep_customer(self, compliance_checker, sample_counterparty):
        """Test AML screening with PEP customer"""
        pep_customer = CustomerProfile(
            customer_id="PEP001",
            name="Political Figure",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.HIGH,
            kyc_level="premium",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 50000, "daily_volume": 5000},
            sanctions_checked=True,
            pep_status=True
        )

        result = compliance_checker._perform_aml_screening(
            pep_customer,
            sample_counterparty,
            10000.0,
            'personal_transfer'
        )

        assert result['pep_screening'] == 'pep_identified_enhanced_review'

    def test_perform_aml_screening_suspicious_purpose(self, compliance_checker, sample_customer, sample_counterparty):
        """Test AML screening with suspicious purpose"""
        result = compliance_checker._perform_aml_screening(
            sample_customer,
            sample_counterparty,
            5000.0,
            'cash'  # Suspicious purpose
        )

        assert result['purpose_verification'] == 'requires_documentation'

    def test_check_sanctions_clear(self, compliance_checker, sample_customer, sample_counterparty):
        """Test sanctions checking with clear results"""
        result = compliance_checker._check_sanctions(
            sample_customer, sample_counterparty)

        assert isinstance(result, dict)
        assert 'customer_sanctions' in result
        assert 'counterparty_sanctions' in result
        assert 'country_sanctions' in result

        assert result['customer_sanctions'] == 'clear'
        assert result['counterparty_sanctions'] == 'clear'
        assert result['country_sanctions'] == 'clear'

    def test_check_sanctions_high_risk_country(self, compliance_checker, sample_customer):
        """Test sanctions checking with high risk country"""
        iran_counterparty = CustomerProfile(
            customer_id="IRAN001",
            name="Iranian Customer",
            country="IRAN",
            entity_type="individual",
            risk_rating=RiskLevel.HIGH,
            kyc_level="basic",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={"monthly_volume": 5000, "daily_volume": 500},
            sanctions_checked=True,
            pep_status=False
        )

        result = compliance_checker._check_sanctions(
            sample_customer, iran_counterparty)

        assert result['customer_sanctions'] == 'clear'
        assert result['counterparty_sanctions'] == 'clear'
        assert 'high_risk_country_IRAN' in result['country_sanctions']

    def test_check_entity_sanctions_clear(self, compliance_checker):
        """Test entity sanctions checking with clear result"""
        result = compliance_checker._check_entity_sanctions(
            "Clean Entity", "United States")

        assert result is None

    def test_check_entity_sanctions_blocked(self, compliance_checker):
        """Test entity sanctions checking with blocked entity"""
        # Mock the sanctions list to include our test entity
        with patch.object(compliance_checker, 'sanctions_lists', {
            'OFAC_SDN': ['BLOCKED_ENTITY_1', 'TEST_BLOCKED_ENTITY'],
            'UN_SANCTIONS': []
        }):
            result = compliance_checker._check_entity_sanctions(
                "TEST_BLOCKED_ENTITY", "TestCountry")

            assert result == 'OFAC_SDN'

    def test_check_regulatory_requirements_corridor_specific(self, compliance_checker):
        """Test regulatory requirements checking for specific corridors"""
        result = compliance_checker._check_regulatory_requirements(
            'USD', 'PHP', 25000.0)

        assert isinstance(result, list)
        assert 'BSP_REGISTRATION' in result
        assert 'AMLC_REPORTING' in result
        assert 'FINCEN_COMPLIANCE' in result
        assert 'CTR_FILING_REQUIRED' in result

    def test_check_regulatory_requirements_large_amount(self, compliance_checker):
        """Test regulatory requirements for large amounts"""
        result = compliance_checker._check_regulatory_requirements(
            'USD', 'SGD', 75000.0)

        assert 'CTR_FILING_REQUIRED' in result
        assert 'SAR_MONITORING' in result
        assert 'FINCEN_COMPLIANCE' in result

    def test_check_regulatory_requirements_small_amount(self, compliance_checker):
        """Test regulatory requirements for small amounts"""
        result = compliance_checker._check_regulatory_requirements(
            'EUR', 'GBP', 5000.0)

        assert 'CTR_FILING_REQUIRED' not in result
        assert 'SAR_MONITORING' not in result

    def test_calculate_overall_risk_low(self, compliance_checker):
        """Test overall risk calculation - low risk"""
        low_risk_customer = CustomerProfile(
            customer_id="LOW001",
            name="Low Risk Customer",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="enhanced",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={"monthly_volume": 5000, "daily_volume": 500},
            sanctions_checked=True,
            pep_status=False
        )

        low_risk_counterparty = CustomerProfile(
            customer_id="LOW002",
            name="Low Risk Counterparty",
            country="Singapore",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="enhanced",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={"monthly_volume": 3000, "daily_volume": 300},
            sanctions_checked=True,
            pep_status=False
        )

        risk_level = compliance_checker._calculate_overall_risk(
            low_risk_customer,
            low_risk_counterparty,
            5000.0,
            'USD',
            'SGD'
        )

        assert risk_level == RiskLevel.LOW

    def test_calculate_overall_risk_high(self, compliance_checker):
        """Test overall risk calculation - high risk"""
        high_risk_customer = CustomerProfile(
            customer_id="HIGH001",
            name="High Risk Customer",
            country="IRAN",
            entity_type="individual",
            risk_rating=RiskLevel.HIGH,
            kyc_level="basic",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 100000, "daily_volume": 10000},
            sanctions_checked=True,
            pep_status=True
        )

        high_risk_counterparty = CustomerProfile(
            customer_id="HIGH002",
            name="High Risk Counterparty",
            country="NORTH_KOREA",
            entity_type="individual",
            risk_rating=RiskLevel.HIGH,
            kyc_level="basic",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 50000, "daily_volume": 5000},
            sanctions_checked=True,
            pep_status=True
        )

        risk_level = compliance_checker._calculate_overall_risk(
            high_risk_customer,
            high_risk_counterparty,
            100000.0,  # Large amount
            'USD',
            'CNY'
        )

        assert risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    def test_determine_compliance_status_approved(self, compliance_checker):
        """Test compliance status determination - approved"""
        kyc_result = {'customer_kyc': 'verified',
                      'counterparty_kyc': 'verified', 'identity_verification': 'verified'}
        aml_result = {'source_of_funds': 'acceptable',
                      'transaction_monitoring': 'normal_patterns'}
        sanctions_result = {'customer_sanctions': 'clear',
                            'counterparty_sanctions': 'clear', 'country_sanctions': 'clear'}
        regulatory_result = []

        status, score = compliance_checker._determine_compliance_status(
            kyc_result,
            aml_result,
            sanctions_result,
            regulatory_result,
            RiskLevel.LOW
        )

        assert status == ComplianceStatus.APPROVED
        assert score >= 60

    def test_determine_compliance_status_rejected(self, compliance_checker):
        """Test compliance status determination - rejected"""
        kyc_result = {'customer_kyc': 'verified',
                      'counterparty_kyc': 'verified', 'identity_verification': 'verified'}
        aml_result = {'source_of_funds': 'acceptable',
                      'transaction_monitoring': 'normal_patterns'}
        sanctions_result = {'customer_sanctions': 'blocked_OFAC_SDN',
                            'counterparty_sanctions': 'clear', 'country_sanctions': 'clear'}
        regulatory_result = []

        status, score = compliance_checker._determine_compliance_status(
            kyc_result,
            aml_result,
            sanctions_result,
            regulatory_result,
            RiskLevel.LOW
        )

        assert status == ComplianceStatus.REJECTED
        assert score == 0

    def test_determine_compliance_status_requires_documentation(self, compliance_checker):
        """Test compliance status determination - requires documentation"""
        kyc_result = {'customer_kyc': 'requires_verification',
                      'counterparty_kyc': 'verified', 'identity_verification': 'pending'}
        aml_result = {'source_of_funds': 'acceptable',
                      'transaction_monitoring': 'normal_patterns'}
        sanctions_result = {'customer_sanctions': 'clear',
                            'counterparty_sanctions': 'clear', 'country_sanctions': 'clear'}
        regulatory_result = []

        status, score = compliance_checker._determine_compliance_status(
            kyc_result,
            aml_result,
            sanctions_result,
            regulatory_result,
            RiskLevel.LOW
        )

        assert status == ComplianceStatus.REQUIRES_DOCUMENTATION
        assert score < 100

    def test_determine_required_documentation_individual(self, compliance_checker):
        """Test required documentation determination for individual"""
        individual_customer = CustomerProfile(
            customer_id="IND001",
            name="Individual Customer",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="basic",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={"monthly_volume": 5000, "daily_volume": 500},
            sanctions_checked=True,
            pep_status=False
        )

        docs = compliance_checker._determine_required_documentation(
            individual_customer,
            25000.0,
            RiskLevel.LOW,
            []
        )

        assert isinstance(docs, list)
        assert 'government_id' in docs
        assert 'proof_of_address' in docs

    def test_determine_required_documentation_corporation(self, compliance_checker):
        """Test required documentation determination for corporation"""
        corporate_customer = CustomerProfile(
            customer_id="CORP001",
            name="Corporate Customer",
            country="United States",
            entity_type="corporation",
            risk_rating=RiskLevel.MEDIUM,
            kyc_level="premium",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 500000, "daily_volume": 25000},
            sanctions_checked=True,
            pep_status=False
        )

        docs = compliance_checker._determine_required_documentation(
            corporate_customer,
            75000.0,
            RiskLevel.MEDIUM,
            ['CTR_FILING_REQUIRED']
        )

        assert isinstance(docs, list)
        assert 'corporate_resolution' in docs
        assert 'authorized_signatory_list' in docs
        assert 'ctr_form' in docs

    def test_determine_required_documentation_high_risk(self, compliance_checker):
        """Test required documentation determination for high risk"""
        high_risk_customer = CustomerProfile(
            customer_id="HIGH001",
            name="High Risk Customer",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.HIGH,
            kyc_level="enhanced",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 100000, "daily_volume": 10000},
            sanctions_checked=True,
            pep_status=True
        )

        docs = compliance_checker._determine_required_documentation(
            high_risk_customer,
            100000.0,
            RiskLevel.HIGH,
            []
        )

        assert isinstance(docs, list)
        assert 'source_of_funds_documentation' in docs
        assert 'beneficial_ownership' in docs
        assert 'transaction_purpose_documentation' in docs

    def test_perform_comprehensive_compliance_check(self, compliance_checker, sample_customer, sample_counterparty):
        """Test comprehensive compliance check integration"""
        result = compliance_checker.perform_comprehensive_compliance_check(
            sample_customer,
            sample_counterparty,
            10000.0,
            'USD',
            'SGD',
            'business_payment'
        )

        assert isinstance(result, ComplianceResult)
        assert result.transaction_id.startswith('COMP_')
        assert isinstance(result.overall_status, ComplianceStatus)
        assert isinstance(result.risk_level, RiskLevel)
        assert isinstance(result.kyc_status, dict)
        assert isinstance(result.aml_status, dict)
        assert isinstance(result.sanctions_status, dict)
        assert isinstance(result.regulatory_requirements, list)
        assert isinstance(result.required_documentation, list)
        assert isinstance(result.compliance_score, float)
        assert isinstance(result.review_required, bool)
        assert isinstance(result.auto_approval, bool)
        assert isinstance(result.expiry_date, datetime)

        # Check expiry date is 30 days from now
        expected_expiry = datetime.now() + timedelta(days=30)
        # Within 1 minute
        assert abs((result.expiry_date - expected_expiry).total_seconds()) < 60

    def test_compliance_result_dataclass(self):
        """Test ComplianceResult dataclass functionality"""
        result = ComplianceResult(
            transaction_id="TEST_COMP_001",
            overall_status=ComplianceStatus.APPROVED,
            risk_level=RiskLevel.LOW,
            kyc_status={'customer_kyc': 'verified'},
            aml_status={'source_of_funds': 'acceptable'},
            sanctions_status={'customer_sanctions': 'clear'},
            regulatory_requirements=['FINCEN_COMPLIANCE'],
            required_documentation=['government_id'],
            compliance_score=85.0,
            review_required=False,
            auto_approval=True,
            expiry_date=datetime(2024, 12, 31)
        )

        assert result.transaction_id == "TEST_COMP_001"
        assert result.overall_status == ComplianceStatus.APPROVED
        assert result.risk_level == RiskLevel.LOW
        assert result.compliance_score == 85.0
        assert result.review_required == False
        assert result.auto_approval == True
