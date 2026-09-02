# AWS EC2 Implementation Guide — Phase 1

## 1. When to use EC2

EC2 is optional for Phase 1. Use it to demonstrate Linux administration, IAM, networking, Docker deployment, remote troubleshooting, cost control, and later Jenkins deployment. Continue writing and testing code locally; use EC2 as a development/demo environment.

The environment must contain synthetic data only. It is not a HIPAA production deployment.

## 2. Low-cost design

Use one AWS Region and one EC2 instance.

Recommended region: `us-east-2` for the project lab. `us-east-1` is also reasonable when a specific service is unavailable in Ohio. Do not build multi-region infrastructure in the portfolio MVP.

| Activity | Suggested instance | Oracle | Notes |
|---|---|---|---|
| API + PostgreSQL | `t3.small` or `t3.medium` | Off | Start with the smaller choice and observe memory |
| Oracle/dbt lab | `t3.large` | On temporarily | 8 GB memory is safer for the combined stack |
| Full Jenkins/monitoring lab | Separate sessions or larger temporary instance | As needed | Do not run every service continuously |

Use x86_64 for the first EC2 implementation to reduce container compatibility surprises. Do not treat any instance type as free without checking the offers shown in your own account.

## 3. Cost controls before creating EC2

### Create a budget

1. Open **Billing and Cost Management**.
2. Select **Budgets** → **Create budget**.
3. Choose a monthly cost budget.
4. Select a small amount you are comfortable spending.
5. Add email alerts at 50%, 80%, and 100%.
6. Add a forecasted alert as well as actual-spend alerts.

Tag all resources:

| Key | Value |
|---|---|
| `Project` | `ZambeCare` |
| `Environment` | `Development` |
| `Owner` | `John` |
| `AutoStop` | `True` |

New AWS accounts may receive credits, but eligibility, duration, and covered services depend on the account. Verify the Billing console instead of assuming an instance is free.

## 4. Create the Systems Manager role

Session Manager is preferred because it avoids exposing SSH.

1. Open **IAM** → **Roles** → **Create role**.
2. Trusted entity: **AWS service**.
3. Use case: **EC2**.
4. Attach `AmazonSSMManagedInstanceCore`.
5. Name the role `ZambeCareEC2SSMRole`.
6. Create the role.

Do not attach administrator access or database-secret permissions during Phase 1.

## 5. Launch the EC2 instance

1. Open **EC2** in `us-east-2`.
2. Select **Launch instance**.
3. Name: `zambecare-dev`.
4. AMI: Ubuntu Server 24.04 LTS, x86_64.
5. Instance type:
   - Begin with `t3.medium` for API/PostgreSQL.
   - Stop and resize temporarily to `t3.large` before running Oracle.
6. Key pair:
   - Session Manager path: proceed without a key pair if your account and AMI setup support it.
   - Fallback SSH path: create an ED25519 key and store the `.pem` securely.
7. Network:
   - Use the default VPC for this personal lab.
   - Auto-assign public IP may be enabled for simple package downloads and testing.
8. Security group: create `zambecare-dev-sg`.
9. Storage: 30–40 GiB `gp3`, encrypted, delete on termination.
10. Advanced details: attach `ZambeCareEC2SSMRole` as the IAM instance profile.
11. Add the project tags.
12. Launch the instance.

## 6. Security-group rules

Preferred Session Manager configuration:

| Direction | Port | Source | Purpose |
|---|---:|---|---|
| Inbound | None | — | Administration through Session Manager |
| Outbound | 443 | Internet | Packages, GitHub, registries and AWS APIs |

For a temporary browser test, add:

| Direction | Port | Source | Purpose |
|---|---:|---|---|
| Inbound | 8000 | `YOUR_PUBLIC_IP/32` | FastAPI demonstration |

If SSH is required, allow TCP 22 from `YOUR_PUBLIC_IP/32` only. Never use `0.0.0.0/0` for SSH, PostgreSQL 5432, Oracle 1521, Jenkins 8080, or FastAPI 8000. Remove temporary rules after testing.

## 7. Connect to EC2

### Preferred: Session Manager

1. EC2 → **Instances**.
2. Select `zambecare-dev`.
3. Select **Connect**.
4. Open the **Session Manager** tab.
5. Select **Connect**.

If the Session Manager tab is unavailable, verify:

- The instance role is attached.
- SSM Agent is installed and running.
- The instance has outbound access to Systems Manager endpoints.

### SSH fallback

```bash
chmod 400 zambecare-dev.pem
ssh -i zambecare-dev.pem ubuntu@EC2_PUBLIC_DNS
```

## 8. Patch the server and install Git

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl git unzip
```

Reboot after important kernel updates:

```bash
sudo reboot
```

Reconnect after the instance becomes healthy.

## 9. Install Docker Engine and Compose

Use Docker's official Ubuntu repository:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Exit and reconnect for group membership to apply. Verify:

```bash
docker version
docker compose version
docker run --rm hello-world
```

Membership in the Docker group is effectively privileged access to the host. Limit server accounts accordingly.

## 10. Transfer the code

### Recommended GitHub method

Create a private GitHub repository from the local Phase 1 project and push the code. On EC2:

```bash
git clone GITHUB_REPOSITORY_URL zambecare
cd zambecare
```

Use a GitHub deploy key or appropriately scoped authentication. Do not place a personal access token in a command, script, repository, or shell history.

### Archive method

From your local computer:

```bash
scp -i zambecare-dev.pem ZambeCare_Phase1.zip \
  ubuntu@EC2_PUBLIC_DNS:/home/ubuntu/
```

On EC2:

```bash
unzip ZambeCare_Phase1.zip
cd zambecare
```

The archive method requires temporary SSH access from your IP.

## 11. Create environment configuration

```bash
cp .env.example .env
chmod 600 .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
nano .env
```

Replace all example passwords and `SECRET_KEY`. Never commit `.env`.

Verify:

```bash
git check-ignore .env
```

## 12. Deploy the lightweight stack

```bash
make validate
docker compose config --quiet
docker compose up --build -d postgres api
docker compose ps
docker compose logs --tail=100 api postgres
```

From EC2:

```bash
curl http://localhost:8000/health
```

From your computer, only when port 8000 is restricted to your IP:

```bash
curl http://EC2_PUBLIC_IP:8000/health
```

Remove the port 8000 rule after testing.

## 13. Verify the database and tests

```bash
docker compose exec postgres psql \
  -U zambecare_app \
  -d zambecare \
  -c "select table_schema, table_name from information_schema.tables where table_schema in ('clinical','security') order by 1,2;"

docker compose run --rm api pytest -q
```

## 14. Temporarily resize for Oracle

1. Stop the Compose services:

   ```bash
   docker compose down
   ```

2. In EC2, select the instance → **Instance state** → **Stop instance**.
3. After it is stopped: **Actions** → **Instance settings** → **Change instance type**.
4. Select `t3.large`.
5. Start and reconnect.
6. Check memory and disk:

   ```bash
   free -h
   df -h
   ```

7. Sign in to Oracle Container Registry and start Oracle:

   ```bash
   docker login container-registry.oracle.com
   docker compose --profile oracle up -d oracle
   docker compose logs -f oracle
   ```

Do not open Oracle port 1521 in the security group. dbt communicates with Oracle on the internal Docker network.

## 15. Initialize Oracle and run dbt

Copy and execute the numbered Oracle scripts as described in `PHASE_1_IMPLEMENTATION.md`, then run:

```bash
docker compose --profile analytics run --rm dbt debug
docker compose --profile analytics run --rm dbt parse
docker compose --profile analytics run --rm dbt build
```

Record errors and fixes in the project documentation; production-style troubleshooting is part of the portfolio evidence.

## 16. GitHub Actions and Jenkins strategy

During Phase 1:

- GitHub Actions validates every pull request.
- EC2 runs the development deployment.
- Jenkins can be installed later as a container or on a separate temporary EC2 session.

Do not run Jenkins continuously on the same small instance as Oracle. In the later CI/CD phase, Jenkins will pull an approved image/version, deploy Compose, run health checks, execute dbt reconciliation, and roll back on failure.

## 17. Stop and restart safely

Before stopping EC2:

```bash
cd ~/zambecare
docker compose --profile oracle --profile analytics stop
docker compose ps
```

Then stop the EC2 instance in the console. Compute charges stop, but EBS storage and public IPv4-related charges may remain. A stopped/started instance normally receives a different public IPv4 address unless a separately charged static address is used.

For this lab, avoid an Elastic IP. Retrieve the current public address after each start.

## 18. Cleanup

When the lab is no longer needed:

1. Preserve source code in GitHub.
2. Export only synthetic artifacts you need.
3. Terminate the EC2 instance if the environment is disposable.
4. Confirm its EBS volume was deleted as configured.
5. Release any Elastic IP.
6. Delete unused snapshots, load balancers, NAT gateways, and security groups.
7. Review Billing and Cost Explorer.

Termination is destructive. Confirm the exact instance and required backups before selecting **Terminate instance**.

## 19. EC2 acceptance checklist

- [ ] Budget and alerts exist.
- [ ] Resources carry ZambeCare tags.
- [ ] EC2 has an SSM role without administrator access.
- [ ] EBS is encrypted.
- [ ] Security group has no unrestricted administrative or database ports.
- [ ] Docker and Compose are installed.
- [ ] `.env` is protected and ignored.
- [ ] Static validation passes.
- [ ] API/PostgreSQL are healthy.
- [ ] API test passes.
- [ ] Oracle is used only on the temporary larger instance size.
- [ ] Oracle 1521 is not exposed publicly.
- [ ] dbt connects and parses/builds.
- [ ] GitHub Actions passes.
- [ ] Instance is stopped after the lab.
- [ ] Only synthetic data is present.

## 20. Official references

- AWS EC2 launch guide: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html
- AWS Session Manager connection: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-with-systems-manager-session-manager.html
- AWS Budgets: https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-create.html
- AWS stopping and starting EC2: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-ec2-instance-stop-start-works.html
- AWS EBS encryption: https://docs.aws.amazon.com/ebs/latest/userguide/ebs-encryption.html
- Docker Engine on Ubuntu: https://docs.docker.com/engine/install/ubuntu/
