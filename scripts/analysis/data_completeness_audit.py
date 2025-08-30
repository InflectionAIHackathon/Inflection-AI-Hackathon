#!/usr/bin/env python3
"""
Data Completeness Audit Script
Analyzes missing data patterns across all datasets and compares with master dataset
"""

import polars as pl
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

def analyze_dataset_completeness(file_path, dataset_name):
    """Analyze completeness of a single dataset"""
    try:
        if file_path.endswith('.csv'):
            df = pl.read_csv(file_path)
        else:
            print(f"Skipping {file_path} - not a CSV file")
            return None
        
        total_rows = len(df)
        total_cols = len(df.columns)
        
        # Count missing values per column
        missing_counts = []
        for col in df.columns:
            missing_count = df.select(pl.col(col).null_count()).item()
            missing_counts.append(missing_count)
        
        missing_percentages = [(count / total_rows) * 100 for count in missing_counts]
        
        # Create completeness summary
        completeness_data = {
            'dataset_name': dataset_name,
            'file_path': str(file_path),
            'total_rows': total_rows,
            'total_columns': total_cols,
            'overall_completeness': ((total_rows * total_cols - sum(missing_counts)) / (total_rows * total_cols)) * 100,
            'columns': {}
        }
        
        # Analyze each column
        for i, col in enumerate(df.columns):
            missing_count = missing_counts[i]
            missing_pct = missing_percentages[i]
            
            completeness_data['columns'][col] = {
                'missing_count': int(missing_count),
                'missing_percentage': round(missing_pct, 2),
                'completeness': round(100 - missing_pct, 2),
                'data_type': str(df[col].dtype)
            }
        
        return completeness_data
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None

def analyze_master_dataset():
    """Analyze the master integrated dataset"""
    master_path = "data/processed/master_water_scarcity_dataset_realistic.csv"
    
    if not Path(master_path).exists():
        print(f"Master dataset not found: {master_path}")
        return None
    
    print("🔍 Analyzing Master Dataset...")
    master_data = analyze_dataset_completeness(master_path, "Master Integrated Dataset")
    
    if master_data:
        print(f"✅ Master Dataset Analysis Complete")
        print(f"   Shape: {master_data['total_rows']} rows × {master_data['total_columns']} columns")
        print(f"   Overall Completeness: {master_data['overall_completeness']:.1f}%")
        
        # Show columns with missing data
        missing_columns = {col: data for col, data in master_data['columns'].items() 
                          if data['missing_count'] > 0}
        
        if missing_columns:
            print(f"\n   Columns with missing data: {len(missing_columns)}")
            for col, data in sorted(missing_columns.items(), 
                                  key=lambda x: x[1]['missing_percentage'], reverse=True):
                print(f"     {col}: {data['missing_count']} missing ({data['missing_percentage']:.1f}%)")
        else:
            print("   ✅ No missing data found")
    
    return master_data

def analyze_original_datasets():
    """Analyze all original source datasets"""
    print("\n🔍 Analyzing Original Source Datasets...")
    
    datasets_to_analyze = [
        ("data/processed/kenya_soil_properties_isric.csv", "ISRIC Soil Data"),
        ("data/processed/kenya_maize_production.csv", "Maize Production Data"),
        ("data/weather_data/weather_data_baringo.csv", "Baringo Weather Data"),
        ("data/weather_data/weather_data_bungoma.csv", "Bungoma Weather Data"),
        ("data/weather_data/weather_data_kisumu.csv", "Kisumu Weather Data"),
        ("data/weather_data/weather_data_migori.csv", "Migori Weather Data")
    ]
    
    original_datasets = {}
    
    for file_path, dataset_name in datasets_to_analyze:
        if Path(file_path).exists():
            print(f"   Analyzing {dataset_name}...")
            data = analyze_dataset_completeness(file_path, dataset_name)
            if data:
                original_datasets[dataset_name] = data
                print(f"     ✅ {data['overall_completeness']:.1f}% complete")
        else:
            print(f"   ⚠️  File not found: {file_path}")
    
    return original_datasets

def compare_datasets(master_data, original_datasets):
    """Compare master dataset with original sources"""
    print("\n🔍 Comparing Master Dataset with Original Sources...")
    
    if not master_data:
        print("   ❌ Cannot compare - master data not available")
        return
    
    comparison_results = {
        'master_completeness': master_data['overall_completeness'],
        'source_datasets': {},
        'completeness_changes': {},
        'data_loss_analysis': {}
    }
    
    # Analyze each source dataset
    for dataset_name, source_data in original_datasets.items():
        print(f"\n   📊 {dataset_name}:")
        print(f"      Original Completeness: {source_data['overall_completeness']:.1f}%")
        
        # Find corresponding columns in master dataset
        common_columns = set(source_data['columns'].keys()) & set(master_data['columns'].keys())
        
        if common_columns:
            print(f"      Common columns with master: {len(common_columns)}")
            
            # Compare completeness for common columns
            for col in common_columns:
                source_comp = source_data['columns'][col]['completeness']
                master_comp = master_data['columns'][col]['completeness']
                change = master_comp - source_comp
                
                if abs(change) > 0.1:  # Significant change
                    print(f"        {col}: {source_comp:.1f}% → {master_comp:.1f}% ({change:+.1f}%)")
        
        comparison_results['source_datasets'][dataset_name] = {
            'original_completeness': source_data['overall_completeness'],
            'common_columns': len(common_columns),
            'columns': source_data['columns']
        }

def identify_data_gaps(master_data):
    """Identify specific patterns in missing data"""
    print("\n🔍 Identifying Data Gap Patterns...")
    
    if not master_data:
        return
    
    # Load the actual data for pattern analysis
    try:
        df = pl.read_csv("data/processed/master_water_scarcity_dataset_realistic.csv")
        
        # Analyze missing patterns by county
        if 'County' in df.columns:
            print("   📍 Missing Data by County:")
            county_missing = df.group_by('County').agg([
                pl.all().null_count().alias('total_missing'),
                pl.count().alias('total_records')
            ])
            
            for row in county_missing.iter_rows():
                county, missing, total = row
                missing_pct = (missing / (total * len(df.columns))) * 100
                if missing_pct > 5:  # More than 5% missing
                    print(f"     {county}: {missing_pct:.1f}% missing data")
        
        # Analyze missing patterns by time period
        if 'Year' in df.columns and 'Month' in df.columns:
            print("\n   📅 Missing Data by Time Period:")
            time_missing = df.group_by(['Year', 'Month']).agg([
                pl.all().null_count().alias('total_missing'),
                pl.count().alias('total_records')
            ])
            
            for row in time_missing.iter_rows():
                year, month, missing, total = row
                missing_pct = (missing / (total * len(df.columns))) * 100
                if missing_pct > 10:  # More than 10% missing
                    print(f"     {year}-{month:02d}: {missing_pct:.1f}% missing data")
        
        # Analyze specific column patterns
        print("\n   🔬 Specific Column Gap Analysis:")
        for col, data in master_data['columns'].items():
            if data['missing_count'] > 0:
                missing_pct = data['missing_percentage']
                if missing_pct > 20:
                    print(f"     🔴 {col}: {missing_pct:.1f}% missing (CRITICAL)")
                elif missing_pct > 10:
                    print(f"     🟠 {col}: {missing_pct:.1f}% missing (HIGH)")
                elif missing_pct > 5:
                    print(f"     🟡 {col}: {missing_pct:.1f}% missing (MEDIUM)")
                else:
                    print(f"     🟢 {col}: {missing_pct:.1f}% missing (LOW)")
    
    except Exception as e:
        print(f"   ❌ Error analyzing patterns: {e}")

def generate_completeness_report(master_data, original_datasets):
    """Generate comprehensive completeness report"""
    print("\n📋 Generating Completeness Report...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'master_dataset': master_data,
        'source_datasets': original_datasets,
        'summary': {
            'total_datasets_analyzed': len(original_datasets) + 1,
            'master_completeness': master_data['overall_completeness'] if master_data else 0,
            'critical_gaps': [],
            'recommendations': []
        }
    }
    
    # Identify critical gaps
    if master_data:
        for col, data in master_data['columns'].items():
            if data['missing_percentage'] > 20:
                report['summary']['critical_gaps'].append({
                    'column': col,
                    'missing_percentage': data['missing_percentage'],
                    'missing_count': data['missing_count'],
                    'impact': 'CRITICAL'
                })
            elif data['missing_percentage'] > 10:
                report['summary']['critical_gaps'].append({
                    'column': col,
                    'missing_percentage': data['missing_percentage'],
                    'missing_count': data['missing_count'],
                    'impact': 'HIGH'
                })
    
    # Generate recommendations
    if report['summary']['critical_gaps']:
        report['summary']['recommendations'].extend([
            "Immediate laboratory analysis of stored soil samples",
            "Implement statistical imputation for non-critical gaps",
            "Establish data quality monitoring systems",
            "Prioritize data collection in high-gap counties"
        ])
    
    # Save report
    report_path = "data/reports/data_completeness_audit_report.json"
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"   ✅ Report saved to: {report_path}")
    return report

def main():
    """Main analysis function"""
    print("🔍 Multi-Omics Data Completeness Audit")
    print("=" * 50)
    
    # Analyze master dataset
    master_data = analyze_master_dataset()
    
    # Analyze original datasets
    original_datasets = analyze_original_datasets()
    
    # Compare datasets
    compare_datasets(master_data, original_datasets)
    
    # Identify data gaps
    identify_data_gaps(master_data)
    
    # Generate report
    report = generate_completeness_report(master_data, original_datasets)
    
    print("\n🎯 Audit Complete!")
    if master_data:
        print(f"   📊 Master Dataset Completeness: {master_data['overall_completeness']:.1f}%")
        print(f"   🚨 Critical Gaps Identified: {len(report['summary']['critical_gaps'])}")
    else:
        print("   ❌ Master dataset analysis failed")
    print(f"   📋 Detailed Report: data/reports/data_completeness_audit_report.json")

if __name__ == "__main__":
    main()
