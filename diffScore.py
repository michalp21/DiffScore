import sys, getopt
import itertools

listr = []
listh = []
totalScore = 0
verbose = False

def readwords(file_object):
    byte_stream = itertools.groupby(
    	itertools.takewhile(lambda c: bool(c),
    		itertools.imap(file_object.read,
    			itertools.repeat(1))), str.isspace)

    return ("".join(group) for pred, group in byte_stream if not pred)

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + " " + result
            x -= 1
            y -= 1
    return result

def myDiffHelper (startBoundR, startBoundH, endBoundR, endBoundH):
	r_temp = ""
	h_temp = ""

	for index_r in range(startBoundR, endBoundR):
		r_temp += listr[index_r] + " "
	for index_h in range(startBoundH, endBoundH):
		h_temp += listh[index_h] + " "
	if (verbose):
		print "  [ R ] " + r_temp + ""
		print "  [ H ] " + h_temp + "\n"
	global totalScore
	totalScore += levenshtein(r_temp[:-1], h_temp[:-1])

def myDiff(r, h):
	lenFileR = -1
	anchors = []

	with open(r, 'r') as f:
		for w in readwords(f):
			myString = str(w).replace('\x00', '')
			if (myString != ''):
				listr.append(myString)
	with open(h, 'r') as f:
		for w in readwords(f):
			myString = str(w).replace('\x00', '')
			if (myString != ''):
				listh.append(myString)

	for w in listr:
		lenFileR += len(w) + 1

	if (verbose):
		print "\n Ref words: " + str(listr)
		print "\n Hyp words: " + str(listh)
 
 	#find a longest common substring
	anchors = lcs(listr,listh).split()
	if(verbose):
		print "\n Anchors: " + str(anchors) + "\n"

	#IF NOT ANCHORS
	if (len(anchors) == 0):
		myDiffHelper(0, 0, len(listr), len(listh))
	else:
		#BEFORE FIRST ANCHOR
		firstAnchorInR = listr.index(anchors[0])
		firstAnchorInH = listh.index(anchors[0])

		myDiffHelper(0, 0, firstAnchorInR, firstAnchorInH)

		for i, _ in enumerate(listr):
			if(i<firstAnchorInR):
				listr[i] = None
		for i, _ in enumerate(listh):
			if(i<firstAnchorInH):
				listh[i] = None

		#ANCHORS
		for anchorIndex in range(len(anchors)-1):
			r1 = listr.index(anchors[anchorIndex])
			r2 = listr.index(anchors[anchorIndex+1])
			h1 = listh.index(anchors[anchorIndex])
			h2 = listh.index(anchors[anchorIndex+1])

			if (r2 - r1 > 1 or h2 - h1 > 1):
				myDiffHelper(r1+1, h1+1, r2, h2)

			for i, _ in enumerate(listr):
				if(i>=r1 and i<r2):
					listr[i] = None
			for i, _ in enumerate(listh):
				if(i>=h1 and i<h2):
					listh[i] = None

		#AFTER LAST ANCHOR
		lastAnchorInR = listr.index(anchors[len(anchors) - 1])
		lastAnchorInH = listh.index(anchors[len(anchors) - 1])
		
		myDiffHelper(lastAnchorInR, lastAnchorInH, len(listr), len(listh))

	print "% Anchor:", len(anchors)/float(len(listr))
	print "% Diff:  ", totalScore/float(lenFileR)


def main(argv):
	hypfile = ''
	reffile = ''
	try:
		opts, args = getopt.getopt(argv,"vh:r:")
	except getopt.GetoptError:
		print 'Requires: -r <ref file> -h <hyp file>'
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--hfile"):
			if (arg[-3:] != "txt"):
				print 'txt file required'
				sys.exit(2)
			hypfile = arg
		elif opt in ("-r", "--rfile"):
			if (arg[-3:] != "txt"):
				print 'txt file required'
				sys.exit(2)
			reffile = arg
		if opt in ("-v", "--verbose"):
			global verbose
			verbose = True


	print '"' + reffile + '" <-- "' + hypfile + '"'

	myDiff(reffile, hypfile)

if __name__ == "__main__":
	main(sys.argv[1:])