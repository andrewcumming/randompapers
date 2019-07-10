import requests
import numpy as np
from datetime import datetime
import os
import time
import glob
from feedgen.feed import FeedGenerator

api_key=''
www_dir = './'

# Rename the index.html file using its creation date
try:
	previous_fname = time.strftime("%Y_%m_%d.html",time.localtime(os.path.getmtime(www_dir+'index.html')))
	os.rename(www_dir+'index.html',www_dir+previous_fname)
except:
	pass

# Open a new index.html file and write the header
fp = open(www_dir+"index.html","w")

print('''<html>
  <head>
	<meta name="viewport" content="width/device-width" charset="utf-8">
  	<title>Random Papers</title>
	<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="heading">
<h1>Random Papers</h1>
</div>
<div class="container">''',file=fp)

print("<h4>This week's papers</h4>",file=fp)

# create RSS feed
fg = FeedGenerator()
fg.title('Random Papers')
fg.link( href='http://randompapers.net' )
fg.description('5 random papers chosen from the astrophysics literature')

# Work out the month and year to search
now = datetime.now()
month = now.month
day = now.day
year = now.year
lastmonth = month-1
if lastmonth == 0:
	lastmonth = 12
	year = year - 1
pubdate = '%4d-%02d' % (year, lastmonth)

# make the request
r=requests.get('https://api.adsabs.harvard.edu/v1/search/query?q=*&fq=pubdate:'+pubdate+'&rows=2000&fq=bibstem:(MNRAS OR ApJ OR A%26A OR AJ)&fq=database:astronomy&fl=bibcode,author,title,pub,abstract',headers={'Authorization' : 'Bearer:'+api_key})
out = r.json()
print('Response: ', r.status_code)

# choose random numbers
num_papers=out["response"]["numFound"]
choice = np.random.choice(num_papers,5,replace=False)
print("num_papers, choice=",num_papers,choice)

# print out the info about the chosen papers
docs = out["response"]["docs"]
choice_count = 1
for i in choice:
	doc = docs[i]
	print('<P><font size="+1">'+str(choice_count)+'. <a href="http://adsabs.harvard.edu/abs/'+doc['bibcode']+'">'+doc['title'][0]+'</a>',file=fp)
	authors = doc['author']
	num_authors = len(authors)
	name = authors[0]
	print(name.split(',')[0], file=fp)
	if num_authors > 2:
		print(' et al. ', file=fp)
	if num_authors == 2:
		name2 = authors[1]
		print(' &amp; ' + name2.split(',')[0], file=fp)
	print(str(year)+', '+doc['pub'],file=fp)
	print('</font></p>',file=fp)
	# add an entry to the feed
	fe = fg.add_entry()
	fe.title(doc['title'][0])
	fe.link( href='http://adsabs.harvard.edu/abs/'+doc['bibcode'])
	namestring=''
	for name in doc['author']:
		namestring = namestring + name + ', '
	fe.content(namestring + doc['pub'] + '<br><br>' + doc['abstract'])
	choice_count+=1

# summary information
print("<P>Selected on %s, %d %s from a total of %d papers published last month in ApJ, AJ, MNRAS and A&amp;A.</p>" % (now.strftime("%A"),now.day,now.strftime("%B %Y"),num_papers),file=fp)

# write out feed
fg.rss_file(www_dir+'feed.xml')

# About
print("<h4>About Random Papers</h4>",file=fp)
print('''<p>We meet every Monday at 2pm at the <a href="http://msi.mcgill.ca/">McGill Space Institute</a> to discuss 5 random astrophysics papers.</p>
<p>The goal of Random Papers is to gain a broad view of current astrophysics research. Each week we run a script to choose 5 random papers published in the last month in refereed astrophysics journals. This gives a different slice of the literature than the typical astro-ph discussion, with papers from outside our own research areas or those that might not otherwise be chosen for discussion.</p>
<p>Rather than reading each paper in depth, the goal is to focus on the big picture, with questions such as: How would we summarize the paper in a few sentences? What are the key figures in the paper? What analysis methods are used? Why is this paper being written, and Why now?
</p>
''', file=fp)

# make a list of previous random papers
print("<h4>Previous random papers</h4>",file=fp)

file_list = glob.glob(www_dir+'*.html')
file_list = [os.path.basename(file) for file in file_list]
file_list.sort(reverse=True)
for fname in file_list:
	if fname!='index.html':
		print('<a href="'+fname+'">'+fname.replace("_",".")[:-5]+'</a> ',file=fp)

print('''<p><br>
Image credit: <a href="https://www.nasa.gov/image-feature/celestial-fireworks">NASA/HST</a><br>
Code: <a href="https://github.com/andrewcumming/randompapers">GitHub</a>
</p>''',file=fp)
print("</div></body></html>",file=fp)

fp.close()
