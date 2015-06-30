#!/usr/bin/python

from __future__ import print_function
import os

def main():
	if(os.path.exists("./synthetic_traces/stall_example.down")):
		os.system("rm ./synthetic_traces/stall_example.down")
	f = file('./synthetic_traces/stall_example.down', 'w')
	for x in range(0, 4000):
		print(str(x), file=f)
	for x in range(4000, 20050, 50):
		print(str(x), file=f)
	for x in range(20050, 100000):
		print(str(x), file=f)

if __name__ == '__main__':
  main()