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
use strict;

my $get;
my $run;
my $zoetweet;
my $jabber;
my $twitter;
my $mail;
my @strings;
my @users;
my @mails;
my @twitters;

GetOptions("get"       => \$get,
           "run"       => \$run,
           "z"         => \$zoetweet, 
           "j"         => \$jabber, 
           "t"         => \$twitter, 
           "m"         => \$mail, 
           "string=s"  => \@strings, 
           "mail=s"    => \@mails, 
           "twitter=s" => \@twitters, 
           "user=s"    => \@users);

if ($get) { 
  &get;  
} elsif ($run and $zoetweet) {
  &tweet_as_zoe;
} elsif ($run and $jabber) {
  &send_by_jabber;
} elsif ($run and $twitter) {
  &send_by_twitter;
} elsif ($run and $mail) {
  &send_by_mail;
}

#
# Lists the commands this script attends
#
sub get {
  print("--z    twit/tuit/tuitea/twitter <string>\n");
  print("--j    di/envía a <user> /por /jabber/gtalk <string>\n");
  print("--t    di/envía/tuitea a <twitter> <string>\n");
  print("--t    di/envía/tuitea a <user> por twitter <string>\n");
  print("--m    di/envía a <mail> <string>\n");
  print("--m    di/envía a <mail>/<user> por mail <string>\n");
}


sub tweet_as_zoe {
  foreach my $message (@strings) {
    print("message dst=twitter&msg=$message\n");
  }
}

sub send_by_jabber {
  foreach my $user (@users) {
    foreach my $message (@strings) {
      print("message dst=jabber&to=$user&msg=$message\n");
    }
  }
}

sub send_by_twitter {
  my @destinations = (@users, @twitters);
  foreach my $dest (@destinations) {
    foreach my $message (@strings) {
      print("message dst=twitter&msg=$message&to=$dest\n");
    }
  }
}

sub send_by_mail {
  my @destinations = (@users, @mails);
  foreach my $dest (@destinations) {
    foreach my $message (@strings) {
      print("message dst=mail&txt=$message&to=$dest\n");
    }
  }
}

