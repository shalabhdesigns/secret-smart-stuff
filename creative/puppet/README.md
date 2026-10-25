# Locked character library ("Sab Theek Hai")

How the characters stay identical from video 1 to video 1,000:

1. **Pose library = whole drawings.** Each pose (`assets/puppet/parts/dev_*`, `rocky_*`, `meera_*`) is one
   complete drawing, head and body together, drawn once with a blank face. Heads are **never** cut off or
   replaced at render time. (v2 did that and it caused neck seams, ghost outlines and torn collars.)
2. **Faces are drawn by code** (`scripts/puppet/puppet.py`, `FigureActor`): eyes, brows, mouth, glasses,
   moustache. Their positions come from the character's master head (`*_head*.png`), mapped onto each pose by
   outline matching (`scripts/puppet/align.py`, cached in `assets/puppet/parts/align_cache.json`).
   Poses with a slightly turned head carry hand-checked anchors (`feat`) in `creative/puppet/rig.json`;
   a drawn mouth is covered with skin via `paint`.
3. **Hair variants** (bowl cut, tuft) are baked once into new pose files (`dev_<pose>_bowl.png`,
   `dev_<pose>_tuft.png`) with `scripts/puppet/bake_variant.py`, then checked at full size.
4. **Head motion** is a soft bend about the base of the neck that fades to zero at the collar. No cut line
   exists, so no seam can appear.
5. **Sizes:** all poses of a character have the same head size. Characters keep real relative heights
   (`height` in rig.json): Dev 1.0, Rocky 0.95, Meera 0.9. Scene `size` = on-screen height (px) of a
   1.0-tall standing character. Someone seated in the barber chair is staged further back (smaller size).
6. **Adding a pose:** generate it from the master sheet, add it to rig.json, run
   `scripts/puppet/qa_faces.py rig.json out.jpg <pose>` and check the face at full size. Only then use it.
7. **Staging rules:** in wide and medium shots, people stand on the floor (`floor`), never float. The frame
   cuts a body only as a deliberate camera framing (waist-up, chest-up). Wide gestures (arms out) get a wide
   camera. Every shot is checked at 4+ frames before assembly.
