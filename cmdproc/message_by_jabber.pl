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
# Sends a user a given message via jabber
#

use Getopt::Long qw(:config pass_through);

my $get;
my $run;
my $me;
my @strings;
my @users;

GetOptions("get" => \$get,
           "run" => \$run,
           "me" => \$me, 
           "string=s" => \@strings, 
           "user=s" => \@users);

if ($get) { 
  &get;  
} elsif ($run and $me) {
  &run_for_me;
} elsif ($run and not $me) {
  &run_for_others;
}

#
# Lists the commands this script attends
#
sub get {
  print("     di/envía a <user> por jabber/gtalk <string>\n");
  print("--me dime <string>\n");
}

#
# Executes the command in the --me case
# This command generates a set of feedback messages 
#
sub run_for_me {
    foreach $message (@strings) {
        print("feedback $message\n");
    }
}

#
# Executes the command in the general case
# This command generates a set of messages that have to be sent back to Zoe
#
sub run_for_others {
  foreach $user (@users) {
    foreach $message (@strings) {
      print("message dst=jabber&touser=$user&msg=$message\n");
    }
  }
}

