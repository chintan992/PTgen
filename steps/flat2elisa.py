#!/usr/bin/env python3

# Input: a 3-letter language code, and a pile of directories and files.
# Output: a file in ELISA's XML format.
#
# Usage: flat2elisa.py -h
#
# To install this script's prerequisites, either apt-get install python3-lxml, or pip install lxml.
# (Python 3, because Python 2 has Unicode bugs.)
#
# Author: Jon May, ISI

import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import os
import gzip
import tempfile
import shutil
import atexit
import hashlib
import lxml.etree as ET # pip install lxml

scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')

def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)

def main():
  parser = argparse.ArgumentParser(description="given files of flat text or directories containing files of flat text, produce an elisa-format file with minimal content",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infiles", "-i", nargs='+', help="input files or directories containing files. Files must conform to naming convention: AAA_BB_CCCCCC_YYYYMMDD_EEEEEEEE.txt representing source language, genre, provenance, date, and index id, respectively")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output elisa file")
  parser.add_argument("--direction", "-d", help="translation direction", default="fromsource")
  parser.add_argument("--language", "-l", required=True, help="iso 639-3 language code of source")
  
  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  workdir = tempfile.mkdtemp(prefix=os.path.basename(__file__), dir=os.getenv('TMPDIR', '/tmp'))

  def cleanwork():
    shutil.rmtree(workdir, ignore_errors=True)
  if args.debug:
    print(workdir)
  else:
    atexit.register(cleanwork)

  outfile = prepfile(args.outfile, 'w')
  
  infilenames = []
  fullidfields = ['SOURCE_LANGUAGE', 'GENRE', 'PROVENANCE', 'DATE', 'INDEX_ID']
  for entry in args.infiles:
    if not os.path.exists(entry):
      sys.stderr.write("{} not found; skipping\n".format(entry))
      continue
    if os.path.isfile(entry):
      infilenames.append(entry)
    else:
      for filename in os.listdir(entry):
        file = os.path.join(entry, filename)
        if os.path.isfile(file):
          infilenames.append(file)
  outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
  outfile.write('<!DOCTYPE ELISA_LRLP_CORPUS SYSTEM "elisa.lrlp.v1.1.dtd">\n')
  outfile.write('<ELISA_LRLP_CORPUS source_language="{}">\n'.format(args.language))
  for infile in infilenames:
    try:
      fullid = os.path.basename(infile).split('.')[0]
      idtoks = fullid.split('_')
      if len(idtoks) != len(fullidfields):
        raise
    except:
      sys.stderr.write("{} is not in proper naming convention; skipping\n".format(infile))
      continue
    outfile.write('<DOCUMENT id="{}">\n'.format(fullid))
    for label, value in zip(fullidfields, idtoks):
      outfile.write("  <{label}>{value}</{label}>\n".format(label=label, value=value))
    outfile.write("  <DIRECTION>%s</DIRECTION>\n" % args.direction)
    currstart = 0
    try:
      for ln, line in enumerate(prepfile(infile, 'r')):
        line = line.strip()
        segroot = ET.Element('SEGMENT')
        xroot = ET.SubElement(segroot, 'SOURCE')
        currend = currstart+len(line)-1
        xroot.set('id', "{}.{}".format(fullid, ln))
        xroot.set('start_char', str(currstart))
        xroot.set('end_char', str(currend))
        currstart=currend+2 # follows most widely seen convention in LDC files
        subelements = []
        subelements.append(("FULL_ID_SOURCE", fullid))
        subelements.append(("ORIG_SEG_ID", "segment-{}".format(ln))) # for nistification
        subelements.append(("ORIG_FILENAME", os.path.basename(infile))) # for nistification
        subelements.append(("MD5_HASH_SOURCE",
                            hashlib.md5(line.encode('utf-8')).hexdigest()))
        subelements.append(("ORIG_RAW_SOURCE", line))
        for key, text in subelements:
          se = ET.SubElement(xroot, key)
          se.text = text
        xmlstr = ET.tostring(segroot, pretty_print=True, encoding='utf-8',
                             xml_declaration=False).decode('utf-8')
        outfile.write(xmlstr)
    except:
      sys.stderr.write("{} had a problem.\n".format(infile))
      # For Tagalog, fix this problem by filtering the input with sed -e 's/Ñ/N/g'.
    outfile.write("</DOCUMENT>\n")
  outfile.write("</ELISA_LRLP_CORPUS>\n")

if __name__ == '__main__':
  main()
