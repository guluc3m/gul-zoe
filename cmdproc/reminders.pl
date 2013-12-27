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
# Publishes a message in twitter
#

use Getopt::Long qw(:config pass_through);
use MIME::Base64;
use Env qw(ZOE_HOME);

my $get;
my $run;
my $meeting;

GetOptions("get" => \$get,
           "run" => \$run, 
           "meeting" => \$meeting);

if ($get) { 
  &get;  
} elsif ($run and $meeting) {
  &meeting;
}

#
# Lists the commands this script dispatches
#
sub get {
  print("--meeting envía el recordatorio de /la reunión /mensual\n");
}

#
# Sends the email
#
sub send {
  my ($basename, $subject, $to) = @_;
  my @files = split(/\n/, `ls $ZOE_HOME/lib/messages/$basename*`);
  my $n = @files;
  my $file = @files[int(rand($n))];
  my $document = do {
    local $/ = undef;
    open my $fh, "<", $file;
    <$fh>;
  };
  $document = encode_base64($document, "");
  print "message dst=mail&to=$to&subject=$subject&txt64=text/plain;file.txt:$document";
}

#
# Sends the meeting mail
#
sub meeting {
  &send("reunion_mensual", "[ORG] Reunión este viernes", "gul\@gul.uc3m.es");
}

