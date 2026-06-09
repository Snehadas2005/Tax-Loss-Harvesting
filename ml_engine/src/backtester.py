import pandas as pd
from src.processor import DataProcessor
from src.prediction import TrendPredictor
from src.clustering import PortfolioClusterer


class TaxBacktester:
    def __init__(
        self, initial_capital=100000, tax_rate=0.15, predictor=None, clusterer=None
    ):
        """
        Research-grade simulation harness. Accepts custom trained or alternative
        algorithmic model implementations directly via dependency injection.
        """
        self.initial_capital = initial_capital
        self.tax_rate = tax_rate  # e.g., 15% Capital Gains Tax rate

        # Inject custom user models; seamlessly defaults to base models if not provided
        self.predictor = predictor if predictor else TrendPredictor()
        self.clusterer = clusterer if clusterer else PortfolioClusterer(n_clusters=3)

    def run_simulation(self, tickers, start_date, end_date):
        """
        Simulates a portfolio over time, applying the true custom ML clustering and
        prediction framework dynamically to harvest losses and calculate Tax Alpha.
        """
        print(
            f"⏳ Initializing historical simulation from {start_date} to {end_date}..."
        )

        # 1. Pipeline Initialization & Ingestion
        processor = DataProcessor(tickers, start_date, end_date)
        prices_df = processor.download_data()

        # Ensure our injected clusterer maps the asset space dataset features
        print(
            f"📊 Calibrating custom structural risk matrices via {type(self.clusterer).__name__}..."
        )
        self.clusterer.fit_clusters(processor)

        # 2. Setup Simulated Portfolios
        # Strategy A: Buy & Hold (Baseline Anchor)
        # Strategy B: Tax-Loss Harvesting Engine (Active ML Tracking)
        dates = prices_df.index
        portfolio_history = []

        primary_asset = tickers[0]
        initial_price = prices_df[primary_asset].iloc[0]
        cost_basis = initial_price
        current_asset = primary_asset

        accumulated_tax_savings = 0.0
        wash_sale_timer = 0

        print("🏃 Running chronological historical loop through market horizons...")
        # Step through time day by day (simulating actual live production execution)
        for idx in range(30, len(dates)):
            current_date = dates[idx]
            current_price = prices_df[current_asset].iloc[idx]

            # Calculate current performance return profile relative to cost basis
            current_loss = (current_price - cost_basis) / cost_basis

            # Lower wash sale countdown timer if active
            if wash_sale_timer > 0:
                wash_sale_timer -= 1

            # Check for harvesting opportunity if asset meets drawdown thresholds
            if current_loss <= -0.10 and wash_sale_timer == 0:
                # Isolate a snapshot historical data frame up to the current simulated day
                # to strictly prevent any future look-ahead data leakage
                historical_snapshot = prices_df.loc[:current_date]

                # Dynamic out-of-sample machine learning inference check
                try:
                    # Queries your true custom regressor weights on the current time-slice matrix
                    predicted_return = self.predictor.predict_next_30d_move(
                        historical_snapshot, current_asset
                    )
                except Exception as e:
                    # Defensive statistical fallback if historical data density window is too narrow
                    predicted_return = 0.01

                # Generate execution signals using your model's predictive rules
                signal = self.predictor.generate_harvest_signal(
                    current_loss, predicted_return
                )

                if signal == "HARVEST_NOW":
                    # Queries your active custom cluster engine for risk alternatives
                    substitutes = self.clusterer.get_substitutes(current_asset)
                    if substitutes:
                        replacement_asset = substitutes[0]

                        # Realize the loss financially on paper
                        realized_loss_per_share = cost_basis - current_price

                        # Estimate accurate realized tax savings credit: (Loss Amount * Tax Rate)
                        tax_saved_today = (
                            realized_loss_per_share
                            * (self.initial_capital / cost_basis)
                            * self.tax_rate
                        )
                        accumulated_tax_savings += tax_saved_today

                        print(
                            f"🔥 [HARVEST SECURED] {current_date.strftime('%Y-%m-%d')}: Sold {current_asset} at a loss. "
                            f"Swapped into twin {replacement_asset}. Tax Saved: ${tax_saved_today:.2f}"
                        )

                        # Execute asset swap within the simulation tracking loop
                        current_asset = replacement_asset
                        cost_basis = prices_df[current_asset].iloc[idx]
                        wash_sale_timer = (
                            30  # Trigger 30-day Wash Sale regulatory lock down period
                        )

            # Calculate final baseline portfolio trajectory vs active strategy compound returns
            baseline_val = (
                prices_df[primary_asset].iloc[idx] / initial_price
            ) * self.initial_capital
            active_val = (prices_df[current_asset].iloc[idx] / cost_basis) * (
                self.initial_capital + accumulated_tax_savings
            )

            portfolio_history.append(
                {
                    "Date": current_date,
                    "Baseline_Value": baseline_val,
                    "Active_Engine_Value": active_val,
                    "Cumulative_Tax_Savings": accumulated_tax_savings,
                }
            )

        history_df = pd.DataFrame(portfolio_history).set_index("Date")

        # 3. Calculate Final Structural Performance Metrics
        final_baseline = history_df["Baseline_Value"].iloc[-1]
        final_active = history_df["Active_Engine_Value"].iloc[-1]
        tax_alpha = ((final_active - final_baseline) / self.initial_capital) * 100

        print("\n🏁 --- Quantitative Simulation Complete ---")
        print(f"Final Baseline Portfolio Value:  ${final_baseline:,.2f}")
        print(f"Final Active Engine Value:      ${final_active:,.2f}")
        print(f"Total Government Tax Avoided:    ${accumulated_tax_savings:,.2f}")
        print(f"Calculated Strategy Tax Alpha:   {tax_alpha:.2f}%")

        self.portfolio_value = final_active
        self.total_tax_avoided = accumulated_tax_savings

        return history_df


if __name__ == "__main__":
    # Local verification framework to test module functionality standalone
    test_universe = ["AAPL", "MSFT", "GOOGL", "JPM", "V", "KO"]

    # Initialize the upgraded backtester running standard default profiles
    backtester = TaxBacktester(initial_capital=100000, tax_rate=0.15)
    metrics_history = backtester.run_simulation(
        tickers=test_universe, start_date="2021-01-01", end_date="2025-01-01"
    )
