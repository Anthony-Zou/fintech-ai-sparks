"""
Unit Tests for Currency Converter Module

Tests all functions in the CurrencyConverter class including:
- Real-time rate fetching
- Route calculation
- Cost optimization
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import aiohttp

from settlement_engine.currency_converter import CurrencyConverter, ConversionRoute


class TestCurrencyConverter:
    """Test suite for CurrencyConverter class"""

    @pytest.fixture
    def converter(self):
        """Create a CurrencyConverter instance for testing"""
        return CurrencyConverter()

    @pytest.fixture
    def mock_rates(self):
        """Mock exchange rates for testing"""
        return {
            'USD': 1.0,
            'EUR': 0.92,
            'GBP': 0.79,
            'SGD': 1.34,
            'JPY': 148.5,
            'PHP': 56.8,
            'INR': 83.2,
            'MXN': 17.1,
            'AED': 3.67
        }

    def test_initialization(self, converter):
        """Test CurrencyConverter initialization"""
        assert converter is not None
        assert hasattr(converter, 'rate_cache')
        assert hasattr(converter, 'cache_expiry')
        assert hasattr(converter, 'supported_pairs')
        assert 'USD' in converter.supported_pairs
        assert 'EUR' in converter.supported_pairs
        assert 'SGD' in converter.supported_pairs

    def test_traditional_corridors_configuration(self, converter):
        """Test traditional corridor configuration"""
        assert ('USD', 'SGD') in converter.traditional_corridors
        assert ('USD', 'PHP') in converter.traditional_corridors
        assert ('USD', 'INR') in converter.traditional_corridors

        # Test corridor fee structure
        usd_sgd = converter.traditional_corridors[('USD', 'SGD')]
        assert 'fee_pct' in usd_sgd
        assert 'fixed_fee' in usd_sgd
        assert 'time' in usd_sgd
        assert isinstance(usd_sgd['fee_pct'], float)
        assert isinstance(usd_sgd['fixed_fee'], (int, float))

    def test_stablecoin_costs_configuration(self, converter):
        """Test stablecoin cost configuration"""
        assert 'USDC' in converter.stablecoin_costs
        assert 'USDT' in converter.stablecoin_costs

        usdc_config = converter.stablecoin_costs['USDC']
        assert 'fee_pct' in usdc_config
        assert 'fixed_fee' in usdc_config
        assert 'time' in usdc_config
        assert usdc_config['fee_pct'] < 0.01  # Less than 1%
        assert usdc_config['fixed_fee'] < 10  # Less than $10

    def test_generate_mock_rates(self, converter):
        """Test mock rate generation"""
        rates = converter._generate_mock_rates('USD')

        assert isinstance(rates, dict)
        assert 'USD' in rates
        assert 'EUR' in rates
        assert 'SGD' in rates
        assert rates['USD'] == 1.0
        assert rates['EUR'] < 1.0  # EUR should be less than USD
        assert rates['SGD'] > 1.0  # SGD should be more than USD

    def test_generate_mock_rates_different_base(self, converter):
        """Test mock rate generation with different base currency"""
        rates = converter._generate_mock_rates('EUR')

        assert isinstance(rates, dict)
        assert 'USD' in rates
        assert 'EUR' in rates
        assert rates['EUR'] == 1.0  # Base currency should be 1.0
        assert rates['USD'] > 1.0  # USD should be more than EUR

    @pytest.mark.asyncio
    async def test_get_real_time_rates_cache(self, converter):
        """Test real-time rate caching mechanism"""
        # First call should populate cache
        rates1 = await converter.get_real_time_rates('USD')
        assert isinstance(rates1, dict)
        assert 'USD' in rates1

        # Second call should use cache
        rates2 = await converter.get_real_time_rates('USD')
        assert rates1 == rates2

        # Check cache was populated
        assert 'USD_rates' in converter.rate_cache
        assert 'USD_rates' in converter.cache_expiry

    @pytest.mark.asyncio
    async def test_get_real_time_rates_cache_expiry(self, converter):
        """Test cache expiry mechanism"""
        # Set expired cache
        converter.rate_cache['USD_rates'] = {'USD': 1.0, 'EUR': 0.92}
        converter.cache_expiry['USD_rates'] = datetime.now(
        ) - timedelta(minutes=10)

        # Should fetch new rates
        rates = await converter.get_real_time_rates('USD')
        assert isinstance(rates, dict)

        # Cache should be updated
        assert converter.cache_expiry['USD_rates'] > datetime.now(
        ) - timedelta(minutes=1)

    @pytest.mark.asyncio
    async def test_fetch_exchangerate_api_rates_success(self, converter):
        """Test successful API rate fetching"""
        mock_response_data = {
            'rates': {
                'USD': 1.0,
                'EUR': 0.92,
                'GBP': 0.79,
                'SGD': 1.34
            }
        }

        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)

            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            rates = await converter._fetch_exchangerate_api_rates('USD')

            assert rates == mock_response_data['rates']
            assert 'USD' in rates
            assert 'EUR' in rates

    @pytest.mark.asyncio
    async def test_fetch_exchangerate_api_rates_failure(self, converter):
        """Test API rate fetching failure"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 500

            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

            rates = await converter._fetch_exchangerate_api_rates('USD')

            assert rates is None

    @pytest.mark.asyncio
    async def test_fetch_exchangerate_api_rates_timeout(self, converter):
        """Test API rate fetching timeout"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = asyncio.TimeoutError()

            rates = await converter._fetch_exchangerate_api_rates('USD')

            assert rates is None

    def test_calculate_traditional_route(self, converter, mock_rates):
        """Test traditional route calculation"""
        route = converter._calculate_traditional_route(
            'USD', 'SGD', 1000.0, mock_rates)

        assert isinstance(route, ConversionRoute)
        assert route.from_currency == 'USD'
        assert route.to_currency == 'SGD'
        assert route.method == 'traditional'
        assert route.amount == 1000.0
        assert route.total_cost > 0
        assert route.final_amount > 0
        assert route.confidence_score == 0.95

    def test_calculate_traditional_route_reverse_corridor(self, converter, mock_rates):
        """Test traditional route calculation with reverse corridor"""
        route = converter._calculate_traditional_route(
            'SGD', 'USD', 1000.0, mock_rates)

        assert isinstance(route, ConversionRoute)
        assert route.from_currency == 'SGD'
        assert route.to_currency == 'USD'
        assert route.method == 'traditional'
        assert route.total_cost > 0
        assert route.final_amount > 0

    def test_calculate_traditional_route_unsupported_corridor(self, converter, mock_rates):
        """Test traditional route calculation for unsupported corridor"""
        route = converter._calculate_traditional_route(
            'USD', 'CNY', 1000.0, mock_rates)

        assert isinstance(route, ConversionRoute)
        assert route.from_currency == 'USD'
        assert route.to_currency == 'CNY'
        assert route.method == 'traditional'
        # Should use default fees for unsupported corridor
        assert route.fee_percentage == 0.025
        assert route.fixed_fee == 20

    def test_calculate_stablecoin_route_usdc(self, converter, mock_rates):
        """Test USDC stablecoin route calculation"""
        route = converter._calculate_stablecoin_route(
            'USD', 'SGD', 1000.0, mock_rates, 'USDC')

        assert isinstance(route, ConversionRoute)
        assert route.from_currency == 'USD'
        assert route.to_currency == 'SGD'
        assert route.method == 'stablecoin_usdc'
        assert route.total_cost > 0
        assert route.final_amount > 0
        assert route.confidence_score == 0.88
        assert route.estimated_time == '5-10 minutes'

    def test_calculate_stablecoin_route_usdt(self, converter, mock_rates):
        """Test USDT stablecoin route calculation"""
        route = converter._calculate_stablecoin_route(
            'USD', 'SGD', 1000.0, mock_rates, 'USDT')

        assert isinstance(route, ConversionRoute)
        assert route.from_currency == 'USD'
        assert route.to_currency == 'SGD'
        assert route.method == 'stablecoin_usdt'
        assert route.total_cost > 0
        assert route.final_amount > 0
        assert route.confidence_score == 0.88
        assert route.estimated_time == '3-8 minutes'

    def test_calculate_stablecoin_route_non_usd_to_usd(self, converter, mock_rates):
        """Test stablecoin route from non-USD to USD"""
        route = converter._calculate_stablecoin_route(
            'EUR', 'USD', 1000.0, mock_rates, 'USDC')

        assert isinstance(route, ConversionRoute)
        assert route.from_currency == 'EUR'
        assert route.to_currency == 'USD'
        assert route.method == 'stablecoin_usdc'
        assert route.total_cost > 0
        assert route.final_amount > 0

    def test_calculate_crypto_route_major_pairs(self, converter, mock_rates):
        """Test direct crypto route for major currency pairs"""
        route = converter._calculate_crypto_route(
            'USD', 'EUR', 1000.0, mock_rates)

        assert isinstance(route, ConversionRoute)
        assert route.from_currency == 'USD'
        assert route.to_currency == 'EUR'
        assert route.method == 'direct_crypto'
        assert route.total_cost > 0
        assert route.final_amount > 0
        assert route.confidence_score == 0.82
        assert route.estimated_time == '30-60 seconds'
        assert route.fee_percentage == 0.0005  # 0.05%

    def test_calculate_crypto_route_unsupported_pair(self, converter, mock_rates):
        """Test direct crypto route for unsupported currency pair"""
        route = converter._calculate_crypto_route(
            'USD', 'PHP', 1000.0, mock_rates)

        assert route is None

    def test_calculate_crypto_route_same_currency(self, converter, mock_rates):
        """Test direct crypto route for same currency"""
        route = converter._calculate_crypto_route(
            'USD', 'USD', 1000.0, mock_rates)

        assert isinstance(route, ConversionRoute)
        assert route.rate == 1.0
        assert route.from_currency == 'USD'
        assert route.to_currency == 'USD'

    @pytest.mark.asyncio
    async def test_calculate_conversion_routes(self, converter):
        """Test comprehensive conversion route calculation"""
        routes = await converter.calculate_conversion_routes('USD', 'SGD', 1000.0)

        assert isinstance(routes, list)
        assert len(routes) > 0

        # Should have at least traditional and stablecoin routes
        methods = [route.method for route in routes]
        assert 'traditional' in methods
        assert any('stablecoin' in method for method in methods)

        # Routes should be sorted by cost (ascending)
        costs = [route.total_cost for route in routes]
        assert costs == sorted(costs)

    @pytest.mark.asyncio
    async def test_calculate_conversion_routes_empty(self, converter):
        """Test conversion route calculation with no valid routes"""
        # Mock a scenario where no routes are available
        with patch.object(converter, '_calculate_traditional_route', return_value=None):
            with patch.object(converter, '_calculate_stablecoin_route', return_value=None):
                with patch.object(converter, '_calculate_crypto_route', return_value=None):
                    routes = await converter.calculate_conversion_routes('USD', 'SGD', 1000.0)

                    assert isinstance(routes, list)
                    assert len(routes) == 0

    @pytest.mark.asyncio
    async def test_get_corridor_analytics(self, converter):
        """Test corridor analytics generation"""
        analytics = await converter.get_corridor_analytics('USD', 'SGD')

        assert isinstance(analytics, dict)
        assert 'corridor' in analytics
        assert 'test_amount' in analytics
        assert 'optimal_route' in analytics
        assert 'routes_available' in analytics
        assert analytics['corridor'] == 'USD -> SGD'
        assert analytics['test_amount'] == 10000

    @pytest.mark.asyncio
    async def test_get_corridor_analytics_no_routes(self, converter):
        """Test corridor analytics with no available routes"""
        with patch.object(converter, 'calculate_conversion_routes', return_value=[]):
            analytics = await converter.get_corridor_analytics('USD', 'SGD')

            assert 'error' in analytics
            assert analytics['error'] == 'No routes available for this corridor'

    @pytest.mark.asyncio
    async def test_get_corridor_analytics_with_savings(self, converter):
        """Test corridor analytics with savings calculation"""
        analytics = await converter.get_corridor_analytics('USD', 'PHP')

        assert isinstance(analytics, dict)
        if 'error' not in analytics:
            assert 'max_savings_pct' in analytics
            assert 'traditional_cost' in analytics
            assert 'stablecoin_cost' in analytics
            assert analytics['max_savings_pct'] >= 0

    def test_conversion_route_dataclass(self):
        """Test ConversionRoute dataclass functionality"""
        route = ConversionRoute(
            from_currency='USD',
            to_currency='SGD',
            method='traditional',
            rate=1.34,
            fee_percentage=0.025,
            fixed_fee=25.0,
            estimated_time='2-3 days',
            total_cost=50.0,
            final_amount=1315.0,
            confidence_score=0.95
        )

        assert route.from_currency == 'USD'
        assert route.to_currency == 'SGD'
        assert route.method == 'traditional'
        assert route.rate == 1.34
        assert route.fee_percentage == 0.025
        assert route.fixed_fee == 25.0
        assert route.estimated_time == '2-3 days'
        assert route.total_cost == 50.0
        assert route.final_amount == 1315.0
        assert route.confidence_score == 0.95

    @pytest.mark.asyncio
    async def test_error_handling_in_calculate_conversion_routes(self, converter):
        """Test error handling in conversion route calculation"""
        with patch.object(converter, 'get_real_time_rates', side_effect=Exception("Network error")):
            routes = await converter.calculate_conversion_routes('USD', 'SGD', 1000.0)

            # Should still return some routes using fallback mechanisms
            assert isinstance(routes, list)

    def test_cost_calculation_accuracy(self, converter, mock_rates):
        """Test accuracy of cost calculations"""
        amount = 1000.0
        route = converter._calculate_traditional_route(
            'USD', 'SGD', amount, mock_rates)

        # Verify cost calculation components
        assert route.total_cost > 0
        assert route.final_amount > 0
        # Final amount should be less due to fees
        assert route.final_amount < amount * route.rate

        # Verify percentage fee calculation
        expected_percentage_fee = amount * route.fee_percentage
        assert abs(route.total_cost -
                   (expected_percentage_fee + route.fixed_fee)) < 0.01

    @pytest.mark.asyncio
    async def test_concurrent_rate_fetching(self, converter):
        """Test concurrent rate fetching doesn't cause issues"""
        # Test multiple concurrent calls
        tasks = [
            converter.get_real_time_rates('USD'),
            converter.get_real_time_rates('EUR'),
            converter.get_real_time_rates('GBP')
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, dict)
            assert len(result) > 0
