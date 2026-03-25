# Affine
Plugin that handles registering images to mask files by detecting keypoints using SIFT or ORB and matching them to the corresponding points in the mask files. 

## Public API

`def positioning_coords(self, coords: tuple[float, float]) -> tuple[int, tuple[float, float]]`
Given mask coordinates, transforms them into camera reference frame. Returns status, coordinates as tuple. On error returns coords (-1,-1).

`def positioning_measurement_points(self)`
Returns tuple of status code and an inner tuple of points, names defined in the list widget. 

`def parse_settings_widget(self):`
Returns status, settings. Also fills to internal settings.

`def setSettings(self, settings: dict):`
Sets internal settings and schedules gui update. 

## Usage
Not to be used as part of sequences, but instead as dependency for plugins that coordinate movement, such as affineMove. 

TODO: what to include here?