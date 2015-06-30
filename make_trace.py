#!/usr/bin/python

from __future__ import print_function

def main():
	f = file('./synthetic_traces/stall_example.down', 'w')
	for x in range(0, 3000):
		print(str(x), file=f)
	for x in range(3000, 10000, 50):
		print(str(x), file=f)


if __name__ == '__main__':
  main()