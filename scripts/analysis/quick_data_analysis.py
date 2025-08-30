#!/usr/bin/env python3
"""
Quick Data Relationship Analysis for Maize Drought Resilience
===========================================================

This script quickly analyzes key relationships in the data:
- Rainfall vs Yield correlation (main focus)
- Soil properties vs Yield relationships
- County-level yield patterns

Following the user's request to "Quickly plot relationships in the data. 
Does lower rainfall correlate with lower yield? Understand the basic patterns."
"""

import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)

def quick_rainfall_yield_analysis(data_path="data/master_water_scarcity_dataset_realistic.csv"):
    """Quick analysis focusing on rainfall vs yield correlation"""
    logger.info("🌧️ Quick Rainfall vs Yield Analysis")
    logger.info("=" * 50)
    
    # Load data
    if not Path(data_path).exists():
        logger.error(f"Dataset not found: {data_path}")
        return
    
    df = pl.read_csv(data_path)
    logger.info(f"✅ Dataset loaded: {len(df):,} records")
    
    # Find rainfall column
    rainfall_cols = [col for col in df.columns if 'rainfall' in col.lower() or 'precipitation' in col.lower()]
    if not rainfall_cols:
        logger.error("No rainfall/precipitation column found")
        return
    
    rainfall_col = rainfall_cols[0]
    logger.info(f"Using rainfall column: {rainfall_col}")
    
    # Check if we have yield data
    if 'Maize_Yield_tonnes_ha' not in df.columns:
        logger.error("No maize yield column found")
        return
    
    # Create annual aggregated dataset
    logger.info("Creating annual rainfall vs yield dataset...")
    
    annual_data = df.group_by(['County', 'Year']).agg([
        pl.col(rainfall_col).sum().alias('Annual_Rainfall_mm'),
        pl.col('Maize_Yield_tonnes_ha').mean().alias('Avg_Yield_tonnes_ha')
    ]).filter(
        (pl.col('Annual_Rainfall_mm') > 0) &
        (pl.col('Avg_Yield_tonnes_ha') > 0)
    )
    
    logger.info(f"✅ Annual dataset: {len(annual_data):,} records")
    
    # Calculate correlation
    correlation_matrix = annual_data.select([
        'Annual_Rainfall_mm', 'Avg_Yield_tonnes_ha'
    ]).corr()
    
    # Extract correlation value (off-diagonal element)
    correlation = correlation_matrix[0, 1]  # or correlation_matrix[1, 0]
    
    logger.info(f"\n📊 Rainfall vs Yield Correlation: {correlation:.4f}")
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Maize Drought Resilience: Rainfall vs Yield Analysis', fontsize=16, fontweight='bold')
    
    # 1. Rainfall vs Yield scatter plot
    axes[0, 0].scatter(annual_data['Annual_Rainfall_mm'], annual_data['Avg_Yield_tonnes_ha'], 
                       alpha=0.6, color='skyblue', edgecolors='navy', s=60)
    axes[0, 0].set_xlabel('Annual Rainfall (mm)')
    axes[0, 0].set_ylabel('Average Yield (tonnes/ha)')
    axes[0, 0].set_title(f'Rainfall vs Yield\nCorrelation: {correlation:.3f}')
    
    # Add trend line
    z = np.polyfit(annual_data['Annual_Rainfall_mm'], annual_data['Avg_Yield_tonnes_ha'], 1)
    p = np.poly1d(z)
    axes[0, 0].plot(annual_data['Annual_Rainfall_mm'], p(annual_data['Annual_Rainfall_mm']), 
                    "r--", alpha=0.8, linewidth=2, label=f'Trend: y = {z[0]:.4f}x + {z[1]:.4f}')
    axes[0, 0].legend()
    
    # 2. Rainfall distribution
    axes[0, 1].hist(annual_data['Annual_Rainfall_mm'], bins=20, alpha=0.7, color='lightblue', edgecolor='navy')
    axes[0, 1].set_xlabel('Annual Rainfall (mm)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Distribution of Annual Rainfall')
    
    # 3. Yield distribution
    axes[1, 0].hist(annual_data['Avg_Yield_tonnes_ha'], bins=20, alpha=0.7, color='lightgreen', edgecolor='darkgreen')
    axes[1, 0].set_xlabel('Average Yield (tonnes/ha)')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Distribution of Average Yields')
    
    # 4. Top counties by yield
    top_counties = annual_data.group_by('County').agg([
        pl.col('Avg_Yield_tonnes_ha').mean().alias('Avg_Yield')
    ]).sort('Avg_Yield', descending=True).head(10)
    
    axes[1, 1].barh(range(len(top_counties)), top_counties['Avg_Yield'], 
                    color='lightcoral', alpha=0.8)
    axes[1, 1].set_yticks(range(len(top_counties)))
    axes[1, 1].set_yticklabels(top_counties['County'])
    axes[1, 1].set_xlabel('Average Yield (tonnes/ha)')
    axes[1, 1].set_title('Top 10 Counties by Average Yield')
    
    plt.tight_layout()
    plt.savefig('data/rainfall_yield_analysis.png', dpi=300, bbox_inches='tight')
    logger.info("📊 Analysis plots saved to 'data/rainfall_yield_analysis.png'")
    
    # Key insights
    logger.info("\n💡 Key Insights:")
    logger.info(f"  • Rainfall-Yield correlation: {correlation:.3f}")
    
    if correlation > 0.5:
        logger.info("    → Strong positive correlation: Higher rainfall generally means higher yields")
        logger.info("    → This suggests rainfall is a key limiting factor for maize production")
    elif correlation > 0.3:
        logger.info("    → Moderate positive correlation: Rainfall has some impact on yields")
        logger.info("    → Other factors (soil, management) also play important roles")
    elif correlation > 0.1:
        logger.info("    → Weak positive correlation: Rainfall has minimal direct impact")
        logger.info("    → Yields may be more dependent on other factors")
    else:
        logger.info("    → Very weak or no correlation: Rainfall doesn't predict yields well")
        logger.info("    → Consider other variables for yield prediction")
    
    # Rainfall thresholds analysis
    rainfall_quartiles = np.percentile(annual_data['Annual_Rainfall_mm'], [25, 50, 75])
    logger.info(f"\n🌧️ Rainfall Thresholds:")
    logger.info(f"  • Low rainfall (<{rainfall_quartiles[0]:.0f}mm): Drought risk")
    logger.info(f"  • Medium rainfall ({rainfall_quartiles[0]:.0f}-{rainfall_quartiles[2]:.0f}mm): Normal conditions")
    logger.info(f"  • High rainfall (>{rainfall_quartiles[2]:.0f}mm): Potential flooding risk")
    
    # Yield by rainfall category
    low_rainfall = annual_data.filter(pl.col('Annual_Rainfall_mm') < rainfall_quartiles[0])
    high_rainfall = annual_data.filter(pl.col('Annual_Rainfall_mm') > rainfall_quartiles[2])
    
    if len(low_rainfall) > 0 and len(high_rainfall) > 0:
        low_yield_avg = low_rainfall['Avg_Yield_tonnes_ha'].mean()
        high_yield_avg = high_rainfall['Avg_Yield_tonnes_ha'].mean()
        
        logger.info(f"\n📈 Yield Comparison:")
        logger.info(f"  • Low rainfall areas: {low_yield_avg:.2f} t/ha")
        logger.info(f"  • High rainfall areas: {high_yield_avg:.2f} t/ha")
        logger.info(f"  • Difference: {high_yield_avg - low_yield_avg:.2f} t/ha")
        
        if high_yield_avg > low_yield_avg:
            improvement = ((high_yield_avg - low_yield_avg) / low_yield_avg) * 100
            logger.info(f"  • Potential improvement: {improvement:.1f}% with better rainfall")
    
    return fig, annual_data

if __name__ == "__main__":
    quick_rainfall_yield_analysis()
