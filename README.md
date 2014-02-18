bibtex-scripts
==============

Scripts to do various useful tricks with tex and bibtex files. Includes:  

1. latex_changes_accept.txt - a vim script to automatically accept all changes
                            marked up with the latex "changes" package.  

2. strip_biblio.py - Constructs .bib files only of those references contained in 
                    a given .tex file.  References are also stripped down by removing 
                    all non-essential details such as personal reviews.

3. make_lit_review.py - Reads a .tex file, strips all bibtex keys from that file, 
                        then scans a .bib file for those references, and produces a 
                        nicely formatted pdf literature review based on the bibtex
                        review fields for each entry.

