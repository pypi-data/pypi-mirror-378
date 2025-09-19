# SPDX-License-Identifier: MIT
#
# Copyright Red Hat
# Author: David Gibson <david@gibson.dropbear.id.au>

EXETER_MANIFEST=""

exeter_check_testid() {
    local testid="$1"
    if ! expr "$testid" : '[a-zA-Z0-9.;_][a-zA-Z0-9.;_]*$' > /dev/null ; then
	echo "exeter(sh): Bad test id \"$testid\"" >&2
	exit 99
    fi
}

exeter_register() {
    local testid="$1"
    shift

    exeter_check_testid "$testid"
    local cmd="$(eval '$EXETER_TEST_'$testid)"
    if [ -n "$cmd" ] ; then
       echo "exeter(sh): Duplicate test id \"$testid\"" >&2
       exit 99
    fi
    EXETER_MANIFEST="$EXETER_MANIFEST $testid"
    if [ -n "$*" ] ; then
	eval "EXETER_TEST_$testid=\"$@\""
    else
	eval "EXETER_TEST_$testid=\"$testid\""
    fi
}

exeter_set_description() {
    local testid="$1"
    local description="$2"

    exeter_check_testid "$testid"
    local cmd="$(eval 'echo $EXETER_TEST_'$testid)"
    if [ -z "$cmd" ]; then
        echo "exeter(sh): Nonexistent test \"$testid\"" >&2
        exit 99
    fi

    eval "EXETER_DESC_$testid=\"\$description\""
}

exeter_usage() {
    local exename="$0"
    cat <<EOF
Usage: ${exename} [OPTIONS] <testcase id>

Exeter (sh) based tests.

Options:
    --exeter         display protocol version and exit
    --help           display this help and exit
    --list           list test cases and exit
    --metadata <id>  output metadata for test case and exit
EOF
}

exeter_cmd() {
    local testid="$1"
    exeter_check_testid "$testid"
    eval 'echo $EXETER_TEST_'"$testid"
}

exeter_list() {
    local list="$EXETER_MANIFEST"
    if [ -n "$*" ]; then
	list="$@"
    fi

    for testid in $list; do
	local cmd=$(exeter_cmd "$testid")
	if [ -z "$cmd" ]; then
	    echo "exeter (sh): Nonexistent test \"$testid\"" >&2
	    exit 99
	fi
	echo "$testid"
    done
}

encode_value() {
    local value="$1" result="" char

    while [ -n "$value" ]; do
        char="${value%"${value#?}"}"
        value="${value#?}"

        case "$char" in
            '\\')
                result="${result}\\\\\\\\"
                ;;
            *)
                if [ "$char" = "$(printf '\n')" ]; then
                    result="${result}\\n"
                elif [ "$char" = "$(printf '\0')" ]; then
                    result="${result}\\0"
                else
                    result="${result}${char}"
                fi
                ;;
        esac
    done

    printf '%s' "$result"
}

exeter_metadata() {
    local testid="$1"
    exeter_check_testid "$testid"

    local cmd=$(exeter_cmd "$testid")
    if [ -z "$cmd" ]; then
	echo "exeter (sh): Nonexistent test \"$testid\"" >&2
	exit 99
    fi

    # Output description if set
    local desc="$(eval 'echo $EXETER_DESC_'$testid)"
    if [ -n "$desc" ]; then
        printf 'description='
        encode_value "$desc"
        printf '\n'
    fi
}

exeter_run() {
    local testid="$1"
    exeter_check_testid "$testid"

    local cmd=$(exeter_cmd "$testid")
    if [ -z "$cmd" ]; then
	echo "exeter (sh): Nonexistent test \"$testid\"" >&2
	exit 99
    fi
    $cmd
    exit $?
}

exeter_main() {
    local exename="$0"
    local testid="$1"

    case "$testid" in
	"--exeter")
	    echo "exeter test protocol 0.4.1"
	    exit 0
	    ;;
	"--help"|"")
	    exeter_usage "$exename"
	    exit 0
	    ;;
	"--list")
	    shift
	    exeter_list "$@"
	    exit 0
	    ;;
	"--metadata")
	    if [ $# -ne 2 ]; then
		exeter_usage "$exename" >&2
		exit 99
	    fi
	    exeter_metadata "$2"
	    exit 0
	    ;;
	*)
	    exeter_run "$@"
	    ;;
    esac

    exeter_usage "$exename" >&2
    exit 99
}
