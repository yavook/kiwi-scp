#!/bin/bash

function read_kiwi_config() {
   local conf_file="${1}"
   local conf_prefix="${2:-conf_}"

   local conf_file_content=$(sed -r 's/^\s*(\S+)/'${conf_prefix}'\1/g' "${conf_file}")
   eval "${conf_file_content}"
}

function write_kiwi_config() {
   local conf_prefix="${2:-conf_}"

   
}