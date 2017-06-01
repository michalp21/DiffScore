import sys, getopt
import itertools

listr = []
listh = []
scores = []

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

def LCS(X, Y):
    m = len(X)
    n = len(Y)
    # An (m+1) times (n+1) matrix
    C = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if X[i-1] == Y[j-1]: 
                C[i][j] = C[i-1][j-1] + 1
            else:
                C[i][j] = max(C[i][j-1], C[i-1][j])
    return C

def backTrack(C, X, Y, i, j):
    if i == 0 or j == 0:
        return ""
    elif X[i-1] == Y[j-1]:
        return backTrack(C, X, Y, i-1, j-1) + " " + X[i-1]
    else:
        if C[i][j-1] > C[i-1][j]:
            return backTrack(C, X, Y, i, j-1)
        else:
            return backTrack(C, X, Y, i-1, j)

def myDiffHelper (startBoundR, startBoundH, endBoundR, endBoundH):
	r_temp = ""
	h_temp = ""

	for index_r in range(startBoundR, endBoundR):
		r_temp += listr[index_r] + " "
	for index_h in range(startBoundH, endBoundH):
		h_temp += listh[index_h] + " "
	print "  [ R ] " + r_temp
	print "  [ H ] " + h_temp + "\n"
	scores.append(levenshtein(r_temp[:-1], h_temp[:-1]))

def myDiff(r, h):
	lenFileR = -1
	anchors = []
	totalScore = 0

	with open(r, 'r') as f:
		for w in readwords(f):
			listr.append(str(w))
	with open(h, 'r') as f:
		for w in readwords(f):
			listh.append(str(w))

	for w in listr:
		lenFileR += len(w) + 1

	print "\n Ref words: " + str(listr)
	print "\n Hyp words: " + str(listh)
 
 	#find a longest common substring
	anchors = backTrack(LCS(listr, listh), listr, listh, len(listr), len(listh)).split()
	print "\n Anchors: " + str(anchors) + "\n"

	#IF NOT ANCHORS
	if (len(anchors) == 0):
		myDiffHelper(0, 0, len(listr), len(listh))

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
		else:
			scores.append(0)

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

	for s in scores:
		totalScore += s

	print "% Anchor:", len(anchors)/float(len(listr))
	print "% Diff:  ", totalScore/float(lenFileR)


def main(argv):
	hypfile = ''
	reffile = ''
	try:
		opts, args = getopt.getopt(argv,"h:r:",["hfile=","rfile="])
	except getopt.GetoptError:
		print 'test.py -i <inputfile> -o <outputfile>'
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

	print 'Hypothesis file is "', hypfile
	print 'Reference file is "', reffile

	myDiff(hypfile, reffile)

if __name__ == "__main__":
	main(sys.argv[1:])