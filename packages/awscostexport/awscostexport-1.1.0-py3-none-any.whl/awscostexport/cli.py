#!/usr/bin/env python3
"""
AWS Cost Export CLI - Export comprehensive AWS cost data for analysis and optimization
"""

import click
import os
import sys
from datetime import datetime
from .exporter import (
    get_date_range, export_marketplace_spend, export_service_breakdown,
    export_ec2_details, export_rds_details, export_container_services,
    export_data_transfer, export_ebs_volumes, export_comprehensive_reservation_analysis,
    check_cur_availability, create_summary_report, create_zip_output
)
import boto3

@click.command()
@click.option('--profile', help='AWS profile to use (from ~/.aws/credentials)')
@click.option('--output-dir', help='Output directory name', 
              default=f"aws_cost_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
@click.option('--months', type=int, default=6, help='Number of months to export (default: 6)')
@click.option('--no-zip', is_flag=True, help='Do not create zip file')
@click.version_option()
def cli(profile, output_dir, months, no_zip):
    """Export comprehensive AWS cost data for analysis and optimization.
    
    This tool extracts detailed cost information from AWS Cost Explorer including:
    
    \b
    OUTPUT FILES:
    - 01_service_breakdown.csv     - Top 10 services by cost (marketplace excluded)
    - 02_ec2_purchase_options.csv  - EC2 costs split by On-Demand/Reserved/Spot/SP
    - 02a_ec2_instance_types.csv   - Top 20 EC2 instance types by cost
    - 03_rds_breakdown.csv         - RDS single vs multi-AZ configuration
    - 03a_rds_engines.csv          - Database engines (MySQL, PostgreSQL, Aurora, etc.)
    - 04_savings_status.csv        - Overall Savings Plans & RI coverage metrics
    - 05_container_services.csv    - ECS/EKS/Fargate costs (if in top 10)
    - 06_data_transfer_nat.csv     - Network egress and NAT gateway costs
    - 07_ebs_volumes.csv           - Storage volume types (GP2, GP3, IO1, etc.)
    - 08_marketplace_spend.csv     - AWS Marketplace purchases (separated)
    - 09_reservation_analysis.csv  - Complete RI/SP analysis for ALL services
    
    \b
    AWS CREDENTIALS:
    The tool uses standard AWS credential chain:
    1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    2. AWS credentials file (~/.aws/credentials)
    3. IAM instance profile (if running on EC2)
    4. SSO credentials (aws sso login)
    
    \b
    REQUIRED PERMISSIONS:
    - ce:Get* (Cost Explorer read access)
    - cur:Describe* (optional, for CUR detection)
    
    \b
    EXAMPLES:
    # Use default AWS credentials
    awscostexport
    
    # Use specific profile from ~/.aws/credentials
    awscostexport --profile production
    
    # Export only last 3 months
    awscostexport --months 3
    
    # Keep raw CSV files (no zip)
    awscostexport --no-zip
    
    # Custom output directory
    awscostexport --output-dir my-cost-data
    """
    click.echo(click.style("AWS Cost Export", bold=True))
    click.echo("=" * 50)
    click.echo(f"This tool will export the last {months} months of AWS cost data")
    click.echo("No changes will be made to your AWS account\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize AWS clients
    session_args = {}
    if profile:
        session_args['profile_name'] = profile
    
    try:
        session = boto3.Session(**session_args)
        ce_client = session.client('ce', region_name='us-east-1')
        cur_client = session.client('cur', region_name='us-east-1')
    except Exception as e:
        click.echo(click.style(f"❌ Error initializing AWS session: {e}", fg='red'))
        sys.exit(1)
    
    # Test AWS access
    click.echo("Testing AWS access...")
    try:
        ce_client.get_cost_and_usage(
            TimePeriod=get_date_range(1),
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
        click.echo(click.style("✓ AWS access confirmed\n", fg='green'))
    except Exception as e:
        click.echo(click.style(f"❌ Error accessing AWS: {e}", fg='red'))
        click.echo("\nPlease ensure:")
        click.echo("1. AWS CLI is configured (run 'aws configure')")
        click.echo("2. Your user has Cost Explorer permissions")
        click.echo("3. You're using the correct profile (use --profile flag if needed)")
        sys.exit(1)
    
    # Get date range
    date_range = get_date_range(months)
    click.echo(f"Analyzing costs from {date_range['Start']} to {date_range['End']}\n")
    
    try:
        # Export marketplace spend first (to exclude from main analysis)
        export_marketplace_spend(ce_client, date_range, output_dir)
        
        # Export main service breakdown (excluding marketplace)
        top_services = export_service_breakdown(ce_client, date_range, output_dir)

        # Check if EC2 is in top services
        if any('EC2' in service[0] or 'Compute' in service[0] for service in top_services):
            export_ec2_details(ce_client, date_range, output_dir)

        # Check if RDS is in top services
        if any('RDS' in service[0] or 'Database' in service[0] for service in top_services):
            export_rds_details(ce_client, date_range, output_dir)

        # Export container services if in top services
        export_container_services(ce_client, date_range, output_dir, top_services)

        # Export data transfer costs
        export_data_transfer(ce_client, date_range, output_dir)

        # Export EBS volumes
        export_ebs_volumes(ce_client, date_range, output_dir)

        # Export comprehensive reservation analysis
        export_comprehensive_reservation_analysis(ce_client, output_dir)

        # Check for CUR
        cur_def = check_cur_availability(cur_client)
        if cur_def:
            click.echo(f"\n✓ Cost and Usage Report found: {cur_def['ReportName']}")
            click.echo("  (Contact us for instructions on sharing CUR data)")
        else:
            click.echo("\n⚠ No Cost and Usage Report configured")
            click.echo("  (CUR provides the most detailed cost data)")
        
        # Create summary
        create_summary_report(output_dir)
        
        click.echo("\n" + "=" * 50)
        
        # Create zip file unless disabled
        if not no_zip:
            zip_file = create_zip_output(output_dir)
            click.echo(click.style("\n✅ Export complete!", fg='green', bold=True))
            click.echo(f"📦 Zip file created: {os.path.abspath(zip_file)}")
            click.echo("\nPlease share this zip file with your optimization team")
        else:
            click.echo(click.style("\n✅ Export complete!", fg='green', bold=True))
            click.echo(f"📁 All files saved to: {os.path.abspath(output_dir)}")
            click.echo("\nPlease zip and share the entire folder with your optimization team")
        
    except Exception as e:
        click.echo(click.style(f"\n❌ Error during export: {e}", fg='red'))
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    cli()
