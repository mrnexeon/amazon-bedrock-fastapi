# Amazon Bedrock FastAPI

Practical example for building REST API on top of the Amazon Bedrock service.

## Getting Started

1. **Clone the repository:**
    ```
    git clone https://github.com/mrnexeon/amazon-bedrock-fastapi.git
    ```
2. **Set up the virtual environment:**
    It is recommended to set up a Python virtual environment.
    ```
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install dependencies:**
    It is recommended to setup the Python virtual enviroment.
    ```
    python3 -m pip install -r requirements.txt
    ```

3. **Launch the server:**
    ```
    fastapi run app/main.py
    ```

4. Test the api:
    Open your browser and go to http://127.0.0.1:8000/docs to access the interactive API documentation provided by FastAPI Swagger UI.