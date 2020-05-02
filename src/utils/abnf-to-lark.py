#!/usr/bin/python3

import re

def concatGroups(inputList):
	result = []
	for i in inputList:
		r = ""
		for b in i:
			r = r + b
		result.append(r)
	return result


def convertHexBytes(x):
	line = x

	# check if this line even contains a %xAA-like sequence
	if not re.search(RE_ABNF_HEX, line):
		return x

	# add %x where its missing
	# %x1a-AA -> %x1a-%xAA
	outp = re.sub(RE_ABNF_HEX_RANGE_2G, r"\1%x\2", line)

	# making lower case hex characters upper case
	# %x1a -> %x1A
	callback = lambda pat: "%x" + pat.group(1).upper()
	outp = re.sub("%x("+ RE_HEX_DIGITS_LOWER +")", callback, outp)

	# replace % with \
	# %x1A -> \x1A
	outp = re.sub("%(x"+ RE_HEX_DIGITS_UPPER +")", r"\\\1", outp)

	# remove whitespaces between pipes
	# \x1A | \x1B-\xBB  ->  \x1A|\x1B-\xBB
	outp = re.sub(RE_LARK_HEX_OR_RANGE_2G+ r" \| ", r"\1|", outp)

	# encase collection of hex char representations with /[]/
	# \x1A|\x1B-\xBB -> /[\x1A|\x1B-\xBB]/
	outp = re.sub(r"(("+ RE_LARK_HEX_OR_RANGE_2G +"\|?)+)", r"/[\1]/", outp)
	# /[\x21|\x23-\x24|\x26-\x27|\x2B-\x5B|\x5E-\x7A|\x7C-\x7E]+/
	return outp


def convertDecBytes(x):
	line = x

	# check if this line even contains a %xAA-like sequence
	if not re.search(RE_ABNF_DEC, line):
		return x

	# add %x where its missing
	# %d1a-AA -> %d1a-%dAA
	outp = re.sub(RE_ABNF_DEC_RANGE_2G, r"\1%d\2", line)

	# replace % with \
	# %d1A -> \d1A
	outp = re.sub("%(d" + RE_DEC_DIGITS + ")", r"\\\1", outp)

	# remove whitespaces between pipes
	# \d1A | \d1B-\dBB  ->  \d1A|\d1B-\dBB
	outp = re.sub(RE_LARK_DEC_OR_RANGE_2G + r" \| ", r"\1|", outp)

	# encase collection of hex char representations with /[]/
	# \d1A|\d1B-\dBB -> /[\d1A|\d1B-\dBB]/
	outp = re.sub(r"((" + RE_LARK_DEC_OR_RANGE_2G + "\|?)+)", r"/[\1]/", outp)
	# /[\d21|\d23-\d24|\d26-\d27|\d2B-\d5B|\d5E-\d7A|\d7C-\d7E]+/
	return outp

def convertOR(x):
	x = re.sub(matchOR, " | ", x)
	return x


def convertNonTerminals(x):
	rulesWithMinus = re.findall(matchMinusInNT, x)
	rulesWithMinus = concatGroups(rulesWithMinus)
	rulesWithUnderscore = []
	for nt in rulesWithMinus:
		if not matchHexaByteList.match(nt):
			rulesWithUnderscore.append(re.sub(r"\-", "_", nt))

	# Wird hier nach länge sortiert, um replacements die andere beinhalten nicht zu stören
	# Z.B. wird somit eine Zeile mit den Regeln "msg-att" und "msg-att-special"
	# nicht ersetzt durch "msg_att" und "msg_att-special", weil als erstes "msg-att" ersetzt würde, sondern anders herum
	# korrekter weise durch "msg_att" und "msg_att_special", mit unterstrich
	rulesWithMinus.sort(key=lambda s: -len(s))
	rulesWithUnderscore.sort(key=lambda s: -len(s))

	for i in range(len(rulesWithMinus)):
		x = x.replace(rulesWithMinus[i], rulesWithUnderscore[i])
	return x


# Searches literals in a line (input_string) and masks them using RE_LITERALS and LITERAL_MASK
def mask_literals(input_string):
	# iterating through all found literals
	# RE_LITERALS will find multiple groups, as a result, group 0 will be mapped to be literal
	for literal in map(lambda x: x[0], re.findall(RE_LITERALS, input_string)):
		# check if literal is already registered in dictionary
		if literal not in literals_mapping.keys():
			# adding literal and mask to dictionaries and replacing it accordingly in input_string
			mask = LITERAL_MASK + str(len(literals_mapping)).zfill(4)
			literals_mapping[literal] = mask
			literals_unmapping[mask] = literal
			input_string = input_string.replace(literal, mask)
		else:
			# replacing literal according to dictionary in input_string
			input_string = input_string.replace(literal, literals_mapping[literal])

	return input_string


# Reverses the effects of mask_literals
def unmask_literals(input_string):
	# checking if input_string contains *any* masked literal
	if input_string.__contains__(LITERAL_MASK):
		# iterating through all documented literals for un-mapping
		for mask, literal in literals_unmapping.items():
			# replacing masks with original literals
			input_string = input_string.replace(mask, literal)

	return input_string

# Only works when the input_string starts with a '('.
# checks character by character and determines the index of the ')' corrosponding to the FIRST '('
def get_closing_parenthesis_index(input_string):
	parenthesis_counter = 0
	for index, char in enumerate(input_string):
		if char == '(':
			parenthesis_counter += 1
		elif char == ')':
			parenthesis_counter -= 1

		if parenthesis_counter == 0:
			return index + 1

	return -1


# NOTE: works recursively and in general is sadly complex and not very clean, so pay attention when you modify this!
# converts strings with quantifiers from abnf to lark syntax.
def convert_quantifiers(input_string):
	# Looking for patterns like " 1*4" first. Then " 1*" or " 2*". Then just " 5" and then " *"
	# The whitespace in front is crucial because names/terms can have numbers in them. So without the space, "\d+"
	# might match names like "base64", which id shouldn't
	p = re.compile(r"\s(\d+\*\d+|\d+\*|\d+|\*)")

	# term_end acts as an indicator for nested parenthesis and non-quantified parts of the input_string
	# to fully understand it, you need to see how its manipulated, please see below
	# Before working on it, make sure you fully understand how term_end is used to both:
	# - put parts of the input_string in the output_string, that have nothing to do with converting the quantifiers
	# - to skip quantified terms nested within quantified terms, so that those can be worked on recursively
	term_end = 0

	if not p.search(input_string):
		return input_string

	output_string = ""

	# iterating through all found quantifiers
	for m in p.finditer(input_string):
		# if the lasts term_end is lager than the current start, that means we are within quantified parentheses
		# In this case, the term has already been properly converted by the last iteration, in its recursive call
		if term_end > m.start():
			continue

		# +1, to skip the whitespace we used in the pattern, to distinguish between quantifiers and numbers in names
		quantifier_start = m.start() + 1
		quantifier_end = m.start() + len(m.group())
		quantifier = input_string[quantifier_start:quantifier_end]

		# convert old quantifier to new quantifier
		new_quantifier = ""
		if quantifier == "*":
			new_quantifier = "*"
		elif quantifier == "1*":
			new_quantifier = "+"
		else:
			# Just like in the pattern above, we look from biggest to smallest. This order is important, as only the
			# smallest would be matched otherwise
			match = re.match(r"(\d+)\*(\d+)", quantifier)
			if match is not None:
				new_quantifier = "~" + match.group(1) + ".." + match.group(2)
			else:
				match = re.match(r"(\d+)\*", quantifier)
				if match is not None:
					new_quantifier = "~" + match.group(1) + "..*"
				else:
					match = re.match(r"\d+", quantifier)
					if match is not None:
						new_quantifier = "~" + match.group(0)

		# add the part of the input_string to the output_string, that is not effected by conversion
		output_string += input_string[term_end:quantifier_start]

		# filtering out quantified term
		term_start = quantifier_end
		term_end = term_start
		if input_string[term_start] == '(':
			# the quantified term ends at the closing parenthesis, matching the one at term_start
			term_end += get_closing_parenthesis_index(input_string[term_start:])
		else:
			# the quatified term ends at the next whitespace
			match = re.match(r"[^\s]+", input_string[term_start:])
			term_end += match.start() + len(match.group(0))
		term = input_string[term_start:term_end]

		# RECURSIVE CALL! Does the same procedure for the nested term, which potentially has quantified terms in it again
		# returns "term" unchanged otherwise
		output_string += convert_quantifiers(term)
		# sets the converted quantifier, as needed for LARK-syntax, behind the term
		output_string += new_quantifier

	# adds the rest of the input_string to the output_string, that does not contain quantified terms
	output_string += input_string[term_end:]

	return output_string


# The hexadecimal representation "\x5D" for the square bracket "]" must be replaced with an
# escaped square bracket "\]" for the lark parser,
# because it will be interpreted as the end of the regular expression otherwise
def replace_regex_square_bracket(input_string):
	return re.sub(r"(/\[.*)(\\x5D)(.*\]/)", "\\g<1>\\]\\g<3>", input_string)


# There might be special literals that can not be parsed properly by the lark parser
# This function replaces them with lark-specific regex counterparts.
# The only one so far is "\" being turned into /[\\]/
def mask_special_literals(input_string):
	return re.sub(r"(.*)(\"\\\")(.*)", "\\g<1>/[\\\\\\]/\\g<3>", input_string)


# For converting Hex Bytes
RE_HEX_DIGITS_LOWER = "[0-9a-f]{2}"		# a1 10 1a
RE_HEX_DIGITS_UPPER = "[0-9A-F]{2}"		# A1 10 1A
RE_HEX_DIGITS = "[0-9A-Fa-f]{2}"		# a1 A1 aa FF 11

RE_ABNF_HEX = "%x[0-9A-Fa-f]{2}"
RE_ABNF_HEX_RANGE_2G = "("+RE_ABNF_HEX+"-)("+RE_HEX_DIGITS+")"
RE_LARK_HEX = r"\\x[0-9A-F]{2}"
RE_LARK_HEX_OR_RANGE_2G = "("+RE_LARK_HEX+"(-"+ RE_LARK_HEX +")?)"

# For converting Decimal Bytes
RE_DEC_DIGITS = "[0-9]{1,3}"

RE_ABNF_DEC = "%d" + RE_DEC_DIGITS
RE_ABNF_DEC_RANGE_2G = "("+RE_ABNF_DEC+"-)("+RE_DEC_DIGITS+")"
RE_LARK_DEC = r"\\d" + RE_DEC_DIGITS
RE_LARK_DEC_OR_RANGE_2G = "("+RE_LARK_DEC+"(-"+ RE_LARK_DEC +")?)"

RE_LITERALS = "(\\\"(\\\\\"|[^\\\"])+\\\")"
LITERAL_MASK = "masked_literal_nr_"

literals_mapping = {}
literals_unmapping = {}

inputFile = open("SMTP/syntax.abnf", "r")

outputFile = open("SMTP/syntax.lark", "w+")

content = inputFile.readlines()

#Regular Expressions:
matchRule			 = re.compile(r"[a-zA-Z]+[0-9a-zA-z\-]+[ ]*\=.+")
matchInlineComment   = re.compile(r"(.*)(;.*)")
matchComment		 = re.compile(r"[ ]*\;.+")
matchMinusInNT		 = re.compile(r"([a-zA-Z]+[0-9a-zA-Z]*)((?:\-[0-9a-zA-Z]+)+)")
matchHexaByteList	 = re.compile(r"x[A-Z0-9]{2}\-\\x[A-Z0-9]{2}")
matchMinusTerminal	 = re.compile(r"\"\-\"")
matchOR				 = re.compile(r" \/ | \/")

noCommentContent = []

# remove comments
for line in content:
	line = mask_literals(line)
	match = matchInlineComment.match(line)
	if match is not None:
		line = unmask_literals(match.group(1))
	else:
		line = unmask_literals(line)

	noCommentContent.append(line)


concatContent = []
currentRule = ""

#Konkateniert Regeln die über mehrere Zeilen gehen und verwirft Kommentare
for x in noCommentContent:
	x = x.strip()

	#checkt, ob die aktuelle Zeile eine Regel ist
	x = mask_literals(x)

	if matchRule.match(x):
		if not currentRule == "":
			concatContent.append(currentRule)
		currentRule = ""
		currentRule = currentRule + x
	elif matchComment.match(x):
		continue
	else:
		currentRule = currentRule + " " + x
		print(x)


if not currentRule == "":
	concatContent.append(currentRule)


for x in concatContent:

	#ersetzt das erste Gleichzeichen durch einen Doppelpunkt (Zuordnung NonTerminal zu Regel)
	x = re.sub(r"\=", ":", x, count=1)

	#ersetze das OR Symbol / durch |
	x = convertOR(x)

	#ersetze HexBytes durch die Regex-Lark-Notation
	x = convertHexBytes(x)

	# Replace BecBytes with the Regex-Lark-Notation
	x = convertDecBytes(x)

	#konvertiert NonTerminals in eine lark-verträgliche Form
	x = convertNonTerminals(x)

	# masks the literals using LITERAL_MASK, to prepare for quantifier conversion
	x = mask_literals(x)

	# converts quantifiers from abnf syntax to lark-readable syntax
	x = convert_quantifiers(x)

	# un-maskes the before masked literals
	x = unmask_literals(x)

	# replace hexadecimal representation of square bracket with square end bracket for lark parser
	x = replace_regex_square_bracket(x)

	# masks literals that can not otherwise be parsed by lark with lark-specific regex counterparts
	x = mask_special_literals(x)

	#print(rulesWithMinus)
	#print(rulesWithUnderscore)

	#print(x)
	outputFile.write(x + '\n')

