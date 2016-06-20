source /usr/share/autojump/autojump.bash

alias .2='cd ../../'
alias .3='cd ../../../'
alias ack='ack-grep -i --follow'
alias xo='xdg-open'
# last modified files
alias lmf="ls -lt | head -10"
# show toast message on completion
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'
alias sqlmagic="find -name '*.sql' | sort -V | xargs cat"
alias taillog='sudo less -nS /var/lib/postgresql/9.?/main/pg_log/$( sudo ls -t /var/lib/postgresql/9.?/main/pg_log | head -1 )'
alias gp='git pull --rebase'
alias gt='git status'
alias gd='git diff'
alias gdnp='git --no-pager diff'
alias gdc='git diff --cached'
alias gca='git commit -a'
alias gl='git --no-pager log -3'
alias zebra="nohup python /home/kmoppel/code/pgtools/pgzebra/src/web.py -c /home/kmoppel/code/pgtools/pgzebra/pgzebra.yaml.live &> /home/kmoppel/pgtools/pgzebra/pgzebra.log &"
alias dl='cd ~/Downloads'
alias temp='cd /data/temp'


function gup() {
    # goes into all subdirs and does a git pull --rebase on them if they have a .git folder
    echo "looking for subfolders with .git and doing pull..."
    for d in $( ls -d */ ) ; do
        if [[ -d "${d}.git" ]] ; then
            pushd . > /dev/null
            echo "** ${d} - git pull ..."
            cd "${d}"
            git pull --rebase
            popd > /dev/null
        fi 
    done
}

export PATH=$PATH:/home/kmoppel/code/pytools/codevalidator
# http://harelba.github.io/q/
export PATH=$PATH:/home/kmoppel/code/pgtools/q/bin
export PATH=$PATH:/home/kmoppel/code/pgtools/pgstats
export PATH=$PATH:/home/kmoppel/code/pgtools/pgbadger
export EDITOR="/usr/bin/vim"
export PAGER=less
export BROWSER=/usr/bin/google-chrome
export LESS='-i'
export T=/data/temp
export PGHOST=localhost
export PGUSER=kmoppel
export PGDATABASE=postgres

fortune | cowsay
