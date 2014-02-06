#!/usr/bin/env perl

use Encode;
use MIME::QuotedPrint::Perl;

$file = $ARGV[0];

local $/;
open(FILE, "<:encoding(iso-8859-1)", $file);
$document = <FILE>; 
close (FILE);

$document = decode_qp($document);

$document =~ s/\n/ /g;

$incoming = $document =~ /alerta de saldo/i;
exit unless $incoming;

my ($d, $m, $y, $account, $balance) = 
	$document =~ m/.*Atendiendo a su petici.*?n, e-Triodos le informa que el d.*?a (\d\d)-(\d\d)-(\d\d\d\d) el saldo contable de su cuenta es el siguiente:.*?Cuenta (.*?): ([0-9\.,]+)/;

$balance =~ s/\.//g;
$balance =~ s/,/\./g;

# Don't forget the \n
print "message dst=banking&tag=check&date=$y-$m-$d&account=$account&balance=$balance\n"
