# EggCounting

Simple GUI (courtesy of ver228) to annotate eggs in videos.

### Installation
``` bash
cd ~/behavgenom_repos
git clone https://github.com/Tierpsy/EggCounting.git
conda create -n eggscounting
conda activate eggscounting
conda install pandas pytables numpy pyqt opencv -c conda-forge
```

### Launch
```bash
conda activate eggscounting
python ~/behavgenom_repos/EggCounting/count_eggs/EggCounter.py
```
To create a desktop launcher:
* put the two lines above into a text file on the desktop, called `eggcounter.command`
* make the file executable, by opening a terminal and typing: `cd ~/Desktop; chmod +x eggcounter.command`

Double-clicking `eggcounter.command` will launch the GUI.

### Usage
Drag and drop a MaskedVideo in the Select File field.  
Double-click on an egg to mark its position.  
Double-click on an erroneous annotation to delete it.  
Make sure all eggs are annotated.
Move to the next frame by either using the slider or the spin box (don't use the `Play` button on MaskedVideos).  
You can see eggs annotated in the previous frame by ticking the `Show Prev Eggs` tick box (they'll be marked with a blue `o`).  
Carry all the annotations from the previous frame to the current frame, using the `Copy Prev` button.  
**Important:** Make sure that all eggs are still in the same position as they were in the last frame: if you spot an annotation with no actual egg, remove the annotation from the current frame and mark the updated position of the egg instead. If in a frame a pre-existing egg is hidden by a worm, it should not be marked in that frame (i.e. if you cannot see an egg, there should not be a red mark).
Make sure that all eggs in the frame are annotated (red marks).
You can also copy all the annotations from the very first frame by clicking on the `Copy First` button.

Save your progress at any time with the SAVE button.
