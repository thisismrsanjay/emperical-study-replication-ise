from revlink import RLA
import argparse

def main():
    """ argument parser """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--project', '-p', type=str, required=True,
                        help='project name')
    parser.add_argument('--cregitrepo', '-c', type=str, required=True,
                        help='path/to/cregit/repository')
    parser.add_argument('--tempdir', '-t', type=str, required=True,
                        help='directory for a temporary file')
    parser.add_argument('--defectfixingcommitdir', '-d', type=str, required=True,
                        help='directory for defect fixing commit data')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='output database name')
    parser.add_argument('--delete', '-b', type=str, required=True,
                        help='delete rate')
    parser.add_argument('--ila', '-i', type=str, required=False, default=None,
                        help='issue linking algorithm data')

    args = parser.parse_args()
    p_name = args.project
    repo_dir = args.cregitrepo
    tempdir = args.tempdir
    defectfixingcommitdir = args.defectfixingcommitdir
    output = args.output
    delete_rate = args.delete
    ila = args.ila

    #print("{0},{1},{2},{3},{4},{5}".format(p_name, repo_dir, tempdir, defectfixingcommitdir, output, ila))
    rla_obj = RLA.RLA(p_name=p_name, repo_dir=repo_dir, out_dir=tempdir, issue2hash_dict_BASE_DIR=defectfixingcommitdir, db_path=output, target_ILA_num_list=ila, delete_rate=delete_rate)
    rla_obj.main()


if __name__=="__main__":
    main()

