import subprocess
import sys


if __name__ == '__main__':
    cmd = ['python', '-m', 'wrapper', 'enc_clingo-dl_lex-makespan_v2.lp', 'instances/1_2_2_L.lp', '0', '2', '0', '0', '--backprop:F','yes','--enum-mode','auto','--eq','121','--eq-dfs:F','yes','--learn-explicit:F','no','--no-gamma:F','yes','--opt-strategy','usc','--sat-prepro:S','yes','--solver','clingo-dl','--trans-ext','all','--opt-strategy:1','k','--opt-strategy:3','succinct','--sat-prepro:0','1','--sat-prepro:1:frozen','27','--sat-prepro:1:iter','2','--sat-prepro:1:occ','24','--sat-prepro:1:size','2096','--sat-prepro:1:time','0','--opt-strategy:2','50']

    proc = subprocess.Popen(cmd,
                            stderr=sys.stderr,
                            stdout=sys.stdout
                            )
    proc.communicate()
