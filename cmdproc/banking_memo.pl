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
# Sends the banking memo by mail
#

use Getopt::Long qw(:config pass_through);

my $get;
my $run;
my $me;
my $account;
my $sender;
my @strings;
my @users;

GetOptions("get" => \$get,
           "run" => \$run,
           "me" => \$me,
           "account" => \$account, 
           "msg-sender=s" => \$sender,
           "strings=s" => \@strings,
           "users=s" => \@users);

if ($get) { 
  &get;  
} elsif ($run) {
  if (not $me and not $account) {
    &run_other_all;	
  } elsif (not $me and $account) {
	  &run_other_account;
  } elsif ($me and not $account) {
  	&run_me_all;
  } elsif ($me and $account) {
	&run_me_account;
  }
}

sub get {
  print("               envía a <user> los movimientos /bancarios\n");
  print("     --account envía a <user> los movimientos /bancarios de la cuenta <string>\n");
  print("--me           dame/envíame los movimientos /bancarios\n");
  print("--me --account dame/envíame los movimientos /bancarios de la cuenta <string>\n");
}

sub run_other_all {
  foreach $user (@users) {
    print("message dst=banking&tag=memo&mail=$user\n");
  }
}

sub run_other_account {
  foreach $user (@users) {
    foreach $account (@accounts) {
      print("message dst=banking&tag=memo&mail=$user&account=$account\n");
    }
  }
}

sub run_me_all {
  print("message dst=banking&tag=memo&mail=$sender\n");
}

sub run_other_account {
  foreach $account (@accounts) {
    print("message dst=banking&tag=memo&mail=$sender&account=$account\n");
  }
}
