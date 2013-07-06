#!/usr/bin/env perl

$file = $ARGV[0];

local $/;
open(FILE, $file);
$document = <FILE>; 
close (FILE);
$document =~ s/=\n//g;
$document =~ s/\n>*//g;
$document =~ s/\n/ /g;

$incoming = $document =~ /alerta de Abono Superior/i;
exit unless $incoming;

# Remove almost everything, leaving only the important part of the message
# I'm pretty sure a Perl Jedi can do this with just one command.
$gist = $document;
$gist =~ s/.*?estimado cliente://i;
$gist =~ s/Quedamos a su disposic.*//i;

# find the relevant parameters of the message
$gist =~ /(\d\d)-(\d\d)-(\d\d\d\d)/;
$d = $1;
$m = $2;
$y = $3;

$gist =~ /cuenta (.*?) por importe/;
$account = $1;

$gist =~ /por importe de (.*?) EUR./;
$amount = $1;
$amount =~ s/,/\./g;

# Don't forget the \n
print "dst=banking&tag=entry&date=$y-$m-$d&account=$account&amount=$amount&what=Intereses\n"
