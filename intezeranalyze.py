# Example Class
import requests
import logging
import json
import os
import time

# Establish Logging.
logging.basicConfig()
logger = logging.getLogger('intezeranalyze')


class intezerAnalyze():
    def __init__(
        self,
        api_key,
        # Replace the base url to the url that you need
        base_url='https://analyze.intezer.com/api',
        prettyPrint=False
    ):
        """
        Example Python Wrapper.

        Available Functions
        - test_connect              Provides a method to test connectivity
        - analyze_by_sha256         Create Analysis By SHA256
        - get_analysis              Get Analysis Result
        - create_analysis           Detonate file

        Usage:

        s = intezerAnalyze(api_key='yourapikey')
        s.function_name(valid_variables)
        """

        # Create Requests Session
        self.session = requests.session()
        # Add API Key to Header
        # Create Base URL variable to allow for updates in the future
        self.base_url = base_url
        # Create API Key variable to pass into each request
        self.api_key = api_key
        # Create Pretty Print variable
        self.prettyPrint = prettyPrint

        # Check to see if API Key is present
        if self.api_key is None:
            raise Exception("No API Key present")

        # Create endpoint
        endpoint = '{}/is-available'.format(self.base_url)

        # Initiate Ping to Example Endpoint
        self.ping = self.session.get(endpoint)

        # Request failed returning false and logging an error
        if self.ping.status_code != 200:
            logger.error(
                "Error connecting to Intezer Analyze code, error message: {}".format(
                    self.ping.text))

    def parse_output(self, input):
        # If prettyPrint set to False
        if self.prettyPrint is False:
            return json.dumps(input)
        # If prettyPrint set to True
        elif self.prettyPrint is True:
            print json.dumps(input, indent=4)

    def check_file(self, file):
        # Check if the file exists first
        if os.path.exists(file):
            # Check if the file is an approved format
            if os.path.getsize(file) / 1024 / 1024 < 19:
                return True
            else:
                logger.warning("check_file: File is over 20mb")
                return "File is over 20mb"
        else:
            logger.warning("check_file: File does not exist")
            return "File does not exist"

    def test_connect(self):
        """
        Function:   Test ping to Example API

        No parameters:

        Usage:
        s = intezerAnalyze(api_key='yourapikey')
        s.test_connect()
        """

        endpoint = '{}/is-available'.format(self.base_url)
        # Make connection to the ping endpoint
        r = self.session.get(endpoint)
        # Specify Output as JSON
        output = r.json()
        # If the request is successful
        if r.status_code == 200:
            return True
        # Request failed returning false and logging an error
        else:
            logger.warning(
                "test_connect:Error with query to intezerAnalyze, error message: {}".format(
                    output['message']))
            return False

    def analyze_by_sha256(self, sha256):
        """
        Function:   Check if a SHA256 hash is present in the Intezer Database

        :param sha256: Required - SHA256 hash

        Usage:
        s = intezerAnalyze(api_key='yourapikey')
        s.analyze_by_sha256("4e553bce90f0b39cd71ba633da5990259e185979c2859ec2e04dd8efcdafe356")
        """
        # URL that we are querying
        endpoint = '{}/v1-2/analyze-by-sha256'.format(self.base_url)

        params = {
            'sha256': sha256,
            'api_key': self.api_key
        }

        # Create a request
        r = self.session.post(endpoint, json=params)
        # Format the response in json
        output = r.json()
        # If the request is successful
        if r.status_code == 200:
            return self.parse_output(r.json())
        # Request failed returning false and logging an error
        else:
            # Write a warning to the console
            logger.warning(
                "analyze_by_sha256:Error with query to intezerAnalyze, error message: {}".format(
                    output['message']))
            return False

    def create_analysis(self, file_name):
        """
        Function:   Consists of 2 different requests:
                    - Create an analysis request and upload a file. Receive a URL for retrieving the result.
                    - Get the analysis request status or result (using the URL received from the previous request).

        :param file_name: Required - The file you want to pass to the create_analysis function

        Usage:
        s = intezerAnalyze(api_key='yourapikey')
        s.create_analysis("./filename.exe")
        """
        # URL that we are querying
        endpoint = '{}/v1-2/analyze?api_key={}'.format(self.base_url, self.api_key)

        # Perform file check
        file_check = self.check_file(file_name)

        # Check file type is correct
        if file_check:
            file_list = {'file': open(file_name, 'rb')}
        else:
            logger.warning(
                "create_analysis:Error with File")
            return file_check
        # Create a request
        r = self.session.post(endpoint, files=file_list)

        # Format the response in json
        output = r.json()

        # If the request is successful
        if r.status_code == 201:
            return self.parse_output(output)

        # Request failed returning false and logging an error
        else:
            # Write a warning to the console
            logger.warning(
                "create_analysis:Error with query to intezerAnalyze, error message: {}".format(r.text))
            return False

    def get_analysis(self, analysis_id):
        """
        Function:   Get the analysis result from either sha256 hash or create_analysis

        Usage:
        s = intezerAnalyze(api_key='yourapikey')
        s.get_analysis("1958f64d-7cc8-49b6-9a11-ca86b25569d7")
        """
        # URL that we are querying
        endpoint = '{}/v1-2/analyses/{}?api_key={}'.format(self.base_url, analysis_id, self.api_key)
        # Create a request
        r = self.session.post(endpoint)
        # Format the response in json
        output = r.json()
        # If the request is successful
        if r.status_code == 202:
            # Report is Queued or In Progress
            i = 0
            # While the result is not succeeded or 50 seconds has not elapsed
            while i < 10 and r.status_code != 200:
                # Sleep 5 seconds
                time.sleep(60)
                r = self.session.post(endpoint)
                i += 1
                if i == 10:
                    logger.warning("get_analysis: Timed out waiting for response. Slept for 10 minutes")
                    return False

        if r.status_code == 200:
            # Report is Available
            return self.parse_output(output)

        # Request failed returning false and logging an error
        else:
            # Write a warning to the console
            logger.warning("get_analysis:Error with query to intezerAnalyze, error message: {}".format(r.text))
            return False
