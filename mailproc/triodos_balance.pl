#!/usr/bin/env perl
#
# This file is part of Zoe Assistant - https://github.com/guluc3m/gul-zoe
#
# Copyright (c) 2013 David Muñoz Díaz <david@gul.es> 
#
# This file is distributed under the MIT LICENSE
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#
# The original mail is saved to a temp file and given as:
#    --original /tmp/...
#
# Mail headers are given as --mail-xxx, like:
#    --mail-(header) (value)
#
# Not all headers are passed, but some common ones:
#    --mail-subject
#    --mail-delivered-to
#    --mail-in-reply-to
#    --mail-date
#    --mail-message-id
#    --mail-from
#    --mail-to
#    --mail-reply-to
#    --mail-list-id
#    --mail-sender
#
# The email body is composed of parts, which are saved to temp files
# and passed as:
#    --(mime-type) (file)
#
# Example:
#    --text/plain /tmp/... --text/html /tmp/... --image/png /tmp/...
#
# All plain text parts are concatenated and stored in a single file:
#    --plain /tmp/...
#
# so, if you are interested in the text and you don't care about the mail
# structure or attachments, you can concentrate only in this parameter.
#
# All text parts are converted to UTF-8

use Getopt::Long qw(:config pass_through);
use strict;

my $subject;
my $plain;

GetOptions("mail-subject=s" => \$subject,
           "plain=s"        => \$plain);


#
# Read the plain text file into $document. 
# Notice that:
#  - The mail agent converts all plain text to utf-8
#  - All \n are removed. 
#

local $/;
open(FILE, "<:encoding(utf-8)", $plain);
my $document = <FILE>; 
close (FILE);
$document =~ s/\n/ /g;

#
# Analyze email
#

#
# Extract the information form the email body
#

if ($document =~ m/.*Atendiendo a su petici.*?n, e-Triodos le informa que el d.*?a (\d\d)-(\d\d)-(\d\d\d\d) el saldo contable de su cuenta es el siguiente:.*?Cuenta (.*?): ([0-9\.,]+)/) {
    my ($d, $m, $y, $account, $balance) = ($1, $2, $3, $4, $5);
    $balance =~ s/\.//g;
    $balance =~ s/,/\./g;
    print "message dst=banking&tag=check&date=$y-$m-$d&account=$account&balance=$balance\n"
}
