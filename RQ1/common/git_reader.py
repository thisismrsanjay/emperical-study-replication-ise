
import subprocess

def get_all_hash(repodir):
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '--all', '--pretty=format:%H'],
            universal_newlines=True
            ).splitlines()
    return hash_list

def get_all_hash_without_merge(repodir):
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '--all', '--no-merges', '--pretty=format:%H'],
            universal_newlines=True
            ).splitlines()
    return hash_list

def get_cur_entier_file(repodir, commit_hash, f_path):
    try:
        content = subprocess.check_output(
                ['git', '-C', '{}'.format(repodir), 'show', '{0}:{1}'.format(commit_hash, f_path)],
                universal_newlines=True
                )
    except UnicodeDecodeError:
        content = subprocess.check_output(
                ['git', '-C', '{}'.format(repodir), 'show', '{0}:{1}'.format(commit_hash, f_path)]
                ).decode('utf-8','replace')
    
    return content

def get_all_modified_files(repodir, commit_hash):
    files = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'diff-tree', '--no-commit-id',
            '--name-only', '-r', commit_hash,  '--diff-filter=ACMRTUX'],
            universal_newlines=True
            ).splitlines()
    
    return files

def git_log_all_without_merge(dirname):
    log = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'log', '--all', '--pretty=fuller', '--no-merges'],
            #['git', '-C', '{}'.format(dirname), 'log', '-10', '--pretty=fuller'],
            universal_newlines=True
            )
    return log
