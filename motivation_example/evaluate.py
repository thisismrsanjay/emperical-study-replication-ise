from Utils import util
import pandas as pd

project_name_list=[
"abinit",
"accumulo",
"activemq",
"amber",
"angular.js",
"ant",
"argouml",
"aspectj.eclipse.jdt.core",
"bitcoin",
"buck",
"bugzilla",
"camel",
"columba",
"core",
"derby",
"flink",
"geronimo",
"gerrit",
"gimp",
"gwt",
"hadoop",
"hadoop-common",
"hbase",
"hoomd-blue",
"ITK",
"itextpdf",
"JDeodorant",
"jackrabbit",
"jaxen",
"jetty.project",
"jruby",
"lammps",
"libmesh",
"liferay-portal",
"linux",
"lucene-solr",
"mahout",
"maven",
"mdanalysis",
"OsmAnd",
"openjpa",
"openstack",
"pcmsolver",
"perl5",
"pig",
"postgres",
"qtbase",
"RMG-Py",
"rails",
"rhino",
"spring-framework",
"synapse",
"tomcat",
"VTK",
"voldemort",
"xenon",
"xorg-xserver",
"xstream"
]

D_name = {
"ITK": "ITK",
"JDeodorant": "JDeodorant",
"OsmAnd": "OsmAnd",
"RMG-Py": "RMG-Py",
"VTK": "VTK",
"abinit": "ABINIT",
"accumulo": "Accumulo",
"activemq": "ActiveMQ",
"amber": "Amber",
"angular.js": "AngularJS",
"ant": "Ant",
"argouml": "ArgoUML",
"aspectj.eclipse.jdt.core": "Eclipse JDT",
"bitcoin": "Bitcoin",
"buck": "Buck",
"bugzilla": "Bugzilla",
"camel": "Camel",
"columba": "Columba",
"core": "LibreOffice",
"derby": "Derby",
"flink": "Flink",
"geronimo": "Geronimo",
"gerrit": "Gerrit",
"gimp": "Gimp",
"gwt": "GWT",
"hadoop": "Hadoop",
"hadoop-common": "Hadoop Common",
"hbase": "HBase",
"hoomd-blue": "HOOMD-blue",
"itextpdf": "iText",
"jackrabbit": "Jackrabbit",
"jaxen": "Jaxen",
"jetty.project": "Jetty",
"jruby": "JRuby",
"lammps": "LAMMPS",
"libmesh": "libMesh",
"liferay-portal": "Liferay Portal",
"linux": "Linux",
"lucene-solr": "Lucene-Solr",
"mahout": "Mahout",
"maven": "Maven",
"mdanalysis": "MDAnalysis",
"openjpa": "OpenJPA",
"openstack": "OpenStack",
"pcmsolver": "PCMSolver",
"perl5": "Perl 5",
"pig": "Pig",
"postgres": "PostgreSQL",
"qtbase": "Qt Base",
"rails": "Rails",
"rhino": "Rhino",
"spring-framework": "Spring Framework",
"synapse": "Synapse",
"tomcat": "Tomcat",
"voldemort": "Voldemort",
"xenon": "Xenon",
"xorg-xserver": "X server",
"xstream": "XStream"
}

def compute_proportion(p_name, data):

    cnt = 0
    for commit_hash in data.keys():
        temp = 0
        for key in data[commit_hash].keys():
            if len(data[commit_hash][key]) > 0:
                temp += 1

        if temp != 0:
            cnt += 1

    print("proportion: {0} ({1:,}/{2:,})".format(round(cnt/len(data), 3),
                                                       cnt, len(data)))

    pro = ("%03.1f" % (100*round(cnt/len(data), 3))) + " ({0:,}/{1:,})".format(cnt, len(data))
    if cnt/len(data) >= 0.8:
        pro = '\\cellcolor{yellow}{' + pro + '}'
    elif cnt/len(data) < 0.5:
        pro = '\\cellcolor{cyan}{' + pro + '}'

    row = [D_name[p_name], "{0}\\\\".format(pro)]


    return row

def main():

    print("Number of extracted projects: {0}".format(len(project_name_list)))

    TABLE = []

    for p_name in project_name_list:
        data = util.load_pickle("./data/{0}_commit2issue.pickle".format(p_name))

        print("\n{0}".format(p_name))
        TABLE.append(compute_proportion(p_name, data))

    #column_index = ["Project", "Proportion", "Clone Date\\\\"]
    column_index = ["Project", "Proportion"]
    TABLE = pd.DataFrame(TABLE,columns=column_index)
    TABLE.to_csv(path_or_buf='./tables/link_proportion.csv', index=False, sep="&")


if __name__=="__main__":
    main()
