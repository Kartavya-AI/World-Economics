import os
from dotenv import load_dotenv
from crewai_tools import SerperDevTool
load_dotenv()
# os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')

# inititlaize the tool for internet searching capabilities
serper_tool = SerperDevTool()


