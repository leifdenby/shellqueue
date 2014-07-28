# Shellqueue

`shellqueue` is a simple filesystem-based task queue, based around four folders:
`planning`, `scheduled`, `processing` and `completed`.

## How to use `shellqueue`

Init a `shellqueue` anywhere with

    > shellqueue init

And start the daemon

    > shellqueue daemon

Copy the entire contents of your current folder as a task into the `shellqueue`
(in `planning/`)

    > shellqueue clone

this will open up your editor where you define the manifest for your task, which
executable to run and the output folder.

Enqueue with

    > shellqueue enqueue
 
this will put your task in `scheduled/`

All processing tasks will be in `processing/`, and once completed will move to
`completed/`.
