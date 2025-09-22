# AWS Cost Export

Export comprehensive AWS cost data for analysis and optimization.

## Installation

```bash
pip install awscostexport
```

## Quick Start

```bash
# Export last 6 months of data (default)
awscostexport

# Export last 3 months
awscostexport --months 3

# Use specific AWS profile
awscostexport --profile prod-account

# Get help
awscostexport --help
```

That's it! Your data will be exported as a zip file.

## What You Get

The script exports comprehensive AWS cost data:
- **Service breakdown** - Top 10 services (marketplace excluded)
- **EC2 analysis** - Purchase options, instance types, Savings Plans vs RIs
- **Database details** - RDS engines, ElastiCache, DynamoDB configurations
- **Reservation analysis** - Complete RI/SP coverage for all eligible services
- **Storage breakdown** - EBS volume types (GP2, GP3, IO1)
- **Network costs** - Data transfer, NAT gateways
- **Marketplace tracking** - Separated from main costs
- **Optimization metrics** - Coverage %, utilization, on-demand opportunities

Output: Single zip file with 10+ CSV files ready for analysis.

## Prerequisites

- Python 3.7 or later
- AWS credentials with Cost Explorer read access

## Output

The script creates a **zip file** containing all your cost data:

| File | Description |
|------|-------------|
| 01_service_breakdown.csv | Top 10 services by cost (excludes marketplace) |
| 02_ec2_purchase_options.csv | EC2 on-demand vs reserved vs Savings Plans |
| 02a_ec2_instance_types.csv | EC2 instance types (if EC2 in top 10) |
| 03_rds_breakdown.csv | Database configurations |
| 03a_rds_engines.csv | Database engines |
| 04_savings_status.csv | Overall Savings Plans & RI coverage metrics |
| 05_container_services.csv | ECS/EKS/Fargate data (if in top 10) |
| 06_data_transfer_nat.csv | Network costs |
| 07_ebs_volumes.csv | Storage volume types |
| 08_marketplace_spend.csv | AWS Marketplace costs (separated) |
| 09_reservation_analysis.csv | **Comprehensive RI/SP analysis for all services** |
| AWS_COST_EXPORT_SUMMARY.md | Summary report |

## Troubleshooting

**"Cannot access AWS Cost Explorer"**
- Check your IAM permissions include `ce:*` access
- Verify credentials: `aws sts get-caller-identity`
- Cost Explorer needs 24 hours after first activation

**"No data returned"**
- Verify you have AWS costs in the time period
- Default exports last 6 months of data

## Support

Email: david.schwartz@devfactory.com

## License

MIT License - See LICENSE file for details.
