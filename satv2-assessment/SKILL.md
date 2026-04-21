---
name: satv2-assessment
description: Deploy and run AWS SATv2 (Self-Service Security Assessment Solution) using Prowler-based security scanning via CloudFormation. Guides users through account selection, scan configuration, deployment, monitoring, result retrieval, and finding review using SATv2's built-in HTML report.
---

## Setup Flow

Ask questions one at a time. Wait for each answer before proceeding.

### Step 1 — Single or Multi-Account?

> **Are we running SATv2 for a single account or multiple accounts in your AWS Organization?**

- **Single account** — scans one account. One CloudFormation stack.
- **Multi-account** — scans all accounts from a central audit account. Requires StackSets + IAM roles in member accounts.

Do NOT proceed until the user explicitly chooses.

### Step 2 — AWS Profiles

List available profiles:
```bash
aws configure list-profiles
```

If no profiles exist or the user needs a new one, guide through SSO setup:
```bash
aws configure sso
```
Walk through: SSO session name → start URL → SSO region → accept default scopes → browser auth → select account + role → default region (`us-west-2`) → output (`json`) → profile name (suggest `mgmt-prod`, `audit-prod`).

**Single account** — ask for one profile.
**Multi-account** — ask for two: management account profile, then audit/Prowler account profile.

For each selected profile, validate the session:
```bash
aws sts get-caller-identity --profile <profile>
```
If expired, guide re-auth: `aws sso login --profile <profile>`, then retry.

Confirm the account ID with the user before proceeding.

Confirm region (default: `us-west-2`).

### Step 3 — Check for Existing Deployment

After profiles are validated, check if SATv2 is already deployed:

```bash
aws cloudformation describe-stacks --profile <profile> --region <region> \
  --query "Stacks[?starts_with(StackName,'sat2')].{Name:StackName,Status:StackStatus,Created:CreationTime}" \
  --output table
```

**If no stack found**, continue to Step 4.

**If a stack is found**, do two things:

#### 3a. Check template version

Compare the deployed template against the latest from GitHub:

```bash
# Get deployed template
aws cloudformation get-template --stack-name <stack-name> \
  --profile <profile> --region <region> \
  --query "TemplateBody" --output text > /tmp/sat2-deployed.yaml

# Get latest template from GitHub
curl -sL https://raw.githubusercontent.com/awslabs/aws-security-assessment-solution/main/2-sat2-codebuild-prowler.yaml > /tmp/sat2-latest.yaml

# Compare
diff /tmp/sat2-deployed.yaml /tmp/sat2-latest.yaml
```

#### 3b. Check CodeBuild scan status

```bash
PROJECT=$(aws cloudformation describe-stack-resources --stack-name <stack-name> \
  --query "StackResources[?ResourceType=='AWS::CodeBuild::Project'].PhysicalResourceId" \
  --output text --profile <profile> --region <region>)

BUILD_ID=$(aws codebuild list-builds-for-project --project-name $PROJECT \
  --query "ids[0]" --output text --profile <profile> --region <region>)

aws codebuild batch-get-builds --ids $BUILD_ID \
  --query "builds[0].{Status:buildStatus,Phase:currentPhase,Start:startTime,End:endTime}" \
  --profile <profile> --region <region>
```

#### 3c. Present options to the user

Summarize what was found and offer clear choices:

> **I found an existing SATv2 deployment: `<stack-name>` (created `<date>`).**
> **Template: `<up to date>` or `<outdated — a newer version is available on GitHub>`**
> **Last scan: `<status>` (`<date>`)**
>
> **What would you like to do?**
> 1. **Review results** — open the HTML report for the last completed scan *(only if SUCCEEDED)*
> 2. **Re-run scan** — trigger a new scan using the existing deployment *(only if SUCCEEDED or FAILED)*
> 3. **Upgrade & scan** — delete the old stack, deploy the latest version, and run a fresh scan *(if template is outdated)*
> 4. **Start fresh** — delete everything and set up from scratch
> 5. **Wait** — the scan is still running, come back after the email *(only if IN_PROGRESS)*

Only show options that apply based on the template version and build status. For example:
- Template outdated + build SUCCEEDED → show options 1, 3, 4
- Template current + build SUCCEEDED → show options 1, 2, 4
- Template outdated + build FAILED → show options 3, 4
- Template current + build IN_PROGRESS → show option 5 only
- Stack exists but no builds → show options 2, 3, 4

**If no stack found**, continue to Step 4.

### Step 4 — Scan Type

> **What level of scan?**

| Type | Checks | Best For |
|------|--------|----------|
| **Basic** (default) | 13 | First-time assessment |
| **Intermediate** | Critical + High | Follow-up |
| **Full** | 500+ | Comprehensive audit |

Recommend Basic for first-time, Intermediate for follow-ups.

### Step 5 — Email & Reporting

**Email is mandatory** — the user comes back after the notification to review results.

> **What email address should I send the scan completion notification to?**

Do NOT proceed without an email.

For **multi-account**, also recommend Reporting (default yes):
> **Reporting consolidates all results into a single CSV and SHIP HealthCheck presentation. Turn it on?**

## Deploy — Single Account

```bash
wget https://raw.githubusercontent.com/awslabs/aws-security-assessment-solution/main/2-sat2-codebuild-prowler.yaml

aws cloudformation deploy \
  --template-file 2-sat2-codebuild-prowler.yaml \
  --stack-name sat2 \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides ProwlerScanType=<type> EmailAddress=<email> \
  --profile <profile> --region <region>
```

After deployment:
> **The scan is running. You'll get an email at `<email>` when it completes. Come back to me then and we'll review the results together.**

## Deploy — Multi-Account

### Step A — Deploy Member Roles (management account)

Look up the root OU ID automatically:
```bash
ROOT_OU=$(aws organizations list-roots --profile <mgmt-profile> --region <region> \
  --query "Roots[0].Id" --output text)
```

Deploy the StackSet:
```bash
wget https://raw.githubusercontent.com/awslabs/aws-security-assessment-solution/main/1-sat2-member-roles.yaml

aws cloudformation create-stack-set \
  --template-body file://1-sat2-member-roles.yaml \
  --stack-set-name sat2-member-roles \
  --permission-model SERVICE_MANAGED \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters ParameterKey=ProwlerAccountID,ParameterValue=<audit-account-id> \
  --region <region> --profile <mgmt-profile>

aws cloudformation create-stack-instances \
  --stack-set-name sat2-member-roles \
  --deployment-targets OrganizationalUnitIds='["'$ROOT_OU'"]' \
  --regions '["<region>"]' \
  --operation-preferences FailureTolerancePercentage=100,MaxConcurrentPercentage=100 \
  --region <region> --profile <mgmt-profile>
```

Note: StackSets don't apply to the management account. Deploy `1-sat2-member-roles.yaml` as a regular Stack in the management account if it also needs scanning.

**Wait for completion** — poll until `SUCCEEDED`:
```bash
OP_ID=$(aws cloudformation list-stack-set-operations --stack-set-name sat2-member-roles \
  --query "Summaries[0].OperationId" --output text --profile <mgmt-profile> --region <region>)

aws cloudformation describe-stack-set-operation --stack-set-name sat2-member-roles \
  --operation-id $OP_ID --query "StackSetOperation.Status" --output text \
  --profile <mgmt-profile> --region <region>
```

If `FAILED`/`STOPPED`, check failures:
```bash
aws cloudformation list-stack-set-operation-results --stack-set-name sat2-member-roles \
  --operation-id $OP_ID --query "Summaries[?Status!='SUCCEEDED']" \
  --profile <mgmt-profile> --region <region>
```

Do NOT proceed until Step A completes.

### Step B — Verify Organizations Access (management account)

Check automatically — do NOT ask the user:
```bash
aws organizations list-delegated-administrators --profile <mgmt-profile> --region <region>
aws organizations describe-resource-policy --profile <mgmt-profile> --region <region>
```

- Audit account in delegated admins list → proceed.
- Resource policy grants audit account `organizations:ListAccounts` → proceed.
- Neither exists → create a resource policy (preferred):
  ```bash
  aws organizations put-resource-policy --content \
  '{
      "Version": "2012-10-17",
      "Statement": [{
          "Sid": "ProwlerListAccounts",
          "Effect": "Allow",
          "Principal": {"AWS": "arn:aws:iam::<audit-account-id>:root"},
          "Action": ["organizations:ListAccounts","organizations:DescribeAccount","organizations:ListTagsForResource"],
          "Resource": "*"
      }]
  }' --profile <mgmt-profile> --region <region>
  ```
  For GovCloud, use delegated admin: `aws organizations register-delegated-administrator --account-id <audit-account-id>`

### Step C — Deploy SATv2 (audit account)

```bash
aws cloudformation deploy \
  --template-file 2-sat2-codebuild-prowler.yaml \
  --stack-name sat2-prowler \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides MultiAccountScan=true Reporting=true ProwlerScanType=<type> EmailAddress=<email> \
  --profile <audit-profile> --region <region>
```

After deployment:
> **The multi-account scan is running. You'll get an email at `<email>` when it completes (and a second email when the consolidated report is ready). Come back to me then and we'll review together.**

## Review the Results

**Starts when the user returns after the email notification, or when Step 3 detects a completed scan.**

Begin immediately — do NOT ask if they want to review.

### Step 0 — Verify Build Succeeded

Before downloading results, confirm the scan actually completed:

```bash
PROJECT=$(aws cloudformation describe-stack-resources --stack-name <stack-name> \
  --query "StackResources[?ResourceType=='AWS::CodeBuild::Project'].PhysicalResourceId" \
  --output text --profile <profile> --region <region>)

BUILD_ID=$(aws codebuild list-builds-for-project --project-name $PROJECT \
  --query "ids[0]" --output text --profile <profile> --region <region>)

aws codebuild batch-get-builds --ids $BUILD_ID \
  --query "builds[0].buildStatus" --output text --profile <profile> --region <region>
```

- **SUCCEEDED** → proceed to Step 1.
- **IN_PROGRESS** → tell the user the scan is still running, come back later.
- **FAILED** → show the logs link (`builds[0].logs.deepLink`), offer to re-run or troubleshoot.

### Step 1 — Download Results

```bash
BUCKET=$(aws cloudformation describe-stack-resources --stack-name <stack-name> \
  --query "StackResources[?LogicalResourceId=='ProwlerFindingsBucket'].PhysicalResourceId" \
  --output text --profile <profile> --region <region>)

aws s3 ls s3://$BUCKET/ --recursive --profile <profile> --region <region>

mkdir -p sat2-results/csv sat2-results/compliance
aws s3 sync s3://$BUCKET/csv/ sat2-results/csv/ --profile <profile> --region <region>
aws s3 sync s3://$BUCKET/compliance/ sat2-results/compliance/ --profile <profile> --region <region>
aws s3 sync s3://$BUCKET/ sat2-results/ --exclude "csv/*" --exclude "compliance/*" --profile <profile> --region <region>
```

### Step 2 — Open HTML Report

SATv2 includes a static HTML report in the reporting folder that loads the consolidated CSV. Open it directly:
```bash
open sat2-results/reports/*.html 2>/dev/null || open sat2-results/**/*.html
```

> **SATv2's HTML report is open in your browser — use it to filter and explore findings by severity, account, service, or region. No additional tools to install.**

### Output Files

| File | Use |
|------|-----|
| `*.html` | Interactive report — loads consolidated CSV for filtering |
| `*.csv` | Tabular data |
| `*.json` / `*.json-ocsf` | Machine-readable / OCSF format for Security Hub |
| `/reports/*.csv` | Consolidated CSV (if Reporting enabled) |
| `/reports/*.pptx` | SHIP HealthCheck presentation (if Reporting enabled) |

## Clean Up

**After the user finishes reviewing results, proactively recommend cleanup.** SATv2 is a point-in-time tool — once the CodeBuild scan completes, the resources sit idle. Cleaning up removes them from the account.

> **You've got your results downloaded locally and the S3 bucket with reports will be retained. Want me to clean up the SATv2 stack now? It's designed to be temporary — you can always re-deploy it for a fresh scan later.**

If yes (or user confirms), proceed:

**Single account:**
```bash
aws cloudformation delete-stack --stack-name <stack-name> --profile <profile> --region <region>
```

**Multi-account:**
```bash
# Delete StackSet instances first
aws cloudformation delete-stack-instances --stack-set-name sat2-member-roles \
  --deployment-targets OrganizationalUnitIds='["'$ROOT_OU'"]' \
  --regions '["<region>"]' --no-retain-stacks \
  --profile <mgmt-profile> --region <region>

# Wait for completion, then delete StackSet
aws cloudformation delete-stack-set --stack-set-name sat2-member-roles \
  --profile <mgmt-profile> --region <region>

# Delete the main stack
aws cloudformation delete-stack --stack-name <stack-name> --profile <audit-profile> --region <region>
```

Tell the user: **Cleaned up. Your scan results are still in the S3 bucket (`<bucket-name>`) and downloaded locally in `sat2-results/`.**

## Next Steps

After the assessment, recommend:
- **Remediate findings with Kiro** — use the Security Hub Remediation Kiro Skill to triage, fix, and track the findings identified by this assessment. Blog walkthrough: [Remediating AWS Security Hub Findings with Kiro Skills](https://builder.aws.com/content/3BT16FE7BgulYKshKicMzXo5NKo/remediating-aws-security-hub-findings-with-kiro-skills)
- **Enable AWS Security Hub** — Foundational Security Best Practices for continuous monitoring
- **Request a formal SHIP engagement** — https://aws.amazon.com/security/security_start_right_run_well/
- **Prowler + Security Hub integration** — https://docs.prowler.cloud/en/latest/tutorials/aws/securityhub/

## Rules

- Always validate AWS profile and account ID with the user before any deployment
- Default region: `us-west-2`
- Show exact commands before execution; wait for confirmation on CloudFormation deploys
- Email is mandatory for all deployments
- For multi-account, always recommend enabling Reporting
