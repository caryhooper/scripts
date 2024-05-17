# ####Example Notes Formatting
# ##Subtitle A
# Topic 1----command 1
# Topic 2----command 2
# Topic 3----command 3
# ##Subtitle B
# Topic 1----command 1
# Topic 2 (multiline command)----"""
# multiline
# command displayed on
# these three lines"""
# Topic 3 (Sublist)----##First Bullet; Second Bullet; Third Bullet;

import os

# 1. loop through all .txt files in directory.
# 2. For each, parse the file line by line.  For ones that have ----##, parse multiple lines (code block)
# 3. Transform to MD

txtfiles = [i for i in os.listdir('cheatsheets/') if '.txt' in i]
#initialize parsing for stupid multiline quotes
in_quote = False
quote_lines = list()

for file in txtfiles:

	f = open(f'cheatsheets/{file}','r')
	lines = f.readlines()
	newfilename = file.split('.')[0] + '.md'

	with open(f'cheatsheets/{newfilename}','w') as nf:
		for line in lines:

			line = line.replace('&gt;','>').replace('&lt;','<').replace('&nbsp;',' ').replace('<br>','').replace('</br>','')

			#Quoted Multiline (center)
			if in_quote and not '"""' in line:
				quote_lines.append(line)
				continue

			#Main Header
			if line.startswith('####'):
				header = line.lstrip('#')
				nf.write('# ' + header)
				nf.write('======\n')
				continue

			#Sub Header
			if line.startswith('##'):
				header = line.lstrip('#')
				nf.write('\n## ' + header)
				nf.write('------\n')
				continue

			#Unordered List
			if '----' in line and '##' in line:
				topic,steps = line.split('----')
				steps = steps.lstrip('#').split(';')
				nf.write('#### ' + topic + '\n')
				for step in steps:
					nf.write(f'+ ' + step + '\n')
				continue

			#End of Quoted Multiline
			if '"""' in line and '----' in line:
				topic,quote = line.split('----')
				nf.write('#### ' + topic)
				quote = quote.lstrip('"')
				in_quote = True
				quote_lines = list()
				quote_lines.append(quote)
				continue

			#Quoted Multiline
			if in_quote and '"""' in line:
				in_quote = False
				nf.write('\n```\n')
				for ql in quote_lines:
					nf.write(ql)
				nf.write('```\n')
				continue

			#Normal Lines
			if '----' in line:
				topic,info = line.split('----')
				nf.write(f'#### {topic}\n')
				nf.write(f'{info}')
