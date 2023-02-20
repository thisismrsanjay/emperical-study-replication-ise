import subprocess
import sys


def execute_bouffier_java():
    subprocess.run(['docker-compose', 'run', '--rm', '-v', '{{absolute path}}RQ1/8/bouffier-java/tmp:/bouffier-java-project', 'parse'], cwd="./bouffier-java/")


if __name__=="__main__":
    execute_bouffier_java()


