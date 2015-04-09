# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

PATH=$PATH:$HOME/bin

export PATH

export LESS="X R"
export EDITOR="vim"
export VISUAL="$EDITOR"

# for use with SBT. If something doesn't work, comment this shit out
# export SBT_OPTS="-XX:+CMSClassUnloadingEnabled -XX:MaxPermSize=256M"

# for aws completion
complete -C aws_completer aws

# a simple http server when you need one
server() {
  open "http://localhost:${1}" && python -m SimpleHTTPServer $1
}

promptFunc() { 
  case $TERM in
    xterm*|rxvt*|screen*) 
      PS1="\[\033[0;32m\][\D{%a, %H:%M}] \[\033[1;34m\]\u@\H\[\033[0m\]:\[\033[1;37m\]\n\w\[\033[0m\] " ;; 
    *)  
      PS1="[\A] \u@\H:\w " ;;
  esac
 
  PS1="${PS1}"
 
  #append a red [root] if we are root
  if [ `whoami` == "root" ]; then 
    PS1="\n$PS1\[\033[31m\][root]\[\033[0m\] "
  fi
 
  PS1="${PS1}\$ "
}

PROMPT_COMMAND=promptFunc

# no double entries in the shell history
export HISTCONTROL="$HISTCONTROL erasedups:ignoreboth"

# wrap these commands for interactive use to avoid accidental overwrites.
rm() { command rm -i "$@"; }
cp() { command cp -i "$@"; }
mv() { command mv -i "$@"; }

# do not overwrite files when redirecting output by default.
set -o noclobber
