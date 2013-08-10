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
# Adds a payment of withdrawal to a banking account
#

use Getopt::Long qw(:config pass_through);

my $get;
my $run;
my $payment;
my $account;
my @strings;
my @floats;
my @integers;
my @dates;

GetOptions("get" => \$get,
           "run" => \$run,
           "payment" => \$payment,
           "account" => \$account, 
           "string=s" => \@strings, 
           "float=s" => \@floats, 
           "integer=s" => \@integers, 
           "date=s" => \@dates);

my @numbers = (@floats, @integers);

sub error
{
  print("@_\n");
  exit();
}

if ($get) 
{ 
  &get;  
} 
elsif ($run) 
{
  # check input parameters
  error("feedback Necesito una única cantidad, entera o decimal") unless (@numbers == 1);
  error("feedback Necesito una única fecha") unless (@dates == 1);
  error("feedback Necesito dos strings: un número de cuenta y un concepto") unless (@strings == 2);  
  &run;
} 

sub get {
  print("          ingreso /de <float>/<integer> /el /día <date> /en /la /cuenta <string> <string>\n");
  print("--payment pago /de <float>/<integer> /el /día <date> /en /la /cuenta <string> <string>\n");
}

sub run {
  my $date = @dates[0];
  my $amount = @numbers[0];
  $amount = "-" . $amount if ($payment);
  my $account = @strings[0];
  my $what = @strings[1];
  print("message dst=banking&tag=entry&date=$date&amount=$amount&account=$account&what=$what\n");  
}

