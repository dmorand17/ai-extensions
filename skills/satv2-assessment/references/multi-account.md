# SATv2 — Multi-Account Deployment

Read this when the user chose multi-account in Step 1 of `SKILL.md`. Covers
StackSets-based member-role deployment, Organizations resource access,
SATv2 stack deployment in the audit account, and multi-account cleanup.

The setup flow (Steps 1–5: profiles, scan type, email) and the result
review flow stay in `SKILL.md` and apply to both single- and multi-account.

## Profiles you'll need

Multi-account scans require **two** AWS profiles:

- **Management profile** — runs in the management account; deploys the
  StackSet that creates IAM roles in member accounts.
- **Audit profile** — runs in the audit/Prowler account; hosts the SATv2
  CodeBuild project that fans out across the org.

Both should have been validated in Step 2 of `SKILL.md` before reading
this file.

## Reporting parameter

Always recommend `Reporting=true` for multi-account. Reporting consolidates
all results into a single CSV plus a SHIP HealthCheck PowerPoint.

## Step A — Deploy member roles (management account)

Look up the root OU ID automatically — do NOT ask the user:

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

> **Note:** StackSets don't apply to the management account itself.
> If the management account also needs scanning, deploy
> `1-sat2-member-roles.yaml` as a regular `Stack` (not StackSet) in the
> management account.

**Wait for completion** — poll until `SUCCEEDED`:

```bash
OP_ID=$(aws cloudformation list-stack-set-operations --stack-set-name sat2-member-roles \
  --query "Summaries[0].OperationId" --output text --profile <mgmt-profile> --region <region>)

aws cloudformation describe-stack-set-operation --stack-set-name sat2-member-roles \
  --operation-id $OP_ID --query "StackSetOperation.Status" --output text \
  --profile <mgmt-profile> --region <region>
```

If `FAILED` / `STOPPED`, inspect failures:

```bash
aws cloudformation list-stack-set-operation-results --stack-set-name sat2-member-roles \
  --operation-id $OP_ID --query "Summaries[?Status!='SUCCEEDED']" \
  --profile <mgmt-profile> --region <region>
```

Do NOT proceed to Step B until Step A reports `SUCCEEDED`.

## Step B — Verify Organizations access (management account)

Check automatically — do NOT ask the user:

```bash
aws organizations list-delegated-administrators --profile <mgmt-profile> --region <region>
aws organizations describe-resource-policy --profile <mgmt-profile> --region <region>
```

- Audit account in the delegated-admins list → proceed.
- Resource policy grants the audit account `organizations:ListAccounts` →
  proceed.
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

  For GovCloud, use delegated admin instead:

  ```bash
  aws organizations register-delegated-administrator --account-id <audit-account-id>
  ```

## Step C — Deploy SATv2 (audit account)

```bash
aws cloudformation deploy \
  --template-file 2-sat2-codebuild-prowler.yaml \
  --stack-name sat2-prowler \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides MultiAccountScan=true Reporting=true ProwlerScanType=<type> EmailAddress=<email> \
  --profile <audit-profile> --region <region>
```

After deployment, tell the user:

> **The multi-account scan is running. You'll get an email at `<email>`
> when it completes (and a second email when the consolidated report is
> ready). Come back to me then and we'll review together.**

## Cleanup — multi-account

After the user has reviewed results and confirmed cleanup (see Clean Up
in `SKILL.md`):

```bash
# Delete StackSet instances first
aws cloudformation delete-stack-instances --stack-set-name sat2-member-roles \
  --deployment-targets OrganizationalUnitIds='["'$ROOT_OU'"]' \
  --regions '["<region>"]' --no-retain-stacks \
  --profile <mgmt-profile> --region <region>

# Wait for completion, then delete the StackSet
aws cloudformation delete-stack-set --stack-set-name sat2-member-roles \
  --profile <mgmt-profile> --region <region>

# Delete the main stack in the audit account
aws cloudformation delete-stack --stack-name <stack-name> --profile <audit-profile> --region <region>
```

Tell the user: **Cleaned up. Your scan results are still in the S3 bucket
(`<bucket-name>`) and downloaded locally in `sat2-results/`.**
