# dockerize_EggCounting

Repo with instructions on how to make the EggCounting app into a Docker image,
and how to run it.

Build:
``` bash
docker build -t eggcounting .
```

(Add `--progress=plain` to read all output)

Run:
Get an X server (XQuartz for Mac), launch it,
enable "Allow connections from network clients", restart Xquartz.
credits:
https://medium.com/@mreichelt/how-to-show-x11-windows-within-docker-on-mac-50759f4b65cb

in the Terminal, add localhost to the list of allowed hosts for Xquartz:
``` bash
xhost + 127.0.0.1
```

Run the image
``` bash
docker run -e DISPLAY=host.docker.internal:0 -v ~/work_repos/EggCounting/data:/home/tierpsy_user/DATA eggcounting
```
