# terraform skill

A simplified Claude Code skill for Terraform and OpenTofu best practices. Inspired by [antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill).

## What It Covers

- **Project & module structure** - directory layout, file conventions
- **Naming conventions** - resources, variables, files
- **Block ordering** - consistent resource and variable block structure
- **count vs for_each** - when to use each and why
- **Testing strategy** - decision matrix from static analysis to full integration tests
- **Version constraints** - pinning strategy for Terraform, providers, and modules
- **Modern features** - `try()`, `optional()`, `moved`, cross-variable validation
- **Security essentials** - scanning tools, secrets management, encryption
- **CI/CD workflow** - PR -> staging -> prod pipeline stages
- **Outputs best practices** - descriptions, sensitive values, object returns
- **Cloud-specific patterns:**
  - **AWS** - S3 backend with native locking (`use_lockfile = true`, Terraform 1.10+), IAM permissions, bucket hardening, provider auth with `assume_role` and `default_tags`, VPC and security group patterns

## Installation

### Recommended: Symlink Installation

Using a symlink ensures you always have the latest version and can easily pull updates from git:

```bash
# Clone this repository
git clone git@github.com:dmorand17/skill-terraform.git
cd skill-terraform

# Claude Code — global installation (recommended)
ln -s $(pwd) ~/.claude/skills/skill-terraform

# Kiro (IDE and CLI) — global installation
ln -s $(pwd) ~/.kiro/skills/skill-terraform

# Or for a specific project (Claude Code)
ln -s $(pwd) /path/to/project/.claude/skills/skill-terraform

# Or for a specific project (Kiro)
ln -s $(pwd) /path/to/project/.kiro/skills/skill-terraform
```

To update the skill later:
```bash
cd skill-terraform
git pull
```

In the Kiro IDE, you can also import directly:
1. Open **Agent Steering & Skills** in the Kiro panel
2. Click **+** → **Import a skill**
3. Choose **Local folder** and select the cloned `skill-terraform` directory

### Alternative: Direct Copy

```bash
git clone git@github.com:dmorand17/skill-terraform.git
cp -r skill-terraform ~/.claude/skills/skill-terraform/
# Or for Kiro
cp -r skill-terraform ~/.kiro/skills/skill-terraform/
```

Note: With this method, you'll need to manually copy files again after updates.

## Usage

Claude automatically activates this skill when you're working with Terraform or OpenTofu. Example prompts:

- "Create a Terraform module for an S3 bucket with versioning and encryption"
- "Review this Terraform configuration for best practices"
- "Help me choose a testing approach for my Terraform modules"
- "Set up a GitHub Actions CI/CD pipeline for Terraform"
- "Refactor this resource to use for_each instead of count"

## Structure

```
skill-terraform/
├── SKILL.md    # Skill content loaded by Claude
└── README.md   # This file
```

## Differences from antonbabenko/terraform-skill

- Single `SKILL.md` file (~250 lines) vs. main skill + 6 reference files
- Focuses on Terraform 1.6+ only (drops legacy guidance)
- Removes provider-specific examples (kept generic)
- No marketplace metadata

## Requirements

- Claude Code with skills support
- Terraform 1.6+ or OpenTofu 1.7+

## License

MIT
