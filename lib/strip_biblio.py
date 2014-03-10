#! /usr/bin/env python

"""
Constructs .bib files only of those references contained in a given .tex file.
References are also stripped down by removing all non-essential details such as
personal reviews.
"""

import re
import regex

# Read .tex file and extract bibtex citation keys:
f = open ('tex_file_name.tex', 'r')
f.seek (0) 
rec = re.compile (r'\\cite')
ref_split = rec.split (f.read ())
print 'File contains', len (ref_split), 'cite commands',
ref_list = []
for cites in ref_split:
    bpos = re.search (r'{', cites).start ()
    if (bpos < 2): # only include actual '\citeX{' commands
        ref_list_temp = re.split (r'{', cites) [1]
        ref_list_temp = re.split (r'}', ref_list_temp) [0]
        cpos = re.search (r',', ref_list_temp)
        if cpos:
            ref_list_split = re.split (r',', ref_list_temp)
            for split_cites in ref_list_split:
                ref_list.append (split_cites)
        else:
            ref_list.append (ref_list_temp)

ref_list = sorted (set (ref_list))
print 'and', len (ref_list), 'unique references.'
f.close ()

"""
First just dump a list of the bibtex cite keys to the file "refs.txt", which can
then be used in "make_lit_review" to dump the formatted reviews of each cited
paper.
"""

fout = open ('refs.txt', 'w')
for cite in ref_list:
    print cite
    fout.write (cite + '\n')

fout.close ()

"""
Then find those citation keys in .bib file and copy citations. This presumes
citations are indeed in the .bib file, and will crash if not. Not having them there
would nevertheless be rather strange.

The routine may produce unpredictable results if non-encoding characters are
encountered, such as sometimes happens with copy-pasted entries. The output thus
must be examined to identify such, and the corresponding entries in the original
.bib file modified. It's much easier that way than modifying this actual program to
potentially flag all such cases (there should generally be very few).

A further issue is single quotations marks (') in titles and author names, which are
also not yet handled correctly.

The extraction of fields is done with the new (Oct 2013) regex search, which allows
recursive searching for nested expressions. Bibtex files often have nested {}, which
are parsed with the regex.search expression below. The commands work thus:
    result = regex.search(r''' (?<rec> \{ (?: [^{}]++ | (?&rec))* \})''',
        entry, flags=regex.VERBOSE)
with the following components, copied from
http://stackoverflow.com/questions/5454322/python-how-to-match-nested-parentheses-with-regex

    result = regex.search(r''' (?<rec> #capturing recursive group
        \{      # open parenthesis
        (?:     # non-capturing group
        [^{}]++ # anyting but brackets one or more times without backtracking
        |       # or
        (?&rec) # recursive substitute of group rec
        )*      # close non-capturing group
        \}      # close parenthesis
        )''', entry, flags=regex.VERBOSE)
"""

fin = open ('main_bibliography_file.bib', 'r')
flen = len (fin.read ())
fin.seek (0)
fout = open ('aaa.bib', 'w')
# There is no matching backwards with regex, so positions of all references are
# first put in an index
entry_start = [m.start() for m in re.finditer('@',fin.read())]
print 'Bibliography has', len (entry_start), 'entries.'
# These are the field names dumped to the reduced .bib - modify as desired.
field_names = ["author", "title", "journal", "year", "volume", "pages", "doi",
"publisher"]
for cite in ref_list:
    fin.seek (0)
    fpos0 = re.search (cite, fin.read ()).start ()
    fpos0 = min (entry_start, key=lambda x:abs (x - fpos0)) # value in entry_start
    fpos1 = entry_start [entry_start.index (fpos0) + 1] # next value in entry_start
    fin.seek (fpos0)
    entry = fin.read (fpos1 - fpos0 - 1) + '\n'
    elen = len (entry)
    epos0 = re.search (r',\n', entry).start ()
    epos0 = epos0 + re.search (r'(\w+)', entry [epos0:len (entry)]).start ()
    entry_strip = entry [0:epos0 - 1]
    # find EOL and cut entry_strip to that point (presumes only one line here)
    eolp = re.search (r'\n', entry_strip)
    if not eolp:
        print 'ERROR'
    else:
        entry_strip = entry_strip[0: eolp.start ()] + '\n'

    end_check = re.search ('}', entry [epos0:elen])
    end_check = True
    eolc = re.compile (r'\n')
    while end_check:
        m = re.match (r'(\w)*', entry [epos0:elen]).group (0)
        if m in field_names:
            epos1 = re.search ('{', entry [epos0:elen])
            if not epos1:
                print 'ERROR: opening { not found in field.'
            else: 
                epos1 = epos0 + epos1.start ()
                result = regex.search (r''' (?<rec> \{ (?: [^{}]++ | (?&rec))* \})''',\
                        entry [epos1:elen], flags=regex.VERBOSE)
                field = result.captures ('rec')
                field = field [len (field) - 1]
                epos1 = epos1 + len (field)
                entry_add = entry [epos0:epos1]
                eolp = [ep.start () for ep in eolc.finditer (entry_add)]
                if not eolp:
                    entry_add = entry_add + ',\n'
                else:
                    eolp = eolp [-1]
                    if len (entry_add) - eolp > 1:
                        entry_add = entry_add + ',\n'


                entry_strip = entry_strip + '   ' + entry_add
        else:
            epos1 = re.search ('}', entry [epos0:elen])
            if epos1:
                epos1 = epos0 + epos1.start ()

        if not epos1: # only fails is m not in field_names as entry ends
            print 'epos1 check failed.'
            end_check = False
        else:
            end_check = re.search (r'\w', entry [epos1:elen])
            if end_check:
                epos0 = epos1 + end_check.start ()

    # Remove comma at end of final entry line:
    slen = len (entry_strip) - 1
    if entry_strip [slen - 1] == ',':
        entry_strip = entry_strip [0:slen - 1] + '\n'

    entry_strip = entry_strip + '}\n\n'
    fout.write (entry_strip)

fin.close ()
fout.close ()
