#/usr/bin/env bash
_xnd_tools_completions()
{
local cur prev opts base
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    #
    #  The basic options we'll complete.
    #
    opts="config kernel module"

    #
    #  Complete the arguments to some of the basic commands.
    #
    case "${prev}" in
        kernel)
            #local running=$(for x in `xm list --long | grep \(name | grep -v Domain-0 | awk '{ print $2 }' | tr -d \)`; do echo ${x} ; done )
	    local lst=$(for x in `ls *.cfg`; do echo ${x} ; done )
            COMPREPLY=( $(compgen -W "${lst}" -- ${cur}) )
            return 0
            ;;
	     *)
        ;;
    esac

   COMPREPLY=($(compgen -W "${opts}" -- ${cur}))  
   return 0
}


complete -F _xnd_tools_completions xnd_tools
