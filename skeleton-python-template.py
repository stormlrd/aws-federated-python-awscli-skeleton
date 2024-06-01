"""
name: skeleton-python-template.py
ver: 1.00
author: Paul Dunlop + AI
purpose:
Primary use case for this script is making python use the aws cli for API calls, not the boto3 library... 
why? why not! this is one way to skin a cat eh.

note: requires external tool called aws-federated-headless-login which is a go app using rod for headless browser automation
"""

# Set up imports
import configparser
import os
import sys
import subprocess
from pathlib import Path

# Path to the AWS CLI Config
aws_config_file = Path.home() / '.aws' / 'config'
print ("Using config file located: ",aws_config_file)

# read in the aws config file storing only profile name and account id for later lookups if needed
def read_aws_config(file_path):
    """
    Reads the AWS CLI configuration file and returns a dictionary of profiles.
    Each profile stores the profile name and account ID found in the sso_account_id parameter.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        return "The AWS CLI config file does not exist."

    # Create a ConfigParser object
    config = configparser.ConfigParser()
    config.read(file_path)

    # Initialize a dictionary to store profiles
    profiles_dict = {}

    # Iterate through the sections (profiles) in the config file
    for section in config.sections():
        # Check if 'sso_account_id' is in the section
        if 'sso_account_id' in config[section]:
            # Extract the profile name and account ID
            profile_name = section.split(' ')[-1]  # Get the last element after splitting
            account_id = config[section]['sso_account_id']
            # Add to the dictionary, ensuring profile_name is a string
            profiles_dict[str(profile_name)] = account_id

    return profiles_dict

# allows you to specify a profile name and get the aws account id it relates too based on the cli config param for sso_account_id
def lookup_profile_by_account_id(profiles_dict, account_id):
    """
    Looks up the profile name given an account ID.
    Returns the profile name if found, otherwise returns a message stating not found.
    """
    # Iterate through the dictionary to find the matching account ID
    for profile_name, acc_id in profiles_dict.items():
        if acc_id == account_id:
            return profile_name
    return "Profile not found for the given account ID."

# logs into all profiles using headless browser automation via external app called aws-federated-headless-login made with go using rod for browser automation
def login_to_profiles(profiles_dict):
    sso_cache_path = os.path.expanduser('~/.aws/sso/cache/')

    # loop through each profile checking if they are logged on or not, and for a profile called primary which gets showen for login input
    for profile in profiles_dict.items():
        profile_name = profile[0]
        #print("Profile Name Found:",profile_name)
        print(f'Checking login status of Profile {profile_name}.')
        
        try:
            # Try to get the caller identity using the profile to see if they are already logged on and skip
            subprocess.run(['aws', 'sts', 'get-caller-identity', '--profile', profile_name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f'Profile {profile_name} is logged in.')
        except subprocess.CalledProcessError:
            print(f'Profile {profile_name} is not logged in. Attempting to log in...')
            try:
                # If the profile is not logged in, initiate SSO login
                # Check if profile is primary which should be our first time to login, which means username + password + MFA by hand...
                if profile_name.lower() == "primary":
                    show_param = "true" 
                else:
                    show_param = "false"

                # Construct the AWS SSO login command
                aws_sso_login_command = ["aws", "sso", "login", "--profile", profile_name, "--no-browser"]
                
                # Construct the aws-federated-headless-login command with the appropriate show parameter
                headless_sso_command = ["./aws-federated-headless-login", f"-show={show_param}"]
                
                # Check if the aws-federated-headless-login file exists
                if not os.path.exists("./aws-federated-headless-login"):
                    print("Error: aws-federated-headless-login script does not exist. Fatal issue! exiting...")
                    sys.exit(1)
                
                # Run the AWS SSO login command and pipe the output to the aws-federated-headless-login command
                aws_sso_login_process = subprocess.Popen(aws_sso_login_command, stdout=subprocess.PIPE)
                subprocess.run(headless_sso_command, stdin=aws_sso_login_process.stdout)
                aws_sso_login_process.stdout.close()
            except subprocess.CalledProcessError as login_error:
                print(f'Failed to login profile {profile_name}: {login_error}')
            #print(f'Profile {profile_name} is not logged in. Initiating SSO login...')
            #subprocess.run(['aws', 'sso', 'login', '--profile', profile_name])

#########################################################
#### MAIN CODE
#########################################################
# read in the profiles
profiles = read_aws_config(aws_config_file)

# log into all the profiles found using primary as the one that you need to enter your userid + password + mfa manually for security
login_to_profiles(profiles)

# Add your code here using profiles as the dict to let you loop thru each "account" to make your API calls now that
# you are logged in.

# example code
for profile_name in profiles:
    try:
        print(f"Listing S3 buckets for profile: {profile_name}")
        result = subprocess.run(['aws', 's3', 'ls', '--profile', profile_name], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Failed to list S3 buckets for profile {profile_name}: {e}")