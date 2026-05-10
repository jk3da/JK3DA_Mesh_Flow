================================================================
JK3DA Mesh Flow — Blender Add-on
================================================================

Version: 0.1.0 Alpha
Author: JK3DA
Website: https://jk3da.com

License: GPL-3.0
Commercial Support License available separately.

AI-assisted development using Claude (Anthropic)
and GitHub Copilot.

================================================================
OVERVIEW
================================================================

JK3DA Mesh Flow is a topology and edge-flow toolkit
for Blender 4.0+.

The add-on focuses on fast mesh cleanup, circularization,
spacing tools, and topology alignment workflows commonly
used in hard-surface modeling, retopology, and production
mesh editing.

Mesh Flow is inspired by traditional edge-flow workflows
and tools such as Blender LoopTools, while aiming for a
faster and more modern workflow integration.

This project is currently in active development.

================================================================
CURRENT DEVELOPMENT STATUS
================================================================

Implemented
------------
- Circle Tool
    Convert edge loops into clean circular shapes

- Straighten Tool (experimental)
    Align selected vertices into straighter edge flow

- Spacing Tool (experimental)
    Redistribute vertex spacing evenly across selections

Work In Progress
----------------
Some tools are still experimental and may produce
unexpected results depending on topology complexity.

Straighten and Spacing are currently considered unstable
and may change significantly during development.

================================================================
FEATURES
================================================================

Circle Tool
------------
- Circularize selected edge loops
- Useful for:
    - holes
    - cylinders
    - mechanical topology
    - cleanup workflows

Straighten Tool (Experimental)
------------------------------
- Straighten edge flow along a direction
- Improve topology readability
- Useful for hard-surface cleanup

Spacing Tool (Experimental)
---------------------------
- Evenly redistribute vertices
- Improve edge consistency
- Useful for retopology and deformation preparation

Workflow Integration
--------------------
- Designed for fast modeling workflows
- Lightweight UI
- Blender-native interaction style

================================================================
INSTALLATION
================================================================

1. Open Blender
2. Go to:
     Edit → Preferences → Add-ons
3. Click:
     Install...
4. Select:
     jk3da_meshflow.zip
5. Enable:
     "JK3DA Mesh Flow"
6. Open the N-Panel:
     JK3DA Mesh Flow tab

================================================================
REQUIREMENTS
================================================================

- Blender 4.0 or newer

================================================================
KNOWN LIMITATIONS
================================================================

This add-on is currently in alpha development.

Some tools may:
  - behave inconsistently on complex topology
  - fail on non-manifold meshes
  - produce unexpected alignment results

Always save your work before using experimental tools.

================================================================
LICENSE
================================================================

JK3DA Mesh Flow is licensed under the GNU General Public
License v3.0 (GPL-3.0).

This means you are free to:
  - use the software commercially
  - modify the source code
  - redistribute the software
  - create derivative works

A separate optional Commercial Support License is available
for studios and companies requiring formal procurement or
production documentation.

See:
  LICENSE_Commercial.txt

Full GPL license:
https://www.gnu.org/licenses/gpl-3.0.html

================================================================
CREDITS
================================================================

Developed by JK3DA
https://jk3da.com

Inspired by traditional edge-flow workflows and modeling tools.

AI-assisted development using:
  - Claude (Anthropic)
  - GitHub Copilot

All design direction, implementation decisions,
testing, and validation were performed by JK3DA.