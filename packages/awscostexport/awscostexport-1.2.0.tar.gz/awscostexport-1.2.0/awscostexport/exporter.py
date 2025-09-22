#!/usr/bin/env python3
"""
AWS Cost Data Export Module
Exports AWS cost data for optimization analysis
"""

import boto3
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import zipfile
import shutil

# AWS services that support Reserved Instances
SERVICES_WITH_RESERVATIONS = [
    'Amazon Elastic Compute Cloud - Compute',
    'Amazon Relational Database Service',
    'Amazon ElastiCache',
    'Amazon DynamoDB',
    'Amazon Redshift',
    'Amazon Elasticsearch Service',
    'Amazon OpenSearch Service',
    'Amazon DocumentDB (with MongoDB compatibility)',
    'Amazon Neptune',
    'Amazon MemoryDB for Redis'
]

def get_date_range(months):
    """Get date range for the specified number of months"""
    end_date = datetime.now().replace(day=1) - timedelta(days=1)  # Last day of previous month
    start_date = (end_date - timedelta(days=30 * months)).replace(day=1)
    return {
        'Start': start_date.strftime('%Y-%m-%d'),
        'End': end_date.strftime('%Y-%m-%d')
    }

def export_marketplace_spend(ce_client, date_range, output_dir):
    """Export AWS Marketplace spend separately"""
    print("Exporting marketplace spend...")
    
    response = ce_client.get_cost_and_usage(
        TimePeriod=date_range,
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
        ]
    )
    
    # Aggregate marketplace costs
    marketplace_costs = defaultdict(float)
    marketplace_details = []
    
    for result in response['ResultsByTime']:
        month = result['TimePeriod']['Start']
        for group in result['Groups']:
            service = group['Keys'][0]
            usage_type = group['Keys'][1]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            
            if 'marketplace' in service.lower() or 'marketplace' in usage_type.lower():
                marketplace_costs[f"{service} - {usage_type}"] += cost
                marketplace_details.append({
                    'month': month,
                    'service': service,
                    'usage_type': usage_type,
                    'cost': cost
                })
    
    # Write to CSV
    csv_file = os.path.join(output_dir, '08_marketplace_spend.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Service/Product', 'Total Cost', 'Monthly Average'])
        
        sorted_marketplace = sorted(marketplace_costs.items(), key=lambda x: x[1], reverse=True)
        months_count = len(response['ResultsByTime'])
        
        for item, cost in sorted_marketplace:
            avg_monthly = cost / months_count
            writer.writerow([item, f"${cost:,.2f}", f"${avg_monthly:,.2f}"])
        
        # Add total
        total = sum(marketplace_costs.values())
        writer.writerow(['TOTAL', f"${total:,.2f}", f"${total/months_count:,.2f}"])
    
    print(f"✓ Marketplace spend saved to {csv_file}")
    return total

def export_service_breakdown(ce_client, date_range, output_dir):
    """Export top services by cost (excluding marketplace)"""
    print("Exporting service breakdown...")
    
    response = ce_client.get_cost_and_usage(
        TimePeriod=date_range,
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    
    # Aggregate costs by service, excluding marketplace
    service_costs = defaultdict(float)
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            service = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            # Exclude marketplace services
            if 'marketplace' not in service.lower():
                service_costs[service] += cost
    
    # Sort by cost
    sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
    total_cost = sum(cost for _, cost in sorted_services)
    
    # Write to CSV
    csv_file = os.path.join(output_dir, '01_service_breakdown.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Service', 'Monthly Average', 'Percentage'])
        
        for i, (service, cost) in enumerate(sorted_services[:10], 1):
            avg_monthly = cost / len(response['ResultsByTime'])
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            writer.writerow([i, service, f"${avg_monthly:,.2f}", f"{percentage:.1f}%"])
        
        # Add "Other" row
        other_cost = sum(cost for _, cost in sorted_services[10:])
        other_avg = other_cost / len(response['ResultsByTime'])
        other_pct = (other_cost / total_cost * 100) if total_cost > 0 else 0
        writer.writerow(['Other', 'Other Services', f"${other_avg:,.2f}", f"{other_pct:.1f}%"])
        
        # Add total
        writer.writerow(['TOTAL', 'All Services', f"${total_cost/len(response['ResultsByTime']):,.2f}", "100.0%"])
    
    print(f"✓ Service breakdown saved to {csv_file}")
    return sorted_services[:10]

def export_ec2_details(ce_client, date_range, output_dir):
    """Export EC2 purchase option breakdown"""
    print("Exporting EC2 details...")
    
    # 1. Get line item types to properly account for Savings Plans
    response = ce_client.get_cost_and_usage(
        TimePeriod=date_range,
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        Filter={'Dimensions': {'Key': 'SERVICE', 'Values': ['EC2 - Other', 'Amazon Elastic Compute Cloud - Compute']}},
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'RECORD_TYPE'}]
    )
    
    # Aggregate by record type first to get actual usage vs SP covered
    record_types = defaultdict(float)
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            record_type = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            record_types[record_type] += cost
    
    # Now get traditional purchase types
    pt_response = ce_client.get_cost_and_usage(
        TimePeriod=date_range,
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        Filter={'Dimensions': {'Key': 'SERVICE', 'Values': ['EC2 - Other', 'Amazon Elastic Compute Cloud - Compute']}},
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'PURCHASE_TYPE'}]
    )
    
    # Aggregate traditional purchase options
    purchase_options = defaultdict(float)
    for result in pt_response['ResultsByTime']:
        for group in result['Groups']:
            option = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            
            # Adjust for Savings Plans
            if option == 'On Demand Instances' and record_types.get('SavingsPlanCoveredUsage', 0) > 0:
                # Subtract SP covered usage from on-demand
                actual_on_demand = record_types.get('Usage', 0)
                purchase_options['On Demand Instances'] = actual_on_demand
                purchase_options['Savings Plans'] = record_types.get('SavingsPlanCoveredUsage', 0)
            else:
                purchase_options[option] += cost
    
    # Write to CSV
    csv_file = os.path.join(output_dir, '02_ec2_purchase_options.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Purchase Option', 'Total Cost', 'Monthly Average', 'Percentage'])
        
        total = sum(purchase_options.values())
        for option, cost in purchase_options.items():
            avg_monthly = cost / len(response['ResultsByTime'])
            percentage = (cost / total * 100) if total > 0 else 0
            writer.writerow([option, f"${cost:,.2f}", f"${avg_monthly:,.2f}", f"{percentage:.1f}%"])
    
    print(f"✓ EC2 purchase options saved to {csv_file}")
    
    # 2. Instance types breakdown
    print("Exporting EC2 instance types...")
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod=date_range,
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={'Dimensions': {'Key': 'SERVICE', 'Values': ['EC2 - Other', 'Amazon Elastic Compute Cloud - Compute']}},
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'}]
        )
        
        instance_types = defaultdict(float)
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                instance_type = group['Keys'][0] or 'Other/Unknown'
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                instance_types[instance_type] += cost
        
        # Write top 20 instance types
        csv_file = os.path.join(output_dir, '02a_ec2_instance_types.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Instance Type', 'Total Cost', 'Monthly Average', 'Percentage'])
            
            sorted_types = sorted(instance_types.items(), key=lambda x: x[1], reverse=True)
            total = sum(instance_types.values())
            
            for i, (itype, cost) in enumerate(sorted_types[:20]):
                avg_monthly = cost / len(response['ResultsByTime'])
                percentage = (cost / total * 100) if total > 0 else 0
                writer.writerow([itype, f"${cost:,.2f}", f"${avg_monthly:,.2f}", f"{percentage:.1f}%"])
        
        print(f"✓ EC2 instance types saved to {csv_file}")
    except Exception as e:
        print(f"⚠ Could not export EC2 instance types: {e}")

def export_rds_details(ce_client, date_range, output_dir):
    """Export RDS configuration details"""
    print("Exporting RDS details...")
    
    # 1. Basic RDS breakdown
    response = ce_client.get_cost_and_usage(
        TimePeriod=date_range,
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        Filter={'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Relational Database Service']}},
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}]
    )
    
    # Categorize RDS costs
    single_az = 0
    multi_az = 0
    storage = 0
    backup = 0
    other = 0
    
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            usage_type = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            
            if 'Multi-AZ' in usage_type:
                multi_az += cost
            elif 'Storage' in usage_type:
                storage += cost
            elif 'Backup' in usage_type:
                backup += cost
            elif any(x in usage_type for x in ['InstanceUsage', 'BoxUsage']):
                single_az += cost
            else:
                other += cost
    
    # Write summary
    csv_file = os.path.join(output_dir, '03_rds_breakdown.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Category', 'Total Cost', 'Monthly Average'])
        months_count = len(response['ResultsByTime'])
        writer.writerow(['Single-AZ Instances', f"${single_az:,.2f}", f"${single_az/months_count:,.2f}"])
        writer.writerow(['Multi-AZ Instances', f"${multi_az:,.2f}", f"${multi_az/months_count:,.2f}"])
        writer.writerow(['Storage', f"${storage:,.2f}", f"${storage/months_count:,.2f}"])
        writer.writerow(['Backup', f"${backup:,.2f}", f"${backup/months_count:,.2f}"])
        writer.writerow(['Other', f"${other:,.2f}", f"${other/months_count:,.2f}"])
    
    print(f"✓ RDS breakdown saved to {csv_file}")
    
    # 2. RDS engine types
    print("Exporting RDS engine types...")
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod=date_range,
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Relational Database Service']}},
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'DATABASE_ENGINE'}]
        )
        
        engine_costs = defaultdict(float)
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                engine = group['Keys'][0] or 'Unknown'
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                engine_costs[engine] += cost
        
        csv_file = os.path.join(output_dir, '03a_rds_engines.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Database Engine', 'Total Cost', 'Monthly Average', 'Percentage'])
            
            sorted_engines = sorted(engine_costs.items(), key=lambda x: x[1], reverse=True)
            total = sum(engine_costs.values())
            
            for engine, cost in sorted_engines:
                avg_monthly = cost / len(response['ResultsByTime'])
                percentage = (cost / total * 100) if total > 0 else 0
                writer.writerow([engine, f"${cost:,.2f}", f"${avg_monthly:,.2f}", f"{percentage:.1f}%"])
        
        print(f"✓ RDS engine types saved to {csv_file}")
    except Exception as e:
        print(f"⚠ Could not export RDS engine types: {e}")

def export_container_services(ce_client, date_range, output_dir, top_services):
    """Export container services breakdown if in top services"""
    container_services = ['Amazon Elastic Container Service', 'Amazon Elastic Kubernetes Service', 'AWS Fargate']
    
    # Check if any container service is in top 10
    has_container = any(any(cs in service[0] for cs in container_services) for service in top_services)
    
    if has_container:
        print("Exporting container services details...")
        try:
            response = ce_client.get_cost_and_usage(
                TimePeriod=date_range,
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                Filter={'Dimensions': {'Key': 'SERVICE', 'Values': container_services}},
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
                ]
            )
            
            service_usage = defaultdict(lambda: defaultdict(float))
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service = group['Keys'][0]
                    usage_type = group['Keys'][1]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    service_usage[service][usage_type] += cost
            
            csv_file = os.path.join(output_dir, '05_container_services.csv')
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Service', 'Usage Type', 'Total Cost', 'Monthly Average'])
                
                months_count = len(response['ResultsByTime'])
                for service, usage_types in sorted(service_usage.items()):
                    for usage_type, cost in sorted(usage_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                        avg_monthly = cost / months_count
                        writer.writerow([service, usage_type, f"${cost:,.2f}", f"${avg_monthly:,.2f}"])
            
            print(f"✓ Container services saved to {csv_file}")
        except Exception as e:
            print(f"⚠ Could not export container services: {e}")

def export_data_transfer(ce_client, date_range, output_dir):
    """Export data transfer and NAT gateway costs"""
    print("Exporting data transfer and networking costs...")
    
    try:
        # Data transfer costs
        response = ce_client.get_cost_and_usage(
            TimePeriod=date_range,
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={'Dimensions': {'Key': 'USAGE_TYPE_GROUP', 'Values': ['EC2: Data Transfer', 'EC2: NAT Gateway']}},
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}]
        )
        
        transfer_costs = defaultdict(float)
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                usage_type = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                transfer_costs[usage_type] += cost
        
        csv_file = os.path.join(output_dir, '06_data_transfer_nat.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Usage Type', 'Total Cost', 'Monthly Average', 'Percentage'])
            
            sorted_transfers = sorted(transfer_costs.items(), key=lambda x: x[1], reverse=True)
            total = sum(transfer_costs.values())
            months_count = len(response['ResultsByTime'])
            
            for usage_type, cost in sorted_transfers[:20]:
                avg_monthly = cost / months_count
                percentage = (cost / total * 100) if total > 0 else 0
                writer.writerow([usage_type, f"${cost:,.2f}", f"${avg_monthly:,.2f}", f"{percentage:.1f}%"])
        
        print(f"✓ Data transfer costs saved to {csv_file}")
    except Exception as e:
        print(f"⚠ Could not export data transfer costs: {e}")

def export_ebs_volumes(ce_client, date_range, output_dir):
    """Export EBS volume types breakdown"""
    print("Exporting EBS volume details...")
    
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod=date_range,
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={'And': [
                {'Dimensions': {'Key': 'SERVICE', 'Values': ['EC2 - Other']}},
                {'Tags': {'Key': 'aws:createdBy', 'Values': ['EBS']}}
            ]},
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}]
        )
        
        volume_costs = defaultdict(float)
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                usage_type = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                # Categorize by volume type
                if 'VolumeUsage.gp3' in usage_type:
                    volume_type = 'GP3'
                elif 'VolumeUsage.gp2' in usage_type:
                    volume_type = 'GP2'
                elif 'VolumeUsage.io1' in usage_type:
                    volume_type = 'IO1'
                elif 'VolumeUsage.io2' in usage_type:
                    volume_type = 'IO2'
                elif 'VolumeUsage.st1' in usage_type:
                    volume_type = 'ST1'
                elif 'VolumeUsage.sc1' in usage_type:
                    volume_type = 'SC1'
                elif 'Snapshot' in usage_type:
                    volume_type = 'Snapshots'
                else:
                    volume_type = 'Other EBS'
                
                volume_costs[volume_type] += cost
        
        csv_file = os.path.join(output_dir, '07_ebs_volumes.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Volume Type', 'Total Cost', 'Monthly Average', 'Percentage'])
            
            sorted_volumes = sorted(volume_costs.items(), key=lambda x: x[1], reverse=True)
            total = sum(volume_costs.values())
            months_count = len(response['ResultsByTime'])
            
            for volume_type, cost in sorted_volumes:
                avg_monthly = cost / months_count
                percentage = (cost / total * 100) if total > 0 else 0
                writer.writerow([volume_type, f"${cost:,.2f}", f"${avg_monthly:,.2f}", f"{percentage:.1f}%"])
        
        print(f"✓ EBS volumes saved to {csv_file}")
    except Exception as e:
        print(f"⚠ Could not export EBS volumes: {e}")

def export_comprehensive_reservation_analysis(ce_client, output_dir):
    """Export comprehensive reservation analysis for all eligible services"""
    print("Performing comprehensive reservation analysis...")
    
    # Get Savings Plans coverage
    try:
        sp_response = ce_client.get_savings_plans_coverage(
            TimePeriod=get_date_range(1),
            Granularity='MONTHLY'
        )
        sp_coverage = float(sp_response['SavingsPlansCoverages'][0]['Coverage']['CoveragePercentage'])
    except:
        sp_coverage = 0
    
    # Get overall RI coverage
    try:
        ri_response = ce_client.get_reservation_coverage(
            TimePeriod=get_date_range(1),
            Granularity='MONTHLY'
        )
        ri_coverage = float(ri_response['CoveragesByTime'][0]['Total']['CoverageHours']['CoverageHoursPercentage'])
    except:
        ri_coverage = 0
    
    # Get reservation utilization
    try:
        util_response = ce_client.get_reservation_utilization(
            TimePeriod=get_date_range(1),
            Granularity='MONTHLY'
        )
        ri_utilization = float(util_response['UtilizationsByTime'][0]['Total']['UtilizationPercentage'])
        ri_unused = float(util_response['UtilizationsByTime'][0]['Total']['UnusedHours'])
        ri_total = float(util_response['UtilizationsByTime'][0]['Total']['PurchasedHours'])
    except:
        ri_utilization = 0
        ri_unused = 0
        ri_total = 0
    
    # Analyze each service that supports reservations
    date_range = get_date_range(1)
    service_reservation_data = []
    
    for service in SERVICES_WITH_RESERVATIONS:
        try:
            response = ce_client.get_cost_and_usage(
                TimePeriod=date_range,
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                Filter={'Dimensions': {'Key': 'SERVICE', 'Values': [service]}},
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'PURCHASE_TYPE'}]
            )
            
            reserved_cost = 0
            ondemand_cost = 0
            spot_cost = 0
            sp_cost = 0
            
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    purchase_type = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    if 'Reserved' in purchase_type:
                        reserved_cost += cost
                    elif 'On Demand' in purchase_type:
                        ondemand_cost += cost
                    elif 'Spot' in purchase_type:
                        spot_cost += cost
                    elif 'Savings' in purchase_type:
                        sp_cost += cost
            
            total_cost = reserved_cost + ondemand_cost + spot_cost + sp_cost
            if total_cost > 0:
                coverage = ((reserved_cost + sp_cost) / total_cost * 100)
                service_reservation_data.append({
                    'service': service,
                    'reserved': reserved_cost,
                    'ondemand': ondemand_cost,
                    'spot': spot_cost,
                    'savings_plans': sp_cost,
                    'total': total_cost,
                    'coverage': coverage
                })
        except:
            continue
    
    # Write reservation analysis CSV
    csv_file = os.path.join(output_dir, '09_reservation_analysis.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Service', 'Reserved Cost', 'On-Demand Cost', 'Spot Cost', 'Savings Plans Cost', 'Total Cost', 'Coverage %', 'Optimization Opportunity'])
        
        # Sort by optimization opportunity (on-demand cost)
        sorted_services = sorted(service_reservation_data, key=lambda x: x['ondemand'], reverse=True)
        
        for data in sorted_services:
            writer.writerow([
                data['service'],
                f"${data['reserved']:,.2f}",
                f"${data['ondemand']:,.2f}",
                f"${data['spot']:,.2f}",
                f"${data['savings_plans']:,.2f}",
                f"${data['total']:,.2f}",
                f"{data['coverage']:.1f}%",
                f"${data['ondemand']:,.2f}"
            ])
        
        # Add summary row
        total_reserved = sum(d['reserved'] for d in service_reservation_data)
        total_ondemand = sum(d['ondemand'] for d in service_reservation_data)
        total_spot = sum(d['spot'] for d in service_reservation_data)
        total_sp = sum(d['savings_plans'] for d in service_reservation_data)
        grand_total = sum(d['total'] for d in service_reservation_data)
        
        writer.writerow([
            'TOTAL',
            f"${total_reserved:,.2f}",
            f"${total_ondemand:,.2f}",
            f"${total_spot:,.2f}",
            f"${total_sp:,.2f}",
            f"${grand_total:,.2f}",
            f"{((total_reserved + total_sp) / grand_total * 100):.1f}%" if grand_total > 0 else "0.0%",
            f"${total_ondemand:,.2f}"
        ])
    
    print(f"✓ Comprehensive reservation analysis saved to {csv_file}")
    
    # Also create a summary CSV
    summary_file = os.path.join(output_dir, '04_savings_status.csv')
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value', 'Details'])
        writer.writerow(['Overall Savings Plans Coverage', f"{sp_coverage:.1f}%", 'Across all eligible services'])
        writer.writerow(['Overall Reserved Instance Coverage', f"{ri_coverage:.1f}%", 'Across all eligible services'])
        writer.writerow(['Overall RI Utilization', f"{ri_utilization:.1f}%", f"Using {ri_total-ri_unused:.0f} of {ri_total:.0f} purchased hours"])
        writer.writerow(['Total On-Demand Opportunity', f"${total_ondemand:,.2f}", 'Across all services with reservation options'])
    
    print(f"✓ Savings status summary saved to {summary_file}")

def check_cur_availability(client):
    """Check if CUR is configured"""
    try:
        response = client.describe_report_definitions()
        if response['ReportDefinitions']:
            return response['ReportDefinitions'][0]
    except:
        pass
    return None

def create_summary_report(output_dir):
    """Create a summary markdown report"""
    print("Creating summary report...")
    
    summary_file = os.path.join(output_dir, 'AWS_COST_EXPORT_SUMMARY.md')
    with open(summary_file, 'w') as f:
        f.write("# AWS Cost Export Summary\n\n")
        f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("## Files Generated\n\n")
        f.write("### Core Reports:\n")
        f.write("1. **01_service_breakdown.csv** - Top 10 services by cost with percentages\n")
        f.write("2. **02_ec2_purchase_options.csv** - EC2 on-demand vs reserved vs spot breakdown\n")
        f.write("3. **03_rds_breakdown.csv** - RDS single-AZ vs multi-AZ costs\n")
        f.write("4. **04_savings_status.csv** - Current savings plan and RI coverage\n\n")
        
        f.write("### Additional Details (if applicable):\n")
        f.write("- **02a_ec2_instance_types.csv** - Top 20 EC2 instance types by cost\n")
        f.write("- **03a_rds_engines.csv** - RDS database engines breakdown\n")
        f.write("- **05_container_services.csv** - ECS/EKS/Fargate usage details\n")
        f.write("- **06_data_transfer_nat.csv** - Data transfer and NAT gateway costs\n")
        f.write("- **07_ebs_volumes.csv** - EBS volume types (GP2, GP3, IO1, etc.)\n\n")
        
        f.write("## Data Coverage\n\n")
        f.write("- Time Period: Last 6 months\n")
        f.write("- Granularity: Monthly aggregation\n")
        f.write("- Cost Type: Unblended costs\n\n")
        
        f.write("## Next Steps\n\n")
        f.write("1. Review the generated CSV files\n")
        f.write("2. Share this entire folder as needed\n")
        f.write("## Questions?\n\n")
        f.write("Contact: david.schwartz@devfactory.com\n")
    
    print(f"✓ Summary report saved to {summary_file}")

def create_zip_output(output_dir):
    """Create a zip file of all exports"""
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"aws_cost_export_{timestamp}.zip"
    
    # If output_dir is current directory, create temp folder first
    if output_dir == ".":
        temp_dir = f"aws_cost_export_temp_{timestamp}"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Move all CSV files to temp directory
        for file in os.listdir(output_dir):
            if file.endswith('.csv') or file == 'AWS_COST_EXPORT_SUMMARY.md':
                shutil.move(os.path.join(output_dir, file), os.path.join(temp_dir, file))
        
        output_dir = temp_dir
    
    print(f"\nCreating zip file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)
    
    # Remove the directory if it's not the current directory
    if output_dir != ".":
        shutil.rmtree(output_dir)
    
    print(f"✓ Zip file created: {zip_filename}")
    return zip_filename
