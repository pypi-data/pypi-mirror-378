from setuptools import setup, find_packages

setup(
    name='mcp-judge',
    version='0.1.2',
    author='Nilavo Boral',
    author_email='nilavoboral@gmail.com',
    description='An interactive application for testing MCP tools.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    project_urls={
        "LinkedIn": "https://www.linkedin.com/in/nilavo-boral-123bb5228/"
    },
    # url='https://github.com/yourusername/mcp-judge-app',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit==1.49.1',
        'fastmcp==2.12.3',
    ],
    entry_points={
        'console_scripts': [
            'mcp-judge = mcp_judge.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.11',
)