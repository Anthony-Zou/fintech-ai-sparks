"""
Real-Time Currency Converter with Multi-Route Optimization

Integrates multiple FX data sources and calculates optimal conversion routes
including traditional FX, stablecoin bridges, and direct crypto pairs.
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass


@dataclass
class ConversionRoute:
    """Represents a currency conversion route with all associated costs"""
    from_currency: str
    to_currency: str
    method: str  # 'traditional', 'stablecoin', 'direct_crypto'
    rate: float
    fee_percentage: float
    fixed_fee: float
    estimated_time: str  # e.g., "2-3 days", "5 minutes"
    total_cost: float
    final_amount: float
    confidence_score: float  # 0-1, based on liquidity and reliability


class CurrencyConverter:
    """
    Advanced currency converter supporting multiple settlement rails:
    - Traditional banking FX rates
    - Stablecoin bridge routes (USD -> USDC -> Target)
    - Direct cryptocurrency pairs
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rate_cache = {}
        self.cache_expiry = {}

        # Major currency corridors with realistic fee structures
        self.traditional_corridors = {
            ('USD', 'SGD'): {'fee_pct': 0.005, 'fixed_fee': 25, 'time': '1-2 days'},
            ('USD', 'PHP'): {'fee_pct': 0.035, 'fixed_fee': 15, 'time': '2-3 days'},
            ('USD', 'INR'): {'fee_pct': 0.025, 'fixed_fee': 20, 'time': '1-3 days'},
            ('USD', 'MXN'): {'fee_pct': 0.030, 'fixed_fee': 12, 'time': '1-2 days'},
            ('SGD', 'PHP'): {'fee_pct': 0.040, 'fixed_fee': 18, 'time': '2-4 days'},
            ('AED', 'INR'): {'fee_pct': 0.028, 'fixed_fee': 22, 'time': '1-3 days'},
        }

        # Stablecoin bridge costs (much lower)
        self.stablecoin_costs = {
            'USDC': {'fee_pct': 0.001, 'fixed_fee': 2.5, 'time': '5-10 minutes'},
            'USDT': {'fee_pct': 0.0015, 'fixed_fee': 1.8, 'time': '3-8 minutes'},
        }

        # Supported currency pairs for direct conversion
        self.supported_pairs = [
            'USD', 'EUR', 'GBP', 'SGD', 'JPY', 'AUD', 'CAD', 'CHF',
            'CNY', 'HKD', 'INR', 'KRW', 'PHP', 'THB', 'MYR', 'IDR',
            'MXN', 'BRL', 'AED', 'SAR'
        ]

    async def get_real_time_rates(self, base_currency: str = 'USD') -> Dict[str, float]:
        """
        Fetch real-time exchange rates from multiple sources
        Returns rates relative to base currency
        """
        cache_key = f"{base_currency}_rates"

        # Check cache (5-minute expiry for real-time rates)
        if (cache_key in self.rate_cache and
            cache_key in self.cache_expiry and
                datetime.now() < self.cache_expiry[cache_key]):
            return self.rate_cache[cache_key]

        try:
            # Primary source: ExchangeRate-API (free tier)
            rates = await self._fetch_exchangerate_api_rates(base_currency)
            if not rates:
                # Fallback: Generate realistic mock rates for demo
                rates = self._generate_mock_rates(base_currency)

            # Cache the results
            self.rate_cache[cache_key] = rates
            self.cache_expiry[cache_key] = datetime.now() + \
                timedelta(minutes=5)

            return rates

        except Exception as e:
            self.logger.error(f"Error fetching rates: {e}")
            return self._generate_mock_rates(base_currency)

    async def _fetch_exchangerate_api_rates(self, base_currency: str) -> Optional[Dict[str, float]]:
        """Fetch rates from ExchangeRate-API"""
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('rates', {})
        except Exception as e:
            self.logger.warning(f"ExchangeRate-API failed: {e}")
        return None

    def _generate_mock_rates(self, base_currency: str = 'USD') -> Dict[str, float]:
        """Generate realistic mock exchange rates for demo purposes"""
        # Realistic rates as of recent market data (for demo)
        mock_rates_usd = {
            'USD': 1.0,
            'EUR': 0.92,
            'GBP': 0.79,
            'SGD': 1.34,
            'JPY': 148.5,
            'AUD': 1.52,
            'CAD': 1.36,
            'CHF': 0.88,
            'CNY': 7.24,
            'HKD': 7.83,
            'INR': 83.2,
            'KRW': 1320.0,
            'PHP': 56.8,
            'THB': 35.4,
            'MYR': 4.68,
            'IDR': 15600.0,
            'MXN': 17.1,
            'BRL': 5.02,
            'AED': 3.67,
            'SAR': 3.75,
        }

        if base_currency != 'USD':
            # Convert rates to different base currency
            base_rate = mock_rates_usd.get(base_currency, 1.0)
            return {curr: rate / base_rate for curr, rate in mock_rates_usd.items()}

        return mock_rates_usd

    async def calculate_conversion_routes(
        self,
        from_currency: str,
        to_currency: str,
        amount: float
    ) -> List[ConversionRoute]:
        """
        Calculate all possible conversion routes and their costs
        Returns sorted list by total cost (lowest first)
        """
        routes = []

        # Get current exchange rates
        rates = await self.get_real_time_rates('USD')

        # 1. Traditional banking route
        traditional_route = self._calculate_traditional_route(
            from_currency, to_currency, amount, rates
        )
        if traditional_route:
            routes.append(traditional_route)

        # 2. Stablecoin bridge routes (via USDC/USDT)
        for stablecoin in ['USDC', 'USDT']:
            stablecoin_route = self._calculate_stablecoin_route(
                from_currency, to_currency, amount, rates, stablecoin
            )
            if stablecoin_route:
                routes.append(stablecoin_route)

        # 3. Direct crypto route (if supported)
        crypto_route = self._calculate_crypto_route(
            from_currency, to_currency, amount, rates
        )
        if crypto_route:
            routes.append(crypto_route)

        # Sort by total cost (ascending)
        routes.sort(key=lambda x: x.total_cost)

        return routes

    def _calculate_traditional_route(
        self,
        from_curr: str,
        to_curr: str,
        amount: float,
        rates: Dict[str, float]
    ) -> Optional[ConversionRoute]:
        """Calculate traditional banking route cost"""

        # Check if we have fee data for this corridor
        corridor = (from_curr, to_curr)
        reverse_corridor = (to_curr, from_curr)

        fee_data = self.traditional_corridors.get(
            corridor) or self.traditional_corridors.get(reverse_corridor)

        if not fee_data:
            # Use average fees for unsupported corridors
            fee_data = {'fee_pct': 0.025, 'fixed_fee': 20, 'time': '1-3 days'}

        # Calculate conversion
        if from_curr == 'USD':
            fx_rate = rates.get(to_curr, 1.0)
        elif to_curr == 'USD':
            fx_rate = 1.0 / rates.get(from_curr, 1.0)
        else:
            # Convert via USD
            usd_amount = amount / rates.get(from_curr, 1.0)
            fx_rate = rates.get(to_curr, 1.0)
            amount = usd_amount

        # Apply fees
        percentage_fee = amount * fee_data['fee_pct']
        total_fees = percentage_fee + fee_data['fixed_fee']
        final_amount = (amount * fx_rate) - (total_fees *
                                             fx_rate if to_curr != 'USD' else total_fees)

        return ConversionRoute(
            from_currency=from_curr,
            to_currency=to_curr,
            method='traditional',
            rate=fx_rate,
            fee_percentage=fee_data['fee_pct'],
            fixed_fee=fee_data['fixed_fee'],
            estimated_time=fee_data['time'],
            total_cost=total_fees,
            final_amount=final_amount,
            confidence_score=0.95  # High confidence for traditional banking
        )

    def _calculate_stablecoin_route(
        self,
        from_curr: str,
        to_curr: str,
        amount: float,
        rates: Dict[str, float],
        stablecoin: str
    ) -> Optional[ConversionRoute]:
        """Calculate stablecoin bridge route cost"""

        stablecoin_data = self.stablecoin_costs[stablecoin]

        # Convert to USD first (if needed)
        if from_curr != 'USD':
            usd_amount = amount / rates.get(from_curr, 1.0)
        else:
            usd_amount = amount

        # Stablecoin conversion fees (USD -> Stablecoin -> Target currency)
        stablecoin_fee = usd_amount * \
            stablecoin_data['fee_pct'] + stablecoin_data['fixed_fee']

        # Convert to target currency
        if to_curr != 'USD':
            fx_rate = rates.get(to_curr, 1.0)
            final_amount = (usd_amount - stablecoin_fee /
                            rates.get(from_curr, 1.0)) * fx_rate
        else:
            fx_rate = 1.0
            final_amount = usd_amount - stablecoin_fee

        return ConversionRoute(
            from_currency=from_curr,
            to_currency=to_curr,
            method=f'stablecoin_{stablecoin.lower()}',
            rate=fx_rate,
            fee_percentage=stablecoin_data['fee_pct'],
            fixed_fee=stablecoin_data['fixed_fee'],
            estimated_time=stablecoin_data['time'],
            total_cost=stablecoin_fee,
            final_amount=final_amount,
            confidence_score=0.88  # Good confidence for stablecoins
        )

    def _calculate_crypto_route(
        self,
        from_curr: str,
        to_curr: str,
        amount: float,
        rates: Dict[str, float]
    ) -> Optional[ConversionRoute]:
        """Calculate direct cryptocurrency route cost"""

        # Direct crypto only available for major pairs
        if not (from_curr in ['USD', 'EUR', 'GBP'] and to_curr in ['USD', 'EUR', 'GBP']):
            return None

        # Ultra-low fees for direct crypto
        crypto_fee_pct = 0.0005  # 0.05%
        crypto_fixed_fee = 0.50

        if from_curr == to_curr:
            fx_rate = 1.0
        elif from_curr == 'USD':
            fx_rate = rates.get(to_curr, 1.0)
        elif to_curr == 'USD':
            fx_rate = 1.0 / rates.get(from_curr, 1.0)
        else:
            # Convert via USD
            usd_amount = amount / rates.get(from_curr, 1.0)
            fx_rate = rates.get(to_curr, 1.0)
            amount = usd_amount

        percentage_fee = amount * crypto_fee_pct
        total_fees = percentage_fee + crypto_fixed_fee
        final_amount = (amount * fx_rate) - (total_fees *
                                             fx_rate if to_curr != 'USD' else total_fees)

        return ConversionRoute(
            from_currency=from_curr,
            to_currency=to_curr,
            method='direct_crypto',
            rate=fx_rate,
            fee_percentage=crypto_fee_pct,
            fixed_fee=crypto_fixed_fee,
            estimated_time='30-60 seconds',
            total_cost=total_fees,
            final_amount=final_amount,
            confidence_score=0.82  # Moderate confidence due to volatility
        )

    async def get_corridor_analytics(self, from_curr: str, to_curr: str) -> Dict:
        """Get detailed analytics for a specific corridor"""
        routes = await self.calculate_conversion_routes(from_curr, to_curr, 10000)  # $10k test amount

        if not routes:
            return {"error": "No routes available for this corridor"}

        traditional = next(
            (r for r in routes if r.method == 'traditional'), None)
        stablecoin = next(
            (r for r in routes if 'stablecoin' in r.method), None)
        crypto = next((r for r in routes if r.method == 'direct_crypto'), None)

        analytics = {
            "corridor": f"{from_curr} -> {to_curr}",
            "test_amount": 10000,
            "optimal_route": routes[0].method if routes else None,
            "max_savings_pct": 0,
            "max_time_savings": "",
            "routes_available": len(routes)
        }

        if traditional and stablecoin:
            cost_savings = traditional.total_cost - stablecoin.total_cost
            savings_pct = (cost_savings / traditional.total_cost) * 100
            analytics["max_savings_pct"] = round(savings_pct, 1)
            analytics["traditional_cost"] = traditional.total_cost
            analytics["stablecoin_cost"] = stablecoin.total_cost
            analytics["annual_savings_10m"] = cost_savings * \
                1000  # Savings on $10M volume

        return analytics
