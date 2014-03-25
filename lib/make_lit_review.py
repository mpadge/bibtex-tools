#! /usr/bin/env python

"""
make_lit_review

Reads a .tex file, strips all bibtex keys from that file, then scans a .bib file for
those references, and produces a nicely formatted pdf literature review based on the
bibtex review fields for each entry.

Uses regex parsing to separate out nested repeats, especially of "{}". This
nevertheless seems not to be failsafe, as odd characters do pop up in the review
field. If the pdf looks odd for some reviews, manual tweaking of the .tex file may
be necessary to remove any strange characters, followed by re-running the commands
in the makePdf() function below.
"""

import re
import regex
import os

wd = "/data/work/"
bibdir = "/data/literature/"

class Ref (object):
    def __init__(self):
        self.__bibkey = None
        self.__author1 = None
        self.__author = None
        self.__title = None
        self.__journal = None
        self.__year = None
        self.__volume = None
        self.__pages = None
        self.__review = None

    def get_bibkey (self):
        return self.__bibkey
    def get_author1 (self):
        return self.__author1
    def get_author (self):
        return self.__author
    def get_title (self):
        return self.__title
    def get_journal (self):
        return self.__journal
    def get_year (self):
        return self.__year
    def get_volume (self):
        return self.__volume
    def get_pages (self):
        return self.__pages
    def get_review (self):
        return self.__review

    def set_bibkey (self, bibkey):
        self.__bibkey = bibkey
    def set_author1 (self, author1):
        self.__author1 = author1
    def set_author (self, author):
        self.__author = author
    def set_title (self, title):
        self.__title = title
    def set_journal (self, journal):
        self.__journal = journal
    def set_year (self, year):
        self.__year = year
    def set_volume (self, volume):
        self.__volume = volume
    def set_pages (self, pages):
        self.__pages = pages
    def set_review (self, review):
        self.__review = review

    bibkey = property (get_bibkey, set_bibkey)
    author1 = property (get_author1, set_author1)
    author = property (get_author, set_author)
    title = property (get_title, set_title)
    journal = property (get_journal, set_journal)
    year = property (get_year, set_year)
    volume = property (get_volume, set_volume)
    pages = property (get_pages, set_pages)
    review = property (get_review, set_review)

# Field names may or may not need capitalisation
field_names = ["Author", "Title", "Journal", "Year", "Volume", "Pages", "Review"]

def writeHeader (fout):
    fout.write ('\\documentclass[a4paper,oneside]{article}\n\n')
    fout.write ('\\usepackage[left=2.54cm,right=2.54cm,top=3cm,bottom=3cm]' +
            '{geometry}\n')
    fout.write ('\\usepackage{color}\n')
    fout.write ('\\renewcommand{\\familydefault}{\\sfdefault}\n')
    fout.write ('\\usepackage{sfmath}\n')
    fout.write ('\\title{Literature review}\n')
    fout.write ('\\author{}\n')
    fout.write ('\\date{}\n')
    fout.write ('\\newcounter{qcounter}\n')

    fout.write ('\\newcommand{\\mitem}[2] {\\noindent\\framebox' +
        '{\\noindent\\begin{minipage}{0.95\\textwidth}\n')
    fout.write ('\t\t{\\arabic{qcounter}.~#1}\\stepcounter{qcounter}\n')
    fout.write ('\t\\end{minipage}}\\newline{}{\\vspace{10pt}\\\\ #2}' +
        '\\newline{}\\vspace{10pt}}\n\n')

    fout.write ('\\definecolor{greencolour}{rgb}{0.30,0.65,0.15}\n')

    fout.write ('\\newcommand{\\greenheading}[1]{%\n')
    fout.write ('\t\\vspace{10pt}\n')
    fout.write ('\t\\noindent\\color{greencolour}\n')
    fout.write ('\t{\\rule[3pt]{0.15\\textwidth}{2pt}}\\hspace{0.025\\textwidth}\n')
    fout.write ('\t{\\bf\\Large{\\framebox[1.5\\width]{#1}}}%\n')
    fout.write ('\t\\color{black}\\normalsize\\vspace{10pt}}\\\\%\n\n')

    fout.write ('\\begin{document}\n')
    fout.write ('\\maketitle\n')
    fout.write ('\\setcounter{qcounter}{1}\n')
    return

def readBibKeys ():
    f = open (wd + 'tex_document.tex', 'r')
    f.seek (0) 
    rec = re.compile (r'\\cite')
    ref_split = rec.split (f.read ())
    print 'File contains', len (ref_split), 'cite commands',
    bibkeys = []
    for cites in ref_split:
        bpos = re.search (r'{', cites).start ()
        if (bpos < 2): # only include actual '\citeX{' commands
            ref_list_temp = re.split (r'{', cites) [1]
            ref_list_temp = re.split (r'}', ref_list_temp) [0]
            cpos = re.search (r',', ref_list_temp)
            if cpos:
                ref_list_split = re.split (r',', ref_list_temp)
                for split_cites in ref_list_split:
                    bibkeys.append (split_cites)
            else:
                bibkeys.append (ref_list_temp)

    bibkeys = sorted (set (bibkeys))
    print 'and', len (bibkeys), 'unique references.'
    f.close ()
    return bibkeys


def readReviews (bibkeys):
    bibfile = open (bibdir + 'library.bib', 'r')
    bibfile.seek (0)
    rec = re.compile (r'@')
    entry_split = rec.split (bibfile.read ())
    print '.bib file contains', len (entry_split), 'entries.'

    reviews = []

    for entry in entry_split:
        entry_line1 = re.split ('\n', entry)
        bibkey = re.search ('{(.*?),', entry_line1 [0])
        if bibkey is not None:
            if bibkey.group (1) in bibkeys:
                ref1 = Ref ()
                ref1.bibkey = bibkey.group (1)
                flen = len (entry)
                year = -9999
                author = ''
                for fn in field_names:
                    # The \s* indicates optional whitespace (of any length)
                    fnplus = fn + "\s*=\s*{"
                    fpos = re.search (fnplus + '(.*?)', entry)
                    if fpos is not None:
                        fpos = fpos.start ()
                        result = regex.search (r''' (?<rec> \{ (?: [^{}]++ | (?&rec))* \})''',\
                                entry [fpos:flen], flags=regex.VERBOSE)
                        field = result.captures ('rec')
                        # field will just be author if there are no {}'s present,
                        # otehrwise regex will parse an entry for the contents of
                        # each '{}', with the desired author string as the final
                        # element of field. This element also starts with '{' and
                        # ends with '}' so is itself reduced to [1:-1] thus:
                        field = field [-1] [1:-1]
                        #if fn == 'Review' and bibkey.group (1) == 'Ives2003':
                        #    print field
                        if fn == 'Author' or fn == 'author':
                            author = re.split (r',', field) [0]
                            # If first entry prior to comma has no spaces, it is
                            # taken as surname, otherwise search for "and" and take
                            # surname as previous word. If there is no and, just
                            # take the last word
                            spos_sp = author.find (" ")
                            if spos_sp >= 0:
                                spos_and = author.find ("and")
                                if spos_and >= 0:
                                    author = re.split (r'and', author) [0]

                                author = author.split () [-1]

                            ref1.author1 = author

                        spos_sp = field.find (" \&")
                        if spos_sp >= 0:
                            field = field.replace (" \&", " \\&")

                        setattr (ref1, str (fn).lower (), field)

                reviews.append (ref1)

    reviews = sorted (reviews, key = lambda s:(s.year, s.author))

    return reviews

def writeReviews (reviews, file):
    year = reviews [0].year
    yearwrite = True

    for rev in reviews:
        if yearwrite:
            fout.write ("\\greenheading{" + str (rev.year) + "}\\\\" + "\n\n")
            yearwrite = False
        elif rev.year > year:
            year = rev.year
            yearwrite = True

        fout.write ("\mitem{" + rev.author + ' (' + str (rev.year) +\
                '), ``' + rev.title + "'' ")
        if not rev.journal is None:
            fout.write ("\\textit{" + rev.journal + "} \\textbf{" + rev.volume + "}")
            if not rev.pages is None:
                fout.write (":" + rev.pages)
        elif not rev.pages is None:
            fout.write (rev.pages)
        fout.write ("}\n") # end mitem

        if not rev.review is None:
            rev.review = rev.review.replace ("\n\t", "\n")
            fout.write ("{" + rev.review + "}")

        fout.write ("\n\n")

    print "Written ", len (reviews), "reviews to lit_review.tex"

    return

def makePdf ():
    os.chdir (wd)
    os.system ("latex -interaction=nonstopmode lit_review.tex");
    os.system ("dvipdfmx lit_review.dvi");
    os.system ("rm lit_review.aux lit_review.dvi lit_review.log");
    return

fout = open (wd + 'lit_review.tex', 'w')
bibkeys = readBibKeys ()
reviews = readReviews (bibkeys)
writeHeader (fout)
writeReviews (reviews, fout)
fout.write ("\\end{document}")
fout.close ()
makePdf ()
