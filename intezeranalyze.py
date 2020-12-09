import requests, logging, json, os, time
logging.basicConfig()
logger = logging.getLogger('intezeranalyze')
class intezerAnalyze:
    def __init__(self, api_key, base_url='https://analyze.intezer.com/api', prettyPrint=False):
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
        self.session = requests.session()
        self.base_url = base_url
        self.api_key = api_key
        self.prettyPrint = prettyPrint
        if self.api_key is None:
            raise Exception('No API Key present')
        endpoint = ('{}/is-available').format(self.base_url)
        self.ping = self.session.get(endpoint)
        if self.ping.status_code != 200:
            logger.error(('test_connect: Error with query to intezerAnalyze, status code: {}, error message: {}').format(self.ping.status_code, self.ping.text))
        return
    def exceptionRaise(self, message):
        problem_message = ('Found Problem: {}').format(message)
        raise Exception(problem_message)
    def parse_output(self, input):
        if self.prettyPrint is False:
            return json.dumps(input)
        if self.prettyPrint is True:
            print json.dumps(input, indent=4)
    def check_file(self, file):
        if os.path.exists(file):
            if os.path.getsize(file) / 1024 / 1024 < 19:
                return True
            logger.warning('check_file: File is over 20mb')
            self.exceptionRaise('File is over 20mb')
        else:
            logger.warning('check_file: File does not exist')
            self.exceptionRaise('File does not exist')
    def test_connect(self):
        """
        Function:   Test ping to Example API
        No parameters:
        Usage:
        s = intezerAnalyze(api_key='yourapikey')
        s.test_connect()
        """
        endpoint = ('{}/is-available').format(self.base_url)
        r = self.session.get(endpoint)
        if r.status_code == 200:
            output = r.json()
            if output['is_available']:
                return True
        else:
            logger.warning(('test_connect:Error with query to intezerAnalyze, status code: {}, error message: {}').format(r.status_code, r.text))
            return False
    def analyze_by_sha256(self, sha256):
        """
        Function:   Check if a SHA256 hash is present in the Intezer Database
        :param sha256: Required - SHA256 hash
        Usage:
        s = intezerAnalyze(api_key='yourapikey')
        s.analyze_by_sha256("4e553bce90f0b39cd71ba633da5990259e185979c2859ec2e04dd8efcdafe356")
        """
        endpoint = ('{}/v2-0/analyze-by-hash').format(self.base_url)
        params = {'sha256': sha256,
           'api_key': self.api_key}
        r = self.session.post(endpoint, json=params)
        if r.status_code == 201:
            output = r.json()
            return self.parse_output(output)
        else:
            logger.warning(('analyze_by_sha256:Error with query to intezerAnalyze, error message: {} {}').format(r.text, r.status_code))
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
        endpoint = ('{}/v2-0/analyze').format(self.base_url)
        params = {'api_key': self.api_key}
        file_check = self.check_file(file_name)
        if file_check:
            file_list = {'file': open(file_name, 'rb')}
        else:
            logger.warning(('create_analysis:Error with File - Message: {}').format(file_check))
            return False
        r = self.session.post(endpoint, files=file_list, json=params)
        if r.status_code == 201:
            output = r.json()
            return self.parse_output(output)
        else:
            logger.warning(('create_analysis:Error with query to intezerAnalyze, status code: {}, error message: {}').format(r.status_code, r.text))
            return False
    def get_analysis(self, analysis_id):
        """
        Function:   Get the analysis result from either sha256 hash or create_analysis
        Usage:
        s = intezerAnalyze(api_key='yourapikey')
        s.get_analysis("1958f64d-7cc8-49b6-9a11-ca86b25569d7")
        """
        endpoint = ('{}/v2-0/analyses/{}').format(self.base_url, analysis_id)
        params = {'api_key': self.api_key}
        r = self.session.post(endpoint, json=params)
        if r.status_code == 202:
            output = r.json()
            i = 0
            while i < 10 and r.status_code != 200:
                time.sleep(60)
                r = self.session.post(endpoint)
                i += 1
                if i == 10:
                    logger.warning('get_analysis: Timed out waiting for response. Slept for 10 minutes')
                    return False
        if r.status_code == 200:
            output = r.json()
            return self.parse_output(output)
        else:
            logger.warning(('get_analysis:Error with query to intezerAnalyze, status code: {}, error message: {}').format(r.status_code, r.text))
            return False