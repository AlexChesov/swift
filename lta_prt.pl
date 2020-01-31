#!/usr/bin/perl
use strict;
use warnings;
#use experimental 'smartmatch';
use File::Basename;
use File::Copy;
use Time::localtime;


# for OSN messages 
# (1) copy_1 to folder: .../In/Nxx
# (2) if mess_type NOT [300|320] => copy_2 to folder .../In/

# for ISN messages
# (1) copy_1 to folder: .../Out/Nxx ACK and NAK together 
# (2) if mess_type NOT [300|320] => copy_2 to folder .../Out/ACK for ACKs or to folder: .../Out/NACK for NAKs

sub timestamp {
  my $t = localtime;
  return sprintf( "%04d-%02d-%02d %02d:%02d:%02d",
                  $t->year + 1900, $t->mon + 1, $t->mday,
                  $t->hour, $t->min, $t->sec );
}
sub today {
  my $t = localtime;
  return sprintf( "%04d-%02d-%02d", $t->year + 1900, $t->mon + 1, $t->mday,);
}

# Flip file to DOS
my $flip = "/usr/alliance/script/flip.linux -d $ARGV[1]";
system ($flip);

my $MessagePartner = $ARGV[0];
my $InputFile = $ARGV[1];
#---
my $dir_root_prt = "/mnt/dfs-it-app-XXI/SWIFT/Print/";

# my $dir_root_prt = "/mnt/dfs-it-app-XXI/SWIFT/Test/Print/";

# ISN - Input Sequence Number, Input to SWIFT, ACK or NAK
# "Out" dir - from ABS to SWIFT
my $dir_root_prt_isn = $dir_root_prt . "Out/";
my $dir_root_prt_ack = $dir_root_prt_isn . "ACK/";
my $dir_root_prt_nack = $dir_root_prt_isn . "NACK/";

# OSN - Output Sequence Number, Output from SWIFT
# "In" dir - input to ABS, received from SWIFT
my $dir_root_prt_osn = $dir_root_prt . "In/";

my $msg_cat_sfx = "xx/";
my $NewFile;
my $FiveXxTmp;
my $Tmp = "Tmp/";
	
my $LogFile = "/usr/alliance/script/log_lta/lta_" . $MessagePartner . "_";
my $LogFileExt = ".log";
#---
$/ = undef;

open INP_FILE, "<$InputFile" or die "cannot open input file\n";
binmode INP_FILE;
my $inp_text = <INP_FILE>;
close INP_FILE;

# --- get MT from file ---
my ($mtyp) = ($inp_text =~ / : FIN (\d{3})/gm);
my $doublecopy_flag = 0;

# check to make double copy to ACK and NACK folders for all categories ecxept 3xx
if ($mtyp !~ /300|320|0\d\d/) {
    $doublecopy_flag = 1;
}

# --- get other information from file ---

#[       Swift Input                   : ]
#[       Swift Output                  : ]
my $corr;
my $ssn_sqn;
my $nstat = "";
my $mdate = today();

my ($dirc) = ($inp_text =~ /Swift (\w{5,6})/gm);
if ($dirc eq "Output")
{
    $dirc = "O";
#[       Sender   : SABRRUMMXXX]
    ($corr) = ($inp_text =~ /Sender   : (\w{11})/gm);
#[       Message Output Reference  : 1715 180905TDBMMNU0AXXX0092000501]
#[       Message Output Reference : 1538 190815COMKRUM0AXXX0105000421]
    my $tmp;
    ($tmp, $mdate, $ssn_sqn) = ($inp_text =~ /Message Output Reference(.+)\d{4} (\d{6})\w{12}(\d{10})/gm);
}
elsif ($dirc eq "Input")
{
    $dirc = "I";
#[       Receiver : BKCHHKHHXXX]
    ($corr) = ($inp_text =~ /Receiver : (\w{11})/gm);

#[       Message Input Reference   : 1036 180803CAXBMNUBAXXX2575169526]
#[       Message Input Reference  : 1229 190815COMKRUM0AXXX0105000216]
    my $tmp;
    ($tmp, $mdate, $ssn_sqn) = ($inp_text =~ /Message Input Reference(.+)\d{4} (\d{6})\w{12}(\d{10})/gm);

# check first letter ACK or NAK?
#       Network Delivery Status  : Network Nack H51
#       Network Delivery Status  : Network Ack
# also for NAK can find substring like this: {451:1}{405:H51}
    ($nstat) = ($inp_text =~ /Network Delivery Status  : Network (\w{1})/gm);
}

# --- log file ---
$LogFile = $LogFile . today() . $LogFileExt;
my ($mp_sess) = (fileparse($InputFile) =~ /(\w+)\.prt/);
open LOG_FILE, ">>$LogFile";
print LOG_FILE "[" . timestamp() . "] Message Partner: $MessagePartner Session: $mp_sess\n";
print LOG_FILE "FileName: $InputFile\n";

# --- create copy_1 ---
if ($dirc eq "I") {
    $NewFile = $dir_root_prt_isn . substr($mtyp, 0,1) . $msg_cat_sfx . $mdate . "-" . $dirc . $mtyp . $corr . $ssn_sqn . "-$nstat" . ".prt";
}
elsif ($dirc eq "O") {
    $NewFile = $dir_root_prt_osn . substr($mtyp, 0,1) . $msg_cat_sfx . $mdate . "-" . $dirc . $mtyp . $corr . $ssn_sqn . ".prt";
}
print LOG_FILE "New File: $NewFile\n";
move($InputFile, $NewFile) or print LOG_FILE "ERROR: cannot move $InputFile to $NewFile\n";

# --- create copy_2 ---
if ($doublecopy_flag) {
    if (($dirc eq "I") && ($nstat eq "A") ){
        $NewFile = $dir_root_prt_ack . $mdate . "-" . $dirc . $mtyp . $corr . $ssn_sqn . "-$nstat" . ".prt";
    }
    elsif (($dirc eq "I") && ($nstat eq "N") ){
        $NewFile = $dir_root_prt_nack . $mdate . "-" . $dirc . $mtyp . $corr . $ssn_sqn . "-$nstat" . ".prt";
    }
    elsif ($dirc eq "O") {
#        $NewFile = $dir_root_prt_osn . substr($mtyp, 0,1) . $msg_cat_sfx . $mdate . "-" . $dirc . $mtyp . $corr . $ssn_sqn . ".prt";
         $NewFile = $dir_root_prt_osn . $mdate . "-" . $dirc . $mtyp . $corr . $ssn_sqn . ".prt";
    
        if (substr($mtyp, 0,1) eq "5") {
             $FiveXxTmp = $dir_root_prt_osn . substr($mtyp, 0,1) . $msg_cat_sfx . $Tmp . $mdate . "-" . $dirc . $mtyp . $corr . $ssn_sqn . ".prt";
             open FIVEXX_TMP, ">$FiveXxTmp" or  print LOG_FILE "ERROR: cannot open $FiveXxTmp to write\n";;
             binmode FIVEXX_TMP;
             print FIVEXX_TMP $inp_text;
             close FIVEXX_TMP;
             print LOG_FILE "New File: $FiveXxTmp\n";
        }
    }
    open NEW_FILE, ">$NewFile" or  print LOG_FILE "ERROR: cannot open $NewFile to write\n";;
    binmode NEW_FILE;
    print NEW_FILE $inp_text;
    close NEW_FILE;
    print LOG_FILE "New File: $NewFile\n";
    print LOG_FILE "------------------------\n";
}
close LOG_FILE;
unlink $InputFile;

