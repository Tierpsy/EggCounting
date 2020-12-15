# EggCounting

Simple GUI (courtesy of ver228) to annotate eggs in videos.

### Installation
```bash
cd ~/behavgenom_repos
git clone https://github.com/Tierpsy/EggCounting.git
conda env create -f environment.yml
conda activate eggcounting
pip install -e .
```

### Update an existing installation
```bash
cd ~/behavgenom_repos/EggCounting
git pull
conda env activate eggcounting
conda env update -f environment.yml
pip install -e .
```

### Launch
```bash
conda activate eggcounting
count_eggs
```
To create a desktop launcher:
* put the two lines above into a text file on the desktop, called `eggcounter.command`
* make the file executable, by opening a terminal and typing: `cd ~/Desktop; chmod +x eggcounter.command`

Double-clicking `eggcounter.command` will launch the GUI.

### Usage

#### Annotation GUI
Drag and drop a MaskedVideo in the Select File field.
Double-click on an egg to mark its position.
Double-click on an erroneous annotation to delete it.
Make sure all eggs are annotated.
Move to the next frame by either using the slider or the spin box (don't use the `Play` button on MaskedVideos).
You can see eggs annotated in the previous frame by ticking the `Show Prev Eggs` tick box (they'll be marked with a blue `o`).

Carry all the annotations from the previous frame to the current frame, using the `Copy Prev` button.
**Important:** Make sure that all eggs are still in the same position as they were in the last frame: if you spot an annotation with no actual egg, remove the annotation from the current frame and mark the updated position of the egg instead. If in a frame a pre-existing egg is hidden by a worm, it should not be marked in that frame (i.e. if you cannot see an egg, there should not be a red mark).
Make sure that all eggs in the frame are annotated (red marks).
You can also copy all the annotations from the very first frame by clicking on the `Copy First` button, or from the earliest annotated frame in the video (which could be after your current frame) by clicking on the `Copy Earliest` button.

Save your progress at any time with the SAVE button.

#### Tool to create timelapses
Command line tool to take a lot of small imgstore files with name matching
`_0000_YYYYMMDD_HHMMSS` and create a single timelapse hdf5 file compatible
with the GUI.
This tool only joins imgstores that exist in the same folder.
```bash
conda activate eggcounting
create_timelapse /path/to/folder/with/time/points
```

#### Tool to add well_name to annotations
When annotating videos that span more than one well in a multiwell plate,
it is useful to know which well an egg was in.
This tool adds that information to existing egg annotations.
To add well names to all annotations in a folder:
```bash
conda activate eggcounting
add_wells_info_folder --data_dir /path/to/folder/with/eggs.csv/and/.hdf5
```
To add well names to a single annotation file:
```bash
conda activate eggcounting
add_wells_info --annotations_fname /path/to/file/ending/in/eggs.csv
```
In both cases one can force the tool to find the well name from scratch
by appending `--ignore_old_well_names True` to the previous commands.

