# Serverless Amazon Bedrock FastAPI

A practical example of building a REST API on top of the Amazon Bedrock service. This guide demonstrates how to create a serverless REST API for a chatbot using AWS Lambda, FastAPI, and Python to interact with Amazon Bedrock LLM base models. The API retains chat history and context. It allows to describe each new chat with a short title.

## Getting Started

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

3. **Launch the server:**
    ```bash
    fastapi dev
    ```

4. **Test the API:**
    Open your browser and go to http://127.0.0.1:8000/docs to access the interactive API documentation provided by FastAPI Swagger UI.

## Deployment

The service uses AWS SAM to deploy the API as a serverless AWS Lambda function. SAM is an extension of the AWS CLI that adds functionality for deploying applications and services. The Lambda function resource is defined in the template.yaml file in this project.

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