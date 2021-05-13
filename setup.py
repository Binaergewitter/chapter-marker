from setuptools import setup

setup(
    name="chapter-marker",
    description="chapter-marking utility",
    version="1.0.0",
    packages=["chapter_marker"],
    license="MIT",
    long_description=open("README.md").read(),
    author="Felix Richter",
    author_email="github@krebsco.de",
    install_requires=[
        "requests",
        "docopt",
        "pyqt5",
        "pynput",
        "notify2"
    ],
    package_data={'chapter_marker': ['res/*.png']},
    entry_points={"console_scripts": [
        "bgt-current-show = chapter_marker.bgt_current_show:main",
        "bgt-get-titles = chapter_marker.bgt_get_titles:main",
        "chapter-marker = chapter_marker.tray:main",
    ]},
    classifiers=[
        "Intended Audience :: Human",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
