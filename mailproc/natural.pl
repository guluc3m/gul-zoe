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

use MIME::Base64;
use Getopt::Long qw(:config pass_through);
use strict;

my $subject;
my $plain;
my $sender;
my $message_id;

GetOptions("mail-subject=s"        => \$subject,
           "plain=s"               => \$plain, 
           "msg-sender-uniqueid=s" => \$sender,
           "mail-message-id=s"     => \$message_id);

local $/;
open(FILE, "<", $plain);
my $document = <FILE>; 
close (FILE);

my ($cmd, $long, $longcmd) = $document =~ m/([^\n]*)(\n\n+(.*))?.*/ms;
$cmd = encode_base64($cmd, "");
my $message = "message src=mail&dst=relay&relayto=natural&tag=command&tag=relay&cmd=$cmd&sender=$sender&inreplyto=$message_id";

if ($longcmd) {
    $longcmd = encode_base64($longcmd, "");
    $message = $message . "&cmdext=$longcmd";
}

print $message . "\n";

