#!/usr/bin/env python3
"""
Analyze ISRIC Soil Data to understand data availability and gaps
"""

import polars as pl
import numpy as np
from pathlib import Path

def analyze_isric_data():
    """Analyze the ISRIC soil properties data"""
    print("🔍 Analyzing ISRIC Soil Properties Data")
    print("=" * 50)
    
    # Read the ISRIC data
    isric_path = "data/processed/kenya_soil_properties_isric.csv"
    
    if not Path(isric_path).exists():
        print(f"❌ ISRIC data not found: {isric_path}")
        return
    
    df = pl.read_csv(isric_path)
    
    print(f"📊 Dataset Shape: {df.shape}")
    print(f"📋 Columns: {len(df.columns)}")
    print(f"📍 Sample Locations: {len(df)}")
    
    print("\n🔬 Column Analysis:")
    print("-" * 30)
    
    # Analyze each column
    for col in df.columns:
        missing_count = df.select(pl.col(col).null_count()).item()
        missing_pct = (missing_count / len(df)) * 100
        
        if missing_count > 0:
            print(f"❌ {col}: {missing_count} missing ({missing_pct:.1f}%)")
        else:
            print(f"✅ {col}: Complete")
    
    print("\n🗺️ Geographic Coverage Analysis:")
    print("-" * 40)
    
    # Check coordinate coverage
    lat_missing = df.select(pl.col("Latitude").null_count()).item()
    lon_missing = df.select(pl.col("Longitude").null_count()).item()
    
    print(f"Latitude missing: {lat_missing} ({lat_missing/len(df)*100:.1f}%)")
    print(f"Longitude missing: {lon_missing} ({lon_missing/len(df)*100:.1f}%)")
    
    # Check for valid coordinates
    valid_coords = df.filter(
        (pl.col("Latitude").is_not_null()) & 
        (pl.col("Longitude").is_not_null())
    )
    
    print(f"Valid coordinate pairs: {len(valid_coords)}")
    
    if len(valid_coords) > 0:
        print(f"Latitude range: {valid_coords['Latitude'].min():.3f} to {valid_coords['Latitude'].max():.3f}")
        print(f"Longitude range: {valid_coords['Longitude'].min():.3f} to {valid_coords['Longitude'].max():.3f}")
    
    print("\n🧪 Soil Properties Analysis:")
    print("-" * 30)
    
    # Key soil properties
    soil_properties = [
        'pH_H2O', 'pH_KCl', 'Organic_Carbon', 'Total_Nitrogen',
        'Clay', 'Sand', 'Silt', 'CEC', 'CaCO3', 'Bulk_Density'
    ]
    
    for prop in soil_properties:
        if prop in df.columns:
            missing = df.select(pl.col(prop).null_count()).item()
            missing_pct = (missing / len(df)) * 100
            
            if missing > 0:
                print(f"❌ {prop}: {missing} missing ({missing_pct:.1f}%)")
            else:
                print(f"✅ {prop}: Complete")
        else:
            print(f"⚠️  {prop}: Column not found")
    
    print("\n📅 Temporal Coverage:")
    print("-" * 25)
    
    if 'Year' in df.columns:
        year_missing = df.select(pl.col("Year").null_count()).item()
        print(f"Year missing: {year_missing} ({year_missing/len(df)*100:.1f}%)")
        
        if year_missing < len(df):
            years = df.filter(pl.col("Year").is_not_null())['Year'].unique()
            print(f"Available years: {sorted(years)}")
    else:
        print("Year column not found")
    
    print("\n🔍 Data Quality Issues:")
    print("-" * 25)
    
    # Check for placeholder values (simplified approach)
    print("Checking for placeholder values...")
    
    # Check for -9999 values in numeric columns
    for col in df.columns:
        if df[col].dtype in [pl.Float64, pl.Float32, pl.Int64, pl.Int32]:
            try:
                minus_9999_count = df.filter(pl.col(col) == -9999.0).height
                if minus_9999_count > 0:
                    print(f"⚠️  {col}: {minus_9999_count} placeholder values (-9999.0)")
            except:
                pass
    
    print("\n💡 Recommendations:")
    print("-" * 20)
    
    # Generate recommendations based on findings
    total_missing = sum(df.select(pl.col(col).null_count()).item() for col in df.columns)
    total_cells = len(df) * len(df.columns)
    overall_completeness = ((total_cells - total_missing) / total_cells) * 100
    
    print(f"Overall data completeness: {overall_completeness:.1f}%")
    
    if overall_completeness < 90:
        print("🔴 Data quality needs improvement")
        print("   - Consider additional soil sampling")
        print("   - Implement data validation procedures")
        print("   - Review data collection protocols")
    elif overall_completeness < 95:
        print("🟡 Data quality is good but could be improved")
        print("   - Focus on filling critical gaps")
        print("   - Validate existing measurements")
    else:
        print("🟢 Data quality is excellent")
    
    return df

if __name__ == "__main__":
    analyze_isric_data()
