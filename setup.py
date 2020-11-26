import setuptools

setuptools.setup(
    name='eggcounting',
    version='0.0.1',
    description='GUI for counting eggs',
    url='https://github.com/Tierpsy/EggCounting',
    author='Luigi Feriani',
    author_email='l.feriani@lms.mrc.ac.uk',
    license='MIT',
    packages=setuptools.find_packages(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "create_timelapse="
            + "eggcounting.timelapse_tools.make_timelapse:"
            + "main",
            "count_eggs="
            + "eggcounting.count_eggs.EggCounter:"
            + "main"
        ]
    },
    )
