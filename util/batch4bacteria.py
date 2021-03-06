#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import tempfile
import subprocess
import shlex
import os
import datetime

import tools

# To do IS element prediction before summarizing prediction if PREDICT = 1
#PREDICT = 1
# To summarize prediction based on the previous prediction to save time if PREDICT = 0
PREDICT = 0

python3 = '/usr/local/bin/python3'
#cmd = 'isPredict.py'
cmd = 'pred.py'


def batch(args):
	dnaListFile4orgs = args['fileList']
	print('Batch running begins at', datetime.datetime.now().ctime())

	# dnaFiles: [(file, org), ..., (file, org)]
	dnaFiles = tools.rdDNAlist(dnaListFile4orgs)
	# file4orgs: {org: files, ..., org: files}
	# files: [file4fileid, ..., file4fileid]
	file4orgs = {}
	for fileOrg in dnaFiles:
		file, org = fileOrg
		if org not in file4orgs.keys():
			file4orgs[org] = []
		file4orgs[org].append(file)
	
	print('number of organisms to process:', len(file4orgs), datetime.datetime.now().ctime())

	if PREDICT == 1:
		'''
		dir2proteome4org = '/home/data/insertion_sequence/output4FragGeneScan1.19_illumina_5_benchmark'
		dir2hmmsearchResults = '/home/data/insertion_sequence/output4hmmsearch_illumina_5_benchmark_cdhit30'
		'''
		dir2proteome4org = '/home/data/insertion_sequence/output4FragGeneScan1.19_illumina_5'
		dir2hmmsearchResults = '/home/data/insertion_sequence/output4hmmsearch_illumina_5_cdhit30'
		cmdargs = [python3, cmd, '', dir2proteome4org, dir2hmmsearchResults]
		# summarize IS elements in each genome DNA and each organism 
		for org in file4orgs.keys():
			files = file4orgs[org]
			fp = tempfile.NamedTemporaryFile(delete=False)
			fp.write(('\n'.join(files)+'\n').encode())
			fp.close()
			cmdargs[2] = fp.name
			cmdline = ' '.join(cmdargs)
			callcmd = shlex.split(cmdline)
			#subprocess.check_call(callcmd, shell=False, universal_newlines=False, stdout=subprocess.DEVNULL)
			#subprocess.check_call(callcmd, shell=False, universal_newlines=False)
			subprocess.check_output(callcmd, shell=False, universal_newlines=False, stderr=subprocess.STDOUT)
			os.remove(fp.name)
			print(org, 'was processed')

	# get summarization of IS elements for each organism and write summarization 
	# for all organisms into file 'is.sum'.

	dir4prediction = args['dir2prediction']
	# write 'organism.sum' in each organism directory
	mDNA, dir4data = tools.fnaFileList2mDNA(dnaListFile4orgs)
	tools.sum4org(mDNA, dir4data, dir4prediction=dir4prediction)

	# prepare and write 'is.sum' in current directory
	sum4is = {}
	for org in file4orgs.keys():
		sumFileByOrg = os.path.join(dir4prediction, org, 'organism.sum')
		if os.path.isfile(sumFileByOrg) and os.stat(sumFileByOrg).st_size > 0:
			sum4is[org] = tools.getSumFull(sumFileByOrg, org)
		#if org in sum4is.keys() and len(sum4is[org]) > 0:
		#	print(org, 'will be integrated into total summarization')
	if len(sum4is) > 0:
		tools.output4sumFull(sum4is, 'is.sum')

	'''
	# summarize genome DNAs
	sum4is4genome = {}
	for org in file4orgs.keys():
		sumFileByOrg = os.path.join(dir4prediction, org, 'organism4genome.sum')
		if os.path.isfile(sumFileByOrg) and os.stat(sumFileByOrg).st_size > 0:
			sum4is4genome[org] = tools.getSumFull(sumFileByOrg, org)
		#if org in sum4is4genome.keys() and len(sum4is4genome[org]) > 0:
		#	print(org, 'will be integrated into total summarization for genome DNAs')
	if len(sum4is4genome) > 0:
		tools.output4sumFull(sum4is4genome, 'is4genome.sum')

	# summarize plasmid DNAs
	sum4is4plasmid = {}
	for org in file4orgs.keys():
		sumFileByOrg = os.path.join(dir4prediction, org, 'organism4plasmid.sum')
		if os.path.isfile(sumFileByOrg) and os.stat(sumFileByOrg).st_size > 0:
			sum4is4plasmid[org] = tools.getSumFull(sumFileByOrg, org)
		#if org in sum4is4plasmid.keys() and len(sum4is4plasmid[org]) > 0:
		#	print(org, 'will be integrated into total summarization for plasmid DNAs')
	if len(sum4is4plasmid) > 0:
		tools.output4sumFull(sum4is4plasmid, 'is4plasmid.sum')

	# summarize phage DNAs
	sum4is4phage = {}
	for org in file4orgs.keys():
		sumFileByOrg = os.path.join(dir4prediction, org, 'organism4phage.sum')
		if os.path.isfile(sumFileByOrg) and os.stat(sumFileByOrg).st_size > 0:
			sum4is4phage[org] = tools.getSumFull(sumFileByOrg, org)
		#if org in sum4is4phage.keys() and len(sum4is4phage[org]) > 0:
		#	print(org, 'will be integrated into total summarization for phage DNAs')
	if len(sum4is4phage) > 0:
		tools.output4sumFull(sum4is4phage, 'is4phage.sum')
	'''
	print('Batch running finishes at', datetime.datetime.now().ctime())
	
if __name__ == "__main__":
	descriptionStr = 'Summarize prediction results of IS elements in each organism and all organisms'
	parser = argparse.ArgumentParser(description = descriptionStr)
	helpStr = 'input file containing NCBI genome fasta files, one file per line, e.g. bacteria.fna.list'
	parser.add_argument('fileList', help = helpStr)
	helpStr = 'directory holding the results of IS prediction, one organism per sub-directory, e.g. /home/data/insertion_sequence/results4MGEScan-IS/prediction'
	parser.add_argument('dir2prediction', help = helpStr)
	args = parser.parse_args()
	args4batch = {
			'fileList':		args.fileList,
			'dir2prediction':	args.dir2prediction,
			}
	batch(args4batch)
