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

$incoming = $document =~ /alerta de Abono Superior/i;
exit unless $incoming;

my ($d, $m, $y, $account, $amount, $balance) = 
	$document =~ m/.*Atendiendo a su petici.n, e-Triodos le informa que el d.a (\d\d)-(\d\d)-(\d\d\d\d) se ha producido un abono en su cuenta (.*?) por importe de (.*?) EUR. El saldo actual es de (.*?) EUR.*/;

$amount =~ s/,/\./g;
$balance =~ s/,/\./g;
$what = "Abono superior";

# Don't forget the \n
print "dst=banking&tag=entry&date=$y-$m-$d&account=$account&amount=$amount&what=$what\n"
