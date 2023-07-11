# 06-Best-Practices

## Testing the code

unit tests with pytest

## Integration tests

with docker-compose

## Testing cloud services

with LocalStack

## Code quality

- linting and formatting
- Git pre-commit hooks
- Makefiles and make

<br>

## Infrastructure as Code

### Project infrastructure modules

* Amazon Web Service (AWS):
  - Kinesis: Streams (Producer & Consumer)
  - Lambda: Serving API
  - S3 Bucket: Model artifacts
  - ECR: Image Registry

![image](AWS-stream-pipeline.png)

<br>

### Part 0

* Pre-Reqs: aws-cli v1, aws secret key pair, terraform client
- Installation material: AWS & TF (refer to previous videos, links in README)

#### Setup

1. If you've already created an AWS account, head to the IAM section, generate your secret-key, and download it locally.
[Instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-prereqs.html)
2. Download [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) as a tool to use on your terminal
3. Check installation

  ```bash
    $ which aws
    /some/local/path/aws 
    $ aws --version
    aws-cli/X.x Python/3.x Darwin/18.x botocore/2.x
  ```

4. [Configure]((https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)) `aws-cli` with your downloaded AWS secret keys:

  ```shell
   $ aws configure
     AWS Access Key ID [None]: xxx
     AWS Secret Access Key [None]: xxx
     Default region name [None]: eu-west-1
     Default output format [None]:
  ```

5. Verify aws config:

  ```shell
   aws sts get-caller-identity
  ```

#### Concepts of Terraform and IaC

(refer to previous videos, links in README)

1. For an introduction to Terraform and IaC concepts, please refer to this video (from the DE Zoomcamp), especially the sections in the time-codes:
    <https://www.youtube.com/watch?v=Hajwnmj0xfQ&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=11>

    - 00:00 Introduction
    - 00:35 What is Terraform?
    - 01:10 What is IaC?
    - 01:43 Advantages of IaC
    - 14:48 Installing Terraform
    - 02:28 More on Installing Terraform

2. For a quickstart tutorial, and understanding the main components of a basic Terraform script, please refer to this 20-min video (from the DE Zoomcamp). Please note that this example uses GCP as a cloud provider, while for MLOps Zoomcamp we are using AWS.
    <https://www.youtube.com/watch?v=dNkEgO-CExg&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=12>

    - 00:00 Introduction
    - 00:20 .terraform-version
    - 01:04 main.tf
    - 01:23 terraform declaration
    - 03:25 provider plugins
    - 04:00 resource example - google_storage_bucket
    - 05:42 provider credentials
    - 06:34 variables.tf
    - 10:54 overview of terraform commands
    - 13:35 running terraform commands
    - 18:08 recap

<br>

### Part 1. Setting up a stream-based pipeline infrastructure in AWS

- What are Modules and Outputs in Terraform?
- Build components for ECR, Kinesis, Lambda, S3
- Demo: apply TF to our use-case, manually deploy & test

<br>

### CI/CD

**Part 1: CI/CD w/ GitHub Actions**
- What are GitHub workflows?
- `test-pr-pipeline.yml`
  - Copy over sections from tests: Env setup, Unit test, Integration test, Terraform plan
  - Create a develop branch & PR (feature branch) to that
  - Execute demo

- `deploy-pipeline.yml`
  - Copy over sections from tests: Terraform plan, Terraform apply, Docker build & ECR push, Update Lamba config
  - Merge PR to `develop`
  - Execute demo

<br>

**Other material:**

Deploying Serverless Machine Learning with AWS (one of my previous videos explaining Lambda integration with Docker images): <https://www.youtube.com/watch?v=79B8AOKkpho&t=689s>


## Getting everything to work

We edited everything to scorecard project. To run the project go to the infrasttructure main directory and run

```
terraform init -var-file=vars/stg.tfvars
terraform apply -var-file=vars/stg.tfvars
```

I started getting errors about null image. So I decided to build a repo via a different rout

```sh
aws ecr create-repository --repository-name risk-scoring-model
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-west-2:410605826834:repository/risk-scoring-model",
        "registryId": "410605826834",
        "repositoryName": "risk-scoring-model",
        "repositoryUri": "410605826834.dkr.ecr.us-west-2.amazonaws.com/risk-scoring-model",
        "createdAt": "2023-07-11T10:02:39-06:00",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": false
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }
}

```

```sh
ECR_REGION=us-west-2
aws ecr get-login-password \
--region ${ECR_REGION} \
| docker login \
--username AWS \
--password-stdin 410605826834.dkr.ecr.${ECR_REGION}.amazonaws.com

```


__worked__ by copying the old one from the repo. Ran it and then checked the hacks in the _deploy_manual.sh_. Then changed permission at `chmod +x deploy_manual.sh` and ran `./deploy_manual.sh` from the script folder. The following output is see

```json
{
    "FunctionName": "stg_prediction_lambda_mlops-zoomcamp",
    "FunctionArn": "arn:aws:lambda:us-west-2:410605826834:function:stg_prediction_lambda_mlops-zoomcamp",
    "Role": "arn:aws:iam::410605826834:role/iam_stg_prediction_lambda_mlops-zoomcamp",
    "CodeSize": 0,
    "Description": "",
    "Timeout": 180,
    "MemorySize": 128,
    "LastModified": "2023-07-11T18:17:55.000+0000",
    "CodeSha256": "813e6029da179171a4406210b58b47c8079662198a922355dc9036b00a50dd86",
    "Version": "$LATEST",
    "Environment": {
        "Variables": {
            "PREDICTIONS_STREAM_NAME": "stg_ride_predictions-mlops-zoomcamp",
            "MODEL_BUCKET": "stg-mlflow-models-moose-solutions-mlops-zoomcamp",
            "RUN_ID": "Test123"
        }
    },
    "TracingConfig": {
        "Mode": "Active"
    },
    "RevisionId": "e6b0d9a3-95e4-4e02-875f-4462117163e2",
    "State": "Active",
    "LastUpdateStatus": "InProgress",
    "LastUpdateStatusReason": "The function is being created.",
    "LastUpdateStatusReasonCode": "Creating",
    "PackageType": "Image",
    "Architectures": [
        "x86_64"
    ],
    "EphemeralStorage": {
        "Size": 512
    }
}
```

We can try to send and event to kinesis.
```sh
export KINESIS_STREAM_INPUT="stg_ride_events-mlops-zoomcamp"

aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --cli-binary-format raw-in-base64-out \
    --data '{
            "cust": {
                "riskperformance": 0,
                "externalriskestimate": 57,
                "msinceoldesttradeopen": 176,
                "msincemostrecenttradeopen": 4,
                "averageminfile": 87,
                "numsatisfactorytrades": 18,
                "numtrades60ever2derogpubrec": 0,
                "numtrades90ever2derogpubrec": 0,
                "percenttradesneverdelq": 89,
                "msincemostrecentdelq": 2,
                "maxdelq2publicreclast12m": 4,
                "maxdelqever": 6,
                "numtotaltrades": 18,
                "numtradesopeninlast12m": 1,
                "percentinstalltrades": 56,
                "msincemostrecentinqexcl7days": 4,
                "numinqlast6m": 1,
                "numinqlast6mexcl7days": 1,
                "netfractionrevolvingburden": 93,
                "netfractioninstallburden": 72,
                "numrevolvingtradeswbalance": 5,
                "numinstalltradeswbalance": 3,
                "numbank2natltradeswhighutilization": 1,
                "percenttradeswbalance": 100
            },
            "cust_id": 19
        }'
```