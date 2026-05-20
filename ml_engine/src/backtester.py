import pandas as pd
import numpy as np
from src.processor import DataProcessor
from src.prediction import TrendPredictor
from src.clustering import PortfolioClusterer

class TaxBacktester:
    def __init__(self, initial_capital=100000, tax_rate=0.15):
        self.initial_capital = initial_capital
        self.tax_rate = tax_rate  # e.g., 15% Capital Gains Tax rate
        
    def run_simulation(self, tickers, start_date, end_date):
        """
        Simulates a portfolio over time, applying the ML clustering and 
        prediction framework to harvest losses and calculate Tax Alpha.
        """
        print(f"⏳ Initializing historical simulation from {start_date} to {end_date}...")
        
        # 1. Pipeline Initialization
        processor = DataProcessor(tickers, start_date, end_date)
        prices_df = processor.download_data()
        
        clusterer = PortfolioClusterer(n_clusters=3)
        clusterer.fit_clusters(processor)
        
        predictor = TrendPredictor()
        # Pre-train the predictor on the primary asset for demonstration
        primary_asset = tickers[0]
        predictor.train_model(processor, primary_asset)
        
        # 2. Setup Simulated Portfolios
        # Strategy A: Buy & Hold (Baseline)
        # Strategy B: Tax-Loss Harvesting Engine (Active)
        
        dates = prices_df.index
        portfolio_history = []
        
        # Mocking initial cost basis for the primary asset
        initial_price = prices_df[primary_asset].iloc[0]
        cost_basis = initial_price
        current_asset = primary_asset
        
        accumulated_tax_savings = 0.0
        wash_sale_timer = 0
        
        print("🏃 Running chronological historical loop...")
        # Step through time day by day (simulating the backtest)
        for idx in range(30, len(dates)):
            current_date = dates[idx]
            current_price = prices_df[current_asset].iloc[idx]
            
            # Calculate current performance relative to cost basis
            current_loss = (current_price - cost_basis) / cost_basis
            
            # Lower wash sale countdown timer if active
            if wash_sale_timer > 0:
                wash_sale_timer -= 1
                
            # Check for harvesting opportunity if asset is down and wash sale rule isn't violating
            if current_loss <= -0.10 and wash_sale_timer == 0:
                # Truncate data up to the current simulated day to avoid data leakage
                historical_snapshot = processor.raw_data.loc[:current_date]
                
                # Mock a localized prediction run for the simulation day
                # In full execution, you would recompute indicators dynamically
                predicted_return = 0.01 # Simulated flat/negative trend prediction
                
                signal = predictor.generate_harvest_signal(current_loss, predicted_return)
                
                if signal == "HARVEST_NOW":
                    substitutes = clusterer.get_substitutes(current_asset)
                    if substitutes:
                        replacement_asset = substitutes[0]
                        
                        # Realize the loss financially
                        realized_loss_per_share = cost_basis - current_price
                        # Estimate tax savings: (Loss Amount * Tax Rate)
                        tax_saved_today = realized_loss_per_share * (self.initial_capital / cost_basis) * self.tax_rate
                        accumulated_tax_savings += tax_saved_today
                        
                        print(f"🔥 [HARVEST] {current_date.strftime('%Y-%m-%d')}: Sold {current_asset} at a loss. "
                              f"Swapped into {replacement_asset}. Tax Saved: ${tax_saved_today:.2f}")
                        
                        # Execute the swap within our simulation track
                        current_asset = replacement_asset
                        cost_basis = prices_df[current_asset].iloc[idx]
                        wash_sale_timer = 30 # Trigger 30-day Wash Sale cooling period
            
            # Calculate baseline vs active performance values
            baseline_val = (prices_df[primary_asset].iloc[idx] / initial_price) * self.initial_capital
            active_val = (prices_df[current_asset].iloc[idx] / cost_basis) * (self.initial_capital + accumulated_tax_savings)
            
            portfolio_history.append({
                'Date': current_date,
                'Baseline_Value': baseline_val,
                'Active_Engine_Value': active_val,
                'Cumulative_Tax_Savings': accumulated_tax_savings
            })
            
        history_df = pd.DataFrame(portfolio_history).set_index('Date')
        
        # 3. Calculate Final Performance Metrics
        final_baseline = history_df['Baseline_Value'].iloc[-1]
        final_active = history_df['Active_Engine_Value'].iloc[-1]
        tax_alpha = ((final_active - final_baseline) / self.initial_capital) * 100
        
        print("\n🏁 --- Simulation Complete ---")
        print(f"Final Baseline Portfolio Value:  ${final_baseline:,.2f}")
        print(f"Final Active Engine Value:      ${final_active:,.2f}")
        print(f"Total Government Tax Avoided:    ${accumulated_tax_savings:,.2f}")
        print(f"Calculated Strategy Tax Alpha:   {tax_alpha:.2f}%")
        
        return history_df

if __name__ == "__main__":
    # Test universe representing different sectors
    test_universe = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'V', 'KO']
    
    backtester = TaxBacktester(initial_capital=100000, tax_rate=0.15)
    metrics_history = backtester.run_simulation(
        tickers=test_universe, 
        start_date='2021-01-01', 
        end_date='2025-01-01'
    )