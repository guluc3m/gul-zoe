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
# Publishes an article in gul.es
#

use Getopt::Long qw(:config pass_through);
use File::Temp qw(tempfile);
use Env qw(ZOE_HOME);
use MIME::Base64;

my $get;
my $run;
my $text;

GetOptions("get" => \$get,
           "run" => \$run,
           "msg-cmdext=s" => \$text);

if ($get) { 
  &get;  
} elsif ($run) {
  &run;
}

#
# Lists the commands this script attends
#
sub get {
  print("publica /esto /en /la /portada/web\n");
}

#
# 
#
sub run {
  $decoded = decode_base64($text);
  ($fh, $filename) = tempfile();
  open (FILE, ">$filename");
  print FILE $decoded;
  close(FILE);
  `$ZOE_HOME/tareas/publish_web.sh $filename`;
  print "feedback hecho\n";
}

