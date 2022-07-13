import json
import boto3

session = boto3.Session(profile_name='wp_mgmt_role')
trustedadvisor = session.client('support', region_name='us-east-1')
guardduty = session.client('guardduty', region_name='us-east-1')

summary = trustedadvisor.describe_trusted_advisor_checks(language='en')
json_object = json.dumps(summary,indent=2)

detector = guardduty.list_detectors()
gd_detector = detector['DetectorIds'][0]
fc = {'Criterion': {'severity': {'Gte': 4}}}
findings = guardduty.list_findings(DetectorId=gd_detector,FindingCriteria=fc)

for finding in findings['FindingIds']:
    find_detail = guardduty.get_findings(DetectorId=gd_detector, FindingIds=[finding])
    print(f'{find_detail}\n')

check_list = {ctgs: [] for ctgs in list(set([checks['category'] for checks in summary['checks']]))}
for checks in summary['checks']:
    if checks['category'] == "security":
        print(checks['name'])
