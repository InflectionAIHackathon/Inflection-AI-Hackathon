#!/usr/bin/env python3
"""
Exploratory Data Analysis (EDA) of Integrated Water Scarcity Dataset
===================================================================

This script performs comprehensive EDA on the master dataset to understand:
- Data structure and quality
- Distributions and patterns
- Correlations between variables
- County-level insights
- Temporal trends
- Key findings for the Water Scarcity Dashboard
"""

import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

def load_and_examine_data():
    """Load the master dataset and examine its structure."""
    logger.info("📊 Loading master dataset...")
    
    data_file = Path("data/master_water_scarcity_dataset.csv")
    if not data_file.exists():
        logger.error("Master dataset not found!")
        return None
    
    df = pl.read_csv(data_file)
    logger.info(f"✅ Dataset loaded: {len(df):,} records, {len(df.columns)} columns")
    
    # Basic info
    logger.info(f"\n📋 Dataset Overview:")
    logger.info(f"  Shape: {df.shape}")
    logger.info(f"  Memory usage: {df.estimated_size() / (1024*1024):.2f} MB")
    
    # Column types
    logger.info(f"\n🔍 Column Types:")
    for col, dtype in zip(df.columns, df.dtypes):
        logger.info(f"  {col}: {dtype}")
    
    return df

def analyze_data_structure(df):
    """Analyze the structure and completeness of the dataset."""
    logger.info("\n🏗️ Data Structure Analysis")
    logger.info("=" * 50)
    
    # Check for missing values
    total_records = len(df)
    logger.info(f"\n📊 Missing Value Analysis:")
    for col in df.columns:
        null_count = df[col].null_count()
        if null_count > 0:
            percentage = (null_count / total_records) * 100
            logger.info(f"  {col}: {null_count:,} ({percentage:.1f}%)")
        else:
            logger.info(f"  {col}: ✅ Complete")
    
    # Unique values for categorical columns
    logger.info(f"\n🏷️ Categorical Variables:")
    categorical_cols = ['County', 'Month_Name', 'Climate_Zone', 'Monthly_Irrigation_Needed']
    for col in categorical_cols:
        if col in df.columns:
            unique_vals = df[col].unique().to_list()
            logger.info(f"  {col}: {len(unique_vals)} unique values")
            if len(unique_vals) <= 20:
                logger.info(f"    Values: {unique_vals}")
    
    # Temporal coverage
    logger.info(f"\n📅 Temporal Coverage:")
    years = sorted(df['Year'].unique().to_list())
    months = sorted(df['Month'].unique().to_list())
    logger.info(f"  Years: {years[0]} - {years[-1]} ({len(years)} years)")
    logger.info(f"  Months: {months[0]} - {months[-1]} ({len(months)} months)")
    logger.info(f"  Total time periods: {len(years) * len(months)}")
    
    # Spatial coverage
    logger.info(f"\n🗺️ Spatial Coverage:")
    counties = sorted(df['County'].unique().to_list())
    logger.info(f"  Counties: {len(counties)}")
    logger.info(f"  County list: {counties}")

def analyze_numeric_distributions(df):
    """Analyze distributions of numeric variables."""
    logger.info("\n📈 Numeric Variable Distributions")
    logger.info("=" * 50)
    
    # Key numeric columns to analyze
    numeric_cols = [
        'Monthly_Temperature_C', 'Monthly_Humidity_Percent', 'Monthly_Pressure_hPa',
        'Monthly_Evapotranspiration_mm', 'Monthly_Precipitation_mm', 'Monthly_Water_Stress_Index',
        'Monthly_Irrigation_Volume_Liters_Ha', 'Monthly_Crop_Yield_Impact_Percent',
        'Monthly_Heat_Stress_Days', 'Water_Scarcity_Score', 'Agricultural_Risk_Index',
        'Irrigation_Priority_Score'
    ]
    
    # Filter to existing columns
    existing_numeric = [col for col in numeric_cols if col in df.columns]
    
    logger.info(f"\n📊 Summary Statistics:")
    for col in existing_numeric:
        col_data = df[col].drop_nulls()
        if len(col_data) > 0:
            stats = {
                'count': len(col_data),
                'mean': float(col_data.mean()),
                'std': float(col_data.std()),
                'min': float(col_data.min()),
                'max': float(col_data.max()),
                'median': float(col_data.median())
            }
            logger.info(f"\n  {col}:")
            logger.info(f"    Count: {stats['count']:,}")
            logger.info(f"    Mean: {stats['mean']:.2f}")
            logger.info(f"    Std: {stats['std']:.2f}")
            logger.info(f"    Min: {stats['min']:.2f}")
            logger.info(f"    Max: {stats['max']:.2f}")
            logger.info(f"    Median: {stats['median']:.2f}")

def analyze_temporal_patterns(df):
    """Analyze temporal patterns and trends."""
    logger.info("\n⏰ Temporal Pattern Analysis")
    logger.info("=" * 50)
    
    # Monthly patterns
    logger.info(f"\n📅 Monthly Patterns:")
    monthly_stats = df.group_by("Month").agg([
        pl.col("Monthly_Temperature_C").mean().alias("Avg_Temperature"),
        pl.col("Monthly_Precipitation_mm").mean().alias("Avg_Precipitation"),
        pl.col("Monthly_Water_Stress_Index").mean().alias("Avg_Water_Stress"),
        pl.col("Monthly_Heat_Stress_Days").mean().alias("Avg_Heat_Stress_Days")
    ]).sort("Month")
    
    for row in monthly_stats.iter_rows(named=True):
        month = row["Month"]
        temp = row["Avg_Temperature"]
        precip = row["Avg_Precipitation"]
        stress = row["Avg_Water_Stress"]
        heat = row["Avg_Heat_Stress_Days"]
        
        logger.info(f"  Month {month:2d}: Temp={temp:5.1f}°C, Precip={precip:6.1f}mm, "
                   f"Stress={stress:5.3f}, Heat={heat:5.1f} days")
    
    # Yearly trends
    logger.info(f"\n📈 Yearly Trends:")
    yearly_stats = df.group_by("Year").agg([
        pl.col("Monthly_Temperature_C").mean().alias("Avg_Temperature"),
        pl.col("Monthly_Precipitation_mm").mean().alias("Avg_Precipitation"),
        pl.col("Monthly_Water_Stress_Index").mean().alias("Avg_Water_Stress"),
        pl.col("Water_Scarcity_Score").mean().alias("Avg_Water_Scarcity_Score")
    ]).sort("Year")
    
    for row in yearly_stats.iter_rows(named=True):
        year = row["Year"]
        temp = row["Avg_Temperature"]
        precip = row["Avg_Precipitation"]
        stress = row["Avg_Water_Stress"]
        scarcity = row["Avg_Water_Scarcity_Score"]
        
        logger.info(f"  {year}: Temp={temp:5.1f}°C, Precip={precip:6.1f}mm, "
                   f"Stress={stress:5.3f}, Scarcity={scarcity:5.1f}")

def analyze_spatial_patterns(df):
    """Analyze spatial patterns across counties."""
    logger.info("\n🗺️ Spatial Pattern Analysis")
    logger.info("=" * 50)
    
    # County-level statistics
    county_stats = df.group_by("County").agg([
        pl.col("Monthly_Temperature_C").mean().alias("Avg_Temperature"),
        pl.col("Monthly_Precipitation_mm").mean().alias("Avg_Precipitation"),
        pl.col("Monthly_Water_Stress_Index").mean().alias("Avg_Water_Stress"),
        pl.col("Water_Scarcity_Score").mean().alias("Avg_Water_Scarcity_Score"),
        pl.col("Agricultural_Risk_Index").mean().alias("Avg_Agricultural_Risk"),
        pl.col("Monthly_Heat_Stress_Days").mean().alias("Avg_Heat_Stress_Days")
    ]).sort("Avg_Water_Scarcity_Score", descending=True)
    
    logger.info(f"\n🏆 Counties by Water Scarcity (Highest to Lowest):")
    for i, row in enumerate(county_stats.iter_rows(named=True)):
        county = row["County"]
        scarcity = row["Avg_Water_Scarcity_Score"]
        temp = row["Avg_Temperature"]
        precip = row["Avg_Precipitation"]
        stress = row["Avg_Water_Stress"]
        risk = row["Avg_Agricultural_Risk"]
        
        rank_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
        logger.info(f"  {rank_icon} {county:20s}: Scarcity={scarcity:5.1f}, "
                   f"Temp={temp:5.1f}°C, Precip={precip:6.1f}mm, "
                   f"Stress={stress:5.3f}, Risk={risk:5.1f}")

def analyze_correlations(df):
    """Analyze correlations between key variables."""
    logger.info("\n🔗 Correlation Analysis")
    logger.info("=" * 50)
    
    # Key variables for correlation analysis
    correlation_vars = [
        'Monthly_Temperature_C', 'Monthly_Precipitation_mm', 'Monthly_Water_Stress_Index',
        'Monthly_Evapotranspiration_mm', 'Water_Scarcity_Score', 'Agricultural_Risk_Index',
        'Irrigation_Priority_Score', 'Monthly_Heat_Stress_Days'
    ]
    
    # Filter to existing columns
    existing_vars = [col for col in correlation_vars if col in df.columns]
    
    if len(existing_vars) >= 2:
        # Create correlation matrix
        corr_data = df.select(existing_vars).drop_nulls()
        
        if len(corr_data) > 0:
            logger.info(f"\n📊 Correlation Matrix (Top 10 strongest correlations):")
            
            # Calculate correlations
            correlations = []
            for i, var1 in enumerate(existing_vars):
                for j, var2 in enumerate(existing_vars):
                    if i < j:  # Avoid duplicates
                        corr = float(corr_data.select(pl.corr(var1, var2)).item())
                        correlations.append((var1, var2, corr))
            
            # Sort by absolute correlation strength
            correlations.sort(key=lambda x: abs(x[2]), reverse=True)
            
            # Display top correlations
            for i, (var1, var2, corr) in enumerate(correlations[:10]):
                strength = "Strong" if abs(corr) > 0.7 else "Moderate" if abs(corr) > 0.4 else "Weak"
                direction = "Positive" if corr > 0 else "Negative"
                logger.info(f"  {i+1:2d}. {var1:25s} ↔ {var2:25s}: {corr:6.3f} ({strength} {direction})")

def analyze_outliers_and_anomalies(df):
    """Analyze outliers and anomalies in the data."""
    logger.info("\n🚨 Outlier and Anomaly Analysis")
    logger.info("=" * 50)
    
    # Key numeric columns to check for outliers
    outlier_cols = [
        'Monthly_Temperature_C', 'Monthly_Precipitation_mm', 'Monthly_Water_Stress_Index',
        'Water_Scarcity_Score', 'Agricultural_Risk_Index'
    ]
    
    existing_cols = [col for col in outlier_cols if col in df.columns]
    
    for col in existing_cols:
        col_data = df[col].drop_nulls()
        if len(col_data) > 0:
            Q1 = float(col_data.quantile(0.25))
            Q3 = float(col_data.quantile(0.75))
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = col_data.filter((col_data < lower_bound) | (col_data > upper_bound))
            
            if len(outliers) > 0:
                logger.info(f"\n⚠️  {col}:")
                logger.info(f"    Q1: {Q1:.2f}, Q3: {Q3:.2f}, IQR: {IQR:.2f}")
                logger.info(f"    Bounds: [{lower_bound:.2f}, {upper_bound:.2f}]")
                logger.info(f"    Outliers: {len(outliers):,} ({len(outliers)/len(col_data)*100:.1f}%)")
                logger.info(f"    Outlier range: [{float(outliers.min()):.2f}, {float(outliers.max()):.2f}]")
            else:
                logger.info(f"✅ {col}: No outliers detected")

def generate_insights_and_recommendations(df):
    """Generate key insights and recommendations based on the EDA."""
    logger.info("\n💡 Key Insights and Recommendations")
    logger.info("=" * 50)
    
    # Calculate overall statistics
    total_counties = df['County'].unique().count()
    total_years = df['Year'].unique().count()
    total_months = df['Month'].unique().count()
    
    # Water scarcity insights
    avg_scarcity = df['Water_Scarcity_Score'].mean()
    high_scarcity_counties = df.filter(pl.col('Water_Scarcity_Score') > 70)['County'].unique().count()
    
    # Agricultural risk insights
    avg_risk = df['Agricultural_Risk_Index'].mean()
    high_risk_counties = df.filter(pl.col('Agricultural_Risk_Index') > 70)['County'].unique().count()
    
    # Temperature insights
    avg_temp = df['Monthly_Temperature_C'].mean()
    temp_range = df['Monthly_Temperature_C'].max() - df['Monthly_Temperature_C'].min()
    
    # Precipitation insights
    avg_precip = df['Monthly_Precipitation_mm'].mean()
    dry_months = df.filter(pl.col('Monthly_Precipitation_mm') < 50)['Month'].unique().count()
    
    logger.info(f"\n🎯 Overall Dataset Insights:")
    logger.info(f"  • Comprehensive coverage: {total_counties} counties × {total_years} years × {total_months} months")
    logger.info(f"  • Average water scarcity score: {avg_scarcity:.1f}/100")
    logger.info(f"  • Counties with high water scarcity (>70): {high_scarcity_counties}")
    logger.info(f"  • Average agricultural risk: {avg_risk:.1f}/100")
    logger.info(f"  • Counties with high agricultural risk (>70): {high_risk_counties}")
    logger.info(f"  • Average temperature: {avg_temp:.1f}°C (range: {temp_range:.1f}°C)")
    logger.info(f"  • Average precipitation: {avg_precip:.1f}mm/month")
    logger.info(f"  • Dry months (<50mm): {dry_months} out of {total_months}")
    
    logger.info(f"\n🚨 Critical Findings:")
    
    # Identify most vulnerable counties
    vulnerable_counties = df.group_by("County").agg([
        pl.col("Water_Scarcity_Score").mean().alias("Avg_Scarcity"),
        pl.col("Agricultural_Risk_Index").mean().alias("Avg_Risk")
    ]).filter(
        (pl.col("Avg_Scarcity") > 70) | (pl.col("Avg_Risk") > 70)
    ).sort("Avg_Scarcity", descending=True)
    
    if len(vulnerable_counties) > 0:
        logger.info(f"  • Most vulnerable counties (high scarcity/risk):")
        for row in vulnerable_counties.head(5).iter_rows(named=True):
            county = row["County"]
            scarcity = row["Avg_Scarcity"]
            risk = row["Avg_Risk"]
            logger.info(f"    - {county}: Scarcity={scarcity:.1f}, Risk={risk:.1f}")
    
    logger.info(f"\n💡 Recommendations for Dashboard:")
    logger.info(f"  • Focus on counties with water scarcity scores >70")
    logger.info(f"  • Highlight seasonal patterns (dry vs. wet months)")
    logger.info(f"  • Monitor counties with high agricultural risk")
    logger.info(f"  • Include temperature and precipitation trend analysis")
    logger.info(f"  • Provide irrigation recommendations based on water stress")

def create_visualizations(df):
    """Create key visualizations for the EDA."""
    logger.info("\n📊 Creating Visualizations")
    logger.info("=" * 50)
    
    # Create output directory
    output_dir = Path("reports/eda_visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up the plotting
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Water Scarcity Dashboard - Key Insights', fontsize=16, fontweight='bold')
    
    # 1. Water Scarcity Score by County
    county_scarcity = df.group_by("County").agg([
        pl.col("Water_Scarcity_Score").mean().alias("Avg_Scarcity")
    ]).sort("Avg_Scarcity", descending=True)
    
    counties = county_scarcity["County"].to_list()
    scarcity_scores = county_scarcity["Avg_Scarcity"].to_list()
    
    axes[0, 0].barh(counties, scarcity_scores, color='coral')
    axes[0, 0].set_title('Average Water Scarcity Score by County')
    axes[0, 0].set_xlabel('Water Scarcity Score (0-100)')
    axes[0, 0].set_ylabel('County')
    
    # 2. Monthly Temperature Patterns
    monthly_temp = df.group_by("Month").agg([
        pl.col("Monthly_Temperature_C").mean().alias("Avg_Temperature")
    ]).sort("Month")
    
    months = monthly_temp["Month"].to_list()
    temps = monthly_temp["Avg_Temperature"].to_list()
    
    axes[0, 1].plot(months, temps, marker='o', linewidth=2, color='red')
    axes[0, 1].set_title('Monthly Temperature Patterns')
    axes[0, 1].set_xlabel('Month')
    axes[0, 1].set_ylabel('Temperature (°C)')
    axes[0, 1].set_xticks(range(1, 13))
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Monthly Precipitation Patterns
    monthly_precip = df.group_by("Month").agg([
        pl.col("Monthly_Precipitation_mm").mean().alias("Avg_Precipitation")
    ]).sort("Month")
    
    precip = monthly_precip["Avg_Precipitation"].to_list()
    
    axes[1, 0].bar(months, precip, color='skyblue', alpha=0.7)
    axes[1, 0].set_title('Monthly Precipitation Patterns')
    axes[1, 0].set_xlabel('Month')
    axes[1, 0].set_ylabel('Precipitation (mm)')
    axes[1, 0].set_xticks(range(1, 13))
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Water Scarcity vs Agricultural Risk
    county_risk = df.group_by("County").agg([
        pl.col("Water_Scarcity_Score").mean().alias("Avg_Scarcity"),
        pl.col("Agricultural_Risk_Index").mean().alias("Avg_Risk")
    ])
    
    scarcity = county_risk["Avg_Scarcity"].to_list()
    risk = county_risk["Avg_Risk"].to_list()
    
    axes[1, 1].scatter(scarcity, risk, alpha=0.7, s=100)
    axes[1, 1].set_title('Water Scarcity vs Agricultural Risk')
    axes[1, 1].set_xlabel('Water Scarcity Score')
    axes[1, 1].set_ylabel('Agricultural Risk Index')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Add county labels to scatter plot
    for i, county in enumerate(county_risk["County"].to_list()):
        axes[1, 1].annotate(county, (scarcity[i], risk[i]), 
                           xytext=(5, 5), textcoords='offset points', 
                           fontsize=8, alpha=0.8)
    
    plt.tight_layout()
    plt.savefig(output_dir / "key_insights.png", dpi=300, bbox_inches='tight')
    logger.info(f"✅ Visualizations saved to: {output_dir}")
    
    plt.close()

def main():
    """Main EDA function."""
    logger.info("🔍 EXPLORATORY DATA ANALYSIS STARTING")
    logger.info("=" * 60)
    
    # Load data
    df = load_and_examine_data()
    if df is None:
        return
    
    # Perform comprehensive EDA
    analyze_data_structure(df)
    analyze_numeric_distributions(df)
    analyze_temporal_patterns(df)
    analyze_spatial_patterns(df)
    analyze_correlations(df)
    analyze_outliers_and_anomalies(df)
    generate_insights_and_recommendations(df)
    
    # Create visualizations
    create_visualizations(df)
    
    # Save EDA summary
    output_file = Path("reports/eda_summary.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("# Water Scarcity Dashboard - EDA Summary\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Dataset Overview\n\n")
        f.write(f"- **Total Records:** {len(df):,}\n")
        f.write(f"- **Counties:** {df['County'].unique().count()}\n")
        f.write(f"- **Years:** {df['Year'].min()} - {df['Year'].max()}\n")
        f.write(f"- **Months:** {df['Month'].min()} - {df['Month'].max()}\n")
        f.write(f"- **Columns:** {len(df.columns)}\n\n")
        f.write("## Key Findings\n\n")
        f.write("### Water Scarcity Patterns\n")
        f.write("- Counties with highest water scarcity scores\n")
        f.write("- Seasonal variations in water stress\n")
        f.write("- Correlation with temperature and precipitation\n\n")
        f.write("### Agricultural Risk Assessment\n")
        f.write("- Counties with highest agricultural risk\n")
        f.write("- Relationship between water scarcity and crop risk\n")
        f.write("- Seasonal risk patterns\n\n")
        f.write("### Recommendations\n")
        f.write("- Focus on high-risk counties\n")
        f.write("- Monitor seasonal patterns\n")
        f.write("- Implement targeted interventions\n\n")
    
    logger.info(f"\n📋 EDA Summary saved to: {output_file}")
    logger.info("\n🎉 EXPLORATORY DATA ANALYSIS COMPLETE!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
