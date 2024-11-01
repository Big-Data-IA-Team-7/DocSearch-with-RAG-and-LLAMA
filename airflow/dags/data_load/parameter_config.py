import boto3
from botocore.exceptions import ClientError

# Define the parameter names to be retrieved
parameter_names = [
    'ACCESS_KEY_ID_AWS',
    'SECRET_ACCESS_KEY_AWS',
    'S3_BUCKET_NAME_AWS_3',
    'SNOWFLAKE_ACCOUNT',
    'SNOWFLAKE_DATABASE',
    'SNOWFLAKE_PASSWORD',
    'SNOWFLAKE_ROLE',
    'SNOWFLAKE_SCHEMA',
    'SNOWFLAKE_USER',
    'SNOWFLAKE_WAREHOUSE'
]

# Create an SSM client
ssm_client = boto3.client('ssm', region_name='us-east-1')  # Replace 'us-east-1' with your AWS region

# Split the parameters into batches
batch = ['ACCESS_KEY_ID_AWS', 'SECRET_ACCESS_KEY_AWS', 'S3_BUCKET_NAME_AWS_3','SNOWFLAKE_ACCOUNT',
    'SNOWFLAKE_DATABASE',
    'SNOWFLAKE_PASSWORD',
    'SNOWFLAKE_ROLE',
    'SNOWFLAKE_SCHEMA',
    'SNOWFLAKE_USER',
    'SNOWFLAKE_WAREHOUSE']

# Fetch first batch of parameters
response_1 = ssm_client.get_parameters(Names=batch, WithDecryption=True)
parameters_1 = {param['Name']: param['Value'] for param in response_1['Parameters']}


# Store the values in variables
AWS_ACCESS_KEY_ID = parameters_1.get('ACCESS_KEY_ID_AWS')
AWS_SECRET_ACCESS_KEY = parameters_1.get('SECRET_ACCESS_KEY_AWS')
AWS_S3_BUCKET_NAME = parameters_1.get('S3_BUCKET_NAME_AWS_3')
SNOWFLAKE_ACCOUNT = parameters_1.get('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_DATABASE = parameters_1.get('SNOWFLAKE_DATABASE')
SNOWFLAKE_PASSWORD = parameters_1.get('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ROLE = parameters_1.get('SNOWFLAKE_ROLE')
SNOWFLAKE_SCHEMA = parameters_1.get('SNOWFLAKE_SCHEMA')
SNOWFLAKE_USER = parameters_1.get('SNOWFLAKE_USER')
SNOWFLAKE_WAREHOUSE = parameters_1.get('SNOWFLAKE_WAREHOUSE')
