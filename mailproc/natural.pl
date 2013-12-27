#!/usr/bin/env perl

use Encode;
use MIME::QuotedPrint::Perl;
use Email::MIME;
use Email::Simple;
use Mail::Address;
use MIME::Base64;
use strict; 

# read the email from the file given as first argument
my $file = $ARGV[0];
local $/;
open(FILE, "<", $file);
my $document = <FILE>; 
close (FILE);

# header parser
my $headers = Email::Simple->new($document);

# extract sender
my $sender_line = $headers->header("From");
my @addrs = Mail::Address->parse($sender_line);
my $sender = $addrs[0]->address();

# extract message ID
my $message_id = $headers->header("Message-ID");

# extract the plain text and images from the email file
my @texts = ();
my @images = ();
process($document, \@texts, \@images);

# I'll concentrate only in the first text part
my $text = $texts[0];
$text =~ s/\r\n/\n/g;

# Right now, images are ignored

# Split text into command and extended text
my ($cmd, $longcmd) = $text =~ m/(.*?)\n\n+(.*).*/ms;
$cmd     = encode_base64($cmd, "");
$longcmd = encode_base64($longcmd, "");

# Don't forget the \n
print "src=mail&dst=natural&tag=command&cmd=$cmd&cmdext=$longcmd&sender=$sender&inreplyto=$message_id\n";




#
# Takes a raw email and extracts texts and images
# USAGE:
# 
#   process ($email, \@texts, \@images)
#
sub process {
  my $email = shift;
  my $texts_ref = shift;
  my $images_ref = shift;

  my $parsed = Email::MIME->new($email);
  my @flat = ();
  extract($parsed, \@flat);
 
  my @text_parts  = grep { $_->content_type =~ /text\/plain/ } @flat;
  my @image_parts = grep { $_->content_type =~ /image/ } @flat;
  
  for my $text_part (@text_parts) {
    my $t = $text_part->body_str;
    $t = encode("UTF-8", $t);
    push(@$texts_ref, $t);
  }
  
  for my $image_part (@image_parts) {
    push(@$images_ref, $image_part->body);
  }
}

#
# Extracts all parts from a multipart email into a single, flat array
# USAGE:
#
#   extract ($email, \@result)
#
sub extract {
  my $part = shift;
  my $flatref = shift;
  my $ct = $part->content_type;
  if ($ct =~ /multipart/) {
    my @subparts = $part->subparts;
    foreach my $p (@subparts) {
      my $mime = $p->content_type;
      my $len = $p->subparts;
      if ($len > 0) {
        extract($p, $flatref);
      } else {
        push(@$flatref, $p);
      }
    }
  } else {
    push(@$flatref, $part)
  }
}

