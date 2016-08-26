#!/bin/Not a script, its only to include.

# Zoe Bash bindings
# Copyright (c) 2013 GUL UC3M
# Written by Roberto Muñoz <roberto@gul.es>
#
# LICENSE:
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

_zoe_bind_ip="127.0.0.1"
_zoe_bind_port="3000"

function _zoe_add_trap(){
  mytrap="$*"
  if trap|grep -v "''"|grep -q EXIT;then
    #Just in case we had a trap already setted...
    mytrap="$(trap|grep "EXIT$"|sed -e "s%trap -- '\(.*\)' EXIT$%\1;${mytrap//&/\\&}%g")"
  fi
  trap "$mytrap" EXIT
}
# Create temporary working dir or "context"
function zoe_init(){
  local tmpdir="$(mktemp -d)"
  _zoe_add_trap rm -rf $tmpdir 
  export _zoe_context=$tmpdir
}

function zoe_serve(){
  local CONTEXT=${1:-$_zoe_context}
  local IP=${2:-$_zoe_bind_ip}
  local PORT=${3:-$_zoe_bind_port}
  [ -e $CONTEXT/fifo ] && rm -rf $CONTEXT/fifo
  mkfifo $CONTEXT/fifo
  (zoe_action <$CONTEXT/fifo  |nc -kl  $IP $PORT > $CONTEXT/fifo ) &
  echo $! >> $CONTEXT/pids
  _zoe_add_trap "kill $! &>/dev/null"
}

function zoe_action(){
  while read linea;do
    zoe_do "$linea"
  done
}

# Get a line in first parameter and create variables according content
# If a variable is listed twice, then you get an array
# Example: if you call with "dst=paco&tag=hola&tag=adios&src=manolo"
#          you get 3 enviroment variables:
#          zoe_var_dst=paco
#          zoe_var_tag[0]=hola
#          zoe_var_tag[1]=adios
#          zoe_var_src=manolo

function zoe_parse(){

  CONTEXT=$_zoe_context
  zoe_cleanvars;
  if echo "$1" |tr -d "\r\n" |grep -q "^[a-zA-Z0-9]\+=[a-zA-Z0-9%\*\.\-\_]*\([a-zA-Z0-9]\+=[a-zA-Z0-9%\*\.\-\_]*&\|&[a-zA-Z0-9]\+=[a-zA-Z0-9%\*\.\-\_]*\)*$";then #filter the data to only permited chars as GET parameters
    IFSBAKAP="$IFS"
    IFS="&"
    for i in ${1// /%20};do
      pre="${i%=*}"
      pos="${i#*=}"
      eval "zoe_var_$pre+=(\"${pos}\")" 
    done
    IFS="$IFSBAKAP"
  fi
}

function zoe_map(){
  CONTEXT=$_zoe_context
  local mapped=""
  for i in  ${!zoe_var*};do 
    j=0;
    k="$i[$((j++))]"
    while [ "${!k}" ];do 
      mapped+="&${i##zoe_var_}=${!k}"
      k="$i[$((j++))]"
    done
  done  
  echo "${mapped#&}"
}

function zoe_cleanvars(){
  unset ${!zoe_var*}
}

function zoe_stop(){
  CONTEXT=${1:-$_zoe_context}
  kill $(< $CONTEXT/pids) 
}
