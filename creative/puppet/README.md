# Locked character library ("Sab Theek Hai")

How the characters stay identical from video 1 to video 1,000:

1. **Master heads** (`assets/puppet/parts/*_head_*.png`, `rocky_head.png`, `meera_head.png`) are drawn once with
   blank faces. Every video uses these exact files. Eyes, brows, mouths, glasses and the moustache are drawn by
   code (`scripts/puppet/puppet.py`), so expressions never change the design.
2. **Pose library** (`dev_*`, `rocky_*`, `meera_*` full-body figures) is drawn once per pose, from the master
   sheets, with correct proportions. In the video the drawn head is removed (skin/hair pixels above the chin only;
   clothing is never touched) and the master head is placed on top, scaled to the face width.
3. **Videos never redraw characters.** A new pose or outfit is added only after `scripts/puppet/posecheck.py`
   renders it with the master head and it passes a visual check (proportions, neck join, no clipped clothing).
   Rejected so far: `meera_pockets` (tilted head merges into the shoulders).
4. **Staging rules:** full figures stand on the floor in wide shots; nothing is cut by the frame edge except in
   deliberate close-ups, which crop at the chest.

Relative sizes (`face_scale` in rig.json): Dev 1.0, Rocky 1.21, Meera 0.83 (all on-screen sizes are Dev-equivalent).
