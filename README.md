# Serverless Amazon Bedrock FastAPI

A practical example of building a chatbot service using Amazon Bedrock.

The service exposes a REST API backed by Python and FastAPI, which can be embedded as a chatbot engine for your front-ends. For example, it can be used in the [`react-tailwind-chatbot-client`](https://github.com/mrnexeon/react-tailwind-chatbot-client) that is the part of this project.

<br/>
<p align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="docs/diagram-dark.png">
        <source media="(prefers-color-scheme: light)" srcset="docs/diagram.png">
        <img alt="Service Architecture Diagram" width="60%">
    </picture>
</p>
<br/>

Serverless architecture of the service allows you to pay for the usage as you go. Amazon Bedrock LLM models charge per tokens, AWS Lambda charges per request.

The API retains chat history by storing each new chat session in DynamoDB and associating sessions with an ID. Using the ID, users can reference the context of previous messages.

Additionally, each new chat session receives a short title that gives an idea about the topic.

## Getting Started

Projects with `boto3` usually require configured AWS credentials. You can install the AWS CLI and set up an AWS profile on your machine to make the project work locally. Refer to the [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and the [AWS CLI Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) for more details.

Otherwise, the SAM project should automatically create the necessary roles to access AWS resources when it comes to deployment. Refer to the [Deployment](#deployment) section for more details.

1. **Clone the repository:**
    ```bash
    git clone https://github.com/mrnexeon/amazon-bedrock-fastapi.git
    ```

2. **Set up the virtual environment:**
    It is recommended to set up a Python virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `.\venv\Scripts\activate`
    ```

3. **Install dependencies:**
    It is recommended to setup the Python virtual enviroment.
    ```bash
    python3 -m pip install -r app/requirements.txt
    ```

4. **Launch the server:**
    ```bash
    fastapi dev
    ```

5. **Test the API:**
    Open your browser and go to http://127.0.0.1:8000/docs to access the interactive API documentation provided by FastAPI Swagger UI.

## Deployment

The service uses AWS SAM to deploy the API as a serverless AWS Lambda function. SAM is an extension of the AWS CLI that adds functionality for deploying applications and services. The Lambda function resource is defined in the `template.yaml` file in this project.

1. **Install AWS CLI:**
    Follow the instructions to install the AWS CLI from [this link](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

2. **Configure AWS CLI:**
    Refer to the [AWS CLI Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) to configure your AWS CLI.

3. **Install SAM CLI:**
    Follow the instructions to install the SAM CLI from [this link](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html).

4. **Request Access to Amazon Bedrock Foundation Models:**
    Navigate to the [Amazon Bedrock Getting Started Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html#getting-started-model-access).
    Follow the instructions on the page to request access to the following models:
    - Amazon Titan Text G1 - Lite
    - Amazon Titan Text G1 - Express
    - Mistral AI Mistral Large
    - Mistral AI Mistral Small

5. **Build the Service:**
    Open your shell and run:
    ```bash
    sam build
    ```

6. **Deploy the Service:**
    In your shell, run:
    ```bash
    sam deploy --guided
    ```

7. Watch out in the SAM deployment logs for the URL endpoints, e.g.:

    ```bash
    Key                 Endpoint                                                                                     
    Description         URL of the REST API endpoint                                                                 
    Value               https://mf6fo...pztt.lambda-url.us-east-1.on.aws/                        

    Key                 RestApiDocs                                                                                  
    Description         Swagger UI REST API documentation                                                            
    Value               https://mf6fo...pztt.lambda-url.us-east-1.on.aws/docs
    ```