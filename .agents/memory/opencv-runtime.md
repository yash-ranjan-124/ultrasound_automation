---
name: OpenCV runtime on Replit
description: Shared Python package environments may combine GUI and headless OpenCV wheels, requiring system XCB libraries.
---

When an OpenCV import reports missing `libxcb.so.1` in this repository, check the Replit runtime libraries as well as the Python dependency declaration. The workspace's shared `.pythonlibs` can contain both the imported root project's `opencv-python` and the backend's `opencv-contrib-python-headless`; the GUI wheel can still be the one Python loads.

**Why:** The headless dependency alone did not prevent `cv2` from loading the conflicting shared GUI wheel, which stopped API test collection and server startup.

**How to apply:** Install `xorg.libxcb` through the Replit system-dependency flow, then restart the workflows and verify `import cv2` from the backend environment. Keep the original prototype dependency intact unless a separately scoped migration asks to change it.