# Simple AWS deployment guide

This personal-project setup uses:

- AWS Amplify Hosting for the React frontend
- One ECS/Fargate task for the FastAPI backend
- Amazon ECR to store the backend Docker image
- An Application Load Balancer (ALB) to give the backend a stable HTTPS endpoint
- The existing PostgreSQL/Supabase database
- AWS Secrets Manager for the OpenAI key and database password

You do not need separate development, testing, and production infrastructure. Run
the app locally while developing and deploy the main branch when it is ready.

The web backend is `Backend/main.py`. `Backend/runner.py` remains a local listing
import script; it does not run inside the web container.

## 1. Rotate the old RapidAPI key

A RapidAPI credential had previously been committed in
`Get-Region-Ids/GetRegionID.py`. It has been removed from the source. Revoke it in
RapidAPI, create a replacement, and keep the replacement in the local project-root
`.env` as `REDFIN_KEY`. The deployed web API does not need this key.

## 2. Test the backend container locally

From the repository root:

```bash
docker build -t nexthomeai-backend .
docker run --rm -p 8000:8000 --env-file .env nexthomeai-backend
```

Open `http://localhost:8000/health`. You do not need a separate cloud testing
environment; this local container is the deployment-equivalent test.

## 3. Push the image to ECR

Replace `ACCOUNT_ID` if necessary:

```bash
aws ecr create-repository --repository-name nexthomeai-backend --region ca-central-1
aws ecr get-login-password --region ca-central-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.ca-central-1.amazonaws.com
docker tag nexthomeai-backend:latest ACCOUNT_ID.dkr.ecr.ca-central-1.amazonaws.com/nexthomeai-backend:latest
docker push ACCOUNT_ID.dkr.ecr.ca-central-1.amazonaws.com/nexthomeai-backend:latest
```

## 4. Run one ECS/Fargate task

Create an ECS cluster, Fargate task definition, and service with:

- Desired task count: `1`
- Container port: `8000`
- Initial size: 0.5 vCPU and 1 GB memory
- ALB health-check path: `/health`
- ALB idle timeout: at least `240` seconds
- CloudWatch Logs enabled
- A public HTTPS ALB using an ACM certificate
- A security group that lets only the ALB reach task port 8000
- Outbound internet access for OpenAI and Supabase

Set these ordinary environment variables on the task:

```env
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://YOUR_AMPLIFY_DOMAIN
OPENAI_MODEL=gpt-5.6-luna
OPENAI_TIMEOUT_SECONDS=180
DATABASE_HOST=YOUR_SUPABASE_POOLER_HOST
DATABASE_PORT=5432
DATABASE_NAME=postgres
DATABASE_USER=YOUR_SUPABASE_DATABASE_USER
DATABASE_SSLMODE=require
DATABASE_CONNECT_TIMEOUT_SECONDS=10
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
```

Store `OPENAI_API_KEY` and `DATABASE_PASSWORD` in Secrets Manager and reference
them in the task definition's `secrets` section. You can instead store one
`DATABASE_URL` secret and omit the individual database settings.

The backend intentionally keeps sessions in memory. This is appropriate for one
personal-project task, but conversations reset whenever that task restarts. Keep
the ECS desired count at one; shared session storage such as DynamoDB is only worth
adding if the project later needs multiple backend tasks or restart-resistant
sessions.

The included rate limiter also lives in that one task. This is enough for basic
protection of a small public OpenAI endpoint. Consider AWS WAF or authentication
only if the app receives meaningful public traffic or abuse.

## 5. Deploy the frontend with Amplify

Connect the repository in Amplify Hosting. The included `amplify.yml` builds the
`Frontend` directory. Add this Amplify environment variable before building:

```env
VITE_API_BASE_URL=https://YOUR_BACKEND_DOMAIN
```

After Amplify gives you the final frontend URL, use that exact origin (scheme and
hostname, without a trailing slash or path) as the backend's `ALLOWED_ORIGINS`.

Add an Amplify rewrite rule for React Router: source `/<*>`, target `/index.html`,
status `200 (Rewrite)`.

## 6. Verify the deployed app

```bash
curl https://YOUR_BACKEND_DOMAIN/health
```

Then perform one complete property search from the Amplify URL and verify that a
second chat message retains the same search state.

## Detailed errors

The API intentionally returns the exception type and message, and the frontend
shows that detail together with a request ID. Full tracebacks go to CloudWatch.
This behavior was kept as requested.
