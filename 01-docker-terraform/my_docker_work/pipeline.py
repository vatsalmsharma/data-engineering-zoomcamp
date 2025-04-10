import sys
import pandas as pd 


print(sys.argv)
date = sys.argv[1]   # First argument [0] is the file name

print(f'sample file to invoke from docker on {date}')