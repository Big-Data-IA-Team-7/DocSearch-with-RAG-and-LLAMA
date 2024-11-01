import boto3

# Define the parameter names to be retrieved
parameter_names = [
    'LLAMA_CLOUD_API_KEY',
    'ACCESS_KEY_ID_AWS',
    'SECRET_ACCESS_KEY_AWS',
    'S3_BUCKET_NAME_AWS'
    'OPENAI_API_KEY',
    'RAG_API_URL',
    'NVIDIA_API_KEY',
    'PINECONE_API_KEY',
    'SNOWFLAKE_USER',
    'SNOWFLAKE_PASSWORD',
]

parameter_names_second = [
    'SNOWFLAKE_ACCOUNT',
    'SNOWFLAKE_WAREHOUSE',
    'SNOWFLAKE_DATABASE',
    'SNOWFLAKE_SCHEMA',
    'SNOWFLAKE_ROLE',
]

# Create an SSM client
ssm_client = boto3.client('ssm', region_name='us-east-1')  # Replace 'your-region' with your AWS region

# Retrieve parameters from AWS SSM Parameter Store
response = ssm_client.get_parameters(
    Names=parameter_names,
    WithDecryption=True  # Ensure secure strings are decrypted
)

response_two = ssm_client.get_parameters(
    Names=parameter_names_second,
    WithDecryption=True
)

# Extract parameters from the response
parameters = response.get('Parameters', [])
parameters_dict = {param['Name']: param['Value'] for param in parameters}


parameters_two = response_two.get('Parameters', [])
parameters_dict_two = {param['Name']: param['Value'] for param in parameters_two}

# Store the values in variables
LLAMA_CLOUD_API_KEY = parameters_dict.get('LLAMA_CLOUD_API_KEY')
ACCESS_KEY_ID_AWS = parameters_dict.get('ACCESS_KEY_ID_AWS')
SECRET_ACCESS_KEY_AWS = parameters_dict.get('SECRET_ACCESS_KEY_AWS')
S3_BUCKET_NAME_AWS = parameters_dict.get('S3_BUCKET_NAME_AWS')
OPENAI_API_KEY = parameters_dict.get('OPENAI_API_KEY')
FAST_API_DEV_URL = parameters_dict.get('RAG_API_URL')
NVIDIA_API_KEY = parameters_dict.get('NVIDIA_API_KEY')
PINECONE_API_KEY = parameters_dict.get('PINECONE_API_KEY')
SNOWFLAKE_USER = parameters_dict.get('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = parameters_dict.get('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ACCOUNT = parameters_dict_two.get('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_WAREHOUSE = parameters_dict_two.get('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = parameters_dict_two.get('SNOWFLAKE_DATABASE')
SNOWFLAKE_SCHEMA = parameters_dict_two.get('SNOWFLAKE_SCHEMA')
SNOWFLAKE_ROLE = parameters_dict_two.get('SNOWFLAKE_ROLE')