---
name: terraform
description: Use when working with Terraform or OpenTofu - creating modules, writing configurations, choosing testing approaches, structuring environments, configuring remote state backends (AWS S3, GCS, Azure Blob), reviewing IaC code, implementing security scanning, or making infrastructure-as-code architecture decisions
license: MIT
metadata:
  version: 1.0.0
---

# Terraform Skill

Opinionated Terraform and OpenTofu guidance covering modules, testing, naming, and production patterns. Based on terraform-best-practices.com.

## When to Use This Skill

**Activate for:**
- Creating or reviewing Terraform/OpenTofu configurations or modules
- Choosing between testing approaches
- Structuring multi-environment deployments
- Implementing CI/CD for IaC
- Security scanning and compliance

**Don't use for:**
- Basic syntax questions (Claude already knows this)
- Provider-specific API reference (link to docs instead)

---

## Project Structure

```
environments/        # Environment-specific root configurations
├── prod/
│   ├── terraform.tfvars
│   └── s3.tfbackend
├── staging/
│   ├── terraform.tfvars
│   └── s3.tfbackend
└── dev/
    ├── terraform.tfvars
    └── s3.tfbackend

modules/             # Reusable internal modules
├── networking/
├── compute/
└── data/

examples/            # Usage examples (also serve as integration tests)
├── complete/
└── minimal/
```

**Key principle:** Separate **environments** (root configs) from **modules** (reusable components). Never mix them.

---

## Module Structure

```
my-module/
├── main.tf           # Primary resources
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── versions.tf       # Provider version constraints
├── README.md         # Usage docs (generate with terraform-docs)
└── examples/
    ├── minimal/
    └── complete/
```

---

## Naming Conventions

**Resources:**
```hcl
# Use "this" for singleton resources (only one of that type in the module)
resource "aws_vpc" "this" {}
resource "aws_security_group" "this" {}

# Use descriptive names for multiple resources of the same type
resource "aws_subnet" "public" {}
resource "aws_subnet" "private" {}

# Avoid generic names
resource "aws_instance" "main" {}   # bad
resource "aws_instance" "web" {}    # good
```

**Variables:** prefix with context (`vpc_cidr_block` not `cidr`)

**Files:** `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `data.tf`

---

## Block Ordering

**Resource blocks:**
1. `count` or `for_each` FIRST, blank line after
2. Required arguments
3. Optional arguments
4. `tags` last
5. `depends_on` after tags (if needed)
6. `lifecycle` at the very end

```hcl
resource "aws_nat_gateway" "this" {
  count = var.create_nat_gateway ? 1 : 0

  allocation_id = aws_eip.this[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(var.tags, { Name = "${var.name}-nat" })

  lifecycle {
    create_before_destroy = true
  }
}
```

**Variable blocks:** `description` -> `type` -> `default` -> `validation` -> `nullable`

```hcl
variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}
```

---

## count vs for_each

| Scenario | Use |
|----------|-----|
| Boolean on/off | `count = condition ? 1 : 0` |
| Fixed identical copies | `count = N` |
| Items may be reordered/removed | `for_each = toset(list)` |
| Reference by key | `for_each = map` |

```hcl
# Good - for_each: removing one AZ doesn't recreate others
resource "aws_subnet" "private" {
  for_each          = toset(var.availability_zones)
  availability_zone = each.key
}

# Bad - count: removing middle AZ recreates all subsequent subnets
resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  availability_zone = var.availability_zones[count.index]
}
```

---

## Testing Strategy

| Situation | Approach | Tools |
|-----------|----------|-------|
| Quick syntax check | Static analysis | `validate`, `fmt` |
| Pre-commit | Static + lint | `validate`, `tflint`, `trivy` |
| Terraform 1.6+, logic testing | Native tests | `terraform test` |
| Complex integration testing | Go-based | Terratest |
| Security/compliance focus | Policy as code | OPA, Sentinel |
| Cost-sensitive workflow | Mock providers (1.7+) | Native tests + mocks |

**Native test example** (`tests/main.tftest.hcl`):
```hcl
run "validates_vpc_cidr" {
  command = plan

  variables {
    vpc_cidr = "10.0.0.0/16"
  }

  assert {
    condition     = aws_vpc.this.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR block mismatch"
  }
}
```

- Use `command = plan` for fast input validation
- Use `command = apply` for computed values and set-type blocks
- Set-type blocks (S3 encryption rules, lifecycle transitions) cannot be indexed with `[0]`; use `for` expressions

---

## Version Constraints

```hcl
terraform {
  required_version = "~> 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

| Component | Strategy | Example |
|-----------|----------|---------|
| Terraform binary | Pin minor | `~> 1.9` |
| Providers | Pin major | `~> 5.0` |
| Modules (prod) | Pin exact | `= 5.1.2` |
| Modules (dev) | Allow patch | `~> 5.1` |

---

## Modern Features

```hcl
# try() - safe fallbacks (0.13+)
output "sg_id" {
  value = try(aws_security_group.this[0].id, "")
}

# optional() with defaults (1.3+)
variable "config" {
  type = object({
    name    = string
    timeout = optional(number, 300)
  })
}

# moved block - refactor without destroy/recreate (1.1+)
moved {
  from = aws_instance.old_name
  to   = aws_instance.new_name
}

# Cross-variable validation (1.9+)
variable "backup_days" {
  type = number
  validation {
    condition     = var.environment == "prod" ? var.backup_days >= 7 : true
    error_message = "Production requires backup_days >= 7"
  }
}
```

---

## Security Essentials

```bash
# Run before every commit
trivy config .
checkov -d .
tflint --recursive
```

**Always:**
- Use AWS Secrets Manager / SSM Parameter Store - never plain vars for secrets
- Enable encryption at rest on all storage resources
- Restrict security group rules (avoid `0.0.0.0/0` for ingress)
- Use dedicated VPCs, not the default VPC
- Enable state backend encryption and access controls
- Mark sensitive outputs with `sensitive = true`

---

## CI/CD Workflow

```
PR opened       -> validate + lint + tflint + trivy + plan
Merge to main   -> integration tests + plan
Manual approve  -> apply to staging
Manual approve  -> apply to prod
```

**Cost control:**
- Use mock providers for PR validation (free, Terraform 1.7+)
- Run real integration tests only on main branch
- Tag all test resources for spend tracking
- Implement auto-cleanup for test environments

---

## Outputs Best Practices

```hcl
output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.this.id
}

output "db_password" {
  description = "Database master password"
  value       = random_password.db.result
  sensitive   = true
}
```

- Always include `description`
- Return related values as an object when consumers need multiple attributes
- Mark secrets with `sensitive = true`

---

## Cloud-Specific Patterns

### AWS

#### S3 Backend with Native State Locking (Terraform 1.10+)

Use S3 native locking (`use_lockfile = true`) instead of DynamoDB. Introduced as opt-in experimental in 1.10; DynamoDB-based locking will be deprecated in a future release.

```hcl
terraform {
  backend "s3" {
    bucket       = "my-org-terraform-state"
    key          = "envs/prod/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true

    # Encryption
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:123456789012:key/mrk-abc123"

    # Versioning recommended on the bucket (enables state recovery)
  }
}
```

**How it works:** A `.tflock` file is written next to the state file in S3. Both must be acquired when combining with DynamoDB; prefer S3-only locking for new setups.

**Partial backend configuration** (keep secrets out of version control):
```hcl
# backend.tf - committed
terraform {
  backend "s3" {}
}
```

**Environment-specific backend config files** — store per-environment backend values in separate files using the [recommended naming convention](https://developer.hashicorp.com/terraform/language/backend#file) `*.backendname.tfbackend`, alongside a `terraform.tfvars` for environment-specific variable values:
```
environments/
├── dev/
│   ├── terraform.tfvars
│   └── s3.tfbackend
├── staging/
│   ├── terraform.tfvars
│   └── s3.tfbackend
└── prod/
    ├── terraform.tfvars
    └── s3.tfbackend
```

```hcl
# s3.tfbackend
bucket       = "my-org-terraform-state"
key          = "networking/prod/terraform.tfstate"
region       = "us-east-1"
use_lockfile = true
encrypt      = true
```

```hcl
# terraform.tfvars
environment = "prod"
project     = "my-app"
aws_region  = "us-east-1"
```

```bash
# Initialize and plan with the appropriate environment configs
terraform init -backend-config=environments/prod/s3.tfbackend
terraform plan -var-file=environments/prod/terraform.tfvars
```

This keeps backend differences (bucket, key, region, encryption settings) explicit per environment while the `backend "s3" {}` block in code stays empty and reusable. Commit `.tfbackend` files to version control (they contain no secrets), but use `-backend-config` CLI flags or environment variables for any sensitive values like `kms_key_id`.

#### AWS Provider Authentication

Prefer IAM roles over static credentials. Never hardcode `access_key` / `secret_key`.

```hcl
provider "aws" {
  region = var.aws_region

  # Use assume_role for cross-account or CI/CD
  assume_role {
    role_arn     = "arn:aws:iam::123456789012:role/TerraformRole"
    session_name = "terraform-${var.environment}"
  }

  default_tags {
    tags = {
      managed-by  = "terraform"
      environment = var.environment
      project     = var.project
    }
  }
}
```

Use `default_tags` to apply consistent tags to all resources without repeating them.

#### AWS Resource Patterns

**VPC with secondary CIDR (use locals for correct deletion order):**
```hcl
locals {
  # Forces correct deletion order: subnets before CIDR association
  vpc_id = try(
    aws_vpc_ipv4_cidr_block_association.secondary[0].vpc_id,
    aws_vpc.this.id
  )
}
```

**Security groups — avoid overly broad rules:**
```hcl
# Good - restrict to known CIDR
resource "aws_vpc_security_group_ingress_rule" "app" {
  security_group_id = aws_security_group.this.id
  cidr_ipv4         = var.allowed_cidr
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

# Bad - open to the world
resource "aws_vpc_security_group_ingress_rule" "app" {
  cidr_ipv4   = "0.0.0.0/0"   # avoid unless explicitly required (ALB, CDN)
  ip_protocol = "-1"
}
```

**Always tag resources** with at least `environment`, `managed-by`, and a cost-allocation tag. Use `default_tags` on the provider rather than repeating tags per resource.
