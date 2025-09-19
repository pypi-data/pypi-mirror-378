# SPDX-License-Identifier: MIT
#
# Copyright Red Hat
# Author: David Gibson <david@gibson.dropbear.id.au>

exeter_srcs = files('exeter.sh')

# Examples & tests
trivial_name = 'trivial.sh'
trivial_src = files(trivial_name)

sh_examples = [ 'example.sh' ]

# Variables used by the top-level meson.build
trivial_examples += { 'sh' / trivial_name : trivial_src }

foreach name : sh_examples
  xpass = files(fs.stem(name) + '.pass')
  xfail = files(fs.stem(name) + '.fail')
  examples += { 'sh' / name : [files(name), xpass, xfail] }
endforeach
