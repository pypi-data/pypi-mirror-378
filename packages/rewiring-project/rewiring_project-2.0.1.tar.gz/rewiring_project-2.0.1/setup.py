from setuptools import setup, find_packages

setup(
    name='rewiring_project',
    version='2.0.1',
    author='Niek Mooij',
    author_email='mooij.niek@gmail.com',
    description='All code used in the rewiring project.',
    classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent'],
    packages=find_packages(),
    install_requires=[
        'networkx',
        'numpy',
        'scipy',
    ],
    entry_points={
        'console_scripts': [
            'erdos_renyi=rewiring_project.generate_graphs.erdos_renyi:main',
            'random_bipartite=rewiring_project.generate_graphs.random_bipartite:main',
            'random_geometric=rewiring_project.generate_graphs.random_geometric:main',
            'barabasi_albert=rewiring_project.generate_graphs.barabasi_albert:main',
            'random_regular=rewiring_project.generate_graphs.random_regular:main',
            'uniform_graph=rewiring_project.generate_graphs.uniform_graph:main',
            'watts_strogatz=rewiring_project.generate_graphs.watts_strogatz:main',
            'get_first_bifurcation=rewiring_project.get_first_bifurcation:main',
            'optimise_clustering=rewiring_project.optimise_clustering.optimise_clustering:main',
            'optimise_coupling=rewiring_project.optimise_coupling.optimise_coupling:main'    
        ]
        ,
    },
)