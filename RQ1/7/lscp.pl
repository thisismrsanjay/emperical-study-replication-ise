#!/usr/bin/perl

use warnings;
use strict;
use lscp;

my $preprocessor = lscp->new;

$preprocessor->setOption("logLevel", "error");
$preprocessor->setOption("inPath", "tmp/in");
$preprocessor->setOption("outPath", "tmp/out");

$preprocessor->setOption("isCode", 1); # processing source code (0: not source code)
$preprocessor->setOption("doIdentifiers", 1); # extract identifiers
$preprocessor->setOption("doStringLiterals", 0); # don't extract string literal (e.g., "XXX")
$preprocessor->setOption("doComments", 0); # don't process comments

$preprocessor->setOption("doRemoveDigits", 1); # remove numbers
$preprocessor->setOption("doLowerCase", 1); # make them to lower case
$preprocessor->setOption("doStemming", 0); # don't stem words
$preprocessor->setOption("doTokenize", 1); # separate some words (e.g,. camel case or snake calse etc.: camelCase,under_scores,dot.notation etc.)
$preprocessor->setOption("doRemovePunctuation", 1); # remove punctuation
$preprocessor->setOption("doRemoveSmallWords", 1); # remove small words?
$preprocessor->setOption("smallWordSize", 1);  # if doRemoveSmallWords is 1, decide the number of small word (in this case, one character words would be removed)
$preprocessor->setOption("doStopwordsEnglish", 1); # remove stop words
$preprocessor->setOption("doStopwordsKeywords", 1); # remove stop words in programing language

$preprocessor->preprocess();
