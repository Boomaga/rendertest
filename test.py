#!/usr/bin/python3

import glob
import sys
import os
import os.path
import shutil
import subprocess
import hashlib

BOOMAGAMERGER="./boomagamerger"
OUT_DIR="out"


def sha256Sum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

class CheckError(BaseException):
	pass

def testFile(pdfFile):
	name=os.path.splitext(os.path.basename(pdfFile))[0]
	outDir = OUT_DIR + "/" + name
	resultFile = "%s/result.pdf" % outDir

	try:
		os.makedirs(outDir)
	except FileExistsError:
		pass

	myEnv = os.environ.copy()
	myEnv["BOOMAGAMERGER_DEBUGPAGES"] = "YES"

	FNULL = open(os.devnull, 'w')
	subprocess.check_call([
		BOOMAGAMERGER,
		pdfFile,
		"0", "0",
		resultFile
		],
		stdout=FNULL,
		env=myEnv)


	subprocess.check_call([
		"gs",
		"-q",
		"-sDEVICE=png16m",
		"-o", ("%s/%%03d_expected.png" % outDir),
		#"-r144",
		pdfFile
		])


	subprocess.check_call([
		"gs",
		"-q",
		"-sDEVICE=png16m",
		"-o", ("%s/%%03d_result.png" % outDir),
		#"-r144",
		resultFile
		])

	for expected in glob.glob("%s/*_expected.png" % outDir):
		#if sha256Sum(expected)
		result = expected[:-13] + "_result.png"
		if sha256Sum(expected) != sha256Sum(result):
			print("Compared files are not the same:")
			print("  expected: ", expected)
			print("  result:   ", result)
			raise CheckError


def main():
	if not os.path.isfile(BOOMAGAMERGER):
		print("Error: boomagamerger not foud")
		sys.exit(1)

	files = []
	if len(sys.argv) > 1:
		files = sys.argv[1:]
	else:
		files = glob.glob('*.pdf')
		files.sort()


	try:
		shutil.rmtree(OUT_DIR)
	except FileNotFoundError:
		pass


	okCnt=0
	errCnt=0
	for inFile in files:
		print(inFile)
		try:
			testFile(inFile)
		except CheckError as e:
			print("  FAIL!")
			errCnt+=1
		else:
			print("  PASS")
			okCnt+=1
		print("")

	print("-----------------------------------------------")
	print("Totals: %d passed, %d failed" % (okCnt, errCnt))


if __name__ == "__main__":
    main()
