import setuptools

setuptools.setup(
    name='eggcounting',
    version='0.0.2',
    description='GUI for counting eggs',
    url='https://github.com/Tierpsy/EggCounting',
    author='Luigi Feriani',
    author_email='l.feriani@lms.mrc.ac.uk',
    license='MIT',
    packages=setuptools.find_packages(),
    package_data={"": ["*.qss"]},
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "create_timelapse="
            + "eggcounting.timelapse_tools.make_timelapse:"
            + "main",
            "count_eggs="
            + "eggcounting.count_eggs.EggCounter:"
            + "main",
            "add_wells_info="
            + "eggcounting.utils.add_wells_division:"
            + "add_wells_to_annotations",
            "add_wells_info_folder="
            + "eggcounting.utils.add_wells_division:"
            + "add_wells_to_annotations_in_folder",
        ]
    },
    )
