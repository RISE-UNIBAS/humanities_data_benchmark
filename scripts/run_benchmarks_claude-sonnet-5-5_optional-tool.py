import os, sys
sys.path.insert(0, os.getcwd())
from ai_client import claude_client
claude_client.ClaudeClient._output_format_schema = staticmethod(lambda schema: None)
assert "generic_llm_api_client" in claude_client.__file__, claude_client.__file__
import run_benchmarks
run_benchmarks.main(limit_to=["T1870", "T1871", "T1872", "T1873", "T1874", "T1875", "T1876", "T1877", "T1878", "T1879", "T1880", "T1881", "T1882", "T1883", "T1884"], workers=10)
