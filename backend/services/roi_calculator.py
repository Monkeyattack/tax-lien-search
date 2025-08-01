from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP

class ROICalculator:
    """Calculate returns and metrics for tax lien investments"""
    
    @staticmethod
    def calculate_redemption_amount(
        purchase_amount: float,
        purchase_date: date,
        redemption_date: date,
        is_homestead: bool = False,
        is_agricultural: bool = False,
        has_mineral_rights: bool = False
    ) -> Dict[str, float]:
        """
        Calculate redemption amount based on Texas tax lien laws
        
        Returns:
        - redemption_amount: Total amount to be paid by redeemer
        - penalty_amount: Penalty/interest amount
        - penalty_rate: Percentage rate applied
        - days_held: Number of days investment was held
        """
        
        days_held = (redemption_date - purchase_date).days
        
        # Determine penalty rate based on property type and timing
        if is_homestead or is_agricultural or has_mineral_rights:
            # 2-year redemption period properties
            if days_held <= 365:
                penalty_rate = 25  # 25% first year
            else:
                penalty_rate = 50  # 50% second year
        else:
            # 6-month redemption period properties
            penalty_rate = 25  # 25% for entire period
        
        penalty_amount = purchase_amount * (penalty_rate / 100)
        redemption_amount = purchase_amount + penalty_amount
        
        return {
            'redemption_amount': round(redemption_amount, 2),
            'penalty_amount': round(penalty_amount, 2),
            'penalty_rate': penalty_rate,
            'days_held': days_held
        }
    
    @staticmethod
    def calculate_annualized_return(
        penalty_amount: float,
        investment_amount: float,
        days_held: int
    ) -> float:
        """Calculate annualized return rate"""
        
        if days_held <= 0 or investment_amount <= 0:
            return 0
        
        daily_return = penalty_amount / investment_amount / days_held
        annualized_return = daily_return * 365 * 100
        
        return round(annualized_return, 2)
    
    @staticmethod
    def calculate_investment_metrics(
        purchase_amount: float,
        purchase_date: date,
        current_date: date = None,
        redemption_deadline: date = None,
        is_homestead: bool = False,
        is_agricultural: bool = False,
        has_mineral_rights: bool = False
    ) -> Dict:
        """Calculate comprehensive investment metrics"""
        
        if not current_date:
            current_date = datetime.now().date()
        
        # Calculate potential redemption amounts
        current_redemption = ROICalculator.calculate_redemption_amount(
            purchase_amount, purchase_date, current_date,
            is_homestead, is_agricultural, has_mineral_rights
        )
        
        # Calculate days until redemption deadline
        days_until_redemption = None
        redemption_expired = False
        if redemption_deadline:
            days_until_redemption = (redemption_deadline - current_date).days
            redemption_expired = current_date > redemption_deadline
        
        # Calculate annualized return
        annualized_return = ROICalculator.calculate_annualized_return(
            current_redemption['penalty_amount'],
            purchase_amount,
            current_redemption['days_held']
        )
        
        # Calculate break-even analysis
        break_even_days = ROICalculator.calculate_break_even_days(
            purchase_amount, 10  # 10% annual return as benchmark
        )
        
        return {
            'current_value': current_redemption,
            'days_until_redemption': days_until_redemption,
            'redemption_expired': redemption_expired,
            'annualized_return': annualized_return,
            'break_even_days': break_even_days,
            'roi_percentage': (current_redemption['penalty_amount'] / purchase_amount) * 100,
            'total_return': current_redemption['redemption_amount']
        }
    
    @staticmethod
    def calculate_break_even_days(investment_amount: float, benchmark_rate: float) -> int:
        """Calculate days needed to beat benchmark annual return"""
        
        # For 25% return to beat benchmark_rate annually
        target_daily_return = benchmark_rate / 365 / 100
        penalty_daily_return = 0.25 / 365  # 25% penalty over potential holding period
        
        if penalty_daily_return <= target_daily_return:
            return 365  # Would take a full year or more
        
        # Calculate days needed for 25% penalty to exceed benchmark
        days_needed = 0.25 / benchmark_rate * 365
        return int(days_needed)
    
    @staticmethod
    def analyze_portfolio_performance(investments: List[Dict]) -> Dict:
        """Analyze overall portfolio performance"""
        
        if not investments:
            return {
                'total_invested': 0,
                'total_current_value': 0,
                'total_profit': 0,
                'average_roi': 0,
                'best_performer': None,
                'worst_performer': None,
                'active_investments': 0,
                'redeemed_investments': 0
            }
        
        total_invested = sum(inv['purchase_amount'] for inv in investments)
        total_current_value = 0
        total_profit = 0
        roi_rates = []
        active_count = 0
        redeemed_count = 0
        
        best_performer = None
        worst_performer = None
        best_roi = float('-inf')
        worst_roi = float('inf')
        
        for inv in investments:
            if inv['status'] == 'active':
                active_count += 1
                current_value = inv['current_redemption_amount']
                profit = current_value - inv['purchase_amount']
            elif inv['status'] == 'redeemed':
                redeemed_count += 1
                current_value = inv['redemption_amount']
                profit = inv['net_profit']
            else:
                continue
            
            total_current_value += current_value
            total_profit += profit
            
            roi = (profit / inv['purchase_amount']) * 100
            roi_rates.append(roi)
            
            if roi > best_roi:
                best_roi = roi
                best_performer = inv
            
            if roi < worst_roi:
                worst_roi = roi
                worst_performer = inv
        
        average_roi = sum(roi_rates) / len(roi_rates) if roi_rates else 0
        
        return {
            'total_invested': round(total_invested, 2),
            'total_current_value': round(total_current_value, 2),
            'total_profit': round(total_profit, 2),
            'average_roi': round(average_roi, 2),
            'best_performer': {
                'property_id': best_performer['property_id'],
                'roi': round(best_roi, 2),
                'profit': round(best_performer.get('net_profit', 0), 2)
            } if best_performer else None,
            'worst_performer': {
                'property_id': worst_performer['property_id'],
                'roi': round(worst_roi, 2),
                'profit': round(worst_performer.get('net_profit', 0), 2)
            } if worst_performer else None,
            'active_investments': active_count,
            'redeemed_investments': redeemed_count,
            'total_roi': round((total_profit / total_invested) * 100, 2) if total_invested > 0 else 0
        }
    
    @staticmethod
    def calculate_risk_score(
        property_value: float,
        purchase_amount: float,
        property_type: str,
        is_homestead: bool = False,
        is_occupied: bool = False,
        title_issues: bool = False
    ) -> Dict[str, float]:
        """Calculate risk score for an investment (0-100, lower is better)"""
        
        risk_score = 0
        risk_factors = []
        
        # Value ratio risk (higher purchase price vs property value = higher risk)
        if property_value > 0:
            value_ratio = purchase_amount / property_value
            if value_ratio > 0.8:
                risk_score += 30
                risk_factors.append("High purchase price relative to property value")
            elif value_ratio > 0.5:
                risk_score += 15
                risk_factors.append("Moderate purchase price relative to property value")
        else:
            risk_score += 20
            risk_factors.append("Unknown property value")
        
        # Property type risk
        high_risk_types = ['land', 'commercial', 'industrial']
        if property_type.lower() in high_risk_types:
            risk_score += 20
            risk_factors.append(f"{property_type} properties have higher liquidity risk")
        
        # Homestead risk (longer redemption period)
        if is_homestead:
            risk_score += 15
            risk_factors.append("Homestead properties have 2-year redemption period")
        
        # Occupancy risk
        if is_occupied:
            risk_score += 10
            risk_factors.append("Occupied properties may require eviction process")
        
        # Title issues risk
        if title_issues:
            risk_score += 25
            risk_factors.append("Potential title issues identified")
        
        # Cap at 100
        risk_score = min(risk_score, 100)
        
        risk_level = "Low"
        if risk_score >= 70:
            risk_level = "High"
        elif risk_score >= 40:
            risk_level = "Medium"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }